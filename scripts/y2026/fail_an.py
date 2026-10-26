"""Failure analysis for the BASE v31 plan: what pushed non-passing evals into the hole (fast_pass.py rolling evals)."""
import collections, sys
from fast_pass import *
from fast_plans import BASE
tr = build_trades(); byd = byday(tr)
def dtype(d):
    b = DB[d]; f = F.get(d)
    if not f: return '?'
    mv = abs(b[-1][4] - f['open']) / f['adr']
    return 'trend' if mv >= .6 else ('chop' if mv < .25 else 'mid')
for y, (a, z) in YEARS.items():
    R = roll(byd, BASE, a, z, keep=True)
    cause = collections.Counter(); tday = collections.Counter(); ev = collections.Counter(); first_loss = collections.Counter(); size = []
    loser_trades = collections.Counter(); win_trades = collections.Counter()
    for r in R:
        eq = 0
        for d, dp, trs in r['log']:
            for s, q, n in trs:
                (loser_trades if n < 0 else win_trades)[s] += abs(n)
        if r['res'] == 'P': continue
        for d, dp, trs in r['log']:
            eq += dp
            if eq <= -800:
                worst = min(trs, key=lambda x: x[2]) if trs else ('none', 0, 0)
                cause[worst[0]] += 1; tday[dtype(d)] += 1; ev['event' if EV.get(d) else 'no event'] += 1; size.append(worst[1]); break
        else:
            cause['never below -800 (too slow)'] += 1
    n = len(R); np_ = sum(r['res'] != 'P' for r in R)
    print(f"\n{y}: {np_}/{n} not passed in 20 days")
    print(' first hole (equity <= -800) caused by:', dict(cause.most_common()))
    print(' day type of that day:', dict(tday), ' news/event day:', dict(ev), ' median contracts on the losing trade:', sorted(size)[len(size)//2] if size else None)
    print(' $ lost by strategy across all evals:', {k: round(v) for k, v in loser_trades.most_common()}, ' $ won:', {k: round(v) for k, v in win_trades.most_common()})
# per-day stats 2026: fraction of days with no signal, trades/day
d26 = [d for d in D if 20260101 <= d <= 20261023]
cnt = collections.Counter(t['d'] for t in tr if t['d'] >= 20260101)
print('\n2026 days', len(d26), 'days with no signal', sum(cnt[d] == 0 for d in d26), 'trades/day', round(sum(cnt.values()) / len(d26), 2))
v = [net1(t) for t in tr if t['d'] >= 20260101]
rk = [(t['r'] + SLIP * T) * PV + 2 * COMM for t in tr if t['d'] >= 20260101]
print('2026 1-lot net', round(sum(v)), 'per day', round(sum(v) / len(d26), 1), 'avg 1-lot risk $', round(sum(rk) / len(rk)), 'expectancy R/trade', round(sum(v) / sum(rk), 3))
for s in PRI:
    x = [t for t in tr if t['d'] >= 20260101 and t['strat'] == s]
    if x: print(' ', s, 'n', len(x), 'avg risk $', round(sum((t['r'] + SLIP * T) * PV + 2 * COMM for t in x) / len(x)), 'R/trade', round(sum(net1(t) for t in x) / sum((t['r'] + SLIP * T) * PV + 2 * COMM for t in x), 3))
