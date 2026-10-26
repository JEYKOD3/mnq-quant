"""Q5: robustness checks on the afternoon continuation candidate (side split, overnight agreement filter, entry-time jitter)."""
from common import *
from q2_tests import P, cond_hold, sig_day
def agree(t):
    return lambda d: (P(d, 930) - ETH[d][0][0]) * (P(d, t) - P(d, 930, 'o')) > 0
for t in (1230, 1300):
    for sk in (None, 0.25):
        tr = cond_hold(sig_day(t), t, 1555, 0.2, 'cont', None, sk)
        print(row(f"{t} stop{sk} longs", [x for x in tr if x['side'] > 0]))
        print(row(f"{t} stop{sk} shorts", [x for x in tr if x['side'] < 0]))
        print(row(f"{t} stop{sk} ON agrees", cond_hold(sig_day(t), t, 1555, 0.2, 'cont', agree(t), sk)))
        print(row(f"{t} stop{sk} ON disagrees", cond_hold(sig_day(t), t, 1555, 0.2, 'cont', lambda d, t=t: not agree(t)(d), sk)))
        print(row(f"{t} stop{sk} exit 15:00", cond_hold(sig_day(t), t, 1500, 0.2, 'cont', None, sk)))
        print(row(f"{t} stop{sk} exit 15:30", cond_hold(sig_day(t), t, 1530, 0.2, 'cont', None, sk)))
for thr in (0.1, 0.15, 0.2, 0.25, 0.3):
    print(row(f"1300 thr{thr} stop0.25", cond_hold(sig_day(1300), 1300, 1555, thr, 'cont', None, 0.25)))
    print(row(f"1300 thr{thr} stop0.35", cond_hold(sig_day(1300), 1300, 1555, thr, 'cont', None, 0.35)))
