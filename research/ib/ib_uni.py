import pandas as pd, numpy as np
df=pd.read_pickle('trades.pkl'); df['loss']=df.res<0
ks=sorted(df.k.unique()); cut=ks[int(len(ks)*0.7)]; df['test']=df.k>=cut
feats=['mins','r_pts','r_atr','mother_atr','n_inside','bo_body','bo_range_atr','bo_ext','ema_dist','lvl_ahead','lvl_behind','day_rng_adr','pos_in_day','open_move','gap','vol_rel','prev_res','n_prev','dow','side']
tr=df[~df.test]; te=df[df.test]
print('base train hit1 %.3f res %.3f | test hit1 %.3f res %.3f'%(tr.hit1.mean(),tr.res.mean(),te.hit1.mean(),te.res.mean()))
for f in feats:
    x=tr[f].dropna()
    if x.nunique()<=7: edges=sorted(x.unique())
    else: edges=list(np.unique(np.quantile(x,[0,.2,.4,.6,.8,1])))
    print('\n==',f)
    if x.nunique()<=7:
        for v in edges:
            a=tr[tr[f]==v]; b=te[te[f]==v]
            print(f"  ={v:<8} n{len(a):5d} hit1 {a.hit1.mean():.3f} res {a.res.mean():+.3f} | test n{len(b):5d} hit1 {b.hit1.mean():.3f} res {b.res.mean():+.3f}")
    else:
        for lo,hi in zip(edges[:-1],edges[1:]):
            a=tr[(tr[f]>=lo)&(tr[f]<=hi)]; b=te[(te[f]>=lo)&(te[f]<=hi)]
            print(f"  {lo:8.2f}-{hi:8.2f} n{len(a):5d} hit1 {a.hit1.mean():.3f} res {a.res.mean():+.3f} | test n{len(b):5d} hit1 {b.hit1.mean():.3f} res {b.res.mean():+.3f}")
