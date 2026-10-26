"""Tonight's pattern: gap fills (touches Friday close), then price swings around Friday close. Test JJ reversion to Friday close AFTER the fill, Sundays only."""
import sys, json, itertools
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair')
from fp import signals, walk, T, PV, COMM
from eth_fp import bars
rows = json.load(open('sun_rows.json'))
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def run(sig, S, Tg, md, end, minA, room=.8):
    out = []; nd = 0
    for r in rows:
        if abs(r['gapA']) < minA: continue
        b = bars(r['d']); F = r['fri']
        fill = next((i for i, x in enumerate(b) if x[3] <= F <= x[2]), None)
        if fill is None or b[fill][0] >= end - 30: continue
        nd += 1; n = 0; losses = 0; busy = -1
        for i in range(fill + 2, len(b) - 1):
            m = b[i][0]
            if m >= end or n >= 4 or losses >= 3: break
            if m < busy: continue
            s, ext = signals(b, F, i, sig)
            if not s: continue
            e = b[i + 1][1] + s * T; dist = (F - e) * s
            tg = Tg if md == 'f' else dist
            if md == 'f' and dist < room * Tg: continue
            if tg <= 2: continue
            w = walk(b, i + 1, s, e, S, tg, None, end + 15)
            net = w['pts'] * PV - 2 * COMM
            out.append((r['d'], net)); n += 1; losses = losses + 1 if net < 0 else 0; busy = w['xm']
    return out, nd
print('After the gap fills, trade back toward Friday close (5m, 1 MNQ, costs in)')
for minA, end in ((.05, 120), (.1, 120), (.1, 240), (.2, 240)):
    for sig, (S, Tg, md) in itertools.product(['either', 'bos', 'disp'], [(25, 25, 'f'), (25, 38, 'f'), (38, 0, 'fair'), (25, 0, 'fair')]):
        tr, nd = run(sig, S, Tg, md, end, minA)
        if len(tr) < 15: continue
        a = [t[1] for t in tr if t[0] <= 20241231]; z = [t[1] for t in tr if t[0] > 20241231]
        print(f"  gap>={minA} until {18+end//60}:00 ({nd} Sundays filled)  {sig:6s} {S}/{Tg or 'fair'}  n{len(tr):3d} win {sum(t[1]>0 for t in tr)/len(tr):.0%} PF {pf([t[1] for t in tr])} ({pf(a)}|{pf(z)})")
