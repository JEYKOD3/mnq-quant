import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
df=pd.read_pickle('trades.pkl')
ks=sorted(df.k.unique()); cut=ks[int(len(ks)*0.7)]; te=df.k>=cut
feats=['mins','r_pts','r_atr','mother_atr','n_inside','bo_body','bo_range_atr','bo_ext','ema_dist','lvl_ahead','lvl_behind','day_rng_adr','pos_in_day','open_move','gap','vol_rel','prev_res','n_prev','dow','side']
X=df[feats]; y=df.hit1.astype(int)
m=HistGradientBoostingClassifier(max_depth=3,learning_rate=0.05,max_iter=200,min_samples_leaf=200).fit(X[~te],y[~te])
p=m.predict_proba(X[te])[:,1]
print('test AUC', round(roc_auc_score(y[te],p),3), ' train AUC', round(roc_auc_score(y[~te],m.predict_proba(X[~te])[:,1]),3))
d=df[te].copy(); d['p']=p
for q in [0,0.5,0.7,0.8,0.9]:
    th=np.quantile(p,q); s=d[d.p>=th]
    print(f"keep top {100-q*100:.0f}%: n{len(s)} hit1 {s.hit1.mean():.3f} avgR {s.res.mean():+.3f} PF {s.res[s.res>0].sum()/-s.res[s.res<0].sum():.2f}")
