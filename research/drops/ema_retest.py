# Jey's idea: price breaks the EMA20, comes back to retest it, then continues the other way.
# Test on MNQ 1m RTH (2021-10..2026-10), the chart he trades. Entry = break of the retest bar, stop = retest high/low.
import numpy as np, pandas as pd, gzip, itertools
days=[]
for line in open('../../data/raw/mnq_rth_1m.txt'):
    d,*bars=line.strip().split('|'); a=np.array([[int(x) for x in b.split(',')] for b in bars],float)
    a[:,1:]/=4; days.append((d,a))
def run(days,emaLen=20,K=15,tol=0.0,tgt=2.0,lock=None,body=0.0,needTrend=False,firstOnly=True,minSep=3):
    out=[]
    for d,a in days:
        t,o,h,l,c=a.T; n=len(c)
        if n<60: continue
        ema=pd.Series(c).ewm(span=emaLen,adjust=False).mean().values
        tp=(h+l+c)/3; vw=np.cumsum(tp)/np.arange(1,n+1)   # no volume in this file: equal-weight session average as VWAP proxy
        tr=np.maximum(h-l,np.abs(np.r_[c[0],c[:-1]]-np.r_[h[:1],h[1:]])); atr=pd.Series(h-l).rolling(14).mean().values
        i=emaLen
        while i<n-5 and t[i]<1555:
            side=0
            if all(c[i-k]>ema[i-k] for k in range(1,minSep+1)) and c[i]<ema[i]: side=-1
            elif all(c[i-k]<ema[i-k] for k in range(1,minSep+1)) and c[i]>ema[i]: side=1
            if side==0 or (body and abs(c[i]-o[i])<body*(h[i]-l[i]+1e-9)) or (needTrend and side*(c[i]-vw[i])<=0): i+=1; continue
            # wait for retest: a bar that touches EMA from the new side without closing back across
            done=False
            for j in range(i+1,min(i+1+K,n-2)):
                if side*(c[j]-ema[j])<0: break                    # closed back across: failed break
                touch=(h[j]>=ema[j]-tol) if side<0 else (l[j]<=ema[j]+tol)
                if not touch: continue
                ext=h[i:j+1].max() if side<0 else l[i:j+1].min()   # stop beyond the retest extreme
                # trigger: next bar closes beyond the retest bar
                for m in range(j+1,min(j+4,n-1)):
                    if side*(c[m]-ema[m])<0: break
                    if (side<0 and c[m]<l[j]) or (side>0 and c[m]>h[j]):
                        e=c[m]; stop=ext+side*-0.25; r=abs(e-stop)
                        if r<=0.5: break
                        res=None; best=0
                        for q in range(m+1,n):
                            if t[q]>=1555: res=side*(c[q]-e)/r; break
                            adv=side*((l[q] if side<0 else h[q])-e)/r; adv_hit=side*((h[q] if side<0 else l[q])-e)/r
                            s_eff=stop if not (lock and best>=lock) else e+side*0.0*r
                            if (side<0 and h[q]>=s_eff) or (side>0 and l[q]<=s_eff): res=(-1.0 if s_eff==stop else 0.0); break
                            best=max(best,adv)
                            if adv>=tgt: res=tgt; break
                        if res is None: res=side*(c[-1]-e)/r
                        out.append((d,t[m],side,res,r)); done=True
                        break
                if done or firstOnly: break
            i=(m+1) if done else i+1
    return pd.DataFrame(out,columns=['d','t','side','R','risk'])
def st(df):
    w=df.R[df.R>0].sum(); L=-df.R[df.R<0].sum()
    return dict(n=len(df),win=round((df.R>0).mean(),3),avgR=round(df.R.mean(),3),PF=round(w/L,3) if L else None,risk=round(df.risk.median(),1),perday=round(len(df)/df.d.nunique(),2) if len(df) else 0)
split='20250101'
rows=[]
for emaLen,tgt,lock,body,trend in itertools.product([20,9],[1.0,1.5,2.0],[None,1.0],[0.0,0.5],[False,True]):
    if lock and lock>=tgt: continue
    df=run(days,emaLen=emaLen,tgt=tgt,lock=lock,body=body,needTrend=trend)
    tr=df[df.d<split]; te=df[df.d>=split]
    s=st(df); rows.append(dict(ema=emaLen,tgt=tgt,lock=lock,body=body,withVWAP=trend,**s,PF_train=st(tr)['PF'],PF_test=st(te)['PF'],
        yrs=' '.join(str(st(df[df.d.str[:4]==y])['PF']) for y in ['2022','2023','2024','2025','2026'])))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('ema_retest_grid.csv',index=False)
