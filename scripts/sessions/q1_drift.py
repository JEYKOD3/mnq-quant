"""Q1: average move per intraday window (pts and %ADR), by IS/OOS and weekday; plus naive hold-the-window trades with costs."""
import statistics as st, sys
from common import *
W = [('18:00-20:00', 1800, 2000), ('20:00-24:00', 2000, 0), ('00:00-03:00', 0, 300), ('03:00-06:00', 300, 600),
     ('06:00-08:30', 600, 830), ('08:30-09:30', 830, 930), ('09:30-12:00', 930, 1200), ('12:00-14:00', 1200, 1400),
     ('14:00-15:00', 1400, 1500), ('15:00-16:00', 1500, 1600), ('16:00-16:55', 1600, 1655), ('18:00-09:30 ON', 1800, 930)]
def mv(d, a, z):
    O, H, L, C = ETH[d]; ka, kz = slot(a), slot(z) if z != 1655 else NS
    return C[kz - 1] - O[ka]
days = list(sessions())
print('sessions', len(days))
print('window          | IS mean pt  %ADR  up%  t   | OOS mean pt %ADR up%  t  | Mon Tue Wed Thu Fri (all yrs, %ADR)')
for nm, a, z in W:
    out = []
    for per in ((20220101, 20250101), (20250101, 21000101)):
        v = [mv(d, a, z) / adr_of(d) * 100 for d in days if per[0] <= d < per[1]]
        p = [mv(d, a, z) for d in days if per[0] <= d < per[1]]
        t = st.mean(v) / (st.stdev(v) / len(v) ** .5)
        out.append(f"{st.mean(p):+6.1f} {st.mean(v):+5.1f} {sum(x>0 for x in v)/len(v):.0%} {t:+4.1f}")
    dw = []
    for w in range(5):
        v = [mv(d, a, z) / adr_of(d) * 100 for d in days if wd(d) == w]
        dw.append(f"{st.mean(v):+5.1f}")
    print(f"{nm:15s} | {out[0]} | {out[1]} | {' '.join(dw)}")
