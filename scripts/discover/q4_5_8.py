from base import *
import statistics as st
P = lambda v: f"{sum(v)/len(v):.0%}" if v else '  -'
print('Q4. Gap fill: open vs prior close, by gap size (% ADR). Filled = trades back to prior close. Chance baseline not obvious, so shown with a fake level the same distance on the other side.')
for lo, hi in ((0, .1), (.1, .2), (.2, .35), (.35, .6), (.6, 9)):
    out = {}
    for p in 'AZ':
        f30 = []; f90 = []; fday = []; fk = []
        for d, b in DAYS:
            if d not in FEAT or per(d) != p or len(b) < 380: continue
            f = FEAT[d]; g = (b[0][1] - f['pdc']) / f['adr']
            if not (lo <= abs(g) < hi): continue
            pdc = f['pdc']; fake = b[0][1] + (b[0][1] - pdc)
            t = next((x[0] for x in b if x[3] <= pdc <= x[2]), None)
            tf = next((x[0] for x in b if x[3] <= fake <= x[2]), None)
            f30.append(t is not None and t < 600); f90.append(t is not None and t < 660); fday.append(t is not None); fk.append(tf is not None)
        out[p] = f"by 10:00 {P(f30)}  by 11:00 {P(f90)}  by close {P(fday)} (fake {P(fk)}) n{len(fday)}"
    print(f"  gap {int(lo*100):2d}-{int(hi*100) if hi<9 else 'up'}%: 22-24 {out['A']} | 25-26 {out['Z']}")
print('\nQ5. After a strong 60-min move, what happens in the next 30 and 60 minutes? (avg move in the same direction, % ADR; >0 = continuation)')
for k in (.2, .3, .45):
    for t0 in (630, 690, 750, 810, 870):
        row = []
        for p in 'AZ':
            n30 = []; n60 = []
            for d, b in DAYS:
                if d not in FEAT or per(d) != p or len(b) < 380: continue
                adr = FEAT[d]['adr']; idx = {x[0]: i for i, x in enumerate(b)}
                if t0 not in idx or t0 + 60 not in idx or t0 - 60 not in idx: continue
                mv = b[idx[t0] - 1][4] - b[idx[t0 - 60]][1]
                if abs(mv) < k * adr: continue
                s = 1 if mv > 0 else -1; e = b[idx[t0]][1]
                n30.append((b[idx[t0 + 30] - 1][4] - e) * s / adr); n60.append((b[idx[t0 + 60] - 1][4] - e) * s / adr)
            row.append(f"{st.mean(n30)*100:+5.1f}% / {st.mean(n60)*100:+5.1f}% (cont {sum(x>0 for x in n60)/len(n60):.0%}, n{len(n60)})" if n60 else '-')
        print(f"  move>={int(k*100)}% ADR, ending {t0//60}:{t0%60:02d}: 22-24 {row[0]:38s} | 25-26 {row[1]}")
print('\nQ8. Noise: from a random entry, how far does price go against you before it goes X in your favour? Stop that survives 70% / 80% of random entries, by entry hour (pts, 2025-26)')
import random; random.seed(2)
for X in (40, 60, 100):
    line = []
    for h0 in (570, 600, 660, 720, 780, 840):
        adv = []
        for d, b in DAYS:
            if d < 20250101 or len(b) < 380: continue
            for _ in range(3):
                i = random.randrange(h0 - 570, min(h0 - 570 + 60, len(b) - 61)); s = random.choice((1, -1)); e = b[i][1]; worst = 0
                for x in b[i:i + 120]:
                    worst = max(worst, (e - x[3]) if s > 0 else (x[2] - e))
                    if ((x[2] - e) if s > 0 else (e - x[3])) >= X: break
                adv.append(worst)
        adv.sort(); line.append(f"{h0//60}:{h0%60:02d} {adv[int(.7*len(adv))]:.0f}/{adv[int(.8*len(adv))]:.0f}")
    print(f"  to gain {X} pts: " + '  '.join(line))
