"""Generic futures prop-firm rules simulator (Oct 25 2026). Reuses the NEW day engine (rulesets.NEW) and the size2 logic of
common.py, with the max-contract cap and daily budget as parameters. Adds a 1m intraday equity path per day so that
(1) EOD / static floors are checked against intraday equity (real-time breach), (2) intraday-trailing drawdowns are
modeled (trail follows intraday equity highs incl. unrealized), (3) hard / soft daily loss limits are checked intraday.
Path per contract: from the entry bar to the bar before the exit bar, adverse = bar low (long) / high (short), favorable
= bar high / low; from the exit bar on, the realized net (incl. +8 pt stop slip and commission). Pre-RTH NEWS trades have
no 1m bars here: adverse = the loss if a loser, else -0.5R (50 pt stop -> -25 pts); flagged in the report."""
import random, statistics, collections, math
import numpy as np
from rulesets import *

G0, G1 = 480, 961                     # minute grid 8:00 .. 16:00
G = G1 - G0
KEEP_ROOM = 1100

def size_day(trs, cush, f=.65, dll=1100, slipx=8.0, sd=3, prof0=0.0, target=3000, best0=0.0, cons=.4, maxq=40, mindays_ok=True):
    """copy of common.size2 (fcfs) with maxq + budget as parameters. Stop-day rule N=3 + (d) 'passed'."""
    done = []
    for t in trs:
        if sd is not None:
            cl = [u for u in done if u['xT'] <= t['eT']]
            rl = -sum(min(0, u['netq']) for u in cl); rp = sum(u['netq'] for u in cl); nl = sum(u['netq'] < 0 for u in cl)
            tg = mindays_ok and prof0 + rp >= target and max(best0, rp) <= cons * (prof0 + rp)
            if rl >= dll - 150 or cush + rp < 400 or (sd and nl >= sd) or tg:
                t['q'] = 0; t['rc'] = 0; t['netq'] = 0.0; t['pc'] = 0.0; done.append(t); continue
        rc = (t['r'] + SLIP * T) * PV + 2 * COMM
        pts = t['pts'] - (slipx if t['why'] in STOPWHY else 0)
        pc = pts * PV - 2 * COMM
        used = 0
        for u in done:
            if u['q'] == 0: continue
            if u['xT'] <= t['eT']: used += max(0, -u['netq'])
            elif u['be'] is not None and u['be'] <= t['eT']: pass
            else: used += u['q'] * u['rc']
        w = t['w']
        budget = min(w * f * cush, f * cush - used, dll - used); q = min(maxq, int(budget // rc)) if budget > 0 else 0
        if q < 1 and w >= 1 and rc < .9 * (cush - used) and rc < dll - used: q = 1
        q = min(q, maxq)
        t['q'] = max(q, 0); t['rc'] = rc; t['pc'] = pc; t['netq'] = t['q'] * pc
        done.append(t)
    return done

# ---------- per-trade per-contract path arrays ----------
_PATH = {}
def path_arrays(t):
    k = (t['d'], t['strat'], t['eT'], t['side'])
    if k in _PATH: return _PATH[k]
    s = t['side']; eP = t['eP']; pts = t['pts']
    A = np.zeros(G); F = np.zeros(G)
    e = t['eT'] - G0; x = t['xT'] - 1 - G0           # exit bar index
    e = max(0, e); x = max(e, min(G - 1, x))
    b = DB.get(t['d'], [])
    bars = {m: (h, l) for m, o, h, l, c in b}
    for i in range(e, x):
        m = i + G0
        if m in bars:
            h, l = bars[m]
            adv = ((l - eP) if s > 0 else (eP - h)); fav = ((h - eP) if s > 0 else (eP - l))
        else:
            adv = pts if pts < 0 else -0.5 * t['r']; fav = max(pts, 0)
        A[i] = adv * PV - COMM; F[i] = fav * PV - COMM
    _PATH[k] = (A, F, x)
    return _PATH[k]

def day_path(done):
    """intraday equity low/high arrays for the sized trades of one day (dollars, relative to start of day)."""
    lo = np.zeros(G); hi = np.zeros(G); any_ = False
    for t in done:
        if t['q'] <= 0: continue
        A, F, x = path_arrays(t); any_ = True
        lo += t['q'] * A; hi += t['q'] * F
        lo[x:] += t['netq']; hi[x:] += t['netq']
    return (lo, hi) if any_ else (None, None)

# ---------- one trading day under a floor ----------
def run_day(trs, bal, floor_fn, peak_intra, P, prof0, best0, maxq, target=None, cons=None, mindays_ok=True):
    """floor_fn: 'eod' -> fixed floor for the day (given), 'intraday' -> trailing on intraday highs.
    returns (dp, status) status in ('ok','fail'), plus new intraday peak."""
    dd = P['dd']; gap = P['gap']; start = 50000.
    lock = start + P['lock'] if P['lock'] is not None else 1e18
    if dd == 'intraday': floor = min(peak_intra - gap, lock)
    else: floor = floor_fn
    cush = bal - floor
    dll = P.get('dll'); budget = 1100 if not dll else min(1100, dll - 150)
    done = size_day([dict(t) for t in trs], cush, dll=budget, prof0=prof0, best0=best0, maxq=maxq,
                    target=target if target is not None else 1e18, cons=cons if cons is not None else 1.0, mindays_ok=mindays_ok)
    dp = sum(t['netq'] for t in done)
    lo, hi = day_path(done)
    if lo is None: return 0.0, 'ok', peak_intra
    # daily loss limit
    if dll:
        hit = np.nonzero(lo <= -dll)[0]
        if len(hit):
            if P.get('dll_hard'): return float(lo[hit[0]]), 'fail', peak_intra
            # soft: flattened at -dll at the first touch, rest of the day ignored
            lo = lo[:hit[0] + 1]; hi = hi[:hit[0] + 1]; dp = -float(dll)
    if dd == 'intraday':
        pk_before = np.maximum.accumulate(np.concatenate(([peak_intra - bal], hi[:-1])))
        pk_before = np.maximum(pk_before, peak_intra - bal)
        fl = np.minimum(pk_before - gap, lock - bal)
        if np.any(lo <= fl): return float(lo[np.nonzero(lo <= fl)[0][0]]), 'fail', peak_intra
        peak_intra = max(peak_intra, bal + float(hi.max()), bal + dp)
    else:
        if np.any(bal + lo <= floor): return float(lo.min()), 'fail', peak_intra
    return dp, 'ok', peak_intra

def floor_eod(P, peak):
    start = 50000.
    if P['dd'] == 'static': return start - P['gap']
    lock = start + P['lock'] if P['lock'] is not None else 1e18
    return min(peak - P['gap'], lock)

def maxq_for(P, profit):
    sc = P.get('scale')
    if not sc: return P['maxq']
    q = sc[0][1]
    for th, mq in sc:
        if profit >= th: q = mq
    return min(q, P['maxq'])

# ---------- evaluation ----------
def eval_seq(byd, seq, plan, H=120):
    E = plan['eval']; start = 50000.; bal = start; peak = start; pki = start; best = 0.; n = 0
    tgt = E['target']; cons = E['cons'] or 1.0; mind = E.get('min_days', 0) or 0
    lim = min(H, E.get('time_limit') or H)
    for d in seq[:lim]:
        n += 1
        fl = floor_eod(E, peak)
        dp, st, pki = run_day(byd.get(d, []), bal, fl, pki, E, bal - start, best, E['maxq'], target=tgt, cons=cons, mindays_ok=n >= mind)
        if st == 'fail': return 'F', n
        bal += dp; best = max(best, dp)
        if E['dd'] != 'intraday' and bal <= floor_eod(E, peak): return 'F', n
        peak = max(peak, bal); pki = max(pki, bal)
        prof = bal - start
        if prof >= tgt and best <= cons * prof and n >= mind: return 'P', n
        if E['dd'] != 'intraday' and bal - floor_eod(E, peak) < 400: return 'S', n     # stalled: engine takes no new entries
    return 'O', n

# ---------- funded ----------
def funded_seq(byd, seq, plan):
    Fp = plan['funded']; start = 50000.; bal = start; peak = start; pki = start
    locked_floor = None; pays = []; qd = 0; cyc_days = 0; cyc_prof = 0.; cyc_best = 0.; first = None; n = 0
    for d in seq:
        n += 1
        prof = bal - start; mq = maxq_for(Fp, prof)
        if locked_floor is not None:
            Pd = dict(Fp); Pd['dd'] = 'eod'; fl = locked_floor
        else:
            Pd = Fp; fl = floor_eod(Fp, peak) if Fp['dd'] != 'intraday' else None
        dp, st, pki = run_day(byd.get(d, []), bal, fl, pki, Pd, -1e9, 0., mq)
        if st == 'fail': return dict(res='bust', pays=pays, first=first, n=n)
        bal += dp
        cur_floor = locked_floor if locked_floor is not None else (floor_eod(Fp, peak) if Fp['dd'] != 'intraday' else min(pki - Fp['gap'], start + (Fp['lock'] if Fp['lock'] is not None else 1e18)))
        if bal <= cur_floor: return dict(res='bust', pays=pays, first=first, n=n)
        peak = max(peak, bal); pki = max(pki, bal)
        cyc_days += 1; cyc_prof += dp; cyc_best = max(cyc_best, dp)
        if dp >= (Fp.get('win_min') or 0) and dp > 0: qd += 1
        # payout check (policy A: ask as soon as allowed)
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
        # policy B: keep at least $1,100 of room above the floor that applies after the request
        if Q.get('floor_after') is not None and locked_floor is None: post = start + Q['floor_after']
        else: post = cur_floor
        amt = min(amt, bal - post - KEEP_ROOM)
        if amt < (Q.get('min_pay') or 0) or amt <= 0: continue
        bal -= amt; pays.append(amt); qd = 0; cyc_days = 0; cyc_prof = 0.; cyc_best = 0.
        if first is None: first = n
        if Q.get('floor_after') is not None:
            locked_floor = start + Q['floor_after'] if locked_floor is None else locked_floor
    return dict(res='open', pays=pays, first=first, n=n)

def day_lists(year):
    a, z = year * 10000 + 101, year * 10000 + 1231
    return [d for d in D if a <= d <= z]

def simulate(plan, tr, year=2026, N=2000, NF=1000, H=120, HF=120, seed=7, roll=True):
    byd = byday(tr); days = day_lists(year)
    rnd = random.Random(seed); R = []
    for _ in range(N):
        seq = [rnd.choice(days) for _ in range(H)]
        R.append(eval_seq(byd, seq, plan, H))
    P = [n for r, n in R if r == 'P']
    p = len(P) / N; f = sum(r == 'F' for r, _ in R) / N
    E = plan['eval']; m = E.get('monthly', 0) or 0
    costs = [E['price'] + (m * ((n - 1) // 21) if m else 0) for r, n in R]
    ecost = statistics.mean(costs)
    st = sum(r == 'S' for r, _ in R) / N
    out = dict(p=round(p, 3), f=round(f, 3), stall=round(st, 3), o=round(1 - p - f - st, 3), med=statistics.median(P) if P else None,
               p40=round(sum(n <= 40 for n in P) / N, 3), attempt_cost=round(ecost, 1))
    act = E.get('activation', 0) or 0
    out['cost_per_funded'] = round(ecost / p + act, 1) if p > 0 else None
    # funded MC
    rnd = random.Random(seed + 4); M = []
    for _ in range(NF):
        seq = [rnd.choice(days) for _ in range(HF)]
        M.append(funded_seq(byd, seq, plan))
    split = plan['funded']['pay'].get('split', .9)
    tot = [sum(x['pays']) for x in M]
    out.update(f_bust=round(sum(x['res'] == 'bust' for x in M) / NF, 3), f_got=round(sum(bool(x['pays']) for x in M) / NF, 3),
               f_first_med=statistics.median([x['first'] for x in M if x['first']]) if any(x['first'] for x in M) else None,
               f_npay=round(statistics.mean(len(x['pays']) for x in M), 2), f_gross=round(statistics.mean(tot)),
               f_trader=round(split * statistics.mean(tot)))
    if out['cost_per_funded']:
        out['net_ev'] = round(out['f_trader'] - out['cost_per_funded'])
        out['ev_per_dollar'] = round(out['f_trader'] / out['cost_per_funded'], 2)
        # per attempt: EV / $ spent
        spend = ecost + p * act
        out['roi_attempt'] = round((p * out['f_trader'] - spend) / spend, 2)
    if roll and year == 2026:
        RR = []
        allD = [d for d in D if d >= 20260101]
        for i in range(len(allD)):
            RR.append(eval_seq(byd, allD[i:], plan, H))
        out['roll_p'] = round(sum(r == 'P' for r, _ in RR) / len(RR), 3); out['roll_f'] = round(sum(r == 'F' for r, _ in RR) / len(RR), 3)
        out['roll_med'] = statistics.median([n for r, n in RR if r == 'P']) if any(r == 'P' for r, _ in RR) else None
    return out
