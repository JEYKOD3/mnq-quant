"""JJ Simon fair price on Sundays only: fair = 18:00 open (or Friday close). Raw reversion vs chance + his entries (5m, displacement/BOS toward fair)."""
import sys, datetime, itertools, json
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair')
from fp import ETH, signals, walk, T, PV, COMM, FEAT
from eth_fp import bars
rows = {r['d']: r for r in json.load(open('sun_rows.json'))}
SUN = sorted(rows)
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
# 1) raw: first touch of F +- D within 18:00-20:00, back to F before going S further?
print('Raw reversion to the 18:00 open on Sundays (window to 20:00), S = 25 pts')
for D in (15, 25, 40):
    back = away = 0
    for d in SUN:
        b = bars(d); F = b[0][1]; st = None
        for m, o, h, l, c in b[1:]:
            if m >= 120: break
            if st is None:
                if h >= F + D: st = -1; lvl = F + D
                elif l <= F - D: st = 1; lvl = F - D
                if st is not None and ((st < 0 and h >= lvl + 25) or (st > 0 and l <= lvl - 25)): away += 1; break
                continue
            if (h >= lvl + 25) if st < 0 else (l <= lvl - 25): away += 1; break
            if (l <= F) if st < 0 else (h >= F): back += 1; break
    n = back + away
    print(f"  {D} pts away: back first {back/n:.0%} vs chance {25/(D+25):.0%} (n {n})")
# 2) his entries on 5m: signal toward F, room >= 0.8 x target, stop/target, max 4 trades, 3 losses, window 18:05-20:00
def run(fair='open', sig='either', S=25, Tg=38, md='f', end=120, room=.8, maxtr=4):
    out = []
    for d in SUN:
        b = bars(d); F = b[0][1] if fair == 'open' else rows[d]['fri']
        n = 0; losses = 0; busy = -1
        for i in range(2, len(b) - 1):
            m = b[i][0]
            if m >= end or n >= maxtr or losses >= 3: break
            if m < busy: continue
            s, ext = signals(b, F, i, sig)
            if not s: continue
            e = b[i + 1][1] + s * T; dist = (F - e) * s
            tg = Tg if md == 'f' else dist
            if md == 'f' and dist < room * Tg: continue
            if tg <= 2: continue
            r = walk(b, i + 1, s, e, S, tg, None, end + 15)
            out.append((d, r['pts'] * PV - 2 * COMM)); n += 1
            losses = losses + 1 if r['pts'] * PV - 2 * COMM < 0 else 0; busy = r['xm']
    return out
print('\nHis reversion entries, Sundays 18:05-20:00 (5m bars, 1 MNQ, costs in)')
res = []
for fair, sig, (S, Tg, md) in itertools.product(['open', 'fri'], ['either', 'disp', 'bos'], [(15, 23, 'f'), (25, 38, 'f'), (25, 25, 'f'), (38, 38, 'f'), (25, 0, 'fair'), (38, 0, 'fair')]):
    tr = run(fair, sig, S, Tg, md)
    if len(tr) < 20: continue
    a = [t[1] for t in tr if t[0] <= 20241231]; z = [t[1] for t in tr if t[0] > 20241231]
    res.append((fair, sig, S, Tg or 'fair', len(tr), round(sum(t[1] > 0 for t in tr) / len(tr), 2), pf([t[1] for t in tr]), pf(a), pf(z)))
for r in sorted(res, key=lambda r: -r[6]):
    print(f"  fair={'18:00 open' if r[0]=='open' else 'Fri close':10s} {r[1]:6s} {r[2]}/{r[3]}  n{r[4]:3d} win {r[5]:.0%} PF {r[6]} ({r[7]}|{r[8]})")
print('PF>1 both periods:', sum(r[7] > 1 and r[8] > 1 for r in res), 'of', len(res))
