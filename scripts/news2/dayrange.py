"""RTH day range and |open->close| in ADR units on each red-folder day vs days with no major red folder."""
from common import *
def dr(d):
    b = RTH[d]; A = adr(d)
    return ((max(x[2] for x in b) - min(x[3] for x in b)) / A, abs(b[-1][4] - b[0][1]) / A) if A else None
clean = [d for d in DLIST if d >= 20220101 and not any(k in MAJOR for k in EXT.get(d, {}))]
def show(lab, ds):
    v = [x for x in (dr(d) for d in ds) if x]
    print(f'{lab:10s} n {len(v):3d}  median range {st.median(x[0] for x in v):.2f} ADR   median |open-close| {st.median(x[1] for x in v):.2f}  trend days (|o-c|>0.6 ADR) {sum(x[1] > .6 for x in v) / len(v):.0%}')
show('CLEAN', clean)
for ev in ('CPI', 'PPI', 'NFP', 'GDP', 'PCE', 'RETAIL', 'CLAIMS', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'TESTIMONY', 'FOMC', 'FOMC_MIN'):
    show(ev, [d for d, _ in event_days(ev) if not (ev == 'CLAIMS' and any(e in MAJOR for e in EXT[d]))])
fd = set(d for d, _ in event_days('FOMC')); show('postFOMC', [next_day(d) for d in fd if next_day(d)])
