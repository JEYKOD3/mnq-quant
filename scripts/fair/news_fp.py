"""8:30 news reversion to the 8:29 price (8:25 5m bar close), 5m ETH bars, 8:30-9:30 entries."""
from fp import ETH, EV, signals, walk, stats, T, PV, COMM
from eth_fp import bars
def run(sig='either', S=38, Tg=57, md='f', end=930, flat=990, room=.8, maxtr=4, maxloss=3, ev=None, first_only=False):
    out=[]
    for d in sorted(ETH):
        if d<20220101 or not EV.get(d): continue
        if ev and ev not in EV[d]: continue
        b=bars(d); idx={x[0]:i for i,x in enumerate(b)}
        if 865 not in idx or 870 not in idx: continue
        F=b[idx[865]][4]; n=0; losses=0; busy=-1
        for i in range(idx[870], len(b)-1):
            m=b[i][0]
            if m>=end or n>=maxtr or losses>=maxloss: break
            if m<busy: continue
            s,ext=signals(b,F,i,sig)
            if not s: continue
            e=b[i+1][1]+s*T; dist=(F-e)*s
            tg=Tg if md=='f' else dist
            if md=='f' and dist<room*Tg: continue
            if tg<=2: continue
            r=walk(b,i+1,s,e,S,tg,None,flat)
            r.update(d=d,R=r['pts']/S,net=r['pts']*PV-2*COMM,em=b[i+1][0],dist=dist,ev='/'.join(sorted(EV[d]))); out.append(r); n+=1
            losses=losses+1 if r['net']<0 else 0; busy=r['xm']
            if first_only: break
    return out
