"""How many trades a year, and what big moves happen without us."""
import sys, json, collections, statistics as st, datetime
sys.path.insert(0, '.')
exec(open('team_sim.py').read().split("if __name__")[0])
byd = collections.defaultdict(list)
for t in ALL: byd[t['d']].append(t)
TD = [d for d in D if d >= 20220103 and d in F and len(DB[d]) >= 380]
yr = collections.defaultdict(lambda: dict(sig=0, taken=0, days=0, tdays=0))
for d in TD:
    ts = [dict(t) for t in byd.get(d, [])]; size2(ts, 2000, 'fcfs')
    y = d // 10000; yr[y]['days'] += 1
    yr[y]['sig'] += len(ts); k = sum(t['q'] > 0 for t in ts); yr[y]['taken'] += k; yr[y]['tdays'] += k > 0
print('per year:', dict(yr))
# day anatomy: for every day, the best "move" available: largest swing in one direction within 9:30-16:00 (max of high-after-low, low-after-high)
def day_moves(b):
    o = b[0][1]; c = b[-1][4]; hi = max(x[2] for x in b); lo = min(x[3] for x in b)
    ih = max(range(len(b)), key=lambda i: b[i][2]); il = min(range(len(b)), key=lambda i: b[i][3])
    return o, c, hi, lo, ih, il
rows = []
for d in TD:
    b = DB[d]; f = F[d]; adr = f['adr']
    o, c, hi, lo, ih, il = day_moves(b)
    ts = [dict(t) for t in byd.get(d, [])]; size2(ts, 2000, 'fcfs')
    taken = [t for t in ts if t['q'] > 0]
    oc = (c - o) / adr; rng = (hi - lo) / adr
    trend = abs(c - o) >= .5 * (hi - lo)
    # late move: 13:00 -> close
    i13 = next(i for i, x in enumerate(b) if x[0] >= 780)
    late = (c - b[i13][1]) / adr
    # reversal day: extreme in first hour then close at the other end
    rev = (ih < 60 and (c - lo) < .3 * (hi - lo)) or (il < 60 and (hi - c) < .3 * (hi - lo))
    # morning (9:30-10:30) move and its follow-through
    m1 = (b[59][4] - o) / adr
    gap = f['gap']
    wd = datetime.date(d // 10000, d // 100 % 100, d % 100).weekday()
    rows.append(dict(d=d, adr=adr, oc=oc, rng=rng, trend=trend, late=late, rev=rev, m1=m1, gap=gap, wd=wd,
                     n=len(taken), pnl=sum(t['netq'] for t in ts), strats=[t['strat'] for t in taken],
                     pts=abs(c - o), biggest=max(hi - b[il][3] if il < ih else 0, b[ih][2] - lo if ih < il else 0, hi - lo) / adr))
nt = [r for r in rows if r['n'] == 0]; tt = [r for r in rows if r['n'] > 0]
print(f"days {len(rows)}; trade days {len(tt)} ({len(tt)/len(rows):.0%}); no-trade days {len(nt)}")
def share(v, f): return f"{sum(f(r) for r in v)/max(1,len(v)):.0%}"
print('trend days among no-trade days', share(nt, lambda r: r['trend']), 'vs trade days', share(tt, lambda r: r['trend']))
big = [r for r in rows if abs(r['oc']) >= .6]
print(f"big open-to-close days (>=0.6 ADR): {len(big)}, of which we had no trade: {sum(r['n']==0 for r in big)}")
# categorize no-trade days
cat = collections.Counter()
for r in nt:
    if r['trend'] and abs(r['m1']) < .3: cat['late trend (quiet first hour, then trend)'] += 1
    elif r['trend']: cat['trend day the filters skipped'] += 1
    elif r['rev']: cat['reversal day (first-hour extreme, closes other end)'] += 1
    elif abs(r['late']) >= .35: cat['afternoon move (13:00-16:00 >= 0.35 ADR)'] += 1
    elif r['rng'] < .8: cat['quiet range day'] += 1
    else: cat['choppy wide day'] += 1
print('no-trade day types:', cat.most_common())
# same categories on ALL days, with how often we already trade them and our P&L
cat2 = collections.defaultdict(list)
for r in rows:
    if r['trend'] and abs(r['m1']) < .3: k = 'late trend'
    elif r['trend']: k = 'early trend'
    elif r['rev']: k = 'reversal'
    elif abs(r['late']) >= .35: k = 'afternoon move'
    elif r['rng'] < .8: k = 'quiet range'
    else: k = 'choppy wide'
    cat2[k].append(r)
for k, v in cat2.items():
    print(f"  {k:16s} days {len(v):4d} we trade {sum(r['n']>0 for r in v)/len(v):.0%}  avg P&L/day ${sum(r['pnl'] for r in v)/len(v):+.0f}  avg open-close {st.mean(abs(r['oc']) for r in v):.2f} ADR  avg range {st.mean(r['rng'] for r in v):.2f} ADR")
json.dump(dict(yr={k: v for k, v in yr.items()}, cat=dict(cat), cat2={k: dict(days=len(v), trade=sum(r['n'] > 0 for r in v) / len(v), pnl=sum(r['pnl'] for r in v) / len(v), oc=st.mean(abs(r['oc']) for r in v), rng=st.mean(r['rng'] for r in v)) for k, v in cat2.items()}), open('missed.json', 'w'))
json.dump(rows, open('missed_rows.json', 'w'))
