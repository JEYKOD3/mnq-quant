# Sequential (one position at a time) FVG-middle scalp on MNQ 1m. Rule:
#  - LuxAlgo FVG forms (threshold 0). Within the next 2 bars price pulls back to the MIDDLE of the gap (must trade 0.5 pt through).
#  - Limit entry at the middle, in the gap's direction. Stop = far edge + 0.5 x ATR(14, 1m). Target 1.5R. Time stop 30 min. Cost 1 pt/round trip.
#  - Optional: banner filter (trade side vs Playbook state), RTH windows, max trades/day, daily stop.
import numpy as np, pandas as pd, sys
exec(open('fvg_lab.py').read().split("def per(dd)")[0])   # loads days + bias helpers
def per(dd): return 0 if dd<'20250101' else (1 if dd[:8]<='20261020' and not dd.endswith('g') else 2)
def run(state_ok=None, win=(930,1555), maxday=99, daystop=None, thru=0.5, ageMax=2, tgtR=1.5, stopA=0.5):
    tr=[]
    for dd,ts,o,h,l,c,v in days:
        n=len(c)
        if n<120: continue
        hm=(ts.hour*100+ts.minute).values
        tp=(h+l+c)/3; vw=np.cumsum(tp*(v if v is not None else 1))/np.cumsum(v if v is not None else np.ones(n))
        e21=pd.Series(c).ewm(span=21,adjust=False).mean().values
        atr=pd.Series(np.maximum(h-l,np.abs(h-np.r_[c[0],c[:-1]]))).ewm(alpha=1/14,adjust=False).mean().values
        slope=(e21-np.r_[np.full(10,np.nan),e21[:-10]])/np.maximum(atr,.25)
        busy=-1; nday=0; pday=0.0
        for i in range(2,n-3):
            if i<=busy or nday>=maxday or (daystop and pday<=-daystop): continue
            for side in (-1,1):
                if side<0 and not(h[i]<l[i-2] and c[i-1]<l[i-2]): continue
                if side>0 and not(l[i]>h[i-2] and c[i-1]>h[i-2]): continue
                top,bot=(l[i-2],h[i]) if side<0 else (l[i],h[i-2]); far=top if side<0 else bot
                e=(top+bot)/2; stop=far-side*stopA*atr[i]; r=abs(e-stop)
                if state_ok is not None and not state_ok(side, c[i], vw[i], slope[i]): continue
                k0=None
                for k in range(i+1,min(i+1+ageMax,n)):
                    if not(win[0]<=hm[k]<win[1]): break
                    if (side<0 and h[k]>=e+thru) or (side>0 and l[k]<=e-thru): k0=k; break
                if k0 is None: continue
                pnl=None; x=None
                if (side<0 and h[k0]>=stop) or (side>0 and l[k0]<=stop): pnl=-r; x=k0
                else:
                    for k in range(k0+1,min(k0+31,n)):
                        if (side<0 and h[k]>=stop) or (side>0 and l[k]<=stop): pnl=-r; x=k; break
                        if (side<0 and l[k]<=e-tgtR*r) or (side>0 and h[k]>=e+tgtR*r): pnl=tgtR*r; x=k; break
                if pnl is None: x=min(k0+30,n-1); pnl=side*(c[x]-e)
                pnl-=1.0; tr.append((dd,per(dd),pnl,r,x-k0+1,side)); busy=x; nday+=1; pday+=pnl; break
    return pd.DataFrame(tr,columns=['day','per','pts','r','mins','side'])
def rep(name,t):
    pf=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2)
    by=t.groupby('per'); dpl=t.groupby('day').pts.sum()
    yrs=t.assign(y=t.day.str[:4]).groupby('y').pts.apply(pf).to_dict()
    print(f"{name:34s} trades/day {len(t)/t.day.nunique():4.1f} win {(t.pts>0).mean():.2f} PF tr {pf(t[t.per==0].pts)} te {pf(t[t.per==1].pts)} rec {pf(t[t.per==2].pts)} | pts/trade {t.pts.mean():+.2f} | med stop {t.r.median():.1f} pts | med hold {t.mins.median():.0f} min | green days {(dpl>0).mean():.2f} | worst day {dpl.min():.0f} pts | years {yrs}",flush=True)
    return t
withtrend=lambda s,c,vw,sl: s*(c-vw)>0 and s*sl>0
rep('all gaps, RTH',run())
rep('all gaps, RTH, max 10/day, stop -40 pts',run(maxday=10,daystop=40))
rep('with VWAP+slope (banner "now")',run(state_ok=withtrend))
rep('with VWAP+slope, max 10/day, -40 pts',run(state_ok=withtrend,maxday=10,daystop=40))
rep('9:30-11:30 only',run(win=(930,1130)))
rep('with trend, 9:30-11:30',run(state_ok=withtrend,win=(930,1130)))
t=rep('tgt 1R',run(tgtR=1.0)); t=rep('tgt 2R',run(tgtR=2.0))
t=rep('stop far+0.25 ATR',run(stopA=0.25)); t=rep('stop far+1 ATR',run(stopA=1.0))
t=rep('thru 1 pt (strict fills)',run(thru=1.0))
