"""Shared data for the discovery questions (Oct 25 2026). RTH 1m bars 2022+, ETH 5m, features, macro calendar."""
import sys, collections, csv
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair'); sys.path.insert(0, '/home/claude/mnq-quant/scripts/lab')
from fp import DAYS, FEAT, ETH, EV
from core import agg
FOMC = set()
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')):
    if r['event'] == 'FOMC': FOMC.add(int(r['date']))
def per(d): return 'A' if d <= 20241231 else 'Z'
def overnight(d):
    e = ETH.get(d)
    if not e: return None
    xs = [v for k, v in e.items() if (k >= 1800 or k < 930)]
    if len(xs) < 100: return None
    return max(x[1] for x in xs), min(x[2] for x in xs)
