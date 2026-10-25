import sys; sys.path.insert(0, '.')
exec(open('combo_tdp.py').read().split('# overlap')[0])
m = 'Playbook + TDP (full size)'
by = collections.defaultdict(list)
for t in VAR[m]:
    if 20261001 <= t['d'] <= 20261031: by[t['d']].append(t)
fm = lambda x: f"{x//60}:{x%60:02d}"
print('October 2026 days, strategies firing, 1-MNQ result:')
for d in sorted(by):
    ts = [dict(t) for t in by[d]]; net = size_day(ts, 2000, 'updated', f=.65, dll=1100)
    print(f"  {d}: {', '.join(t['strat'] for t in by[d]):40s} eval-sized ${net:+.0f}   1 MNQ each ${sum(t['pts']*PV-2*COMM for t in by[d]):+.0f}")
def ledger(d, cush=2000, f=.65, dll=1100):
    ts = [dict(t) for t in by[d]]; size_day(ts, cush, 'updated', f=f, dll=dll)
    print(f"\n===== {d} ledger (room above max-loss line ${cush}, 65% = ${f*cush:.0f}, daily budget ${dll}) =====")
    ev = []
    for t in ts:
        ev.append((t['eT'], 0, t)); ev.append((t['xT'], 1, t))
        if t.get('be') is not None: ev.append((t['be'], .5, t))
    for tm, kind, t in sorted(ev, key=lambda e: (e[0], e[1])):
        if kind == 0:
            openr = [(u['strat'], u['q'] * u['rc']) for u in ts if u is not t and u['eT'] < t['eT'] and u['xT'] > t['eT'] and u['q'] and not (u.get('be') is not None and u['be'] <= t['eT'])]
            lost = sum(-u['netq'] for u in ts if u['xT'] <= t['eT'] and u['netq'] < 0 and u['q'])
            used = sum(x[1] for x in openr) + lost
            print(f"{fm(tm)}  SIGNAL {t['strat']} {'LONG' if t['side']>0 else 'SHORT'} @ {t['eP']:.2f}, stop {t['stp']:.2f} = {t['r']:.1f} pts -> ${t['rc']:.2f} risk per MNQ (incl. 1 tick + fees)")
            print(f"        in use: open risk {', '.join(f'{a} ${b:.0f}' for a,b in openr) or 'none'} + losses today ${lost:.0f} = ${used:.0f}  -> available min(${dll}-{used:.0f}, ${f*cush:.0f}-{used:.0f}{', half-size cap $'+str(int(t['w']*f*cush)) if t['w']<1 else ''}) = ${min(dll-used, f*cush-used, t['w']*f*cush):.0f}  -> {t['q']} MNQ (risk ${t['q']*t['rc']:.0f})")
        elif kind == .5:
            print(f"{fm(tm)}  {t['strat']} +1R reached: stop moved to breakeven -> its ${t['q']*t['rc']:.0f} risk is freed")
        else:
            print(f"{fm(tm)}  EXIT {t['strat']} {t['why']} {t['pts']:+.1f} pts x {t['q']} = ${t['netq']:+.0f}" + (" (no contracts, signal skipped)" if not t['q'] else ''))
    print(f"DAY TOTAL ${sum(t['netq'] for t in ts):+.0f}   (same trades at 1 MNQ each: ${sum(t['pts']*PV-2*COMM for t in ts):+.0f})")
best = max(by, key=lambda d: (len({t['strat'] for t in by[d]}), len(by[d])))
ledger(best)
