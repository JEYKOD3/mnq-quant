# Quick sanity check of the 2-week patterns on 5y RTH 1m (VWAP = equal-weight proxy, no volume in that file).
import numpy as np, pandas as pd
res={'T1':[],'T2':[]}
for line in open('../../data/raw/mnq_rth_1m.txt'):
    dd,*bars=line.strip().split('|'); a=np.array([[int(x) for x in b.split(',')] for b in bars],float); a[:,1:]/=4
    t,o,h,l,c=a.T; n=len(c)
    if n<380: continue
    vw=np.cumsum((h+l+c)/3)/np.arange(1,n+1); yr=dd[:4]
    def run(side,e,stop,tgt,i0,tend):
        for j in range(i0,n):
            if t[j]>tend: return side*(c[j-1]-e)-1
            if (side<0 and h[j]>=stop) or (side>0 and l[j]<=stop): return side*(stop-e)-1
            if tgt is not None and ((side<0 and l[j]<=tgt) or (side>0 and h[j]>=tgt)): return abs(tgt-e)-1
        return side*(c[-1]-e)-1
    i12=np.searchsorted(t,1159); i10=np.searchsorted(t,959)
    if c[i12]>vw[i12] and c[i12]>o[0] and vw[i12]<c[i12]-10: res['T1'].append((yr,run(-1,c[i12],h[:i12+1].max()+5,vw[i12],i12+1,1530)))
    if c[i10]>vw[i10]: res['T2'].append((yr,run(1,c[i10],l[:i10+1].min()-5,None,i10+1,1200)))
for k,v in res.items():
    df=pd.DataFrame(v,columns=['yr','pts']); pf=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2)
    print(k,'n',len(df),'PF',pf(df.pts),'avg pts',round(df.pts.mean(),1),'by year',df.groupby('yr').pts.apply(pf).to_dict())
