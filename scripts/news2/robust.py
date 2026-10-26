"""Robustness for the candidate ideas: (1) permutation p-value vs random clean days at the same clock time and same
number of days, (2) neighbour parameters, (3) pooled families across events."""
import random
from common import *
from trades import days_for, rule_fade15, rule_follow, rule_nextday, RULES
random.seed(11)
def run(f, DD): return [dict(d=d, net=v) for d, h in DD for v in [f(d, h)] if v is not None]
def pval(f, ev, sign=1, it=2000):
    DD = days_for(ev); hh = DD[0][1]; tr = run(f, DD); tot = sum(t['net'] for t in tr) * sign
    cd = clean_days(hh); cache = {d: f(d, hh) for d in cd}
    k = 0
    for _ in range(it):
        s = random.sample(cd, len(DD)); v = sum(cache[d] for d in s if cache[d] is not None) * sign
        k += v >= tot
    return tr, k / it
C = [('FOMC', 'fade15 k.10 tgt=F', lambda d, h: rule_fade15(d, h, .10, 1.0), 1),
     ('FOMC', 'fade30 ->close', lambda d, h: rule_follow(d, h, 30, .10, .25, fade=True), 1),
     ('FOMC', 'fade60 ->close', lambda d, h: rule_follow(d, h, 60, .10, .25, fade=True), 1),
     ('FOMC', 'follow30 ->close (claim: loses)', lambda d, h: rule_follow(d, h, 30, .10, .25), -1),
     ('FOMC', 'next day fade', lambda d, h: rule_nextday(d, h, True), 1),
     ('FOMC_PC', 'fade15 k.10 tgt=F', lambda d, h: rule_fade15(d, h, .10, 1.0), 1),
     ('FOMC_PC', 'follow60 ->close', lambda d, h: rule_follow(d, h, 60, .10, .25), 1),
     ('NFP', 'fade30 ->close', lambda d, h: rule_follow(d, h, 30, .10, .25, fade=True), 1),
     ('NFP', 'fade60 ->close', lambda d, h: rule_follow(d, h, 60, .10, .25, fade=True), 1),
     ('CPI', 'fade15 k.10 tgt=F', lambda d, h: rule_fade15(d, h, .10, 1.0), 1),
     ('CPI', 'follow60 (claim: loses)', lambda d, h: rule_follow(d, h, 60, .10, .25), -1),
     ('RETAIL', 'next day fade', lambda d, h: rule_nextday(d, h, True), 1),
     ('PCE', 'follow60 ->close', lambda d, h: rule_follow(d, h, 60, .10, .25), 1),
     ('JOLTS', 'follow30 2R', lambda d, h: rule_follow(d, h, 30, .10, .25, tgtR=2), 1),
     ('ISM_MFG', 'fade15 (claim: loses)', lambda d, h: rule_fade15(d, h, .10, 1.0), -1),
     ('ISM_SRV', 'fade15 (claim: loses)', lambda d, h: rule_fade15(d, h, .10, 1.0), -1),
     ('FOMC_MIN', 'follow30 (claim: loses)', lambda d, h: rule_follow(d, h, 30, .10, .25), -1)]
print('1) permutation p-value (share of random clean-day samples doing at least as well in the claimed direction)')
for ev, lab, f, sg in C:
    tr, p = pval(f, ev, sg)
    print(f'  {ev:8s} {lab:32s} {fmt(tstats(tr))}  p={p:.3f}')
print('\n2) neighbours')
for ev in ('FOMC', 'NFP'):
    DD = days_for(ev)
    for w in (15, 20, 30, 45, 60, 90):
        for k in (.05, .10, .15):
            for sk in (.20, .25, .35):
                tr = run(lambda d, h: rule_follow(d, h, w, k, sk, fade=True), DD)
                o = tstats(tr)
                if sk == .25 or k == .10: print(f'  {ev} fade at T+{w} hold to close, k{k} stop{sk}ADR: {fmt(o)}')
DD = days_for('FOMC')
for k in (.03, .05, .10, .15, .20):
    for rr in (.5, .75, 1.0, 1.5):
        print(f'  FOMC fade15 to F (target=F) k{k} stop{rr}x dist: {fmt(tstats(run(lambda d, h: rule_fade15(d, h, k, rr), DD)))}')
for ev in ('RETAIL', 'FOMC', 'CPI', 'NFP', 'PCE'):
    for sk in (.3, .5, .8):
        for k in (0, .2, .4):
            print(f'  {ev} next-day fade k{k} stop{sk}: {fmt(tstats(run(lambda d, h: rule_nextday(d, h, True, sk, k), days_for(ev))))}')
print('\n3) pooled families (all major events: CPI PPI NFP GDP PCE RETAIL ISM_MFG ISM_SRV JOLTS FOMC FOMC_PC FOMC_MIN TESTIMONY)')
EVS = ['CPI', 'PPI', 'NFP', 'GDP', 'PCE', 'RETAIL', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'FOMC', 'FOMC_PC', 'FOMC_MIN', 'TESTIMONY']
for lab, f in RULES:
    tr = []
    for ev in EVS: tr += run(f, days_for(ev))
    cl = []
    for hh in ('0830', '1000', '1400'): cl += run(f, [(d, hh) for d in clean_days(hh)])
    print(f'  {lab:32s} events {fmt(tstats(tr))}\n  {"":32s} clean  {fmt(tstats(cl))}')
