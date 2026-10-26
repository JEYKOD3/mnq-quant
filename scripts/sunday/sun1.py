"""Sunday 6 PM reopen patterns, MNQ 5m ETH bars 2022-2026."""
import sys, datetime, statistics as st, collections
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair'); sys.path.insert(0, '/home/claude/mnq-quant/scripts/lab')
from fp import ETH, FEAT
from eth_fp import bars
keys = sorted(ETH)
rows = []
for i, d in enumerate(keys):
    if d < 20220101 or i == 0: continue
    dt = datetime.date(d // 10000, d // 100 % 100, d % 100)
    if dt.weekday() != 0: continue          # session keyed by Monday = opens Sunday 18:00
    prev = keys[i - 1]
    pb = bars(prev); b = bars(d)
    if not pb or not b or b[0][0] != 0: continue
    fri = pb[-1][4]                          # Friday last 5m close (~16:59)
    adr = None
    for k in sorted(FEAT):
        if k <= d: adr = FEAT[k]['adr']
    if not adr: continue
    o = b[0][1]; gap = o - fri
    idx = {x[0]: j for j, x in enumerate(b)}
    def px(m): return b[idx[m] - 1][4] if m in idx else None   # close of bar ending at minute m
    def touched(level, m_end):
        for x in b:
            if x[0] >= m_end: break
            if x[2] >= level >= x[3]: return x[0]
        return None
    s = 1 if gap > 0 else -1
    rows.append(dict(d=d, fri=fri, o=o, gap=gap, gapA=gap / adr, adr=adr,
                     fill30=touched(fri, 30), fill120=touched(fri, 120), fill_rth=touched(fri, 930),
                     fake120=touched(o + gap, 120) if gap else None,
                     m30=(px(30) - o) * s / adr if px(30) else None, m60=(px(60) - o) * s / adr if px(60) else None,
                     m120=(px(120) - o) * s / adr if px(120) else None,
                     rng60=(max(x[2] for x in b if x[0] < 60) - min(x[3] for x in b if x[0] < 60)) / adr,
                     rng120=(max(x[2] for x in b if x[0] < 120) - min(x[3] for x in b if x[0] < 120)) / adr,
                     rthdir=(b[-1][4] - px(930)) if px(930) else None, eve=(px(120) - o) if px(120) else None,
                     on=(px(930) - o) if px(930) else None))
print('Sunday sessions:', len(rows), rows[0]['d'], '->', rows[-1]['d'])
g = [abs(r['gap']) for r in rows]; gA = [abs(r['gapA']) for r in rows]
print(f"gap size: median {st.median(g):.0f} pts ({st.median(gA)*100:.0f}% ADR), 75th pct {sorted(g)[int(.75*len(g))]:.0f} pts, max {max(g):.0f}")
print('gap direction up:', sum(r['gap'] > 0 for r in rows), 'down:', sum(r['gap'] < 0 for r in rows))
for lo, hi in ((0, .05), (.05, .1), (.1, .2), (.2, .4), (.4, 9)):
    v = [r for r in rows if lo <= abs(r['gapA']) < hi and r['gap'] != 0]
    if not v: continue
    f = lambda k: sum(r[k] is not None for r in v) / len(v)
    print(f"  gap {int(lo*100):2d}-{int(hi*100) if hi<9 else 'up'}% ADR (n{len(v):3d}): fills by 18:30 {f('fill30'):.0%}, by 20:00 {f('fill120'):.0%}, by Mon 9:30 {f('fill_rth'):.0%} | fake level same distance other side by 20:00 {f('fake120'):.0%} | move in gap direction 30m {st.mean(r['m30'] for r in v if r['m30'] is not None)*100:+.1f}% 2h {st.mean(r['m120'] for r in v if r['m120'] is not None)*100:+.1f}% ADR")
print(f"first 2h range: median {st.median(r['rng120'] for r in rows)*100:.0f}% ADR (first 1h {st.median(r['rng60'] for r in rows)*100:.0f}%)")
# weekday evening comparison: 18:00-20:00 range for other days
other = []
for d in keys:
    if d < 20220101: continue
    dt = datetime.date(d // 10000, d // 100 % 100, d % 100)
    if dt.weekday() == 0: continue
    b = bars(d)
    if not b or b[0][0] != 0: continue
    a = [k for k in sorted(FEAT) if k <= d]
    if not a: continue
    adr = FEAT[a[-1]]['adr']
    w = [x for x in b if x[0] < 120]
    other.append((max(x[2] for x in w) - min(x[3] for x in w)) / adr)
print(f"other weekday evenings 18:00-20:00 range: median {st.median(other)*100:.0f}% ADR")
# does Sunday evening direction (18:00-20:00) predict Monday RTH?
v = [r for r in rows if r['eve'] is not None and r['rthdir'] is not None and abs(r['eve']) > 0]
print('Sunday 18-20 direction = Monday 9:30-16:00 direction:', f"{sum((r['eve']>0)==(r['rthdir']>0) for r in v)/len(v):.0%} (n{len(v)})")
v = [r for r in rows if r['on'] is not None and r['rthdir'] is not None]
print('Sunday open->Mon 9:30 direction = Monday RTH direction:', f"{sum((r['on']>0)==(r['rthdir']>0) for r in v)/len(v):.0%}")
print('gap direction = Sunday 18-20 direction:', f"{sum((r['gap']>0)==(r['eve']>0) for r in rows if r['eve'] and r['gap'])/len([r for r in rows if r['eve'] and r['gap']]):.0%}")
import json; json.dump(rows, open('sun_rows.json', 'w'))
