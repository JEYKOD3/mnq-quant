"""Priority 3 + 4: 2026 YTD brief per strategy (OLD vs NEW), optional evening modules, prop-firm validation.
Writes knowledge/src/y2026_summary.json and scratch tables (printed). Run from scripts/y2026."""
import json, random, statistics, collections, sys, os
from rulesets import *
from d2_team import evals
Y0 = 20260101
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
STR = ['NEWS', 'V4+', 'D2', 'TDP', 'Pinball', 'H2']
SETS2 = {'OLD': OLD(), 'NEW': NEW()}
DAYS26 = [d for d in D if d >= Y0]
ALLD = [d for d in D if d >= 20220301]

def fixed_room(tr, sd=None, a=Y0, z=20991231):
    """engine sizing with a fresh $2,000 room every day (fresh-eval view). Returns per-trade netq (set on copies)."""
    g = byday(tr); out = []
    for d in sorted(g):
        if not (a <= d <= z): continue
        ts = [dict(t) for t in g[d]]; size2(ts, 2000, sd=sd); out += ts
    return out

def streak(v):
    m = c = 0
    for x in v:
        c = c + 1 if x <= 0 else 0; m = max(m, c)
    return m

def full_stats(tr, eng=None):
    x = [t for t in tr if t['d'] >= Y0]
    v = [net1(t) for t in x]
    if not v: return dict(n=0)
    W = [y for y in v if y > 0]; Lo = [y for y in v if y <= 0]
    dy = collections.defaultdict(float)
    for t in x: dy[t['d']] += net1(t)
    mon = collections.defaultdict(float)
    for t in x: mon[t['d'] // 100 % 100] += net1(t)
    out = dict(n=len(v), wins=len(W), win=round(len(W) / len(v), 3), pf=pf(v), net1=round(sum(v)),
               avgw=round(sum(W) / len(W)) if W else 0, avgl=round(sum(Lo) / len(Lo)) if Lo else 0, dd=round(maxdd(v)),
               best=round(max(dy.values())), bestd=max(dy, key=dy.get), worst=round(min(dy.values())), worstd=min(dy, key=dy.get),
               streak=streak(v), hold=round(sum(t['xT'] - t['eT'] for t in x) / len(x)), last_exit=max(t['xT'] for t in x),
               mon={MON[m - 1]: round(mon.get(m, 0)) for m in range(1, 11)})
    if eng is not None:
        e = [t for t in eng if t['d'] >= Y0]
        ev = [t['netq'] for t in e]
        out.update(neteng=round(sum(ev)), ddeng=round(maxdd(ev)), contracts=round(sum(t['q'] for t in e) / max(1, len(e)), 1),
                   zero=sum(t['q'] == 0 for t in e))
    out['yr'] = {y: dict(n=stat1(tr, y * 10000 + 101, y * 10000 + 1231)['n'], net=stat1(tr, y * 10000 + 101, y * 10000 + 1231)['net'],
                         pf=stat1(tr, y * 10000 + 101, y * 10000 + 1231)['pf']) for y in range(2022, 2027)}
    return out

def brief():
    res = {}
    for k, tr in SETS2.items():
        eng = fixed_room(tr, a=20220101)
        res[k] = {s: full_stats([t for t in tr if t['strat'] == s], [t for t in eng if t['strat'] == s]) for s in STR}
        res[k]['TEAM'] = full_stats(tr, eng)
    return res

def evening():
    sys.path.insert(0, '/home/claude/mnq-quant/scripts/sessions'); cwd = os.getcwd()
    os.chdir('/home/claude/mnq-quant/scripts/sessions')
    mine = sys.modules.pop('common')          # sessions/ has its own common.py
    from q7_selloff_grid import a1g
    sys.modules['common'] = mine
    os.chdir('/home/claude/mnq-quant/scripts/sunday')
    g = {}; exec(open('sun3.py').read().split('res = []')[0], g)
    os.chdir(cwd)
    mods = {'S2 sell-off evening long (18:05, stop 0.30 ADR, exit 03:30)': [dict(d=t['d'], net=t['net']) for t in a1g()],
            'S2 cut at 20:00 (fits 18:00-20:00 window)': [dict(d=t['d'], net=t['net']) for t in a1g(exit_=2000)],
            'Sunday Gap Pullback (half-gap limit, stop 0.15 ADR, exit 20:00)': [dict(d=t[0], net=t[1]) for t in g['run'](g['style_pull'], .05, .5, .15, None)]}
    out = {}
    for k, tr in mods.items():
        x = [t for t in tr if t['d'] >= Y0]; v = [t['net'] for t in x]
        mon = collections.defaultdict(float)
        for t in x: mon[t['d'] // 100 % 100] += t['net']
        yr = {}
        for y in range(2022, 2027):
            w = [t['net'] for t in tr if t['d'] // 10000 == y]; yr[y] = dict(n=len(w), net=round(sum(w)), pf=pf(w))
        out[k] = dict(n=len(v), wins=sum(y > 0 for y in v), win=round(sum(y > 0 for y in v) / max(1, len(v)), 3), pf=pf(v), net1=round(sum(v)),
                      avgw=round(statistics.mean([y for y in v if y > 0])) if any(y > 0 for y in v) else 0,
                      avgl=round(statistics.mean([y for y in v if y <= 0])) if any(y <= 0 for y in v) else 0,
                      dd=round(maxdd(v)), best=round(max(v)), worst=round(min(v)), streak=streak(v), mon={MON[m - 1]: round(mon.get(m, 0)) for m in range(1, 11)}, yr=yr)
    return out

def roll26(tr, cons=.4, sd=None, **kw):
    byd = byday(tr); R = []
    for s in DAYS26: R.append(eval_run(byd, s, ALLD, cons=cons, sd=sd, **kw))
    n = len(R); P = [r for r in R if r['res'] == 'P']
    blk = [r for r in R if r['tgt_n'] is not None]
    blk2 = [r for r in blk if r['res'] != 'P' or r['n'] > r['tgt_n']]
    extra = [r['n'] - r['tgt_n'] for r in blk2 if r['res'] == 'P']
    closed = [r for r in R if r['res'] != 'O']
    return dict(n=n, p=round(len(P) / n, 3), f=round(sum(r['res'] == 'F' for r in R) / n, 3), o=round(sum(r['res'] == 'O' for r in R) / n, 3),
                p40=round(sum(r['n'] <= 40 for r in P) / n, 3), med=statistics.median([r['n'] for r in P]) if P else None,
                p_closed=round(len(P) / len(closed), 3) if closed else None,
                worst=round(min(r['worst'] for r in R)), worst_med=round(statistics.median([r['worst'] for r in R])),
                cons_hit=len(blk2), cons_hit_pct=round(len(blk2) / max(1, len(blk)), 3),
                extra_med=statistics.median(extra) if extra else None, extra_max=max(extra) if extra else None)

def mc(tr, cons=.4, sd=None, N=10000, H=40, seed=7, **kw):
    byd = byday(tr); rnd = random.Random(seed); P = F = 0; ns = []
    for _ in range(N):
        seq = [rnd.choice(DAYS26) for _ in range(H)]
        bal = 50000.; peak = 50000.; best = 0.; res = 'O'
        for i, d in enumerate(seq):
            mll = min(peak - 2000, 50100); cush = bal - mll
            dp = size2([dict(t) for t in byd.get(d, [])], cush, sd=sd, prof0=bal - 50000, best0=best, cons=cons, **kw); bal += dp; best = max(best, dp)
            if bal <= mll: res = 'F'; break
            peak = max(peak, bal)
            if bal - 50000 >= 3000 and best <= cons * (bal - 50000): res = 'P'; ns.append(i + 1); break
        P += res == 'P'; F += res == 'F'
    return dict(p=round(P / N, 3), f=round(F / N, 3), o=round(1 - (P + F) / N, 3), med=statistics.median(ns) if ns else None)

def skip_test(tr, frac=.2, seeds=100, cons=.4, sd=None):
    ps = []; fs = []; ms = []; p4 = []
    for s in range(seeds):
        rnd = random.Random(1000 + s)
        sk = {(t['d'], t['eT'], t['strat']) for t in tr if t['d'] >= Y0 and rnd.random() < frac}
        r = roll26(tr, cons=cons, sd=sd, skip=sk); ps.append(r['p']); fs.append(r['f']); ms.append(r['med'] or 0); p4.append(r['p40'])
    return dict(p40=round(statistics.mean(p4), 3), p40_lo=round(sorted(p4)[5], 3), p=round(statistics.mean(ps), 3), p_lo=round(sorted(ps)[5], 3), f=round(statistics.mean(fs), 3), f_hi=round(sorted(fs)[-5], 3), med=statistics.median(ms))

def funded_run(byd, start, days_list, sd=None, policy='A', maxpay=5):
    bal = 50000.; peak = 50000.; locked = False; q = 0; pays = []; n = 0; first = None
    for d in days_list:
        if d < start: continue
        n += 1; mll = 50100 if locked else min(peak - 2000, 50100); cush = bal - mll
        dp = size2([dict(t) for t in byd.get(d, [])], cush, sd=sd, prof0=-1e9)
        bal += dp
        if bal <= mll: return dict(res='bust', pays=pays, n=n, first=first)
        peak = max(peak, bal)
        if dp >= 150: q += 1
        if q >= 5 and bal > 50000:
            amt = min(2000, .5 * (bal - 50000))
            if amt >= 500 and (policy == 'A' or bal - amt - 50100 >= 1100):
                bal -= amt; pays.append(round(amt)); locked = True; q = 0
                if first is None: first = n
                if len(pays) >= maxpay: return dict(res='done', pays=pays, n=n, first=first)
    return dict(res='open', pays=pays, n=n, first=first)

def funded(tr, sd=None, policy='A', cons=.4):
    """chain: every 2026 eval start that passes -> funded starts the next trading day (historical, truncated at data end)
    plus a Monte Carlo funded phase (bootstrap 2026 days, 120 trading days)."""
    byd = byday(tr); R = []
    for s in DAYS26:
        e = eval_run(byd, s, ALLD, cons=cons, sd=sd)
        if e['res'] != 'P': continue
        i = ALLD.index(s) + e['n']
        if i >= len(ALLD): continue
        R.append(funded_run(byd, ALLD[i], ALLD, sd=sd, policy=policy))
    rnd = random.Random(11); M = []
    for _ in range(3000):
        seq = [rnd.choice(DAYS26) for _ in range(120)]
        M.append(funded_run({k: byd.get(d, []) for k, d in enumerate(seq)}, 0, list(range(120)), sd=sd, policy=policy))
    def summ(X):
        if not X: return {}
        fp = [x['first'] for x in X if x['first']]
        return dict(n=len(X), bust=round(sum(x['res'] == 'bust' for x in X) / len(X), 3), bust_before_pay=round(sum(x['res'] == 'bust' and not x['pays'] for x in X) / len(X), 3),
                    got_pay=round(sum(bool(x['pays']) for x in X) / len(X), 3), first_med=statistics.median(fp) if fp else None,
                    pays_avg=round(statistics.mean(len(x['pays']) for x in X), 2), gross_avg=round(statistics.mean(sum(x['pays']) for x in X)),
                    trader_avg=round(.9 * statistics.mean(sum(x['pays']) for x in X)), pay_med=statistics.median([p for x in X for p in x['pays']]) if any(x['pays'] for x in X) else None)
    return dict(hist=summ(R), mc120=summ(M))

def stopday_hist(tr):
    out = {}
    for N, dm in ((None, 'pass'), (0, 'pass'), (1, 'pass'), (2, 'pass'), (3, 'pass'), (4, 'pass'), (3, 'naive')):
        lab = 'off' if N is None else ('a,b,d only' if N == 0 else f'N={N}') + (' naive (d)' if dm == 'naive' else '')
        ev = evals(tr, sd=N, dmode=dm)
        nets = {}
        for y in range(2022, 2027):
            e = fixed_room(tr, sd=N, a=y * 10000 + 101, z=y * 10000 + 1231); nets[y] = round(sum(t['netq'] for t in e))
        out[lab] = dict(ev=ev, net=nets)
    return out

if __name__ == '__main__':
    J = {}
    J['brief'] = brief(); print('brief done', flush=True)
    J['evening'] = evening(); print('evening done', flush=True)
    J['stopday'] = {k: stopday_hist(tr) for k, tr in SETS2.items()}; print('stopday done', flush=True)
    for k in J['stopday']:
        for lab, v in J['stopday'][k].items(): print(k, lab, v)
    SD = 3
    P = {}
    for k, tr in SETS2.items():
        P[k] = {}
        for cons in (.4, .5):
            for sd in (None, SD):
                P[k][f'roll cons{int(cons*100)} sd{sd}'] = roll26(tr, cons=cons, sd=sd)
                P[k][f'mc cons{int(cons*100)} sd{sd}'] = mc(tr, cons=cons, sd=sd)
        for x in (1, 2, 4):
            P[k][f'stress +{x}pt'] = roll26(tr, sd=SD, slipx=8 + x, xent=x)
        P[k]['stress 1-tick only (no +8 stop slip)'] = roll26(tr, sd=SD, slipx=0)
        P[k]['comm $1.00 RT'] = roll26(tr, sd=SD, comm=.5)
        P[k]['skip 20%'] = skip_test(tr, sd=SD)
        P[k]['funded A (request asap)'] = funded(tr, sd=SD, policy='A')
        P[k]['funded B (keep $1,100 room)'] = funded(tr, sd=SD, policy='B')
        for kk, v in P[k].items(): print(k, kk, v, flush=True)
    J['prop'] = P
    J['meta'] = dict(data_end=max(D), days2026=len(DAYS26), stopday_default=SD, note='1 MNQ: 2.37/side + 1 tick slip on entries and stops. Engine: 65% of room, $1,100 budget, +8 pt stop slip, 40% consistency unless noted, MLL locks 50,100.')
    os.makedirs('/home/claude/mnq-quant/knowledge/src', exist_ok=True)
    json.dump(J, open('/home/claude/mnq-quant/knowledge/src/y2026_summary.json', 'w'), indent=1, default=str)
    print('written')
