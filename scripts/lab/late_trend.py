"""Late trend = quiet first hour, then a trend. Real-time test: initial-balance (9:30-10:30) breakout after 10:30 on quiet mornings.
Also: reversal days (first-hour extreme beyond prior-day high/low that fails)."""
import sys, collections, itertools
sys.path.insert(0, '.')
from rules2 import D, DB, F, TRD, PV, COMM, T
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def rep(lab, tr):
    o = []
    for a, z in ((0, 20241231), (20250101, 99999999)):
        v = [t[1] for t in tr if a <= t[0] <= z]
        o.append(f"n{len(v):4d} win {sum(x>0 for x in v)/max(1,len(v)):.0%} PF {pf(v):.2f}")
    yrs = ' '.join(f"{y%100}:{pf([t[1] for t in tr if t[0]//10000==y]):.2f}" for y in range(2022, 2027))
    print(f"  {lab:58s} 22-24 {o[0]:24s} | 25-26 {o[1]:24s} | {yrs}")
def walk(b, j, s, e, stp, tgt, flat=955):
    for k in range(j, len(b)):
        m, o, h, l, c = b[k]
        if (s > 0 and l <= stp) or (s < 0 and h >= stp): return (stp - s * T - e) * s
        if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)): return (tgt - e) * s
        if m >= flat: return (c - e) * s
    return (b[-1][4] - e) * s
def ibo(quiet=.35, wmax=.6, t1=780, stop='mid', R=None, trend=False, close_conf=False, flat=955):
    out = []
    for d in D:
        if d < 20220103 or d not in F or len(DB[d]) < 380: continue
        b = DB[d]; f = F[d]; adr = f['adr']; o = b[0][1]
        ih = max(x[2] for x in b[:60]); il = min(x[3] for x in b[:60])
        if abs(b[59][4] - o) > quiet * adr or (ih - il) > wmax * adr: continue
        for i in range(60, len(b) - 1):
            m, oo, h, l, c = b[i]
            if m >= t1: break
            s = 1 if (h > ih if not close_conf else c > ih) else -1 if (l < il if not close_conf else c < il) else 0
            if not s: continue
            if trend and TRD.get(d) != s: break
            e = (ih + T if s > 0 else il - T) if not close_conf else b[i + 1][1]
            e += s * T
            j = i if not close_conf else i + 1
            stp = (ih + il) / 2 if stop == 'mid' else (il - T if s > 0 else ih + T) if stop == 'other' else e - s * stop * adr
            r = abs(e - stp)
            tgt = e + s * R * r if R else None
            pts = walk(b, j + (0 if close_conf else 1), s, e, stp, tgt, flat)
            out.append((d, pts * PV - 2 * COMM, s))
            break
    return out
print('IB breakout on quiet mornings (first hour |net| <= q ADR and range <= w ADR); first break of the 9:30-10:30 range before t1')
for q, w in ((.25, .5), (.35, .6), (.5, .8)):
    for stop in ('mid', 'other', .25):
        for R in (None, 1.5, 2):
            for tr in (False, True):
                rep(f"q{q} w{w} stop {stop} R {R} {'with daily trend' if tr else ''}", ibo(q, w, 780, stop, R, tr))
