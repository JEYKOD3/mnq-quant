"""Plan grid for fast_pass.py."""
ALL = None
BASE = dict(f=.65, budget=1050, sd=3, rec=True, guard=True)
def V(**k): d = dict(BASE); d.update(k); return d
def plans_for(mode):
    if mode == 'grid':
        P = [('BASE v31 $1050 f.65', BASE)]
        for b in (1500, 2000, 2500, 4000):
            for f in (.65, .8, 1.0):
                P.append((f'bud{b} f{f}', V(budget=b, f=f)))
        for f in (.8, 1.0): P.append((f'bud1050 f{f}', V(f=f)))
        for q in (2, 4, 6, 8): P.append((f'fixed {q} MNQ', V(fixed=q, budget=4000)))
        for pc in (900, 1200, 1500):
            P.append((f'bud2000 f.8 pcap{pc}', V(budget=2000, f=.8, pcap=pc)))
            P.append((f'base pcap{pc}', V(pcap=pc)))
        P.append(('front 2000,2000,1050', V(budget=[2000, 2000, 1050], f=.8)))
        P.append(('front 2500,1500,1050', V(budget=[2500, 1500, 1050], f=1.0)))
        for nm, S in (('V4+D2', {'V4+', 'D2'}), ('V4+D2+NEWS', {'V4+', 'D2', 'NEWS'}), ('no Pin/H2', {'NEWS', 'V4+', 'D2', 'TDP'}),
                      ('no H2', {'NEWS', 'V4+', 'D2', 'TDP', 'Pinball'}), ('no TDP', {'NEWS', 'V4+', 'D2', 'Pinball', 'H2'}), ('no NEWS', {'V4+', 'D2', 'TDP', 'Pinball', 'H2'})):
            P.append((f'base {nm}', V(strats=S)))
            P.append((f'bud2000 f.8 {nm}', V(strats=S, budget=2000, f=.8)))
        for sd in (2, 4, 0): P.append((f'bud2000 f.8 sd{sd}', V(budget=2000, f=.8, sd=sd)))
        return P
    raise SystemExit('unknown mode')

def plans_risk():
    P = [('BASE v31', BASE)]
    for rd in (300, 400, 500, 600, 750, 900):
        P.append((f'risk ${rd}/trade', V(riskd=rd, budget=1200)))
    for rd, g in ((400, .2), (500, .2), (500, .35), (600, .25)):
        P.append((f'risk ${rd} +{g}xprofit', V(riskd=rd, grow=g, budget=1200)))
    for rd in (500, 600, 750):
        P.append((f'risk ${rd} pcap1200', V(riskd=rd, budget=1200, pcap=1200)))
        P.append((f'risk ${rd} no Pin', V(riskd=rd, budget=1200, strats={'NEWS', 'V4+', 'D2', 'TDP', 'H2'})))
    return P
_pf = plans_for
def plans_for(mode):
    if mode == 'risk': return plans_risk()
    return _pf(mode)

def plans_aggr():
    P = [('BASE v31', BASE)]
    for f in (.65, .8, 1.0):
        for b in (1200, 2000):
            P.append((f'f{f} bud{b} no-rec/no-guard', V(f=f, budget=b, rec=False, guard=False)))
            P.append((f'f{f} bud{b} guard, no rec', V(f=f, budget=b, rec=False)))
    for rd in (900, 1100, 1300, 1600):
        P.append((f'risk ${rd} no-rec', V(riskd=rd, budget=max(rd, 1200), rec=False)))
        P.append((f'risk ${rd} no-rec pcap1200', V(riskd=rd, budget=max(rd, 1200), rec=False, pcap=1200)))
    return P
_pf2 = plans_for
def plans_for(mode):
    if mode == 'aggr': return plans_aggr()
    return _pf2(mode)
