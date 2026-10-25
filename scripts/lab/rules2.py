"""Playbook rule sets 'current' vs 'updated' (2026-10-25):
updated = V4+ stop to breakeven (+1.25 pt) once +1R; Pinball 120-min time cap; H2 trend-day threshold 0.30;
sizing: one $1,100 day budget = realized losses + open risk (a trade at breakeven or closed in profit frees its risk).
Returns per-trade dicts with minute times so sizing can be time-aware."""
import sys, json, datetime as dt, zoneinfo, collections, csv; sys.path.insert(0,'.')
import shortterm as ST
from core import features, COMM, PV, SLIP, T, v4_trades, v4bias, manage
NY=zoneinfo.ZoneInfo('America/New_York')
r=json.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/mnq1_tv.json'))
tv=collections.OrderedDict()
for t,o,h,l,c in r['bars']:
    x=dt.datetime.fromtimestamp(t,NY); m=x.hour*60+x.minute
    if 570<=m<960: tv.setdefault(int(x.strftime('%Y%m%d')),[]).append((m,o,h,l,c))
SRC={d:'server' for d,_ in ST.days}
for d,b in tv.items():
    if d not in SRC: ST.days.append((d,b)); SRC[d]='TradingView'
days=ST.days; F=ST.F=features(days); D=ST.D=[d for d,_ in days]; C=ST.C={d:b[-1][4] for d,b in days}
TRD={}; SMA={}
for i,d in enumerate(D):
    if i>=21: s=sum(C[x] for x in D[i-20:i])/20; SMA[d]=s; TRD[d]=1 if C[D[i-1]]>s else -1
ST.TRD=TRD; DB=dict(days)
EV=collections.defaultdict(set)
for x in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(x['date'])].add(x['event'])
def walk_be(b,i0,s,eP,stp,tgt,flat=955):
    """2R target, stop -> entry+1.25 once price reached +1R. returns (xi,xP,why,beMinute)"""
    r=abs(eP-stp); be=None; st=stp
    for j in range(i0,len(b)):
        m,o,h,l,c=b[j]
        if (s>0 and l<=st) or (s<0 and h>=st): return j,(st-s*SLIP*T if be is None else st),('stop' if be is None else 'breakeven'),be
        if (s>0 and h>=tgt) or (s<0 and l<=tgt): return j,tgt,'target',be
        if m>=flat: return j,c,'time exit',be
        if be is None and ((s>0 and h>=eP+r) or (s<0 and l<=eP-r)): be=m+1; st=eP+s*1.25
    return len(b)-1,b[-1][4],'time exit',be
def build(rules, a=20220101, z=20991231, be=None, pcap=None, h2th=None, v4t=2.0, h2t=2.0, d2t=None, pint=None):
    up=rules=='updated'; out=[]
    be=up if be is None else be; pcap=(120 if up else 0) if pcap is None else pcap; h2th=(.3 if up else .4) if h2th is None else h2th
    v4=collections.defaultdict(list)
    for t in v4_trades(days,F,tf=1,tgtR=v4t,bias=lambda f: v4bias(f,.4,.4,0)):
        if TRD.get(t['d'])==t['side']: v4[t['d']].append(t)
    h2=collections.defaultdict(list)
    for t in ST.run('h2',h2t,None,trendday=True,dtrend=True,tdth=h2th,maxtr=3): h2[t['d']].append(t)
    for d in D:
        if d<a or d>z or d not in TRD: continue
        b=DB[d]; f=F[d]; k=D.index(d); tr=TRD[d]; idx={x[0]:j for j,x in enumerate(b)}
        for t in v4[d]:
            s=t['side']; eP=t['eP']; stp=t['stp']; rr=t['r']; tgt=eP+s*v4t*rr; i=idx[t['eT']]
            if be and not ((s>0 and b[i][3]<=stp) or (s<0 and b[i][2]>=stp)):
                xi,xP,why,beM=walk_be(b,i+1,s,eP,stp,tgt)
                out.append(dict(d=d,strat='V4+',side=s,eT=t['eT'],eP=eP,stp=stp,tgt=tgt,xT=b[xi][0],xP=xP,why=why,r=rr,pts=(xP-eP)*s,be=beM,w=1.0))
            else:
                out.append(dict(d=d,strat='V4+',side=s,eT=t['eT'],eP=eP,stp=stp,tgt=tgt,xT=t['xT'],xP=t['xP'],why={'close':'time exit'}.get(t['why'],t['why']),r=rr,pts=t['pts'],be=None,w=1.0))
        if not ({'FOMC','CPI'}&EV.get(d,set())):
            j=idx.get(629)
            if j is not None:
                px=b[j][4]; mv=(px-f['open'])/f['adr']
                if abs(mv)>=.5:
                    s=1 if mv>0 else -1; eP=px+s*SLIP*T; stp=f['open']-s*T
                    xi,xP,why,_,_=manage(b,j+1,s,eP,stp,(eP+s*d2t*abs(eP-stp)) if d2t else None,0,900)
                    out.append(dict(d=d,strat='D2',side=s,eT=630,eP=eP,stp=stp,tgt=None,xT=b[xi][0],xP=xP,why=why if why in('stop','target') else 'time exit',r=abs(eP-stp),pts=(xP-eP)*s,be=None,w=1.0 if tr==s else .5))
        ch=[C[D[q]]-C[D[q-1]] for q in range(k-3,k)]; u=sum(x for x in ch if x>0); dn=-sum(x for x in ch if x<0)
        rsi=100 if dn==0 else 100-100/(1+u/dn); s=1 if rsi<30 else (-1 if rsi>70 else 0)
        if s and tr==s:
            IB=[x for x in b if x[0]<630]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB); lvl=hi+T if s>0 else lo-T
            for i,(m,o,h,l,c) in enumerate(b):
                if m<630 or m>900: continue
                if (s>0 and h>=lvl) or (s<0 and l<=lvl):
                    eP=(max(o,lvl) if s>0 else min(o,lvl))+s*SLIP*T; stp=(lo-T) if s>0 else (hi+T)
                    if (s>0 and l<=stp) or (s<0 and h>=stp): xi,xP,why=i,stp-s*SLIP*T,'stop'
                    else: xi,xP,why,_,_=manage(b,i+1,s,eP,stp,(eP+s*pint*abs(eP-stp)) if pint else None,pcap,955)
                    out.append(dict(d=d,strat='Pinball',side=s,eT=m,eP=eP,stp=stp,tgt=None,xT=b[xi][0],xP=xP,why=why if why in('stop','target') else ('time exit (2h)' if why=='time' else 'time exit'),r=abs(eP-stp),pts=(xP-eP)*s,be=None,w=1.0,rsi=rsi)); break
        for t in h2[d]:
            s=t['side']; eP=b[idx[t['eT']]][1]+s*SLIP*T
            out.append(dict(d=d,strat='H2',side=s,eT=t['eT'],eP=eP,stp=eP-s*t['r'],tgt=eP+s*h2t*t['r'],xT=t['eT']+t['hold'],xP=eP+s*t['pts'],why={'tgt':'target','stop':'stop'}.get(t['why'],'time exit'),r=t['r'],pts=t['pts'],be=None,w=.5))
    out.sort(key=lambda t:(t['d'],t['eT']))
    return out
def size_day(trs, cush, mode, f=.65, dll=1100, slipx=0.0):
    """mode 'current': cumulative risk budget; 'updated': realized losses + open risk at each entry. Sets q, netq."""
    used=0; done=[]
    for t in trs:
        rc=(t['r']+SLIP*T)*PV+2*COMM; pts=t['pts']-(slipx if t['why'] in('stop','breakeven') else 0); pc=pts*PV-2*COMM
        if mode=='updated':
            occ=0
            for u in done:
                if u['q']==0: continue
                if u['xT']<=t['eT']: occ+=max(0,-u['netq'])            # closed: only a loss counts
                elif u['be'] is not None and u['be']<=t['eT']: occ+=0     # at breakeven: no risk
                else: occ+=u['q']*u['rc']
            used=occ
        w=t['w']
        budget=min(w*f*cush, f*cush-used, dll-used); q=min(40,int(budget//rc)) if budget>0 else 0
        if q<1 and w>=1 and rc<.9*(cush-used) and rc<dll-used: q=1
        q=max(q,0); t['q']=q; t['rc']=rc; t['netq']=q*pc; t['net1']=t['pts']*PV-2*COMM
        if mode=='current': used+=q*rc
        done.append(t)
    return sum(t['netq'] for t in trs)
