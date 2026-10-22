"""MNQSCALP backtest analyzer: Run Log + Futures History.
Usage: python3 analyze_backtest.py <runlog.csv> <history.csv>
MNQ = $2/pt/contract. History times are CT; Run Log times are ET.
"""
import csv, sys, datetime, collections

runlog, hist = sys.argv[1], sys.argv[2]
P = lambda s: float(str(s).replace(',', '').replace('$', '') or 0)

h = list(csv.DictReader(open(hist, encoding='utf-8-sig')))
fills = [r for r in h if r['Status'] == 'Filled']
ft = lambda r: datetime.datetime.strptime(r['Fill Time'].replace(' (CT)', ''), '%b %d, %Y %H:%M:%S')
fills.sort(key=ft)

pos, cur, trades = 0, None, []
for r in fills:
    q, px, fee = int(r['Fill Qty']), P(r['Fill Price']), P(r['Total'])
    sgn = 1 if r['Side'] == 'Buy' else -1
    if pos == 0:
        cur = {'start': ft(r), 'side': 'LONG' if sgn > 0 else 'SHORT', 'gross': 0, 'fees': 0, 'legs': []}
    pos += sgn * q
    cur['gross'] -= sgn * q * px * 2
    cur['fees'] += fee
    cur['legs'].append((ft(r).strftime('%H:%M'), r['Side'], q, px, r['Order Type'], r['Trigger price']))
    if pos == 0:
        cur['end'] = ft(r); cur['net'] = cur['gross'] - cur['fees']; trades.append(cur); cur = None

net = sum(t['net'] for t in trades)
wins = sum(t['net'] > 0 for t in trades)
eq = peak = dd = 0
for t in trades:
    eq += t['net']; peak = max(peak, eq); dd = min(dd, eq - peak)
print(f"TRADES {len(trades)}  NET ${net:.2f}  WIN {wins}/{len(trades)}  "
      f"FEES ${sum(t['fees'] for t in trades):.2f}  MAX DD ${dd:.2f}  OPEN AT END {pos}")
print('orders by type/status:', dict(collections.Counter((r['Side'], r['Order Type'], r['Status']) for r in h)))
for t in trades:
    print(f"  {t['start']:%b %d %H:%M}CT {t['side']} net ${t['net']:.2f} legs={t['legs']}")

# stop slippage
for r in h:
    if r['Order Type'].startswith('Stop') and r['Status'] == 'Filled' and r['Trigger price']:
        print(f"  STOP SLIP {r['Fill Time']}: trigger {r['Trigger price']} fill {r['Fill Price']} "
              f"= {abs(P(r['Trigger price']) - P(r['Fill Price'])):.2f} pts")

L = [x for x in csv.reader(open(runlog, encoding='utf-8-sig')) if len(x) >= 5]
msgs = [(x[0], x[1].strip(), x[3], ','.join(x[4:])) for x in L]
keys = ['V4 ENTRY SUBMITTED', 'PER-TRADE STATE RESET', 'ORPHAN STOP', 'STRUCTURAL STOP SUBMITTED',
        'STOP ERROR', 'STOP SUBMISSION', 'FILL EXCEEDS', 'ERROR', 'UNPROTECTED', 'NEW ENTRY DETECTED',
        'MODIFICATION REQUEST', 'STOP NOT WORKING', 'THREE HOUR', 'TP1 DEADLINE']
print('\nRUN LOG COUNTS:', {k: sum(k in m[3] for m in msgs) for k in keys})
# protection delay: entry submit -> stop submit
sub = [m for m in msgs if 'V4 ENTRY SUBMITTED' in m[3] or 'STRUCTURAL STOP SUBMITTED' in m[3]]
for m in sub:
    print('  ', m[0], m[1], m[3][:60])
errs = [m for m in msgs if 'ERROR' in m[3]]
for m in errs[:15]:
    print('  ERR', m[0], m[1], m[2], m[3][:150])
