"""Avoid-trading rules: do our existing strategies (V4+, D2, Pinball, H2, TDP as in scripts/lab/news_test.py) do worse around
red folders? 1 MNQ per trade, net = pts*2 - 4.74 (slippage already inside pts). Run from anywhere."""
import os, sys, collections
os.chdir('/home/claude/mnq-quant/scripts/lab'); sys.path.insert(0, '.'); sys.path.insert(0, '../discover')
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from rules2 import build
    import td
    PB = build("current", be=True, v4t=1.25)
    TDr = td.run(E=.6, mode='retrace', k=.33, stop='adr', a=.4, R=1.5, hold=999, tend=720)
ALL = [dict(d=t['d'], strat=t['strat'], eT=t['eT'], xT=t['xT'], pts=t['pts']) for t in PB] + \
      [dict(d=t['d'], strat='TDP', eT=t['em'], xT=t['xT'], pts=t['pts']) for t in TDr]
for t in ALL: t['net'] = t['pts'] * 2 - 4.74
sys.path.insert(0, '/home/claude/mnq-quant/scripts/news2')
import csv
EXT = collections.defaultdict(dict)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates_ext.csv')): EXT[int(r['date'])][r['event']] = int(r['time_et'])
def mm(hhmm): return hhmm // 100 * 60 + hhmm % 100
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return g / l if l else 9.9
def rep(lab, tr):
    o = []
    for a, z in ((0, 20241231), (20250101, 99999999)):
        v = [t['net'] for t in tr if a <= t['d'] <= z]
        o.append(f"n{len(v):4d} PF {pf(v):4.2f} avg ${sum(v) / max(1, len(v)):+4.0f} tot ${sum(v):+6.0f}")
    print(f"  {lab:58s} 22-24 {o[0]} | 25-26 {o[1]}")
print(f'{len(ALL)} trades')
rep('ALL trades', ALL)
MAJOR = ['CPI', 'PPI', 'NFP', 'GDP', 'PCE', 'RETAIL', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'FOMC', 'FOMC_MIN', 'TESTIMONY', 'CLAIMS']
print('\n1) by event day (all trades that day)')
for ev in MAJOR: rep(f'{ev} days', [t for t in ALL if ev in EXT.get(t['d'], {})])
rep('days with no major red folder (claims allowed)', [t for t in ALL if not any(e in EXT.get(t['d'], {}) for e in MAJOR[:-1])])
print('\n2) intraday 10:00 / 14:00 events: trades entered in [T-15, T+15) vs held across T vs the rest of that day')
for ev in ('ISM_MFG', 'ISM_SRV', 'JOLTS', 'TESTIMONY', 'PCE', 'FOMC', 'FOMC_MIN'):
    near = []; across = []; other = []
    for t in ALL:
        T = EXT.get(t['d'], {}).get(ev)
        if T is None or T == 830: continue
        T = mm(T)
        if T - 15 <= t['eT'] < T + 15: near.append(t)
        elif t['eT'] < T <= t['xT']: across.append(t)
        else: other.append(t)
    rep(f'{ev}: entered T-15..T+15', near); rep(f'{ev}: open across T', across); rep(f'{ev}: rest of the day', other)
print('\n3) any 10:00 red folder (ISM, JOLTS, testimony, 10:00 PCE): entries 9:45-10:15 vs same window on days without one')
def has10(d): return any(v == 1000 for e, v in EXT.get(d, {}).items() if e in MAJOR)
w = lambda t: 585 <= t['eT'] < 615
rep('entered 9:45-10:15 on 10:00 red-folder days', [t for t in ALL if w(t) and has10(t['d'])])
rep('entered 9:45-10:15 on other days', [t for t in ALL if w(t) and not has10(t['d'])])
rep('open across 10:00 on 10:00 red-folder days', [t for t in ALL if t['eT'] < 600 <= t['xT'] and has10(t['d'])])
rep('open across 10:00 on other days', [t for t in ALL if t['eT'] < 600 <= t['xT'] and not has10(t['d'])])
print('\n4) candidate avoid rules: total $ effect if we skip these entries')
rules = {
    'skip entries 9:50-10:05 on 10:00 red-folder days': lambda t: 590 <= t['eT'] < 605 and has10(t['d']),
    'skip entries 13:45-14:30 on FOMC days': lambda t: 825 <= t['eT'] < 870 and 'FOMC' in EXT.get(t['d'], {}),
    'skip entries after 13:30 on FOMC days': lambda t: t['eT'] >= 810 and 'FOMC' in EXT.get(t['d'], {}),
    'skip entries 13:45-14:15 on FOMC minutes days': lambda t: 825 <= t['eT'] < 855 and 'FOMC_MIN' in EXT.get(t['d'], {}),
    'skip all FOMC days': lambda t: 'FOMC' in EXT.get(t['d'], {}),
    'skip the day after FOMC': lambda t: any('FOMC' in EXT.get(x, {}) for x in [prev.get(t['d'])]),
}
days = sorted(set(t['d'] for t in ALL)); import bisect
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair')
from fp import DAYS as _D
DL = [d for d, _ in _D]; prev = {DL[i]: DL[i - 1] for i in range(1, len(DL))}
for lab, f in rules.items():
    sk = [t for t in ALL if f(t)]; kept = [t for t in ALL if not f(t)]
    rep(f'{lab}: skipped trades', sk)
    rep(f'{lab}: kept', kept)
print('\n5) by strategy, trades held across a 10:00 red folder or FOMC 14:00')
for s in ('V4+', 'D2', 'Pinball', 'H2', 'TDP'):
    rep(f'{s}: open across 10:00 red folder', [t for t in ALL if t['strat'] == s and t['eT'] < 600 <= t['xT'] and has10(t['d'])])
    rep(f'{s}: open across 10:00 other days', [t for t in ALL if t['strat'] == s and t['eT'] < 600 <= t['xT'] and not has10(t['d'])])
