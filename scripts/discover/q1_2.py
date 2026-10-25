from base import *
import statistics as st
# Q1: 15-min slot profile, RTH (1m) + overnight (5m)
slot = collections.defaultdict(lambda: collections.defaultdict(list))
for d, b in DAYS:
    adr = FEAT[d]['adr'] if d in FEAT else None
    if not adr: continue
    g = collections.OrderedDict()
    for m, o, h, l, c in b:
        k = m // 15 * 15
        if k not in g: g[k] = [o, h, l, c]
        else: a = g[k]; a[1] = max(a[1], h); a[2] = min(a[2], l); a[3] = c
    for k, (o, h, l, c) in g.items():
        s = slot[k][per(d)]; s.append(((h - l) / adr, abs(c - o) / ((h - l) or 1), (c - o) / adr))
print('Q1. Each 15-minute slot (ET): range as % of the day\'s average range (ADR), efficiency = |net| / range (high = trends inside the slot)')
print('slot   rangeA  rangeZ  effA  effZ  driftA  driftZ')
for k in sorted(slot):
    A, Z = slot[k]['A'], slot[k]['Z']
    if len(A) < 50: continue
    f = lambda v, i: st.mean(x[i] for x in v) * 100
    print(f"{k//60:02d}:{k%60:02d}  {f(A,0):5.1f}%  {f(Z,0):5.1f}%  {f(A,1)/100:.2f}  {f(Z,1)/100:.2f}  {f(A,2):+5.2f}% {f(Z,2):+5.2f}%")
# Q2: does the first 30 / 60 min predict the rest of the day?
print('\nQ2. Direction of the first N minutes vs the rest of the day (from minute N to 15:59 close)')
for N in (15, 30, 60, 90):
    for big in (0, .15, .25):
        r = {'A': [0, 0], 'Z': [0, 0]}; mv = {'A': [], 'Z': []}
        for d, b in DAYS:
            if d not in FEAT or len(b) < 380: continue
            adr = FEAT[d]['adr']; o = b[0][1]; cN = b[N - 1][4]; cl = b[-1][4]
            m1 = cN - o
            if abs(m1) < big * adr: continue
            s = 1 if m1 > 0 else -1
            r[per(d)][0] += (cl - cN) * s > 0; r[per(d)][1] += 1; mv[per(d)].append((cl - cN) * s / adr)
        print(f"  first {N:2d} min, move >= {int(big*100):2d}% ADR: rest of day same way  22-24 {r['A'][0]/r['A'][1]:.0%} (n{r['A'][1]}, avg {st.mean(mv['A'])*100:+.1f}% ADR) | 25-26 {r['Z'][0]/r['Z'][1]:.0%} (n{r['Z'][1]}, avg {st.mean(mv['Z'])*100:+.1f}% ADR)")
