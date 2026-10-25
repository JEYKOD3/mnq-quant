from base import *
import random
random.seed(1)
def test(b, lv, start, x):
    p0 = b[start - 1][4]
    if abs(p0 - lv) < 2: return None
    fromb = p0 < lv; t = None
    for i in range(start, len(b)):
        m, o, h, l, c = b[i]
        if t is None:
            if (fromb and h >= lv) or (not fromb and l <= lv): t = i
            else: continue
        brk = (h >= lv + x) if fromb else (l <= lv - x)
        bnc = (l <= lv - x) if fromb else (h >= lv + x)
        if brk and bnc: return None
        if brk or bnc: return bnc, b[t][0]
    return None
res = collections.defaultdict(lambda: {'A': [0, 0], 'Z': [0, 0]})
for d, b in DAYS:
    if d not in FEAT or len(b) < 380: continue
    f = FEAT[d]; adr = f['adr']; on = overnight(d)
    L = {'prior day high': (f['pdh'], 1), 'prior day low': (f['pdl'], 1), 'prior day close': (f['pdc'], 1),
         'OR30 high': (max(x[2] for x in b[:30]), 30), 'OR30 low': (min(x[3] for x in b[:30]), 30), '9:30 open': (b[0][1], 1)}
    if on: L['overnight high'] = (on[0], 1); L['overnight low'] = (on[1], 1)
    for X in (.08, .15):
        for nm, (lv, st) in L.items():
            for kind, lev in (('real', lv), ('fake', lv + random.choice((-1, 1)) * random.uniform(.15, .35) * adr)):
                r = test(b, lev, st, X * adr)
                if r is None: continue
                rr = res[(nm, X, kind)][per(d)]; rr[0] += r[0]; rr[1] += 1
print('Q3b. Bounce rate at real level minus bounce rate at a fake level 15-35% ADR away (same day, same rules)')
for nm in ['prior day high', 'prior day low', 'prior day close', 'overnight high', 'overnight low', 'OR30 high', 'OR30 low', '9:30 open']:
    for X in (.08, .15):
        out = []
        for p in ('A', 'Z'):
            R = res[(nm, X, 'real')][p]; F = res[(nm, X, 'fake')][p]
            out.append(f"{R[0]/R[1]:.0%} vs fake {F[0]/F[1]:.0%} = {100*(R[0]/R[1]-F[0]/F[1]):+.0f} pts (n{R[1]})")
        print(f"  {nm:16s} X={int(X*100):2d}%  22-24: {out[0]:34s} | 25-26: {out[1]}")
