"""Budget rules x strategy combinations, Lucid Flex 50K eval sim (Oct 25 2026)."""
import sys, itertools, json, collections, multiprocessing as mp
sys.path.insert(0, '.'); sys.path.insert(0, '../discover'); sys.path.insert(0, '../fair')
from rules2 import *
import td, news_fp
PB = build("current", be=True, v4t=1.25)
TD = td.run(E=.6, mode='retrace', k=.33, stop='adr', a=.4, R=1.5, hold=999, tend=720)
NW = news_fp.run('either', 50, 50, 'f')
ALL = list(PB)
ALL += [dict(d=t['d'], strat='TDP', side=t['s'], eT=t['em'], eP=t['eP'], stp=t['stp'], xT=t['xT'], why=t['why'], r=t['risk'], pts=t['pts'], be=None, w=1.0) for t in TD]
for t in NW:
    eT = (t['em'] + 1080) % 1440; xT = (t['xm'] + 1080) % 1440
    ALL.append(dict(d=t['d'], strat='NEWS', side=t['s'], eT=eT, eP=t['eP'], stp=t['stp'], xT=xT, why=t['why'], r=50.0, pts=t['pts'], be=None, w=1.0))
ALL.sort(key=lambda t: (t['d'], t['eT']))
STR = ['V4+', 'D2', 'TDP', 'Pinball', 'H2', 'NEWS']
PFQ = {'V4+': 1, 'Pinball': 1, 'TDP': 1, 'NEWS': 1, 'D2': .5, 'H2': .5}
def size2(trs, cush, rule, f=.65, dll=1100, slipx=8.0):
    done = []
    for t in trs:
        rc = (t['r'] + SLIP * T) * PV + 2 * COMM; pts = t['pts'] - (slipx if t['why'] in ('stop', 'breakeven') else 0); pc = pts * PV - 2 * COMM
        used = 0
        for u in done:
            if u['q'] == 0: continue
            if u['xT'] <= t['eT']: used += max(0, -u['netq'])
            elif u['be'] is not None and u['be'] <= t['eT']: pass
            else: used += u['q'] * u['rc']
        w = t['w']
        if rule == 'priority': w = min(w, PFQ[t['strat']])
        cap = dll - used
        if rule == 'cap60': cap = min(cap, .6 * dll)
        if rule == 'cap50': cap = min(cap, .5 * dll)
        budget = min(w * f * cush, f * cush - used, cap); q = min(40, int(budget // rc)) if budget > 0 else 0
        if q < 1 and w >= 1 and rc < .9 * (cush - used) and rc < dll - used: q = 1
        t['q'] = max(q, 0); t['rc'] = rc; t['netq'] = t['q'] * pc
        done.append(t)
    return sum(t['netq'] for t in trs)
DAYS = [d for d in D if 20220301 <= d]
def sim(args):
    combo, rule = args
    byd = collections.defaultdict(list)
    for t in ALL:
        if t['strat'] in combo: byd[t['d']].append(t)
    out = {}
    for lab, a, z in (('A', 20220301, 20241231), ('Z', 20250101, 20261023)):
        sts = [d for d in DAYS if a <= d <= z][::3]; R = []
        for s in sts:
            bal = 50000.; peak = 50000.; best = 0.; n = 0; res = ('O', 0)
            for d in DAYS:
                if d < s: continue
                n += 1; mll = min(peak - 2000, 50000); cush = bal - mll
                dp = size2([dict(t) for t in byd.get(d, [])], cush, rule); bal += dp; best = max(best, dp)
                if bal <= mll: res = ('F', n); break
                peak = max(peak, bal)
                if bal - 50000 >= 3000 and best <= .5 * (bal - 50000): res = ('P', n); break
                if n >= 250: break
            R.append(res)
        n = len(R); P = [x[1] for x in R if x[0] == 'P']
        out[lab] = dict(p20=sum(x <= 20 for x in P) / n, p40=sum(x <= 40 for x in P) / n, fail=sum(x[0] == 'F' for x in R) / n)
    return dict(combo='+'.join(combo), rule=rule, **out)
if __name__ == '__main__':
    print('NEWS trades:', len(NW), ' check sides', collections.Counter(t['strat'] for t in ALL))
    jobs = [(c, 'fcfs') for k in range(1, 7) for c in itertools.combinations(STR, k)]
    jobs += [(tuple(STR), r) for r in ('cap60', 'cap50', 'priority')] + [(tuple(s for s in STR if s != 'NEWS'), r) for r in ('cap60', 'cap50', 'priority')]
    with mp.Pool(2) as p: res = p.map(sim, jobs, chunksize=2)
    json.dump(res, open('team_sim.json', 'w'))
    for r in sorted(res, key=lambda r: -(r['A']['p40'] + r['Z']['p40']))[:25]:
        print(f"{r['combo']:34s} {r['rule']:8s}  22-24: 20d {r['A']['p20']:.0%} 40d {r['A']['p40']:.0%} fail {r['A']['fail']:.0%} | 25-26: 20d {r['Z']['p20']:.0%} 40d {r['Z']['p40']:.0%} fail {r['Z']['fail']:.0%}")
