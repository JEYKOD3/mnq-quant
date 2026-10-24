import pickle, sys, collections, datetime
sys.path.insert(0,'.'); from core import *
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb'))
for tf in (1,5):
    tr=[t for t in v4_trades(days,F,tf=tf,tgtR=None) if t['d']>=20220101]   # hold to close, no target: see full path
    print(f'\n######## V4 {tf}m, NO target (hold to close), n={len(tr)}  overall',summary(tr))
    W=[t for t in tr if t['R']>0]; L=[t for t in tr if t['R']<=0]
    st=[t for t in tr if t['why']=='stop']
    print('exits',collections.Counter(t['why'] for t in tr))
    q=lambda v,p: sorted(v)[int(p*(len(v)-1))] if v else None
    print('stopped trades: MFE before stop (R) quantiles 25/50/75/90:',[round(q([t['mfeR'] for t in st],p),2) for p in (.25,.5,.75,.9)],
          ' share reaching >=1R first:',round(sum(t['mfeR']>=1 for t in st)/len(st),2),' >=0.5R:',round(sum(t['mfeR']>=.5 for t in st)/len(st),2))
    print('winners: MAE (R) quantiles 25/50/75/90:',[round(q([t['maeR'] for t in W],p),2) for p in (.25,.5,.75,.9)], ' winners with MAE<0.5R:',round(sum(t['maeR']<.5 for t in W)/len(W),2))
    print('all trades MFE (R) quantiles 50/75/90:',[round(q([t['mfeR'] for t in tr],p),2) for p in (.5,.75,.9)])
    def grp(key,lab):
        g=collections.defaultdict(list)
        for t in tr: g[key(t)].append(t)
        print(lab+':  '+' | '.join(f"{k}: n{len(v)} PF{summary(v)['pf']} avgR{summary(v)['avgR']:+.2f}" for k,v in sorted(g.items())))
    grp(lambda t: f"{t['eT']//60}h", 'entry hour')
    grp(lambda t: 'gap' if abs(t['f']['gap'])>=.6 else 'or15', 'bias source')
    grp(lambda t: 'w<.25' if t['orw']/t['f']['adr']<.25 else ('.25-.4' if t['orw']/t['f']['adr']<.4 else '>=.4'), 'OR width/ADR')
    grp(lambda t: 'r<40' if t['r']<40 else ('40-80' if t['r']<80 else ('80-130' if t['r']<130 else '>=130')), 'stop size pts')
    grp(lambda t: datetime.date(t['d']//10000,t['d']//100%100,t['d']%100).strftime('%a'), 'weekday')
    grp(lambda t: 'long' if t['side']>0 else 'short', 'side')
    grp(lambda t: 'agree' if (t['f']['gap']*t['f']['orDir']>0) else 'disagree', 'gap vs first15 agree')
    grp(lambda t: 'pd<.8' if t['f']['pdRel']<.8 else ('.8-1' if t['f']['pdRel']<1 else '1-1.2'), 'prior day range/ADR')
    grp(lambda t: str(t['d'])[4:6], 'month')
