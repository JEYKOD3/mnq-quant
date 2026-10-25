"""Do JJ Simon's news rules help our trades? 1 MNQ results, 2022-24 | 2025-26."""
import sys, collections, csv, statistics as st
sys.path.insert(0, '.'); sys.path.insert(0, '../discover')
from rules2 import *
import td
PB = build("current", be=True, v4t=1.25)
TDr = td.run(E=.6, mode='retrace', k=.33, stop='adr', a=.4, R=1.5, hold=999, tend=720)
ALL = PB + [dict(d=t['d'], strat='TDP', eT=t['em'], xT=t['xT'], pts=t['pts']) for t in TDr]
EVT = collections.defaultdict(set)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EVT[int(r['date'])].add(r['event'])
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return g / l if l else 9.9
def rep(lab, tr):
    o = []
    for a, z in ((0, 20241231), (20250101, 99999999)):
        v = [t['pts'] * 2 - 4.74 for t in tr if a <= t['d'] <= z]
        o.append(f"n{len(v):4d} PF {pf(v):.2f} avg ${sum(v)/max(1,len(v)):+.0f}")
    print(f"  {lab:52s} 22-24 {o[0]:28s} | 25-26 {o[1]}")
# 1) shock detector: 1m bar range >= k x median range of prior 30 bars and >= 0.06 ADR, outside 9:30-9:34
shock = collections.defaultdict(list)
for d in D:
    b = DB[d]; adr = F[d]['adr'] if d in F else None
    if not adr: continue
    rg = [x[2] - x[3] for x in b]
    for i in range(30, len(b)):
        med = st.median(rg[i - 30:i])
        if rg[i] >= 4 * med and rg[i] >= .06 * adr: shock[d].append(b[i][0])
print('days with a shock bar after 10:00:', sum(1 for d in shock if any(m >= 600 for m in shock[d])), 'of', len(D))
print('\n1) Entries soon after an unexpected spike (shock bar = 1m range >= 4x the last 30 bars and >= 6% ADR)')
for W in (15, 30):
    near = [t for t in ALL if any(0 <= t['eT'] - m <= W for m in shock[t['d']])]
    far = [t for t in ALL if not any(0 <= t['eT'] - m <= W for m in shock[t['d']])]
    rep(f'entered within {W} min after a shock', near); rep(f'no shock in the {W} min before entry', far)
print('\n2) Trades open while a shock happens')
hit = [t for t in ALL if any(t['eT'] < m < t['xT'] for m in shock[t['d']])]
nohit = [t for t in ALL if not any(t['eT'] < m < t['xT'] for m in shock[t['d']])]
rep('a shock happened during the trade', hit); rep('no shock during the trade', nohit)
print('\n3) Scheduled events (CPI/PPI/NFP at 8:30, FOMC at 14:00)')
for e in ('CPI', 'PPI', 'NFP', 'FOMC'):
    rep(f'{e} days, all trades', [t for t in ALL if e in EVT.get(t['d'], ())])
rep('normal days', [t for t in ALL if not EVT.get(t['d'])])
rep('FOMC days, trades still open at 14:00', [t for t in ALL if 'FOMC' in EVT.get(t['d'], ()) and t['eT'] < 840 < t['xT']])
rep('FOMC days, trades closed before 14:00', [t for t in ALL if 'FOMC' in EVT.get(t['d'], ()) and t['xT'] <= 840])
print('\n   by strategy on FOMC days:', {s: round(pf([t['pts']*2-4.74 for t in ALL if t['strat']==s and 'FOMC' in EVT.get(t['d'],())]),2) for s in ('V4+','D2','Pinball','H2','TDP')})
print('   by strategy on CPI days:', {s: round(pf([t['pts']*2-4.74 for t in ALL if t['strat']==s and 'CPI' in EVT.get(t['d'],())]),2) for s in ('V4+','D2','Pinball','H2','TDP')})
