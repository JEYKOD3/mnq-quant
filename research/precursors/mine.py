# Which conditions came before DROPs / RIPs more often than normal, in BOTH weeks?
import pandas as pd, numpy as np, itertools, warnings; warnings.filterwarnings('ignore')
m=pd.read_pickle('feat5m.pkl')
F=['r1','r3','r6','r12','r24','dvwap','dema','slope','pos12','pos48','volz','rangez','upwick','dnwick','body','dnrun','uprun','rsi','fail_hi','fail_lo','brk_lo','brk_hi','dPDL','dPDH','dPDC','dSessH','dSessL','hr','struct']
bins={}
for f in F:
    x=m[f]
    if x.nunique()<=6: bins[f]=sorted(x.unique()); m[f+'_b']=x
    else:
        q=np.unique(np.nanquantile(x,[0,.2,.4,.6,.8,1])); q[0]-=1e-9; q[-1]+=1e-9
        m[f+'_b']=pd.cut(x,q,labels=False)
for target in ['DROP','RIP']:
    base={w:m[m.week==w][target].mean() for w in (1,2)}
    rows=[]
    for f in F:
        for b in sorted(m[f+'_b'].dropna().unique()):
            s=m[m[f+'_b']==b]
            r={w:s[s.week==w][target].mean() for w in (1,2)}; nn={w:(s.week==w).sum() for w in (1,2)}
            if min(nn.values())<40: continue
            lo,hi=s[f].min(),s[f].max()
            rows.append(dict(cond=f'{f} in [{lo:.2f},{hi:.2f}]',wk1=round(r[1],3),wk2=round(r[2],3),lift=round(min(r[1]/base[1],r[2]/base[2]),2),n1=nn[1],n2=nn[2]))
    R=pd.DataFrame(rows).sort_values('lift',ascending=False)
    print(f'\n===== {target}: base rate wk1 {base[1]:.3f} wk2 {base[2]:.3f}. Single conditions with the highest lift in BOTH weeks =====')
    print(R.head(12).to_string(index=False))
    # pairs among the top 15 single conditions
    top=R.head(15)
    keys=[]
    for _,row in top.iterrows():
        f=row.cond.split(' in ')[0]; lo,hi=[float(x) for x in row.cond.split('[')[1].rstrip(']').split(',')]
        keys.append((f,lo,hi,row.cond))
    pr=[]
    for (f1,a1,b1,c1),(f2,a2,b2,c2) in itertools.combinations(keys,2):
        if f1==f2: continue
        s=m[(m[f1]>=a1)&(m[f1]<=b1)&(m[f2]>=a2)&(m[f2]<=b2)]
        nn={w:(s.week==w).sum() for w in (1,2)}
        if min(nn.values())<20: continue
        r={w:s[s.week==w][target].mean() for w in (1,2)}
        pr.append(dict(cond=c1+' AND '+c2,wk1=round(r[1],3),wk2=round(r[2],3),lift=round(min(r[1]/base[1],r[2]/base[2]),2),n1=nn[1],n2=nn[2]))
    P=pd.DataFrame(pr).sort_values('lift',ascending=False)
    print(f'--- best pairs ({target}) ---'); print(P.head(10).to_string(index=False))
    R.to_csv(f'single_{target}.csv',index=False); P.to_csv(f'pairs_{target}.csv',index=False)
