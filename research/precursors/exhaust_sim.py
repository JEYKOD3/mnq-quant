# "Exhaustion" system on 5m (Oct 19 -> Oct 30 07:00): sell rally exhaustion, buy volume-flush exhaustion.
import pandas as pd, numpy as np, itertools, warnings; warnings.filterwarnings('ignore')
m=pd.read_pickle('feat5m.pkl'); n=len(m)
H,L,C,O=m.high.values,m.low.values,m.close.values,m.open.values; A=m.atr.values
def signals(variant):
    s=np.zeros(n,int)
    shortc=(m.r12>1.6)&(m.rsi>59)
    longc=(m.r6<-1.34)&(m.volz>0.72)&(m.rsi<39)
    if variant=='tight':
        shortc&=(m.pos48>0.58); longc&=(m.pos12<0.17)
    s[shortc.values]=-1; s[longc.values]=1
    return s
def sim(sig,stopA,tgtA,hold,confirm):
    out=[]; busy=-1; i=0
    while i<n-1:
        if i<=busy or sig[i]==0: i+=1; continue
        side=sig[i]; k=i
        if confirm:   # wait up to 3 bars for a bar closing in trade direction below/above the prior bar
            k=None
            for j in range(i+1,min(i+4,n)):
                if (side<0 and C[j]<O[j] and C[j]<L[j-1]) or (side>0 and C[j]>O[j] and C[j]>H[j-1]): k=j; break
            if k is None: i+=1; continue
        e=C[k]; a=A[k]; stop=e-side*stopA*a; tgt=e+side*tgtA*a; pnl=None; x=k
        for j in range(k+1,min(k+1+hold,n)):
            x=j
            if (side>0 and L[j]<=stop) or (side<0 and H[j]>=stop): pnl=-stopA*a; break
            if (side>0 and H[j]>=tgt) or (side<0 and L[j]<=tgt): pnl=tgtA*a; break
        if pnl is None: pnl=side*(C[x]-e)
        out.append((m.index[k],m.week.iat[k],side,pnl-1,stopA*a)); busy=x; i=x+1
    return pd.DataFrame(out,columns=['t','wk','side','pts','risk'])
pf=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2) if len(x) else np.nan
rows=[]
for var,stopA,tgtA,hold,conf in itertools.product(['base','tight'],[1.0,1.5,2.0],[1.0,1.5,2.0,3.0],[6,12],[False,True]):
    T=sim(signals(var),stopA,tgtA,hold,conf)
    if len(T)<20: continue
    rows.append(dict(rules=var,stop=stopA,target=tgtA,hold_min=hold*5,confirm=conf,trades=len(T),win=round((T.pts>0).mean(),2),pts=round(T.pts.sum()),
        PF_wk1=pf(T[T.wk==1].pts),PF_wk2=pf(T[T.wk==2].pts),PF_short=pf(T[T.side<0].pts),PF_long=pf(T[T.side>0].pts),med_stop_pts=round(T.risk.median())))
R=pd.DataFrame(rows); R['minPF']=R[['PF_wk1','PF_wk2']].min(axis=1)
pd.set_option('display.width',250); print(R.sort_values('minPF',ascending=False).head(15).to_string(index=False))
R.to_csv('exhaust_grid.csv',index=False)
