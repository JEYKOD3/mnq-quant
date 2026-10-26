"""Shared loaders for the red-folder study (Oct 25 2026). Times: ETH 5m bars keyed by minutes from 18:00 (m18).
Prices in points. 1 MNQ = $2/pt, costs 2.37/side + 1 tick slippage on entry and stops (same as fp.walk)."""
import sys, csv, collections, statistics as st
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair'); sys.path.insert(0, '/home/claude/mnq-quant/scripts/lab')
from fp import DAYS, FEAT, ETH, walk, T, PV, COMM
from eth_fp import bars as eth_bars
RTH = dict(DAYS)
DLIST = [d for d, _ in DAYS]
EXT = collections.defaultdict(dict)   # date -> {event: 'hhmm'}
APPROX = {}
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates_ext.csv')):
    EXT[int(r['date'])][r['event']] = r['time_et']; APPROX[(int(r['date']), r['event'])] = int(r['approx'])
MAJOR = {'CPI', 'PPI', 'NFP', 'FOMC', 'GDP', 'PCE', 'RETAIL', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'FOMC_MIN', 'TESTIMONY', 'JACKSON'}
def m18(hhmm): h, m = divmod(int(hhmm), 100); return (h * 60 + m - 1080) % 1440
_EB = {}
def eb(d):
    if d not in _EB:
        b = eth_bars(d) if d in ETH else []
        _EB[d] = (b, {x[0]: i for i, x in enumerate(b)})
    return _EB[d]
def adr(d): f = FEAT.get(d); return f['adr'] if f else None
def per(d): return 'IS' if d <= 20241231 else 'OOS'
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def tstats(tr):
    o = {}
    for p in ('IS', 'OOS', 'ALL'):
        v = [t['net'] for t in tr if p == 'ALL' or per(t['d']) == p]
        o[p] = (len(v), pf(v) if v else 0, round(sum(v) / len(v)) if v else 0, round(sum(x > 0 for x in v) / len(v), 2) if v else 0)
    return o
def fmt(o): return ' | '.join(f"{p} n{o[p][0]:3d} PF {o[p][1]:4.2f} ${o[p][2]:+4d} w{o[p][3]:.0%}" for p in ('IS', 'OOS', 'ALL'))
def event_days(ev):
    return sorted((d, t[ev]) for d, t in EXT.items() if ev in t and d in ETH and d in RTH and d >= 20220101)
def clean_days(hhmm):
    """baseline: trading days with no major red folder at all and nothing (incl. claims) at this time"""
    out = []
    for d in DLIST:
        if d < 20220101 or d not in ETH: continue
        e = EXT.get(d, {})
        if any(k in MAJOR for k in e) or hhmm in e.values(): continue
        out.append(d)
    return out
def next_day(d):
    i = DLIST.index(d); return DLIST[i + 1] if i + 1 < len(DLIST) else None
