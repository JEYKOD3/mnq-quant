"""Pre-FOMC drift check (Lucca-Moench 2015 found US stocks drift UP in the 24h before the 14:00 statement).
Signed move in ADR units: prior day 14:00 -> FOMC day 13:55, and 9:30 -> 13:55, vs clean days. Also a long-only trade."""
from common import *
def mv(d, a_day, a_hm, b_hm):
    pass
rows = {'FOMC': [], 'CLEAN': []}
fomc = set(d for d, _ in event_days('FOMC')); clean = set(clean_days('1400'))
for i, d in enumerate(DLIST):
    if d < 20220101 or i == 0: continue
    p = DLIST[i - 1]; b = RTH[d]; pb = RTH[p]; A = adr(d)
    if not A: continue
    ix = {x[0]: x for x in b}; pix = {x[0]: x for x in pb}
    if 835 not in ix or 840 not in pix: continue
    a24 = (ix[835][4] - pix[840][1]) / A; day = (ix[835][4] - b[0][1]) / A
    net = (ix[835][4] - b[0][1] - 2 * T) * PV - 2 * COMM   # long at the open, exit 13:55
    k = 'FOMC' if d in fomc else 'CLEAN' if d in clean else None
    if k: rows[k].append((d, a24, day, net))
for k, v in rows.items():
    for p in ('IS', 'OOS', 'ALL'):
        vv = [x for x in v if p == 'ALL' or per(x[0]) == p]
        if not vv: continue
        print(f"{k:5s} {p:3s} n {len(vv):3d}  24h drift mean {sum(x[1] for x in vv) / len(vv):+.3f} ADR (up {sum(x[1] > 0 for x in vv) / len(vv):.0%})"
              f"  9:30->13:55 mean {sum(x[2] for x in vv) / len(vv):+.3f} (up {sum(x[2] > 0 for x in vv) / len(vv):.0%})  long open->13:55 PF {pf([x[3] for x in vv]):.2f} avg ${sum(x[3] for x in vv) / len(vv):+.0f}")
