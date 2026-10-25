"""Day-by-day table Sep 1 - Oct 23 2026, all four strategies with CURRENT rules. Server 1m data + TradingView 1m days."""
import sys, json, datetime as dt, zoneinfo, collections, csv; sys.path.insert(0,'.')
import shortterm as ST
from core import features, COMM, PV, SLIP, T, v4_trades, v4bias, manage, agg
NY=zoneinfo.ZoneInfo('America/New_York')
r=json.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/mnq1_tv.json'))
tv=collections.OrderedDict()
for t,o,h,l,c in r['bars']:
    x=dt.datetime.fromtimestamp(t,NY); m=x.hour*60+x.minute
    if 570<=m<960: tv.setdefault(int(x.strftime('%Y%m%d')),[]).append((m,o,h,l,c))
src={}
have={d for d,_ in ST.days}
for d in have: src[d]='server'
for d,b in tv.items():
    if d not in have: ST.days.append((d,b)); src[d]='TradingView'
days=ST.days; F=ST.F=features(days); D=ST.D=[d for d,_ in days]; C=ST.C={d:b[-1][4] for d,b in days}
TRD={}; SMA={}
for i,d in enumerate(D):
    if i>=21: s=sum(C[x] for x in D[i-20:i])/20; SMA[d]=s; TRD[d]=1 if C[D[i-1]]>s else -1
ST.TRD=TRD
EV=collections.defaultdict(set)
for x in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(x['date'])].add(x['event'])
DB=dict(days); hm=lambda m:f"{m//60}:{m%60:02d}"
A,Z=20260901,20261023
sel=[d for d in D if A<=d<=Z]
V4={t['d']:t for t in v4_trades(days,F,tf=1,tgtR=2,bias=lambda f: v4bias(f,.4,.4,0))}
H2=collections.defaultdict(list)
for t in ST.run('h2',2,None,trendday=True,dtrend=True,tdth=.4,maxtr=3): H2[t['d']].append(t)
rows=[]
for d in sel:
    b=DB[d]; f=F[d]; tr=TRD[d]; k=D.index(d); adr=f['adr']; ev=sorted(EV.get(d,[]))
    day=dict(d=d,src=src[d],trend='UP' if tr>0 else 'DOWN',prevclose=C[D[k-1]],sma20=round(SMA[d],2),adr=round(adr),open=f['open'],
             gap=f['gap'],orDir=f['orDir'],orh=f['orh'],orl=f['orl'],close=b[-1][4],hi=max(x[2] for x in b),lo=min(x[3] for x in b),events=ev,trades=[],notes={})
    # V4+
    G=abs(f['gap'])>=.4; Dd=abs(f['orDir'])>=.4
    bias=(1 if f['gap']>0 else -1) if G else ((1 if f['orDir']>0 else -1) if Dd else 0)
    why_b=f"gap {f['gap']:+.2f} ADR, first-15m {f['orDir']:+.2f}"
    t=V4.get(d)
    if not bias: day['notes']['V4+']=f"No trade: open not committed ({why_b}; needs 0.40)"
    elif bias!=tr: day['notes']['V4+']=f"No trade: open bias {'LONG' if bias>0 else 'SHORT'} is against the {day['trend']} trend ({why_b})"
    elif not t: day['notes']['V4+']=f"Armed {'LONG' if bias>0 else 'SHORT'} ({why_b}) but no breakout-retest-rejection before 13:00"
    else:
        s=t['side']; day['trades'].append(dict(strat='V4+',side=s,eT=hm(t['eT']),eP=t['eP'],stp=t['stp'],tgt=round(t['eP']+s*2*t['r'],2),xT=hm(t['xT']),xP=t['xP'],why=t['why'],r=t['r'],pts=t['pts'],
            setup=f"OR {f['orl']}-{f['orh']}; {why_b}; break, retest, rejection candle"))
    # D2
    px=[x for x in b if x[0]==629][0][4]; mv=(px-f['open'])/adr
    if {'FOMC','CPI'}&EV.get(d,set()): day['notes']['D2']=f"Skipped: {'/'.join(sorted({'FOMC','CPI'}&EV[d]))} day (move at 10:29 was {mv:+.2f} ADR)"
    elif abs(mv)<.5: day['notes']['D2']=f"No trade: move at 10:29 {mv:+.2f} ADR (needs 0.50)"
    else:
        s=1 if mv>0 else -1; i=[j for j,x in enumerate(b) if x[0]==629][0]; eP=px+s*SLIP*T; stp=f['open']-s*T
        xi,xP,why,_,_=manage(b,i+1,s,eP,stp,None,0,900)
        day['trades'].append(dict(strat='D2',side=s,eT='10:30',eP=eP,stp=stp,tgt=None,xT=hm(b[xi][0]),xP=xP,why=why if why!='close' else 'time 15:00',r=abs(eP-stp),pts=(xP-eP)*s,
            w=1.0 if tr==s else .5,setup=f"move at 10:29 {mv:+.2f} ADR; stop at the open; {'with' if tr==s else 'AGAINST'} trend ({'full' if tr==s else 'half'} size)"))
    # Pinball
    ch=[C[D[j]]-C[D[j-1]] for j in range(k-3,k)]; up=sum(x for x in ch if x>0); dn=-sum(x for x in ch if x<0)
    rsi=100 if dn==0 else 100-100/(1+up/dn); s=1 if rsi<30 else (-1 if rsi>70 else 0)
    if not s: day['notes']['PIN']=f"No setup: RSI3 {rsi:.0f} (needs <30 or >70)"
    elif tr!=s: day['notes']['PIN']=f"No setup: RSI3 {rsi:.0f} {'oversold' if s>0 else 'overbought'} but trend is {day['trend']}"
    else:
        IB=[x for x in b if x[0]<630]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB); lvl=hi+T if s>0 else lo-T; got=False
        for i,(m,o,h,l,c) in enumerate(b):
            if m<630 or m>900: continue
            if (s>0 and h>=lvl) or (s<0 and l<=lvl):
                eP=(max(o,lvl) if s>0 else min(o,lvl))+s*SLIP*T; stp=(lo-T) if s>0 else (hi+T)
                if (s>0 and l<=stp) or (s<0 and h>=stp): xi,xP,why=i,stp-s*SLIP*T,'stop'
                else: xi,xP,why,_,_=manage(b,i+1,s,eP,stp,None,0,955)
                day['trades'].append(dict(strat='Pinball',side=s,eT=hm(m),eP=eP,stp=stp,tgt=None,xT=hm(b[xi][0]),xP=xP,why=why if why!='close' else 'time 15:55',r=abs(eP-stp),pts=(xP-eP)*s,
                    setup=f"RSI3 {rsi:.0f}, trend {day['trend']}; stop order beyond first hour {lo}-{hi}")); got=True; break
        if not got: day['notes']['PIN']=f"Setup {'LONG' if s>0 else 'SHORT'} (RSI3 {rsi:.0f}) but first-hour {'high' if s>0 else 'low'} never broke 10:30-15:00"
    # H2
    tdm=mv
    if abs(tdm)<.4: day['notes']['H2']=f"Not a trend day: {tdm:+.2f} ADR at 10:29 (needs 0.40)"
    elif (1 if tdm>0 else -1)!=tr: day['notes']['H2']=f"Trend day {'UP' if tdm>0 else 'DOWN'} but against the daily trend"
    elif not H2.get(d): day['notes']['H2']="Trend day, but no second-entry pullback signal"
    for t in H2.get(d,[]):
        s=t['side']; j=[i for i,x in enumerate(b) if x[0]==t['eT']][0]; eP=b[j][1]+s*SLIP*T
        day['trades'].append(dict(strat='H2',side=s,eT=hm(t['eT']),eP=eP,stp=round(eP-s*t['r'],2),tgt=round(eP+s*2*t['r'],2),xT=hm(t['eT']+t['hold']),xP=round(eP+s*t['pts'],2),why=t['why'].replace('tgt','target').replace('time','time 15:55'),r=t['r'],pts=t['pts'],w=.5,
            setup=f"trend day {tdm:+.2f} ADR; 5m pullback then bar closing back in trend direction"))
    day['trades'].sort(key=lambda t:(int(t['eT'].split(':')[0])*60+int(t['eT'].split(':')[1])))
    rows.append(day)
# eval sizing, start Sep 1, shared $1,100 day budget, 65% of room (same as the eval simulations)
bal=50000.; peak=50000.
for day in rows:
    mll=min(peak-2000,50000); cush=bal-mll; used=0; dp=0
    day['bal0']=round(bal,2); day['room']=round(cush,2)
    for t in day['trades']:
        t['net1']=round((t['pts']-2*COMM/PV)*PV,2); t['R']=round((t['pts']-2*COMM/PV)/t['r'],2)
        w=t.get('w',1.0); rc=(t['r']+SLIP*T)*PV+2*COMM
        budget=min(w*.65*cush,.65*cush-used,1100-used); q=min(40,int(budget//rc))
        if q<1 and w>=1 and rc<.9*(cush-used) and rc<1100-used: q=1
        q=max(q,0); used+=q*rc; t['q']=q; t['risk$']=round(q*rc); t['netq']=round(q*t['net1'],2); dp+=t['netq']
    bal+=dp; peak=max(peak,bal); day['dayq']=round(dp,2); day['bal1']=round(bal,2); day['day1']=round(sum(t['net1'] for t in day['trades']),2)
json.dump(rows,open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/sepoct.json','w'))
n=sum(len(x['trades']) for x in rows); print(len(rows),'days',n,'trades')
for day in rows:
    print(day['d'],day['src'][:2],day['trend'],f"{day['day1']:+8.0f} {day['dayq']:+8.0f} bal {day['bal1']:.0f}", ' | '.join(f"{t['strat']} {'L' if t['side']>0 else 'S'} {t['eT']}->{t['xT']} {t['why']} {t['pts']:+.0f}pt q{t['q']}" for t in day['trades']))
