"""Multiple-testing check: how often does a rule 'pass' (IS PF >= 1.2 and OOS PF >= 1.2, OOS n >= 8) on RANDOM clean days
at the same clock time, with the same sample size as a real event (55 days)? Gives the false-positive rate of the screen."""
import random
from common import *
from trades import RULES
random.seed(7)
for hh in ('0830', '1000', '1400'):
    cd = clean_days(hh); res = {}
    cache = {lab: {d: f(d, hh) for d in cd} for lab, f in RULES}
    passes = 0; tot = 0
    for it in range(300):
        s = random.sample(cd, 55)
        for lab, _ in RULES:
            tr = [dict(d=d, net=cache[lab][d]) for d in s if cache[lab][d] is not None]
            o = tstats(tr)
            if o['IS'][0] and o['OOS'][0]:
                tot += 1; passes += (o['IS'][1] >= 1.2 and o['OOS'][1] >= 1.2 and o['OOS'][0] >= 8)
    print(f'{hh}: random 55-day samples, rules passing the screen: {passes}/{tot} = {passes / tot:.1%}')
