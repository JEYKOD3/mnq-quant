import pickle, numpy as np
src=open('propmath.py').read().split("def edge(R)")[0]
exec(src)
alld=[l.split('|')[0] for l in open('../../data/raw/mnq_rth_1m.txt')]
for tf,path in [('100% (to B)','../drops/pb618_R_by_day.pkl'),('80%','../drops/pb618_R_tf0.8.pkl'),('60%','../drops/pb618_R_tf0.6.pkl'),('40%','../drops/pb618_R_tf0.4.pkl')]:
    dd={}
    for d,r in pickle.load(open(path,'rb')): dd.setdefault(d,[]).append(r)
    PB[:]=[dd.get(d,[]) for d in alld]
    for risk in (250,300,350):
        p,f,md=eval_sim('pullback',risk,N=10000)
        pay,anyp,npay=funded_sim('pullback',risk,N=4000)
        print(f'target {tf:12s} ${risk}: pass {100*p:4.1f}% fail {100*f:4.1f}% days {md} | funded pays ${pay:,.0f} (>=1 payout {100*anyp:.0f}%) | per eval ${p*pay-130.2:,.0f}',flush=True)
