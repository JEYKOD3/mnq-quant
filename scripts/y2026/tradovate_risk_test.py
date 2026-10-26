"""Tradovate platform risk settings test (Oct 25 2026).
Baseline: Lucid Flex 50K eval + funded (prop_plans), R9 recovery mode (recovery_test.VARIANTS['R9']), stop-day rules
(a) realized loss >= dayCap - $150, (c) 3 losers, (d) passed, engine daily budget dayCap = $1,050, and a platform daily
loss limit (DLL) of $1,150 on net P/L incl. open P/L and fees from the 18:00 ET session start.
Every platform limit liquidates all open positions at the first 1m touch and locks trading:
  dll  : day net P/L incl. open <= -dll                 -> flat at -dll, locked for the rest of the session
  wll  : week net P/L incl. open <= -wll                -> flat, locked for the rest of the week
  dpt  : day net P/L incl. open >= +dpt (profit trigger)-> flat at +dpt, locked for the rest of the session
  wpt  : week net P/L incl. open >= +wpt                -> flat, locked for the rest of the week
Fill model for a forced liquidation: the trigger level minus 1 tick (+ extra stress slippage) per open contract.
Loss checks run before profit checks inside the same 1m bar (conservative).
Week = 5 consecutive drawn days in the Monte Carlo, the ISO calendar week in the rolling check.
Run:  python tradovate_risk_test.py main | stress | roll
"""
import sys, json, random, statistics, datetime
import numpy as np
from prop_sim import *
from prop_sim import _PATH
from prop_plans import PLANS
from recovery_test import size_day_v, VARIANTS, pct

V9 = VARIANTS['R9']
INF = 1e18
BASE = dict(dcap=1050, dll=1150, wll=None, dpt=None, wpt=None)
LUCID = [p for p in PLANS if (p['firm'], p['plan']) == ('Lucid Trading', 'LucidFlex')][0]

def newS(): return dict(rec=False, entries=0, rec_tr=0, rec_skip=0, rec_days=0, run=0, maxrun=0, minroom=1e9)
def newC(): return dict(trig_dll=0, trig_wll=0, trig_dpt=0, trig_wpt=0, forced=0, forced_win=0, forced_lose=0,
                        forced_dll=0, forced_dll_before_stop=0, tie_L=0, tie_U=0, skipped=0, skipped_win=0, foregone=0.0, locked_days=0)

def run_day_t(trs, bal, floor, P, prof0, best0, maxq, S, slipx, PS, W, C, target=None, cons=None, mindays_ok=True):
    """one session under the platform settings PS. W = week state (pnl, locked). C = counters. Returns (dp, status, minroom)."""
    cush = bal - floor
    if W['locked']:
        if trs: C['locked_days'] += 1
        return 0.0, 'ok', cush
    L = min(PS['dll'] or INF, (PS['wll'] + W['pnl']) if PS['wll'] else INF)
    U = min(PS['dpt'] or INF, (PS['wpt'] - W['pnl']) if PS['wpt'] else INF)
    kw = dict(dll=PS['dcap'], slipx=slipx, prof0=prof0, best0=best0, maxq=maxq,
              target=target if target is not None else 1e18, cons=cons if cons is not None else 1.0, mindays_ok=mindays_ok)
    S0 = dict(S)
    done = size_day_v([dict(t) for t in trs], cush, V9, S0, **kw)
    lo, hi = day_path(done)
    if lo is None:
        S.update(S0); return 0.0, 'ok', cush
    iL = np.nonzero(lo <= -L)[0]; iU = np.nonzero(hi >= U)[0]
    hL = int(iL[0]) if len(iL) else None; hU = int(iU[0]) if len(iU) else None
    if hL is None and hU is None:
        S.update(S0)
        dp = sum(t['netq'] for t in done)
        if np.any(bal + lo <= floor): return float(lo.min()), 'fail', cush + float(lo.min())
        W['pnl'] += dp
        return dp, 'ok', cush + float(lo.min())
    kind = 'L' if (hL is not None and (hU is None or hL <= hU)) else 'U'
    h = hL if kind == 'L' else hU
    # real-time floor breach before the trigger bar
    if h > 0 and np.any(bal + lo[:h] <= floor): return float(lo[:h].min()), 'fail', cush + float(lo[:h].min())
    orig = {(t['strat'], t['eT'], t['side']): t['netq'] for t in done}
    dp0 = sum(t['netq'] for t in done)
    # second pass: only trades entered at or before the trigger bar (sizing of earlier trades is unchanged)
    keep = [dict(t) for t in trs if t['eT'] - G0 <= h]
    done2 = size_day_v(keep, cush, V9, S, **kw)
    nopen = 0
    for t in done2:
        if t['q'] <= 0: continue
        A, F, x = path_arrays(t)
        if max(0, t['eT'] - G0) <= h < x:
            nopen += t['q']; C['forced'] += 1
            if orig[(t['strat'], t['eT'], t['side'])] > 0: C['forced_win'] += 1
            else: C['forced_lose'] += 1
            if kind == 'L': C['forced_dll'] += 1
            if kind == 'L' and t['why'] in STOPWHY and t['netq'] < 0: C['forced_dll_before_stop'] += 1
    for t in done:
        if t['q'] > 0 and t['eT'] - G0 > h:
            C['skipped'] += 1
            if t['netq'] > 0: C['skipped_win'] += 1
    liq = nopen * (SLIP * T + (slipx - 8.0)) * PV
    if nopen == 0:
        # the line was crossed by a fill (stop or target) on the trigger bar: nothing to liquidate, the fill stands,
        # the platform only locks the rest of the session
        C['tie_' + kind] += 1
        dp = float(lo[h])
        if kind == 'L':
            weekly = PS['wll'] and (PS['wll'] + W['pnl']) <= (PS['dll'] or INF)
            C['trig_wll' if weekly else 'trig_dll'] += 1
        else:
            weekly = PS['wpt'] and (PS['wpt'] - W['pnl']) <= (PS['dpt'] or INF)
            C['trig_wpt' if weekly else 'trig_dpt'] += 1
    elif kind == 'L':
        dp = -L - liq
        weekly = PS['wll'] and (PS['wll'] + W['pnl']) <= (PS['dll'] or INF)
        C['trig_wll' if weekly else 'trig_dll'] += 1
    else:
        dp = U - liq
        weekly = PS['wpt'] and (PS['wpt'] - W['pnl']) <= (PS['dpt'] or INF)
        C['trig_wpt' if weekly else 'trig_dpt'] += 1
    if weekly: W['locked'] = True
    C['foregone'] += dp0 - dp
    W['pnl'] += dp
    mn = float(min(lo[:h + 1].min(), dp)) if kind == 'L' else float(lo[:h + 1].min())
    if bal + dp <= floor: return dp, 'fail', cush + mn
    return dp, 'ok', cush + mn

def weeks_mc(H): return [i // 5 for i in range(H)]
def weeks_cal(seq): return [datetime.date(d // 10000, d // 100 % 100, d % 100).isocalendar()[:2] for d in seq]

def eval_t(byd, seq, wk, plan, PS, slipx=8.0, H=120):
    E = plan['eval']; start = 50000.; bal = start; peak = start; best = 0.; n = 0
    tgt = E['target']; cons = E['cons'] or 1.0; mind = E.get('min_days', 0) or 0
    S = newS(); C = newC(); W = dict(pnl=0., locked=False, id=None); first_tgt = None
    for d, w in zip(seq[:H], wk[:H]):
        n += 1
        if w != W['id']: W.update(pnl=0., locked=False, id=w)
        fl = floor_eod(E, peak)
        dp, st, mn = run_day_t(byd.get(d, []), bal, fl, E, bal - start, best, E['maxq'], S, slipx, PS, W, C, target=tgt, cons=cons, mindays_ok=n >= mind)
        S['minroom'] = min(S['minroom'], mn)
        if st == 'fail': return 'F', n, S, C, None, best
        bal += dp; best = max(best, dp)
        if bal <= floor_eod(E, peak): return 'F', n, S, C, None, best
        peak = max(peak, bal)
        prof = bal - start
        if prof >= tgt and first_tgt is None: first_tgt = n
        if prof >= tgt and best <= cons * prof and n >= mind: return 'P', n, S, C, first_tgt, best
    room = bal - floor_eod(E, peak)
    return ('S' if room < 400 else 'O'), n, S, C, first_tgt, best

def funded_t(byd, seq, wk, plan, PS, slipx=8.0):
    Fp = plan['funded']; start = 50000.; bal = start; peak = start
    locked_floor = None; pays = []; qd = 0; cyc_days = 0; cyc_prof = 0.; cyc_best = 0.; first = None; n = 0
    S = newS(); C = newC(); W = dict(pnl=0., locked=False, id=None)
    for d, w in zip(seq, wk):
        n += 1
        if w != W['id']: W.update(pnl=0., locked=False, id=w)
        prof = bal - start; mq = maxq_for(Fp, prof)
        if locked_floor is not None: Pd = dict(Fp); Pd['dd'] = 'eod'; fl = locked_floor
        else: Pd = Fp; fl = floor_eod(Fp, peak)
        dp, st, mn = run_day_t(byd.get(d, []), bal, fl, Pd, -1e9, 0., mq, S, slipx, PS, W, C)
        S['minroom'] = min(S['minroom'], mn)
        if st == 'fail': return dict(res='bust', pays=pays, first=first, n=n, S=S, C=C)
        bal += dp
        cur_floor = locked_floor if locked_floor is not None else floor_eod(Fp, peak)
        if bal <= cur_floor: return dict(res='bust', pays=pays, first=first, n=n, S=S, C=C)
        peak = max(peak, bal)
        cyc_days += 1; cyc_prof += dp; cyc_best = max(cyc_best, dp)
        if dp >= (Fp.get('win_min') or 0) and dp > 0: qd += 1
        Q = Fp['pay']
        if len(pays) >= Q.get('max_n', 99): continue
        ok = qd >= (Q.get('win_days') or 0) and cyc_days >= (Q.get('min_cycle_days') or 1)
        ok = ok and cyc_prof >= (Q.get('cycle_min') or 0.01) and bal >= start + (Q.get('min_bal') or 0)
        if Q.get('cons'): ok = ok and cyc_best <= Q['cons'] * cyc_prof
        if not ok: continue
        caps = Q.get('caps') or [1e9]; cap = caps[min(len(pays), len(caps) - 1)]
        amt = min(cap, bal - (start + (Q.get('keep') or 0)))
        if Q.get('frac'): amt = min(amt, Q['frac'] * ((bal - start) if Q.get('frac_base', 'total') == 'total' else cyc_prof))
        if Q.get('cyc_mult'): amt = min(amt, Q['cyc_mult'] * cyc_prof)
        post = start + Q['floor_after'] if (Q.get('floor_after') is not None and locked_floor is None) else cur_floor
        amt = min(amt, bal - post - KEEP_ROOM)
        if amt < (Q.get('min_pay') or 0) or amt <= 0: continue
        bal -= amt; pays.append(amt); qd = 0; cyc_days = 0; cyc_prof = 0.; cyc_best = 0.
        if first is None: first = n
        if Q.get('floor_after') is not None:
            locked_floor = start + Q['floor_after'] if locked_floor is None else locked_floor
    return dict(res='open', pays=pays, first=first, n=n, S=S, C=C)

def agg(Cs, n):
    out = {}
    for k in newC():
        out[k] = round(100 * sum(c[k] for c in Cs) / n, 1) if k != 'foregone' else round(sum(c[k] for c in Cs) / n)
    return out     # per 100 runs (foregone: $ per run)

def sim_t(PS, tr, year, slipx=8.0, N=2000, NF=1000, H=120, seed=7, roll=False, plan=LUCID, fund_ps=None):
    byd = byday(tr); days = day_lists(year); wk = weeks_mc(H)
    rnd = random.Random(seed); R = []
    for _ in range(N):
        seq = [rnd.choice(days) for _ in range(H)]
        R.append(eval_t(byd, seq, wk, plan, PS, slipx, H))
    p = sum(r[0] == 'P' for r in R) / N; f = sum(r[0] == 'F' for r in R) / N; s = sum(r[0] == 'S' for r in R) / N
    P_ = [r[1] for r in R if r[0] == 'P']
    price = plan['eval']['price']
    tg = [r for r in R if r[4] is not None]
    delays = [r[1] - r[4] for r in R if r[0] == 'P']
    out = dict(p=round(p, 3), bust=round(f, 3), stuck=round(s, 3), open=round(1 - p - f - s, 3),
               med=statistics.median(P_) if P_ else None, p75=pct(P_, .75), cpf=round(price / p, 1) if p else None,
               reach_tgt=round(len(tg) / N, 3),
               cons_delayed=round(sum(d > 0 for d in delays) / max(1, len(delays)), 3),
               cons_delay_mean=round(statistics.mean(delays), 1) if delays else None,
               cons_delay_p90=pct(delays, .9),
               tgt_not_pass=round(sum(r[0] != 'P' for r in tg) / N, 3),
               best_med_pass=round(statistics.median([r[5] for r in R if r[0] == 'P'])) if P_ else None,
               minroom_min=round(min(r[2]['minroom'] for r in R)),
               ev=agg([r[3] for r in R], N))
    rnd = random.Random(seed + 4); M = []
    FPS = fund_ps or PS
    wkf = weeks_mc(120)
    for _ in range(NF):
        seq = [rnd.choice(days) for _ in range(120)]
        M.append(funded_t(byd, seq, wkf, plan, FPS, slipx))
    split = plan['funded']['pay'].get('split', .9)
    tot = [sum(x['pays']) for x in M]
    out.update(f_bust=round(sum(x['res'] == 'bust' for x in M) / NF, 3), f_got=round(sum(bool(x['pays']) for x in M) / NF, 3),
               f_first_med=statistics.median([x['first'] for x in M if x['first']]) if any(x['first'] for x in M) else None,
               f_trader=round(split * statistics.mean(tot)), f_minroom=round(min(x['S']['minroom'] for x in M)),
               fev=agg([x['C'] for x in M], NF))
    out['net_ev'] = round(out['f_trader'] - out['cpf']) if out['cpf'] else None
    if roll:
        allD = [d for d in D if year * 10000 + 101 <= d <= year * 10000 + 1231]
        RR = [eval_t(byd, allD[i:], weeks_cal(allD[i:]), plan, PS, slipx, H) for i in range(len(allD))]
        n = len(RR); PP = [r[1] for r in RR if r[0] == 'P']
        out.update(roll_p=round(sum(r[0] == 'P' for r in RR) / n, 3), roll_bust=round(sum(r[0] == 'F' for r in RR) / n, 3),
                   roll_stuck=round(sum(r[0] == 'S' for r in RR) / n, 3), roll_med=statistics.median(PP) if PP else None)
    return out

def V(**k): x = dict(BASE); x.update(k); return x
GRID = {
    'BASE': V(),
    'CAL_R9': V(dcap=1100, dll=None),                  # calibration: should equal RECOVERY_MODE_TEST R9 Lucid row
    'NO_DLL': V(dll=None),
    'WLL800': V(wll=800), 'WLL1000': V(wll=1000), 'WLL1300': V(wll=1300), 'WLL1600': V(wll=1600),
    'DPT900': V(dpt=900), 'DPT1100': V(dpt=1100), 'DPT1150': V(dpt=1150), 'DPT1400': V(dpt=1400),
    'WPT1500': V(wpt=1500), 'WPT2000': V(wpt=2000),
    'CAP1000': V(dcap=1000), 'CAP1100': V(dcap=1100),
    'BEST': V(wll=1600, dpt=1150),                     # recommended set (the profit trigger is removed once funded)
}
EVAL_ONLY = {'DPT900', 'DPT1100', 'DPT1150', 'DPT1400', 'WPT1500', 'WPT2000', 'BEST'}
def funded_of(PS): return dict(PS, dpt=None, wpt=None)   # 'eval only': profit triggers switched off in the funded account   # also scored with the trigger removed in funded
PATH = '/home/claude/mnq-quant/knowledge/src/tradovate_risk_test.json'
KEYS = ('p', 'bust', 'stuck', 'med', 'cpf', 'cons_delayed', 'cons_delay_mean', 'f_bust', 'f_trader', 'net_ev')

def main():
    tr = NEW()
    which = sys.argv[1] if len(sys.argv) > 1 else 'main'
    if which == 'main':
        OUT = dict(meta=dict(date='2026-10-25', base=BASE, plan='Lucid Flex 50K', recovery='R9', N=2000, NF=1000, H=120), res=[])
        for year in (2026, 2025, 2022):
            for k, PS in GRID.items():
                if year != 2026 and k == 'CAL_R9': continue
                r = sim_t(PS, tr, year, roll=(year == 2026))
                OUT['res'].append(dict(var=k, year=year, slip=0, ps=PS, **r))
                print(year, k, {x: r[x] for x in KEYS}, r['ev'], flush=True)
                if k in EVAL_ONLY:   # funded without the trigger: f_trader of BASE funded, cpf of this eval
                    r2 = sim_t(PS, tr, year, NF=1000, fund_ps=funded_of(PS))
                    OUT['res'].append(dict(var=k + '_EVALONLY', year=year, slip=0, ps=PS, **r2))
                    print(year, k + '_EVALONLY', {x: r2[x] for x in KEYS}, flush=True)
        json.dump(OUT, open(PATH, 'w'), indent=1, default=str)
    elif which.startswith('stress'):   # python tradovate_risk_test.py stress:BASE,WLL1600,...
        ks = which.split(':')[1].split(',')
        OUT = json.load(open(PATH)); OUT['res'] = [x for x in OUT['res'] if not x['slip']]
        for year in (2026, 2025, 2022):
            for k in ks:
                PS = GRID[k.replace('_EVALONLY', '')]
                fps = funded_of(PS) if k.endswith('_EVALONLY') else None
                r = sim_t(PS, tr, year, slipx=10.0, fund_ps=fps)
                OUT['res'].append(dict(var=k, year=year, slip=2, ps=PS, **r))
                print('STRESS', year, k, {x: r[x] for x in KEYS}, r['ev'], flush=True)
        json.dump(OUT, open(PATH, 'w'), indent=1, default=str)

if __name__ == '__main__':
    main()
