"""Candidate A: 10:30 trend-day continuation. Candidate B: break of the overnight high/low or prior-day high/low, hold 15-60 min."""
from base import *
T = .25; PV = 2; COMM = 2.37
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return g / l if l else 9.9
def rep(lab, tr):
    o = []
    for P in 'AZ':
        v = [t for t in tr if per(t[0]) == P]
        o.append(f"n{len(v):4d} win {sum(x[1]>0 for x in v)/max(1,len(v)):.0%} PF {pf([x[1] for x in v]):.2f} avg ${sum(x[1] for x in v)/max(1,len(v)):+.0f}")
    yrs = ' '.join(f"{y%100}:{pf([t[1] for t in tr if t[0]//10000==y]):.2f}" for y in range(2022, 2027))
    print(f"  {lab:46s} 22-24 {o[0]:40s} | 25-26 {o[1]:40s} | {yrs}")
def walk(b, j, s, e, stop, tgt, tmax, trail=None):
    hi = e
    for k in range(j, len(b)):
        m, o, h, l, c = b[k]
        if (s > 0 and l <= stop) or (s < 0 and h >= stop): return (stop - s * T - e) * s
        if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)): return (tgt - e) * s
        if m >= tmax: return (c - e) * s
        if trail:
            hi = max(hi, h) if s > 0 else min(hi, l)
            ns = hi - s * trail
            stop = max(stop, ns) if s > 0 else min(stop, ns)
    return (b[-1][4] - e) * s
print('Candidate A: at 10:30, first hour efficiency >= E and price outside prior-day range -> trade in that direction (1 MNQ, costs in)')
for E in (.5, .6, .7):
    for stopk, sl in (('first-hour mid', 'mid'), ('0.25 ADR', .25), ('0.4 ADR', .4)):
        for ex, (tg, tm, tr) in (('hold to 15:55', (None, 955, None)), ('60 min', (None, 690, None)), ('1.5R', ('1.5R', 955, None)), ('trail 0.3 ADR', (None, 955, .3))):
            out = []
            for d, b in DAYS:
                if d not in FEAT or len(b) < 380: continue
                f = FEAT[d]; adr = f['adr']; o = b[0][1]
                h1 = max(x[2] for x in b[:60]); l1 = min(x[3] for x in b[:60]); p = b[59][4]
                if abs(p - o) < E * (h1 - l1): continue
                if not (p > f['pdh'] or p < f['pdl']): continue
                s = 1 if p > o else -1
                if (p > f['pdh']) != (s > 0): continue
                e = b[60][1] + s * T
                stp = (h1 + l1) / 2 if sl == 'mid' else e - s * sl * adr
                R = (e - stp) * s
                if R <= 5: continue
                tgt = e + s * 1.5 * R if tg == '1.5R' else None
                pts = walk(b, 60, s, e, stp, tgt, tm, tr * adr if tr else None)
                out.append((d, pts * PV - 2 * COMM))
            rep(f"E{E} stop {stopk:14s} exit {ex}", out)
