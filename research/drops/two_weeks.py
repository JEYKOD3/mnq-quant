# What MNQ did Oct 19-30 2026 (MNQZ6 1m, all hours, through Oct 30 05:09 ET).
import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()[['open','high','low','close','volume']]
d['sess']=[(t-pd.Timedelta(hours=18)).date()+pd.Timedelta(days=1) for t in d.index]   # trading day label (Globex day ends 17:00)
d=d[d.sess>=pd.Timestamp('2026-10-19').date()]
rows=[]
for s,g in d.groupby('sess'):
    on=g.between_time('18:00','09:29'); rth=g.between_time('09:30','15:59')
    if len(rth)==0: continue
    path=np.abs(np.diff(g.close.values)).sum(); eff=abs(g.close.iat[-1]-g.open.iat[0])/path
    rows.append(dict(day=str(s),open=g.open.iat[0],high=g.high.max(),low=g.low.min(),close=g.close.iat[-1],
        chg=round(g.close.iat[-1]-g.open.iat[0],1),range=round(g.high.max()-g.low.min(),1),
        overnight_chg=round(on.close.iat[-1]-on.open.iat[0],1) if len(on) else np.nan,
        rth_chg=round(rth.close.iat[-1]-rth.open.iat[0],1),rth_range=round(rth.high.max()-rth.low.min(),1),
        close_loc=round((g.close.iat[-1]-g.low.min())/(g.high.max()-g.low.min()),2),efficiency=round(eff,3),
        hi_time=g.high.idxmax().strftime('%a %H:%M'),lo_time=g.low.idxmin().strftime('%a %H:%M')))
D=pd.DataFrame(rows); print('== SESSIONS (18:00 prior day -> 17:00) =='); print(D.to_string(index=False))
# hourly contribution
d['hr']=d.index.hour
h=d.groupby([d.sess,d.hr]).agg(o=('open','first'),c=('close','last'),hi=('high','max'),lo=('low','min'))
h['chg']=h.c-h.o; h['rng']=h.hi-h.lo
hh=h.groupby(level=1).agg(net_chg_sum=('chg','sum'),avg_chg=('chg','mean'),down_share=('chg',lambda x:(x<0).mean()),avg_range=('rng','mean'))
print('\n== BY HOUR ET (sum of net change over all sessions; avg range) =='); print(hh.round(1).T.to_string())
wk=d[d.sess>=pd.Timestamp('2026-10-26').date()]
hw=wk.groupby([wk.sess,wk.hr]).agg(o=('open','first'),c=('close','last')); hw['chg']=hw.c-hw.o
print('\n== SINCE MONDAY: net change by hour =='); print(hw.groupby(level=1).chg.sum().round(0).to_frame().T.to_string())
# key levels: prior-day H/L/C, overnight H/L, round 100s; how price reacted on first touch (held = reversed >= 30 pts before closing 10 pts beyond)
lv=[]
sess=sorted(d.sess.unique())
for k in range(1,len(sess)):
    p=d[d.sess==sess[k-1]]; g=d[d.sess==sess[k]]; on=g.between_time('18:00','09:29'); rth=g.between_time('09:30','16:59')
    levels={'PDH':p.high.max(),'PDL':p.low.min(),'PDC':p.close.iat[-1]}
    if len(on): levels.update({'ONH':on.high.max(),'ONL':on.low.min()})
    for nm,L in levels.items():
        seg=rth if nm.startswith('ON') else g
        if len(seg)<5: continue
        c=seg.close.values; hi=seg.high.values; lo=seg.low.values
        start_side=np.sign(c[0]-L)
        for i in range(1,len(c)):
            touched=(lo[i]<=L<=hi[i])
            if not touched: continue
            res='open'
            for j in range(i,min(i+120,len(c))):
                if start_side>0 and c[j]<L-10: res='broke'; break
                if start_side<0 and c[j]>L+10: res='broke'; break
                if start_side>0 and hi[j]-L>=30: res='held'; break
                if start_side<0 and L-lo[j]>=30: res='held'; break
            lv.append(dict(day=str(sess[k]),level=nm,price=L,from_='above' if start_side>0 else 'below',time=seg.index[i].strftime('%H:%M'),result=res)); break
LV=pd.DataFrame(lv); print('\n== FIRST TOUCH OF KEY LEVELS (held = 30 pts reaction before a 10-pt close beyond) =='); print(LV.to_string(index=False))
print(LV.groupby(['level','result']).size().unstack(fill_value=0))
# round numbers: 100-pt levels touched in RTH since Monday
D.to_csv('two_weeks_sessions.csv',index=False); LV.to_csv('two_weeks_levels.csv',index=False)
