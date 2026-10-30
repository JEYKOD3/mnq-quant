# Rules built from the 2-week tendencies, checked trade by trade (Oct 19-30). 1 MNQ = $2/pt, 1 pt cost per trade.
import pandas as pd, numpy as np
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()
d['sess']=[(t-pd.Timedelta(hours=18)).date()+pd.Timedelta(days=1) for t in d.index]
def sim(g,side,e,stop,tgt,start,end):
    s=g.loc[start:end]
    for t,b in s.iterrows():
        if (side<0 and b.high>=stop) or (side>0 and b.low<=stop): return round(side*(stop-e)-1,1),t.strftime('%H:%M'),'stop'
        if tgt is not None and ((side<0 and b.low<=tgt) or (side>0 and b.high>=tgt)): return round(abs(tgt-e)-1,1),t.strftime('%H:%M'),'target'
    return round(side*(s.close.iat[-1]-e)-1,1),s.index[-1].strftime('%H:%M'),'time'
out=[]
sess=sorted(d.sess.unique())
for k in range(1,len(sess)):
    p=d[d.sess==sess[k-1]]; g=d[d.sess==sess[k]]; day=str(sess[k])
    rth=g.between_time('09:30','15:59')
    if len(rth)<300: continue
    D=pd.Timestamp(day,tz='America/New_York')
    vw=((rth.high+rth.low+rth.close)/3*rth.volume).cumsum()/rth.volume.cumsum()
    PDH,PDL=p.high.max(),p.low.min(); on=g.between_time('18:00','09:29'); ONH,ONL=on.high.max(),on.low.min()
    # T1 midday fade: 12:00, price above VWAP and above 9:30 open -> short; stop above the morning high; target VWAP; exit 15:30
    t12=D+pd.Timedelta(hours=12); b=rth.loc[:t12].iloc[-1]; mh=rth.loc[:t12].high.max(); o930=rth.open.iat[0]
    if b.close>vw.loc[:t12].iat[-1] and b.close>o930:
        e=b.close; stop=mh+5; tgt=vw.loc[:t12].iat[-1]
        if tgt<e-10: out.append(('T1 midday fade short',day,'12:00',e,stop,tgt)+sim(rth,-1,e,stop,tgt,t12+pd.Timedelta(minutes=1),D+pd.Timedelta(hours=15,minutes=30)))
    # T2 10:00 morning long: 10:00 close above 9:30-10:00 VWAP -> long; stop below 9:30-10:00 low; exit 12:00
    t10=D+pd.Timedelta(hours=10); a=rth.loc[:t10]; b=a.iloc[-1]
    if b.close>vw.loc[:t10].iat[-1]:
        e=b.close; stop=a.low.min()-5
        out.append(('T2 10:00 long to noon',day,'10:00',e,stop,None)+sim(rth,1,e,stop,None,t10+pd.Timedelta(minutes=1),D+pd.Timedelta(hours=12)))
    # T3 key-level break (RTH, first 1m close 5 pts beyond PDL/ONL short, PDH/ONH long); stop 30 pts back inside; target 2R
    used=set()
    for t,bb in rth.loc[:D+pd.Timedelta(hours=15)].iterrows():
        for nm,L,side in [('PDL',PDL,-1),('ONL',ONL,-1),('PDH',PDH,1),('ONH',ONH,1)]:
            if nm in used: continue
            if (side<0 and bb.close<L-5) or (side>0 and bb.close>L+5):
                used.add(nm); e=bb.close; stop=L-side*25; r=abs(e-stop); tgt=e+side*2*r
                out.append((f'T3 break {nm}',day,t.strftime('%H:%M'),e,stop,tgt)+sim(rth,side,e,stop,tgt,t+pd.Timedelta(minutes=1),D+pd.Timedelta(hours=15,minutes=55)))
O=pd.DataFrame(out,columns=['rule','day','time','entry','stop','target','pts','exit','how'])
pd.set_option('display.width',200); print(O.to_string(index=False))
O['wk']=np.where(O.day>='2026-10-26','wk2','wk1'); O['rule2']=O.rule.str.replace(r' (PDL|ONL|PDH|ONH)$',lambda m:' '+('low' if m.group(1) in('PDL','ONL') else 'high'),regex=True)
print(O.groupby(['rule2','wk']).pts.agg(['count','sum','mean']).round(1))
