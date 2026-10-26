"""Shared engine for the 2026 YTD study (Oct 25 2026).
Old rules = exactly scripts/lab/team_sim.py ALL (live Pine v6). New rules are rebuilt here with one generic 1m walker
that supports R targets, time caps, hard flat times, breakeven and trailing stops.
Costs: 2.37/side commission, 1 tick slippage on entries and stop exits (1 MNQ stats).
Engine sizing: size2 logic from team_sim (65% of room, $1,100 shared budget, open risk + realized losses), stop exits pay
extra slippage `slipx` points (8 = existing convention)."""
import sys, collections, math
L = '/home/claude/mnq-quant/scripts/lab'
for p in (L, '/home/claude/mnq-quant/scripts/discover', '/home/claude/mnq-quant/scripts/fair'):
    if p not in sys.path: sys.path.insert(0, p)
import os
_cwd = os.getcwd(); os.chdir(L)
from rules2 import *          # days, F, D, DB, TRD, EV, build, SLIP, T, PV, COMM, manage, v4_trades, v4bias, ST
import rules2 as R2
import td, news_fp
os.chdir(_cwd)

STOPWHY = ('stop', 'breakeven', 'trail')

def walk(b, i0, s, eP, stp, tgt, tend, be_R=None, be_off=1.25, trail_R=None, trail_trig=1.0, t5=None):
    """walk 1m bars from index i0. Order inside a bar: stop, target, time, then stop updates (effective next bar).
    tend: exit at the close of the first bar with minute >= tend. Returns (xi, xP, why, riskfree_minute)."""
    r = abs(eP - stp); st = stp; ext = eP; moved = False; rf = None
    for j in range(i0, len(b)):
        m, o, h, l, c = b[j]
        if (s > 0 and l <= st) or (s < 0 and h >= st):
            if not moved: return j, st - s * SLIP * T, 'stop', rf
            if abs(st - (eP + s * be_off)) < 1e-9: return j, st, 'breakeven', rf
            return j, st - s * SLIP * T, 'trail', rf
        if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)): return j, tgt, 'target', rf
        if m >= tend: return j, c, 'time exit', rf
        ext = max(ext, h) if s > 0 else min(ext, l)
        mfe = (ext - eP) * s
        nst = st
        if be_R is not None and mfe >= be_R * r: nst = eP + s * be_off if (eP + s * be_off - nst) * s > 0 else nst
        if trail_R is not None and mfe >= trail_trig * r:
            x = ext - s * trail_R * r
            if (x - nst) * s > 0: nst = x
        if t5 is not None and mfe >= t5 * r and (m - 570) % 5 == 4 and j >= 4:
            x = (min(z[3] for z in b[j - 4:j + 1]) - T) if s > 0 else (max(z[2] for z in b[j - 4:j + 1]) + T)
            if (x - nst) * s > 0 and (x - c) * s < 0: nst = x
        if (nst - st) * s > 0:
            st = nst; moved = True
            if rf is None and (st - eP) * s >= 0: rf = m + 1
    return len(b) - 1, b[-1][4], 'time exit', rf

def mk(d, strat, s, eT, eP, stp, xi, xP, why, rf, b, w=1.0, **kw):
    r = abs(eP - stp)
    t = dict(d=d, strat=strat, side=s, eT=eT, eP=eP, stp=stp, xT=b[xi][0] + 1, xP=xP, why=why, r=r, pts=(xP - eP) * s, be=rf, w=w)
    t.update(kw); return t

# ---------------- D2 ----------------
def d2(th=.5, entry='mkt', tgtR=None, cap=0, flat=900, be_R=None, trail_R=None, trail_trig=1.0, t5=None, stop='open', a=20220101, z=20991231):
    """entry 'mkt' = 10:29 close + 1 tick; 'pbK' = limit K x ADR back from the 10:29 close, valid until 11:30;
    'pb5' = first 5m bar after 10:30 closing against the move, then stop entry 1 tick beyond its extreme (until 12:00).
    stop 'open' = opening price - 1 tick (live); 'half' = halfway between open and the 10:29 close."""
    out = []
    for d in D:
        if d < a or d > z or d not in TRD or ({'FOMC', 'CPI'} & EV.get(d, set())): continue
        b = DB[d]; f = F[d]; idx = {x[0]: j for j, x in enumerate(b)}; j = idx.get(629)
        if j is None or f is None: continue
        px = b[j][4]; mv = (px - f['open']) / f['adr']
        if abs(mv) < th: continue
        s = 1 if mv > 0 else -1; w = 1.0 if TRD[d] == s else .5
        stp = f['open'] - s * T if stop == 'open' else (f['open'] + px) / 2 - s * T
        if entry == 'mkt':
            eP = px + s * SLIP * T; i0 = j + 1; eT = 630
        elif entry.startswith('pb') and entry != 'pb5':
            k = float(entry[2:]); lvl = px - s * k * f['adr']; eP = None
            for i in range(j + 1, len(b)):
                m, o, h, l, c = b[i]
                if m >= 690: break
                if (s > 0 and l <= stp) or (s < 0 and h >= stp): break
                if (s > 0 and l <= lvl - T) or (s < 0 and h >= lvl + T):
                    eP = min(o, lvl) if s > 0 else max(o, lvl); eT = m; fi = i; break
            if eP is None: continue
            if (s > 0 and b[fi][3] <= stp) or (s < 0 and b[fi][2] >= stp):
                out.append(mk(d, 'D2', s, eT, eP, stp, fi, stp - s * SLIP * T, 'stop', None, b, w)); continue
            i0 = fi + 1
        elif entry == 'pb5':
            eP = None; arm = None
            for i in range(j + 1, len(b)):
                m, o, h, l, c = b[i]
                if m >= 720: break
                if arm is not None and ((s > 0 and h >= arm) or (s < 0 and l <= arm)):
                    eP = (max(o, arm) if s > 0 else min(o, arm)) + s * SLIP * T; eT = m; fi = i; break
                if (m - 570) % 5 == 4:
                    c5 = b[i - 4:i + 1]; o5 = c5[0][1]; cl = c5[-1][4]
                    if (cl - o5) * s < 0: arm = (max(x[2] for x in c5) + T) if s > 0 else (min(x[3] for x in c5) - T)
            if eP is None or (eP - stp) * s <= 0: continue
            if (s > 0 and b[fi][3] <= stp) or (s < 0 and b[fi][2] >= stp):
                out.append(mk(d, 'D2', s, eT, eP, stp, fi, stp - s * SLIP * T, 'stop', None, b, w)); continue
            i0 = fi + 1
        r = abs(eP - stp); tgt = eP + s * tgtR * r if tgtR else None
        tend = min(flat, eT + cap - 1) if cap else flat
        xi, xP, why, rf = walk(b, i0, s, eP, stp, tgt, tend, be_R, 1.25, trail_R, trail_trig, t5)
        out.append(mk(d, 'D2', s, eT, eP, stp, xi, xP, why, rf, b, w))
    return out

# ---------------- V4+ ----------------
_V4 = None
def v4(tgtR=1.25, cap=0, flat=955, be_R=1.0, a=20220101, z=20991231):
    global _V4
    if _V4 is None:
        _V4 = collections.defaultdict(list)
        for t in v4_trades(days, F, tf=1, tgtR=1.25, bias=lambda f: v4bias(f, .4, .4, 0)):
            if TRD.get(t['d']) == t['side']: _V4[t['d']].append(t)
    out = []
    for d in D:
        if d < a or d > z or d not in TRD: continue
        b = DB[d]; idx = {x[0]: j for j, x in enumerate(b)}
        for t in _V4[d]:
            s = t['side']; eP = t['eP']; stp = t['stp']; i = idx[t['eT']]
            if (s > 0 and b[i][3] <= stp) or (s < 0 and b[i][2] >= stp):
                out.append(mk(d, 'V4+', s, t['eT'], eP, stp, i, stp - s * SLIP * T, 'stop', None, b)); continue
            r = abs(eP - stp); tgt = eP + s * tgtR * r
            tend = min(flat, t['eT'] + cap - 1) if cap else flat
            xi, xP, why, rf = walk(b, i + 1, s, eP, stp, tgt, tend, be_R)
            out.append(mk(d, 'V4+', s, t['eT'], eP, stp, xi, xP, why, rf, b))
    return out

# ---------------- Pinball ----------------
def pinball(tgtR=None, cap=0, flat=955, last=900, be_R=None, a=20220101, z=20991231):
    out = []
    for d in D:
        if d < a or d > z or d not in TRD: continue
        b = DB[d]; k = D.index(d); tr = TRD[d]
        ch = [C[D[q]] - C[D[q - 1]] for q in range(k - 3, k)]; u = sum(x for x in ch if x > 0); dn = -sum(x for x in ch if x < 0)
        rsi = 100 if dn == 0 else 100 - 100 / (1 + u / dn); s = 1 if rsi < 30 else (-1 if rsi > 70 else 0)
        if not s or tr != s: continue
        IB = [x for x in b if x[0] < 630]; hi = max(x[2] for x in IB); lo = min(x[3] for x in IB); lvl = hi + T if s > 0 else lo - T
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 630 or m > min(last, flat - 1): continue
            if (s > 0 and h >= lvl) or (s < 0 and l <= lvl):
                eP = (max(o, lvl) if s > 0 else min(o, lvl)) + s * SLIP * T; stp = (lo - T) if s > 0 else (hi + T)
                if (s > 0 and l <= stp) or (s < 0 and h >= stp):
                    out.append(mk(d, 'Pinball', s, m, eP, stp, i, stp - s * SLIP * T, 'stop', None, b)); break
                r = abs(eP - stp); tgt = eP + s * tgtR * r if tgtR else None
                tend = min(flat, m + cap - 1) if cap else flat
                xi, xP, why, rf = walk(b, i + 1, s, eP, stp, tgt, tend, be_R)
                out.append(mk(d, 'Pinball', s, m, eP, stp, xi, xP, why, rf, b)); break
    return out

# ---------------- TDP ----------------
_TDE = None
def tdp(tgtR=1.5, cap=0, flat=955, be_R=None, a=20220101, z=20991231):
    """entries from td.run (retrace k=.33, stop .4 ADR, entries until 12:00), exits re-walked here."""
    global _TDE
    if _TDE is None: _TDE = td.run(E=.6, mode='retrace', k=.33, stop='adr', a=.4, R=1.5, hold=999, tend=720)
    out = []
    for t in _TDE:
        d = t['d']
        if d < a or d > z or d not in DB: continue
        b = DB[d]; idx = {x[0]: j for j, x in enumerate(b)}; i = idx[t['em']]; s = t['s']; eP = t['eP']; stp = t['stp']
        if (s > 0 and b[i][3] <= stp) or (s < 0 and b[i][2] >= stp):
            out.append(mk(d, 'TDP', s, t['em'], eP, stp, i, stp - s * T, 'stop', None, b)); continue
        r = abs(eP - stp); tgt = eP + s * tgtR * r if tgtR else None
        tend = min(flat, t['em'] + cap - 1) if cap else flat
        xi, xP, why, rf = walk(b, i + 1, s, eP, stp, tgt, tend, be_R)
        out.append(mk(d, 'TDP', s, t['em'], eP, stp, xi, xP, why, rf, b))
    return out

# ---------------- H2 ----------------
def h2(tgtR=2.0, cap=None, flat=955, th=.4, a=20220101, z=20991231):
    orig = ST.mgmt
    def mg(b1, i, s, eP, stp, tgt, tcap, flat_=flat): return orig(b1, i, s, eP, stp, tgt, tcap, flat_)
    ST.mgmt = mg
    try: raw = ST.run('h2', tgtR, cap, trendday=True, dtrend=True, tdth=th, maxtr=3, end=min(900, flat - 5))
    finally: ST.mgmt = orig
    out = []
    for t in raw:
        d = t['d']
        if d < a or d > z or d not in DB: continue
        b = DB[d]; idx = {x[0]: j for j, x in enumerate(b)}; s = t['side']; eP = b[idx[t['eT']]][1] + s * SLIP * T
        out.append(dict(d=d, strat='H2', side=s, eT=t['eT'], eP=eP, stp=eP - s * t['r'], xT=t['eT'] + t['hold'] + 1, xP=eP + s * t['pts'],
                        why={'tgt': 'target', 'stop': 'stop'}.get(t['why'], 'time exit'), r=t['r'], pts=t['pts'], be=None, w=.5))
    return out

# ---------------- NEWS ----------------
def news():
    out = []
    for t in news_fp.run('either', 50, 50, 'f'):
        eT = (t['em'] + 1080) % 1440; xT = (t['xm'] + 1080) % 1440
        out.append(dict(d=t['d'], strat='NEWS', side=t['s'], eT=eT, eP=t['eP'], stp=t['stp'], xT=xT, why={'tgt': 'target', 'be': 'breakeven'}.get(t['why'], t['why']),
                        r=50.0, pts=t['pts'], be=None, w=1.0))
    return out

def old_team():
    """exact copy of team_sim ALL (live rules)."""
    PB = build("current", be=True, v4t=1.25)
    TD = td.run(E=.6, mode='retrace', k=.33, stop='adr', a=.4, R=1.5, hold=999, tend=720)
    A = [dict(t) for t in PB]
    A += [dict(d=t['d'], strat='TDP', side=t['s'], eT=t['em'], eP=t['eP'], stp=t['stp'], xT=t['xT'], why=t['why'], r=t['risk'], pts=t['pts'], be=None, w=1.0) for t in TD]
    A += news()
    for t in A:
        if t['why'] == 'tgt': t['why'] = 'target'
    A.sort(key=lambda t: (t['d'], t['eT']))
    return A

# ---------------- stats ----------------
def net1(t): return t['pts'] * PV - 2 * COMM
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def maxdd(v):
    eq = pk = dd = 0
    for x in v: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    return dd
def stat1(tr, a=20260101, z=20991231):
    x = [t for t in tr if a <= t['d'] <= z]
    v = [net1(t) for t in x]
    if not v: return dict(n=0, net=0, pf=0, win=0, hold=0, dd=0)
    return dict(n=len(v), net=round(sum(v)), pf=pf(v), win=round(sum(y > 0 for y in v) / len(v), 3),
                hold=round(sum(t['xT'] - t['eT'] for t in x) / len(x)), dd=round(maxdd(v)), last=max(t['xT'] for t in x))

# ---------------- sizing + eval ----------------
def size2(trs, cush, f=.65, dll=1100, slipx=8.0, xent=0.0):
    """team_sim.size2 'fcfs'. slipx = extra pts on stop-type exits; xent = extra pts on every entry (stress)."""
    done = []
    for t in trs:
        rc = (t['r'] + SLIP * T) * PV + 2 * COMM
        pts = t['pts'] - (slipx if t['why'] in STOPWHY else 0) - xent
        pc = pts * PV - 2 * COMM
        used = 0
        for u in done:
            if u['q'] == 0: continue
            if u['xT'] <= t['eT']: used += max(0, -u['netq'])
            elif u['be'] is not None and u['be'] <= t['eT']: pass
            else: used += u['q'] * u['rc']
        w = t['w']
        budget = min(w * f * cush, f * cush - used, dll - used); q = min(40, int(budget // rc)) if budget > 0 else 0
        if q < 1 and w >= 1 and rc < .9 * (cush - used) and rc < dll - used: q = 1
        t['q'] = max(q, 0); t['rc'] = rc; t['netq'] = t['q'] * pc
        done.append(t)
    return sum(t['netq'] for t in trs)

def byday(tr, strats=None):
    g = collections.defaultdict(list)
    for t in tr:
        if strats is None or t['strat'] in strats: g[t['d']].append(t)
    return g

def eval_run(byd, start, days_list, slipx=8.0, xent=0.0, target=3000, mll_gap=2000, horizon=9999, keep=False):
    """returns dict(res 'P'/'F'/'O', n days, worst dd from start, consistency-blocked days, day pnl list)"""
    bal = 50000.; peak = 50000.; best = 0.; n = 0; res = 'O'; worst = 0.; hit_target_day = None; pnl = []
    for d in days_list:
        if d < start: continue
        n += 1; mll = min(peak - mll_gap, 50000); cush = bal - mll
        dp = size2([dict(t) for t in byd.get(d, [])], cush, slipx=slipx, xent=xent); bal += dp; best = max(best, dp); pnl.append((d, dp))
        worst = min(worst, bal - 50000)
        if bal <= mll: res = 'F'; break
        peak = max(peak, bal)
        if bal - 50000 >= target and hit_target_day is None: hit_target_day = n
        if bal - 50000 >= target and best <= .5 * (bal - 50000): res = 'P'; break
        if n >= horizon: break
    return dict(res=res, n=n, worst=worst, tgt_n=hit_target_day, pnl=pnl if keep else None, end=bal - 50000)

def rolling(tr, a, z, step=1, horizon=40, slipx=8.0, strats=None, end_days=None):
    byd = byday(tr, strats)
    DAYS = [d for d in D if d >= 20220301]
    sts = [d for d in DAYS if a <= d <= z][::step]; R = []
    for s in sts: R.append(eval_run(byd, s, DAYS, slipx=slipx, horizon=horizon))
    n = len(R)
    return dict(n=n, p=sum(r['res'] == 'P' for r in R) / n, f=sum(r['res'] == 'F' for r in R) / n, o=sum(r['res'] == 'O' for r in R) / n,
                med=sorted([r['n'] for r in R if r['res'] == 'P'])[len([r for r in R if r['res'] == 'P']) // 2] if any(r['res'] == 'P' for r in R) else None, R=R)
