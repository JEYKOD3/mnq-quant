"""Sanity check of the date list: range of the release 5m bar / median range of the 12 bars before (ETH 5m).
Real release days should show a clearly larger ratio than clean days at the same time."""
from common import *
def ratio(d, hhmm):
    b, ix = eb(d); k = m18(hhmm)
    if k not in ix or ix[k] < 12: return None
    i = ix[k]; med = st.median(x[2] - x[3] for x in b[i - 12:i]) or .25
    return (b[i][2] - b[i][3]) / med
base = {}
for hh in ('0830', '1000', '1400', '1430'):
    v = [r for r in (ratio(d, hh) for d in clean_days(hh)) if r]; base[hh] = st.median(v)
    print(f'clean days {hh}: median ratio {st.median(v):.2f} n {len(v)}')
for ev in ('CPI', 'PPI', 'NFP', 'GDP', 'PCE', 'RETAIL', 'CLAIMS', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'FOMC', 'FOMC_PC', 'FOMC_MIN', 'TESTIMONY', 'JACKSON'):
    xs = [(d, ratio(d, t)) for d, t in event_days(ev)]; xs = [x for x in xs if x[1]]
    v = [r for _, r in xs]
    low = [d for d, r in xs if r < base[event_days(ev)[0][1]] * 1.0]
    print(f'{ev:10s} n {len(v):3d} median ratio {st.median(v):5.2f}  share > 2x clean-median {sum(r > 2 * base[event_days(ev)[0][1]] for r in v) / len(v):.0%}  below clean median: {len(low)} {low[:12]}')
