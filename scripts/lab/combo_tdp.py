"""Playbook (final defaults) + Trend-Day Pullback, Lucid Flex 50K eval sim (Oct 25 2026)."""
import sys, collections; sys.path.insert(0, '.'); sys.path.insert(0, '../discover')
from rules2 import *
import td
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return g / l if l else 9.9
PB = build("current", be=True, v4t=1.25)
TDPraw = td.run(E=.6, mode='retrace', k=.33, stop='adr', a=.4, R=1.5, hold=999, tend=720)
def tdp(w):
    return [dict(d=t['d'], strat='TDP', side=t['s'], eT=t['em'], eP=t['eP'], stp=t['stp'], tgt=None, xT=t['xT'], xP=t['eP'] + t['s'] * t['pts'],
                 why=t['why'], r=t['risk'], pts=t['pts'], be=None, w=w) for t in TDPraw]
VAR = {'Playbook only': PB, 'TDP only': tdp(1.0), 'Playbook + TDP (full size)': PB + tdp(1.0), 'Playbook + TDP (half size)': PB + tdp(.5)}
for k in VAR: VAR[k] = sorted(VAR[k], key=lambda t: (t['d'], t['eT']))
DAYS = [d for d in D if 20220301 <= d]
byd = {k: collections.defaultdict(list) for k in VAR}
for k in VAR:
    for t in VAR[k]: byd[k][t['d']].append(t)
# overlap
pbd = {t['d'] for t in PB}; tdd = {t['d'] for t in TDPraw}
print(f"TDP days {len(tdd)}, of which Playbook also traded {len(tdd & pbd)}; same-day correlation of 1-MNQ results:")
pbday = collections.defaultdict(float); tdday = collections.defaultdict(float)
for t in PB: pbday[t['d']] += t['pts'] * PV - 2 * COMM
for t in TDPraw: tdday[t['d']] += t['net']
both = sorted(tdd & pbd)
import statistics as st
if len(both) > 3: print('  corr', round(st.correlation([pbday[d] for d in both], [tdday[d] for d in both]), 2))
for k, v in VAR.items():
    R = [t['pts'] * PV - 2 * COMM for t in v]
    print(f"  {k:28s} trades {len(v):5d}  1-MNQ PF {pf(R):.2f}  $ {sum(R):+8.0f}")
def attempt(m, start, f=.65, horizon=250):
    bal = 50000.; peak = 50000.; best = 0.; td_ = 0
    for d in DAYS:
        if d < start: continue
        td_ += 1; mll = min(peak - 2000, 50000); cush = bal - mll
        dp = size_day([dict(t) for t in byd[m].get(d, [])], cush, 'updated', f=f, slipx=8.0)
        bal += dp; best = max(best, dp)
        if bal <= mll: return 'F', td_
        peak = max(peak, bal)
        if bal - 50000 >= 3000 and best <= .5 * (bal - 50000): return 'P', td_
        if td_ >= horizon: return 'O', td_
    return 'O', td_
print("\nLucid Flex 50K eval sim (start every 2nd day, +8 pt extra slip on stops, 65% of room, $1,100 daily budget)")
for lab, a, z in (('2022-24', 20220301, 20241231), ('2025-26', 20250101, 20261023)):
    sts = [d for d in DAYS if a <= d <= z][::2]
    for m in VAR:
        R = [attempt(m, s) for s in sts]; n = len(R); P = sorted(x[1] for x in R if x[0] == 'P')
        med = P[len(P) // 2] if P else None
        print(f"  {lab} {m:28s} pass by 10d {100*sum(x<=10 for x in P)/n:3.0f}%  20d {100*sum(x<=20 for x in P)/n:3.0f}%  40d {100*sum(x<=40 for x in P)/n:3.0f}%  60d {100*sum(x<=60 for x in P)/n:3.0f}%  fail {100*sum(x[0]=='F' for x in R)/n:3.0f}%  median days {med}")
