"""MNQ Day Engine (6 strategies, one shared budget): full test battery. Output JSON for the chart widget."""
import sys, json, random, collections, statistics as st
sys.path.insert(0, '.')
exec(open('team_sim.py').read().split("if __name__")[0])
random.seed(7)
STRS = ['NEWS', 'V4+', 'D2', 'TDP', 'Pinball', 'H2']
byd = collections.defaultdict(list)
for t in ALL: byd[t['d']].append(t)
TD = [d for d in D if d >= 20220103]
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def net1(t, slip=0, fee=1): return (t['pts'] - (slip if t['why'] in ('stop', 'breakeven') else 0)) * PV - 2 * COMM * fee
out = {}
# 1. per strategy x year (1 MNQ per signal)
yrs = [2022, 2023, 2024, 2025, 2026]
ps = {}
for s in STRS + ['ALL']:
    x = [t for t in ALL if s == 'ALL' or t['strat'] == s]
    v = [net1(t) for t in x]
    ps[s] = dict(n=len(x), win=round(sum(a > 0 for a in v) / len(v), 3), pf=pf(v), usd=round(sum(v)),
                 yr={y: pf([net1(t) for t in x if t['d'] // 10000 == y]) for y in yrs},
                 yrusd={y: round(sum(net1(t) for t in x if t['d'] // 10000 == y)) for y in yrs})
out['strat'] = ps
# 2. daily P&L with budget sizing on a constant $2,000 room (eval-style, no compounding)
def day_pnl(d, slipx=8.0, rule='fcfs', excl=None, fee=1):
    ts = [dict(t) for t in byd.get(d, []) if t['strat'] != excl]
    if fee != 1:
        for t in ts: t['pts'] -= (fee - 1) * 2 * COMM / PV
    return size2(ts, 2000, rule, slipx=slipx)
daily = {d: day_pnl(d) for d in TD}
eq = []; c = 0; pk = 0; dd = 0
mon = collections.OrderedDict()
for d in TD:
    c += daily[d]; pk = max(pk, c); dd = min(dd, c - pk)
    mon.setdefault(str(d)[:6], 0); mon[str(d)[:6]] += daily[d]
    eq.append(round(c))
out['equity'] = dict(dates=[str(d) for d in TD][::5], eq=eq[::5], maxdd=round(dd))
out['months'] = {k: round(v) for k, v in mon.items()}
tv = [daily[d] for d in TD if byd.get(d)]
out['daystats'] = dict(trade_days=len(tv), green=sum(x > 0 for x in tv), red=sum(x < 0 for x in tv), best=round(max(tv)), worst=round(min(tv)),
                       avg=round(sum(tv) / len(tv)), green_months=sum(v > 0 for v in mon.values()), months=len(mon))
# 3. eval sim by start year (real sequence)
def ev_attempt(start, src=None, horizon=120, **kw):
    bal = 50000.; peak = 50000.; best = 0.; n = 0
    seq = src if src is not None else [d for d in TD if d >= start]
    for d in seq:
        n += 1; mll = min(peak - 2000, 50000); cush = bal - mll
        dp = size2([dict(t) for t in byd.get(d, []) if t['strat'] != kw.get('excl')], cush, kw.get('rule', 'fcfs'), slipx=kw.get('slip', 8.0))
        bal += dp; best = max(best, dp)
        if bal <= mll: return 'F', n
        peak = max(peak, bal)
        if bal - 50000 >= 3000 and best <= .5 * (bal - 50000): return 'P', n
        if n >= horizon: break
    return 'O', n
evy = {}
for y in yrs:
    sts = [d for d in TD if d // 10000 == y][::2]
    R = [ev_attempt(s) for s in sts]; n = len(R); P = sorted(x[1] for x in R if x[0] == 'P')
    evy[y] = dict(n=n, p10=round(sum(x <= 10 for x in P) / n, 3), p20=round(sum(x <= 20 for x in P) / n, 3), p40=round(sum(x <= 40 for x in P) / n, 3),
                  p60=round(sum(x <= 60 for x in P) / n, 3), fail=round(sum(x[0] == 'F' for x in R) / n, 3), med=P[len(P) // 2] if P else None)
out['eval_year'] = evy
allR = [ev_attempt(s) for s in TD[::2]]
out['eval_days_hist'] = collections.Counter(min(x[1] // 5 * 5, 120) for x in allR if x[0] == 'P')
out['eval_all'] = dict(n=len(allR), pass_=sum(x[0] == 'P' for x in allR), fail=sum(x[0] == 'F' for x in allR))
# 4. Monte Carlo: random day order (bootstrap from all trading days), 1,000 evals
pool = TD
mc = []
for _ in range(1000):
    seq = [random.choice(pool) for _ in range(120)]
    mc.append(ev_attempt(None, src=seq))
P = sorted(x[1] for x in mc if x[0] == 'P')
out['mc'] = dict(p10=sum(x <= 10 for x in P) / 1000, p20=sum(x <= 20 for x in P) / 1000, p40=sum(x <= 40 for x in P) / 1000, p60=sum(x <= 60 for x in P) / 1000,
                 p120=len(P) / 1000, fail=sum(x[0] == 'F' for x in mc) / 1000, med=P[len(P) // 2] if P else None)
# 5. stress tests (40-day pass and fail over 2022-2026 starts every 4th day)
def ev_rate(**kw):
    R = [ev_attempt(s, **kw) for s in TD[::4]]; n = len(R)
    return dict(p40=round(sum(x[0] == 'P' and x[1] <= 40 for x in R) / n, 3), fail=round(sum(x[0] == 'F' for x in R) / n, 3))
stress = {}
stress['Base (+8 pt stop slip)'] = ev_rate()
stress['No extra slip'] = ev_rate(slip=0)
stress['+16 pt stop slip'] = ev_rate(slip=16)
stress['+30 pt stop slip'] = ev_rate(slip=30)
for s in STRS: stress['Without ' + s] = ev_rate(excl=s)
out['stress'] = stress
pfs = {}
for lab, kw in (('Base', {}), ('Fees x2', dict(fee=2)), ('+16 pt slip', dict(slip=16)), ('+30 pt slip', dict(slip=30))):
    v = [net1(t, kw.get('slip', 8), kw.get('fee', 1)) for t in ALL]; pfs[lab] = pf(v)
out['stress_pf'] = pfs
# 6. funded: after passing, 120 trading days on a funded Flex 50K
def funded(start_idx):
    seq = TD[start_idx:start_idx + 120]
    bal = 50000.; peak = 50000.; mll = 48000.; paid = 0.; good = 0; first = True; npay = 0; prof_since = 0.
    for d in seq:
        cush = bal - mll
        dp = size2([dict(t) for t in byd.get(d, [])], cush, 'fcfs')
        bal += dp
        if bal <= mll: return paid, npay, 'blown'
        if first: peak = max(peak, bal); mll = min(peak - 2000, 50000)
        if dp >= 150: good += 1
        if good >= 5 and bal > 50000 + (100 if not first else 0):
            prof = bal - 50000
            amt = min(.5 * prof, 2000)
            if amt >= 500:
                paid += .9 * amt; bal -= amt; npay += 1; good = 0
                if first: first = False; mll = 50100.
    return paid, npay, 'alive'
F = [funded(i) for i in range(0, len(TD) - 120, 3)]
out['funded'] = dict(n=len(F), avg_paid=round(sum(x[0] for x in F) / len(F)), any_payout=round(sum(x[1] > 0 for x in F) / len(F), 3),
                     blown=round(sum(x[2] == 'blown' for x in F) / len(F), 3), avg_npay=round(sum(x[1] for x in F) / len(F), 2),
                     hist=collections.Counter(int(x[0] // 1000) for x in F))
# 7. entries by hour and weekday (1 MNQ PF)
import datetime
hr = {}
for h in range(8, 15):
    v = [net1(t) for t in ALL if t['eT'] // 60 == h]
    if v: hr[f"{h}:00"] = dict(n=len(v), pf=pf(v), usd=round(sum(v)))
out['hour'] = hr
wd = {}
for i, nm in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri']):
    v = [daily[d] for d in TD if datetime.date(d // 10000, d // 100 % 100, d % 100).weekday() == i and byd.get(d)]
    wd[nm] = dict(n=len(v), usd=round(sum(v)), win=round(sum(x > 0 for x in v) / len(v), 2))
out['weekday'] = wd
json.dump(out, open('engine_tests.json', 'w'), default=str)
print(json.dumps({k: out[k] for k in ('daystats', 'eval_year', 'eval_all', 'mc', 'stress', 'stress_pf', 'funded')}, default=str, indent=0)[:4000])
