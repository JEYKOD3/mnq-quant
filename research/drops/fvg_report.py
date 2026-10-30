import pandas as pd, numpy as np
pd.set_option('display.width',250)
df=pd.read_pickle('fvg_rows.pkl')
df['withtrend']=df.side==df.trend
regname={1:'UP STRONG',2:'UP WEAK',3:'UP PULLBACK',4:'UP BREAKING',-1:'DOWN STRONG',-2:'DOWN WEAK',-3:'DOWN BOUNCE',-4:'DOWN BREAKING',0:'CHOP'}
# express banner state relative to the trade side: e.g. bearish FVG in DOWN STRONG = "with STRONG"
def rel(r):
    s,g=r.side,r.reg
    if g==0: return 'CHOP'
    same=np.sign(g)==s; k=abs(g)
    return ('with ' if same else 'against ')+{1:'STRONG',2:'WEAK',3:'PULLBACK/BOUNCE',4:'BREAKING'}[k]
df['state']=df.apply(rel,axis=1)
print('touches',len(df),' days',df.day.nunique())
print('\n== What happens after the first pullback into the gap (all periods) ==')
t=df[df.out!='none'].groupby('state').out.value_counts(normalize=True).unstack().round(2); t['n']=df[df.out!='none'].groupby('state').size(); print(t)
cols=[c for c in df.columns if '|' in c]
def pf(x): x=x.dropna(); return round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2) if len(x) else np.nan
res=[]
for c in cols:
    for st in ['ALL']+sorted(df.state.unique()):
        g=df if st=='ALL' else df[df.state==st]
        res.append(dict(rule=c,state=st,n_train=g[g.per==0][c].notna().sum(),pf_train=pf(g[g.per==0][c]),pf_test=pf(g[g.per==1][c]),n_recent=g[g.per==2][c].notna().sum(),pf_recent=pf(g[g.per==2][c]),avgR_test=round(g[g.per==1][c].mean(),3)))
R=pd.DataFrame(res); R['minpf']=R[['pf_train','pf_test']].min(axis=1)
print('\n== best FVG entries (min of train/test PF, n_train>=300) ==')
print(R[R.n_train>=300].sort_values('minpf',ascending=False).head(15).to_string(index=False))
print('\n== ALL states, each rule ==')
print(R[R.state=='ALL'].sort_values('minpf',ascending=False).head(8).to_string(index=False))
R.to_csv('fvg_rules.csv',index=False)
# size and time effects for continuation probability
d2=df[df.out!='none'].copy(); d2['cont']=d2.out=='cont'
print('\n== continuation rate by gap size (ATR) ==');print(d2.groupby(pd.cut(d2.size_atr,[0,0.25,0.5,1,2,50]),observed=True).cont.agg(['mean','size']).round(2))
print('\n== by age (bars before first touch) ==');print(d2.groupby(pd.cut(d2.age,[0,2,5,15,60,200]),observed=True).cont.agg(['mean','size']).round(2))
d2['hr']=d2.hm//100; print('\n== by hour (RTH) ==');print(d2[d2.per<2].groupby('hr').cont.agg(['mean','size']).round(2).T)
