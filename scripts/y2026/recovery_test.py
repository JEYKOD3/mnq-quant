"""Recovery mode test (Oct 25 2026). Replaces stop-day rule (b) (hard stop when room above the max-loss line < $400) with a
1-MNQ recovery mode, on the prop_sim firm-rules simulator (NEW rule set, 65% of room, $1,100 budget, stop-day N=3 + (d)).

Variants
  BASE : current engine, rule (b) blocks all entries when room < $400; eval ends 'stuck' at a close with room < $400.
  R1   : room < $400 -> recovery: 1 MNQ on V4+, D2, H2 only, take a trade only if 1-contract risk <= live room - $100.
  R10  : R9 with entry threshold $600 (R5 + R9 combined).
         Normal sizing resumes when live room >= $700 (hysteresis).
  R2   : R1 with V4+ and H2 only.
  R3   : R1 with all strategies.
  R4   : R1 with risk cap live room - $200.
  R5   : R1 with entry threshold $600.
  R6   : no recovery mode, rule (b) removed: 65% of room sizing, min 1 contract only if 1-contract risk <= live room - $100.
  R7   : R3 without D2 and Pinball (lower minimum risk set: NEWS, V4+, TDP, H2).
  R8   : R7 restricted to trades whose 1-contract risk <= $150 (H2 and NEWS mostly).
  R9   : R3 plus the R6 guard in normal mode: never size so that qty x 1-contract risk > live room - $100.
1-contract risk = (stop pts + 1 tick + 8 pt coded stop slip) * $2 + $4.74. Live room = start-of-day room + closed P&L today
- open risk of open, not risk-free trades (1-contract risk x qty).
Recovery state is carried across days and from eval to nothing (funded starts fresh, same rules applied in funded).
An eval in a recovery variant never ends 'stuck' early: it runs to pass, fail or the 120-day horizon. 'Stuck' = still open
at the horizon with room < $400 (BASE: stalled at a close)."""
import sys, json, random, statistics, collections
import numpy as np
from prop_sim import *
from prop_sim import _PATH
from prop_plans import PLANS

RISK_SLIP = 8.0                       # coded slippage allowance in the 1-contract risk check (pts)
def risk1(t): return (t['r'] + SLIP * T + RISK_SLIP) * PV + 2 * COMM

ALL = {'NEWS', 'V4+', 'D2', 'TDP', 'Pinball', 'H2'}
VARIANTS = {
    'BASE': dict(mode='base'),
    'R1': dict(mode='rec', thr=400, ex=700, cap=100, allow={'V4+', 'D2', 'H2'}),
    'R2': dict(mode='rec', thr=400, ex=700, cap=100, allow={'V4+', 'H2'}),
    'R3': dict(mode='rec', thr=400, ex=700, cap=100, allow=ALL),
    'R4': dict(mode='rec', thr=400, ex=700, cap=200, allow={'V4+', 'D2', 'H2'}),
    'R5': dict(mode='rec', thr=600, ex=700, cap=100, allow={'V4+', 'D2', 'H2'}),
    'R6': dict(mode='r6', cap=100),
    'R7': dict(mode='rec', thr=400, ex=700, cap=100, allow={'NEWS', 'V4+', 'TDP', 'H2'}),
    'R8': dict(mode='rec', thr=400, ex=700, cap=100, allow={'NEWS', 'V4+', 'TDP', 'H2'}, maxr=150),
    'R9': dict(mode='rec', thr=400, ex=700, cap=100, allow=ALL, guard=True),
    'R10': dict(mode='rec', thr=600, ex=700, cap=100, allow=ALL, guard=True),
}

def size_day_v(trs, cush, V, S, f=.65, dll=1100, slipx=8.0, sd=3, prof0=0.0, target=3000, best0=0.0, cons=.4, maxq=40, mindays_ok=True):
    """prop_sim.size_day with rule (b) replaced per variant V. S = mutable state dict (rec flag, counters)."""
    done = []
    for t in trs:
        cl = [u for u in done if u['xT'] <= t['eT']]
        rl = -sum(min(0, u['netq']) for u in cl); rp = sum(u['netq'] for u in cl); nl = sum(u['netq'] < 0 for u in cl)
        tg = mindays_ok and prof0 + rp >= target and max(best0, rp) <= cons * (prof0 + rp)
        room = cush + rp
        rc = (t['r'] + SLIP * T) * PV + 2 * COMM
        pts = t['pts'] - (slipx if t['why'] in STOPWHY else 0)
        pc = pts * PV - 2 * COMM
        used = 0; openr = 0
        for u in done:
            if u['q'] == 0: continue
            if u['xT'] <= t['eT']: used += max(0, -u['netq'])
            elif u['be'] is not None and u['be'] <= t['eT']: pass
            else: used += u['q'] * u['rc']; openr += u['q'] * u['r1']
        t['rc'] = rc; t['pc'] = pc; t['r1'] = risk1(t); t['recq'] = 0
        blocked = rl >= dll - 150 or (sd and nl >= sd) or tg
        if V['mode'] == 'base' and room < 400: blocked = True
        if V['mode'] == 'rec':
            if S['rec'] and room >= V['ex']: S['rec'] = False
            if not S['rec'] and room < V['thr']: S['rec'] = True; S['entries'] += 1
        if blocked:
            t['q'] = 0; t['netq'] = 0.0; done.append(t); continue
        if V['mode'] == 'rec' and S['rec']:
            ok = t['strat'] in V['allow'] and t['r1'] <= room - openr - V['cap'] and rc <= dll - used
            if ok and V.get('maxr') and t['r1'] > V['maxr']: ok = False
            q = 1 if ok else 0
            if q: S['rec_tr'] += 1; t['recq'] = 1
            else: S['rec_skip'] += 1
        else:
            w = t['w']
            budget = min(w * f * cush, f * cush - used, dll - used); q = min(maxq, int(budget // rc)) if budget > 0 else 0
            if V['mode'] == 'r6':
                if q < 1 and w >= 1 and rc < .9 * (cush - used) and rc < dll - used and t['r1'] <= room - openr - V['cap']: q = 1
                if q >= 1 and room < 400: S['rec_tr'] += 1
                # never size above what live room minus the cap can absorb
                if q >= 1 and q * t['r1'] > room - openr - V['cap']: q = max(0, int((room - openr - V['cap']) // t['r1']))
            else:
                if q < 1 and w >= 1 and rc < .9 * (cush - used) and rc < dll - used: q = 1
                if V.get('guard') and q >= 1 and q * t['r1'] > room - openr - V['cap']: q = max(0, int((room - openr - V['cap']) // t['r1']))
            q = min(q, maxq)
        t['q'] = max(q, 0); t['netq'] = t['q'] * pc
        done.append(t)
    return done

def run_day_v(trs, bal, floor, P, prof0, best0, maxq, V, S, slipx, target=None, cons=None, mindays_ok=True):
    cush = bal - floor
    dll = P.get('dll'); budget = 1100 if not dll else min(1100, dll - 150)
    done = size_day_v([dict(t) for t in trs], cush, V, S, dll=budget, slipx=slipx, prof0=prof0, best0=best0, maxq=maxq,
                      target=target if target is not None else 1e18, cons=cons if cons is not None else 1.0, mindays_ok=mindays_ok)
    dp = sum(t['netq'] for t in done)
    lo, hi = day_path(done)
    if lo is None: return 0.0, 'ok', cush
    if dll:
        hit = np.nonzero(lo <= -dll)[0]
        if len(hit):
            if P.get('dll_hard'): return float(lo[hit[0]]), 'fail', cush + float(lo[hit[0]])
            lo = lo[:hit[0] + 1]; dp = -float(dll)
    mn = cush + float(lo.min())
    if np.any(bal + lo <= floor): return float(lo.min()), 'fail', mn
    return dp, 'ok', mn

def eval_v(byd, seq, plan, V, slipx=8.0, H=120):
    E = plan['eval']; start = 50000.; bal = start; peak = start; best = 0.; n = 0
    tgt = E['target']; cons = E['cons'] or 1.0; mind = E.get('min_days', 0) or 0
    S = dict(rec=False, entries=0, rec_tr=0, rec_skip=0, rec_days=0, run=0, maxrun=0, minroom=1e9)
    for d in seq[:H]:
        n += 1
        fl = floor_eod(E, peak)
        if S['rec'] or (V['mode'] == 'r6' and bal - fl < 400):
            S['rec_days'] += 1; S['run'] += 1; S['maxrun'] = max(S['maxrun'], S['run'])
        else: S['run'] = 0
        dp, st, mn = run_day_v(byd.get(d, []), bal, fl, E, bal - start, best, E['maxq'], V, S, slipx, target=tgt, cons=cons, mindays_ok=n >= mind)
        S['minroom'] = min(S['minroom'], mn)
        if st == 'fail': return 'F', n, S, bal - fl
        bal += dp; best = max(best, dp)
        if bal <= floor_eod(E, peak): return 'F', n, S, 0
        peak = max(peak, bal)
        prof = bal - start
        if prof >= tgt and best <= cons * prof and n >= mind: return 'P', n, S, bal - floor_eod(E, peak)
        room = bal - floor_eod(E, peak)
        if V['mode'] == 'base' and room < 400: return 'S', n, S, room
    room = bal - floor_eod(E, peak)
    return ('S' if room < 400 else 'O'), n, S, room

def funded_v(byd, seq, plan, V, slipx=8.0):
    Fp = plan['funded']; start = 50000.; bal = start; peak = start
    locked_floor = None; pays = []; qd = 0; cyc_days = 0; cyc_prof = 0.; cyc_best = 0.; first = None; n = 0
    S = dict(rec=False, entries=0, rec_tr=0, rec_skip=0, rec_days=0, run=0, maxrun=0, minroom=1e9)
    for d in seq:
        n += 1
        prof = bal - start; mq = maxq_for(Fp, prof)
        if locked_floor is not None: Pd = dict(Fp); Pd['dd'] = 'eod'; fl = locked_floor
        else: Pd = Fp; fl = floor_eod(Fp, peak)
        if S['rec']: S['rec_days'] += 1
        dp, st, mn = run_day_v(byd.get(d, []), bal, fl, Pd, -1e9, 0., mq, V, S, slipx)
        S['minroom'] = min(S['minroom'], mn)
        if st == 'fail': return dict(res='bust', pays=pays, first=first, n=n, S=S)
        bal += dp
        cur_floor = locked_floor if locked_floor is not None else floor_eod(Fp, peak)
        if bal <= cur_floor: return dict(res='bust', pays=pays, first=first, n=n, S=S)
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
    stuck = bal - (locked_floor if locked_floor is not None else floor_eod(Fp, peak)) < 400
    return dict(res='open', pays=pays, first=first, n=n, S=S, stuck=stuck)

def pct(v, q):
    v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))] if v else None

def sim_v(plan, V, tr, year, slipx=8.0, N=2000, NF=1000, H=120, seed=7, roll=True):
    byd = byday(tr); days = day_lists(year)
    rnd = random.Random(seed); R = []
    for _ in range(N):
        seq = [rnd.choice(days) for _ in range(H)]
        R.append(eval_v(byd, seq, plan, V, slipx, H))
    p = sum(r[0] == 'P' for r in R) / N; f = sum(r[0] == 'F' for r in R) / N; s = sum(r[0] == 'S' for r in R) / N
    P_ = [r[1] for r in R if r[0] == 'P']
    E = plan['eval']; price = E['price']; act = E.get('activation', 0) or 0
    out = dict(p=round(p, 3), bust=round(f, 3), stuck=round(s, 3), open=round(1 - p - f - s, 3), med=statistics.median(P_) if P_ else None,
               p75=pct(P_, .75), cpf=round(price / p + act, 1) if p else None,
               days_per_funded=round(statistics.mean(r[1] for r in R) / p, 1) if p else None,
               rec_entered=round(sum(r[2]['entries'] > 0 for r in R) / N, 3),
               rec_trades=round(statistics.mean(r[2]['rec_tr'] for r in R), 2),
               rec_days_p95=pct([r[2]['rec_days'] for r in R], .95), rec_run_max=max(r[2]['maxrun'] for r in R),
               minroom_p01=round(pct([r[2]['minroom'] for r in R], .01)), minroom_min=round(min(r[2]['minroom'] for r in R)),
               pass_after_rec=round(sum(r[0] == 'P' and r[2]['entries'] > 0 for r in R) / N, 3))
    # stuck diagnostics: final room of stuck runs
    sr = [r[3] for r in R if r[0] == 'S']
    out['stuck_room_med'] = round(statistics.median(sr)) if sr else None
    out['stuck_room_lt250'] = round(sum(x < 250 for x in sr) / N, 3) if sr else 0
    rnd = random.Random(seed + 4); M = []
    for _ in range(NF):
        seq = [rnd.choice(days) for _ in range(120)]
        M.append(funded_v(byd, seq, plan, V, slipx))
    split = plan['funded']['pay'].get('split', .9)
    tot = [sum(x['pays']) for x in M]
    out.update(f_bust=round(sum(x['res'] == 'bust' for x in M) / NF, 3), f_got=round(sum(bool(x['pays']) for x in M) / NF, 3),
               f_stuck=round(sum(x.get('stuck', False) for x in M) / NF, 3),
               f_trader=round(split * statistics.mean(tot)), f_trader_p10=round(split * pct(tot, .10)),
               f_minroom=round(min(x['S']['minroom'] for x in M)))
    out['net_ev'] = round(out['f_trader'] - out['cpf']) if out['cpf'] else None
    if roll:
        allD = [d for d in D if d >= year * 10000 + 101 and d <= year * 10000 + 1231]
        RR = [eval_v(byd, allD[i:], plan, V, slipx, H) for i in range(len(allD))]
        n = len(RR)
        out.update(roll_p=round(sum(r[0] == 'P' for r in RR) / n, 3), roll_stuck=round(sum(r[0] == 'S' for r in RR) / n, 3),
                   roll_bust=round(sum(r[0] == 'F' for r in RR) / n, 3),
                   roll_minroom=round(min(r[2]['minroom'] for r in RR)))
        # worst calendar path: start date with the lowest intraday room among rolling starts
        w = min(range(n), key=lambda i: RR[i][2]['minroom'])
        out['roll_worst'] = dict(start=allD[w], res=RR[w][0], days=RR[w][1], minroom=round(RR[w][2]['minroom']), rec_days=RR[w][2]['rec_days'])
    return out

def main():
    tr = NEW()
    firms = [p for p in PLANS if (p['firm'], p['plan']) in (('Lucid Trading', 'LucidFlex'), ('Tradeify', 'Select Flex'))]
    which = sys.argv[1] if len(sys.argv) > 1 else 'main'
    OUT = dict(meta=dict(date='2026-10-25', risk1='(stop + 1 tick + 8 pt) * $2 + $4.74', N=2000, NF=1000, H=120), res=[])
    path = '/home/claude/mnq-quant/knowledge/src/recovery_test.json'
    if which == 'main' or which.startswith('add:'):
        ks = list(VARIANTS) if which == 'main' else which.split(':')[1].split(',')
        if which != 'main': OUT = json.load(open(path)); OUT['res'] = [x for x in OUT['res'] if x['var'] not in ks]
        for year in (2026, 2025, 2022):
            for p in firms:
                for k in ks:
                    V = VARIANTS[k]
                    r = sim_v(p, V, tr, year)
                    OUT['res'].append(dict(firm=p['firm'], plan=p['plan'], var=k, year=year, slip=0, **r))
                    print(year, p['plan'], k, {x: r[x] for x in ('p', 'bust', 'stuck', 'open', 'med', 'cpf', 'f_bust', 'f_trader', 'net_ev', 'rec_trades')}, flush=True)
        json.dump(OUT, open(path, 'w'), indent=1, default=str)
    elif which.startswith('horizon:'):   # long horizon check: python recovery_test.py horizon:R3,R9
        OUT = json.load(open(path)); OUT['horizon'] = []
        for k in ['BASE'] + which.split(':')[1].split(','):
            for p in firms[1:]:
                for H in (120, 250):
                    byd = byday(tr); days = day_lists(2026); rnd = random.Random(7)
                    R = [eval_v(byd, [rnd.choice(days) for _ in range(H)], p, VARIANTS[k], 8.0, H) for _ in range(2000)]
                    r = dict(var=k, plan=p['plan'], H=H, p=sum(x[0] == 'P' for x in R) / 2000, stuck=sum(x[0] == 'S' for x in R) / 2000,
                             open=sum(x[0] == 'O' for x in R) / 2000, bust=sum(x[0] == 'F' for x in R) / 2000)
                    OUT['horizon'].append(r); print('H', r, flush=True)
        json.dump(OUT, open(path, 'w'), indent=1, default=str)
    else:   # stress: python recovery_test.py stress:R3,R9
        vs = which.split(':')[1].split(',')
        OUT = json.load(open(path))
        OUT['res'] = [x for x in OUT['res'] if not x['slip']]
        for year in (2026, 2025, 2022):
            for p in firms:
                for k in ['BASE'] + vs:
                    for sx in (2, 4):
                        r = sim_v(p, VARIANTS[k], tr, year, slipx=8.0 + sx, roll=False)
                        OUT['res'].append(dict(firm=p['firm'], plan=p['plan'], var=k, year=year, slip=sx, **r))
                        print('STRESS', year, p['plan'], k, sx, {x: r[x] for x in ('p', 'bust', 'stuck', 'cpf', 'f_bust', 'f_trader', 'net_ev')}, flush=True)
        json.dump(OUT, open(path, 'w'), indent=1, default=str)

if __name__ == '__main__':
    main()
