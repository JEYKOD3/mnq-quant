"""Run all researched plans (2026 primary, 2025 check) + propfirmmatch CSV eval screen. Writes knowledge/src/prop_firms.json."""
import json, csv, sys
from prop_sim import *
from prop_plans import PLANS, PLANS_INTRA
tr = NEW()
OUT = dict(meta=dict(date='2026-10-25', engine='NEW rules (rulesets.NEW), stop-day N=3 + (d) passed, 65% of room, $1,100 daily budget (min(1100, DLL-150) when a DLL exists), +8 pt stop slip, 2.37/side',
                     mc='2,000 bootstrapped evals (120 trading days, or the time limit) and 1,000 bootstrapped funded runs (120 trading days) per plan per year; rolling = every 2026 start to data end',
                     cost='cost per funded = mean fees per attempt (price + monthly rebill every 21 trading days while open) / pass prob + activation',
                     data_end=max(D)), plans=[], intraday=[], csv_screen=[])
def go(lst, key):
    for p in lst:
        r26 = simulate(p, tr, 2026); r25 = simulate(p, tr, 2025, roll=False)
        OUT[key].append(dict(p, r2026=r26, r2025=r25)); print(p['firm'], '|', p['plan'], r26, '|2025', {k: r25[k] for k in ('p', 'f', 'cost_per_funded', 'f_trader', 'net_ev')}, flush=True)
go(PLANS, 'plans'); go(PLANS_INTRA, 'intraday')
rows = [r for r in csv.DictReader(l for l in open('/home/claude/mnq-quant/data/propfirmmatch_50k_1step_2026-10-25.csv') if not l.startswith('#'))]
for r in rows:
    dd = {'eod': 'eod', 'static': 'static', 'intraday': 'intraday', 'trailing': 'eod'}[r['dd_type']]
    ec = r['eval_consistency'].split()[0]; ec = None if ec == 'none' else float(ec) / 100
    act = float(r['activation_fee'].split()[0]); mq = int(r['max_micros']) if r['max_micros'] != 'na' else 40
    price = float(r['price_discounted'])
    E = dict(price=price, monthly=price if r['billing'] == 'monthly' else 0, activation=act, target=float(r['target']), gap=float(r['max_loss']),
             dd=dd, lock=(None if dd == 'static' else 100), dll=None, cons=ec, min_days=0, maxq=mq)
    Fu = dict(dd=dd, gap=float(r['max_loss']), lock=(None if dd == 'static' else 100), dll=None, maxq=mq, scale=None, win_min=150,
              pay=dict(win_days=5, frac=.5, caps=[2000], min_pay=500, floor_after=(None if dd == 'static' else 100), split=float(r['split']) / 100, max_n=5))
    p = dict(firm=r['firm'], plan=r['plan'], eval=E, funded=Fu)
    x = simulate(p, tr, 2026, N=1000, NF=300, roll=False)
    OUT['csv_screen'].append(dict(firm=r['firm'], plan=r['plan'], dd=dd, price=price, billing=r['billing'], activation=act, target=E['target'], max_loss=E['gap'],
                                  eval_cons=ec, max_micros=mq, p=x['p'], f=x['f'], stall=x['stall'], med=x['med'], cost_per_funded=x['cost_per_funded']))
    print('CSV', r['firm'], r['plan'], x['p'], x['f'], x['cost_per_funded'], flush=True)
json.dump(OUT, open('/home/claude/mnq-quant/knowledge/src/prop_firms.json', 'w'), indent=1, default=str)
print('done')
