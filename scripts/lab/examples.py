import sys; sys.path.insert(0, '.')
exec(open('combo_tdp.py').read().split('# overlap')[0])
m = 'Playbook + TDP (full size)'
days = collections.defaultdict(list)
for t in VAR[m]:
    if t['d'] >= 20250101: days[t['d']].append(t)
def fm(x): return f"{x//60}:{x%60:02d}"
rows = []
for d, trs in days.items():
    ts = [dict(t) for t in trs]; net = size_day(ts, 2000, 'updated', f=.65, dll=1100)
    rows.append((d, net, ts))
# overall stats per strategy 2025-26 and 2022-24
for P, a, z in (('2022-24', 20220101, 20241231), ('2025-26', 20250101, 20991231)):
    for s in ('V4+', 'D2', 'Pinball', 'H2', 'TDP'):
        x = [t for t in VAR[m] if t['strat'] == s and a <= t['d'] <= z]
        R = [t['pts'] * PV - 2 * COMM for t in x]
        hold = sum(t['xT'] - t['eT'] for t in x) / len(x)
        print(f"{P} {s:8s} n{len(x):4d} ({len(x)/(3 if P=='2022-24' else 1.8):4.0f}/yr) win {sum(r>0 for r in R)/len(R):.0%} PF {pf(R):.2f} avg entry {fm(int(sum(t['eT'] for t in x)/len(x)))} avg hold {hold:.0f} min")
multi = [r for r in rows if len({t['strat'] for t in r[2]}) >= 3]
print('\ndays with 3+ strategies (2025-26):', len(multi), 'of', len(rows), 'trading days')
pick = sorted(rows, key=lambda r: -r[1])[:3] + sorted(rows, key=lambda r: r[1])[:2]
for d, net, ts in sorted(rows, key=lambda r: r[0])[-6:] + pick:
    print(f"\n{d}  day net ${net:+.0f} (fresh 50K eval, $2,000 room)")
    for t in ts:
        print(f"   {t['strat']:7s} {'LONG ' if t['side']>0 else 'SHORT'} in {fm(t['eT'])} @ {t['eP']:.2f}  stop {t['stp']:.2f} ({t['r']:.0f} pts)  out {fm(t['xT'])} {t['why']:9s} {t['pts']:+7.1f} pts  x{t['q']} MNQ = ${t['netq']:+.0f}")
