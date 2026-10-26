"""Edge optimization, stage 1 (Oct 26 2026): one row per team trade (v31 rules) + evening SGP/WCC, with features known at
entry time, 1-contract net R after costs, and MFE / MAE in R (RTH trades). Writes edge_trades.json."""
import os, sys, json, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast_pass as FP
from common import D, DB, F, EV, COMM, SLIP, T

HERE = os.path.dirname(os.path.abspath(__file__))
PV = 2.0
SLIPX = 8.0

# ---- overnight range from ETH 5m (18:00 prev day .. 09:25) ----
ONR = {}
for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
    p = ln.strip().split('|')
    if len(p) < 2: continue
    hi = -1e18; lo = 1e18
    for x in p[1:]:
        t, o, h, l, c = x.split(','); t = int(t)
        if t >= 1800 or t < 930:
            hi = max(hi, int(h) / 4); lo = min(lo, int(l) / 4)
    if hi > lo: ONR[int(p[0])] = hi - lo

# ---- RTH day stats ----
DAYS = sorted(DB)
RNG = {}; CLS = {}; OPN = {}
for d in DAYS:
    b = DB[d]
    if not b: continue
    RNG[d] = max(x[2] for x in b) - min(x[3] for x in b); CLS[d] = b[-1][4]; OPN[d] = b[0][1]

def prev_days(d, n):
    i = DAYS.index(d)
    return DAYS[max(0, i - n):i]

FEAT = {}
for d in DAYS:
    f = F.get(d)
    if not f or not f.get('adr'): continue
    pv = prev_days(d, 60)
    if len(pv) < 20: continue
    adr = f['adr']
    med60 = statistics.median(RNG[x] for x in pv if x in RNG)
    sma20 = statistics.mean(CLS[x] for x in pv[-20:])
    pd = pv[-1]
    b = DB[d]
    fh = [x for x in b if x[0] < 630]
    FEAT[d] = dict(
        gap=abs(OPN[d] - CLS[pd]) / adr,                   # gap size in ADR
        adrReg=adr / med60,                               # vol regime: 10d ADR vs 60d median range
        pdr=RNG[pd] / adr,                                # prior-day range vs ADR
        onr=ONR.get(d, float('nan')) / adr,               # overnight range vs ADR
        fhr=(max(x[2] for x in fh) - min(x[3] for x in fh)) / adr if fh else float('nan'),
        trend=1 if CLS[pd] > sma20 else -1,
        news=1 if EV.get(d) else 0,
        wd=f.get('wd'),
    )

def mfe_mae(t):
    b = DB.get(t['d'])
    if not b or t['eT'] < 570: return None, None
    s = t['side']; mf = 0.0; ma = 0.0
    for m, o, h, l, c in b:
        if m < t['eT']: continue
        if m >= t['xT']: break
        mf = max(mf, (h - t['eP']) * s if s > 0 else (t['eP'] - l)); ma = max(ma, (t['eP'] - l) if s > 0 else (h - t['eP']))
    return mf / t['r'], ma / t['r']

rows = []
for t in FP.build_trades():
    fe = FEAT.get(t['d'])
    if fe is None: continue
    rk = (t['r'] + SLIP * T + SLIPX) * PV + 2 * COMM
    pts = t['pts'] - (SLIPX if t['why'] in FP.STOPWHY else 0)
    net = pts * PV - 2 * COMM
    mf, ma = mfe_mae(t)
    r = dict(d=t['d'], strat=t['strat'], side=t['side'], eT=t['eT'], why=t['why'], rpts=round(t['r'], 2), net=round(net, 2),
             R=round(net / rk, 3), mfe=None if mf is None else round(mf, 3), mae=None if ma is None else round(ma, 3),
             withT=1 if t['side'] == fe['trend'] else 0, tbin=t['eT'] // 30 * 30)
    r.update({k: (round(v, 3) if isinstance(v, float) else v) for k, v in fe.items() if k not in ('trend',)})
    if t['eT'] < 630: r['fhr'] = None                     # first hour not complete yet: not usable
    rows.append(r)

# evening (booked on day d, session 18:00-20:00 after RTH of d)
for t in json.load(open(os.path.join(HERE, 'more_evening.json'))):
    d = t['d']; fe = FEAT.get(d)
    if fe is None: continue
    rk = (t['r'] + SLIP * T + 2.0) * PV + 2 * COMM
    pts = t['pts'] - (2.0 if t['why'] == 'stop' else 0)
    net = pts * PV - 2 * COMM
    dayDir = 1 if CLS[d] > OPN[d] else -1
    rows.append(dict(d=d, strat=t['strat'], side=t['side'], eT=1080, why=t['why'], rpts=round(t['r'], 2), net=round(net, 2), R=round(net / rk, 3),
                     mfe=None, mae=None, withT=1 if t['side'] == dayDir else 0, tbin=1080, gap=fe['gap'], adrReg=fe['adrReg'],
                     pdr=round(RNG[d] / F[d]['adr'], 3), onr=None, fhr=None, news=fe['news'], wd=fe['wd']))

json.dump(rows, open(os.path.join(HERE, 'edge_trades.json'), 'w'))
import collections
print(len(rows), collections.Counter(r['strat'] for r in rows))
