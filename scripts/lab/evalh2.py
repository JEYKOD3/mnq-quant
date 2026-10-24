import sys, collections, csv, pickle; sys.path.insert(0,'.')
from shortterm import run as strun
from core import SLIP, T, PV, COMM, v4_trades, v4bias, manage
import shortterm as ST
days=ST.days; F=ST.F; TRD=ST.TRD; D=ST.D; C=ST.C
EV=collections.defaultdict(set)
for x in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(x['date'])].add(x['event'])
# streams (per-day lists of trades with keys d,side,r,pts,why,eT)
def by_day(tr):
    m=collections.defaultdict(list)
    for t in tr: m[t['d']].append(t)
    return m
V4=[dict(d=t['d'],side=t['side'],r=t['r'],pts=t['pts'],why=t['why'],eT=t['eT']) for t in v4_trades(days,F,tf=1,tgtR=2,bias=lambda f: v4bias(f,.4,.4,0)) if t['d'] in TRD and TRD[t['d']]==t['side']]
D2=[]
for d,b in days:
    f=F.get(d)
    if not f or d<20220101 or d not in TRD or {'FOMC','CPI'}&EV.get(d,set()): continue
    idx=[i for i,x in enumerate(b) if x[0]==629]
    if not idx: continue
    i=idx[0]; px=b[i][4]; mv=(px-f['open'])/f['adr']
    if abs(mv)<.5: continue
    s=1 if mv>0 else -1; eP=px+s*SLIP*T; stp=f['open']-s*T
    xi,xP,why,_,_=manage(b,i+1,s,eP,stp,None,0,900)
    D2.append(dict(d=d,side=s,r=abs(eP-stp),pts=(xP-eP)*s,why=why,eT=630,w=1.0 if TRD[d]==s else .5))
PIN=[]
for k,d in enumerate(D):
    if d<20220101 or d not in TRD: continue
    ch=[C[D[j]]-C[D[j-1]] for j in range(k-3,k)]; up=sum(x for x in ch if x>0); dn=-sum(x for x in ch if x<0)
    rsi=100 if dn==0 else 100-100/(1+up/dn); s=1 if rsi<30 else (-1 if rsi>70 else 0)
    if not s or TRD[d]!=s: continue
    b=dict(days)[d]; IB=[x for x in b if x[0]<630]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB); lvl=hi+T if s>0 else lo-T
    for i,(m,o,h,l,c) in enumerate(b):
        if m<630 or m>900: continue
        if (s>0 and h>=lvl) or (s<0 and l<=lvl):
            eP=(max(o,lvl) if s>0 else min(o,lvl))+s*SLIP*T; stp=(lo-T) if s>0 else (hi+T)
            if (s>0 and l<=stp) or (s<0 and h>=stp): xP,why=stp-s*SLIP*T,'stop'
            else: _,xP,why,_,_=manage(b,i+1,s,eP,stp,None,0,955)
            PIN.append(dict(d=d,side=s,r=abs(eP-stp),pts=(xP-eP)*s,why=why,eT=m)); break
H2=strun('h2',2,None,trendday=True,dtrend=True,tdth=.4,maxtr=3)
pickle.dump(dict(V4=V4,D2=D2,PIN=PIN,H2=H2),open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/streams.pkl','wb'))
DAYS=[d for d in D if d>=20220301]
def sched(names):
    S=collections.defaultdict(list)
    for nm in names:
        for t in {'V4':V4,'D2':D2,'PIN':PIN,'H2':H2}[nm]: S[t['d']].append(t)
    for d in S: S[d].sort(key=lambda t:t['eT'])
    return S
def attempt(S,start,f,dll=1100,slipx=8.0,horizon=250):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for t in S.get(d,[]):
            w=t.get('w',1.0)
            rc=(t['r']+SLIP*T)*PV+2*COMM; pts=t['pts']-(slipx if t['why']=='stop' else 0); pc=pts*PV-2*COMM
            budget=min(w*f*cush, f*cush-used, dll-used); q=min(40,int(budget//rc))
            if q<1 and w>=1 and rc<.9*(cush-used) and rc<dll-used: q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def ev(S,f,a,z,step=2):
    st=[d for d in DAYS if a<=d<=z][::step]; R=[attempt(S,s,f) for s in st]; n=len(R)
    P=sorted(r[1] for r in R if r[0]=='P'); Fl=sum(r[0]=='F' for r in R)
    return [sum(x<=k for x in P)/n for k in (10,20,40,60)]+[Fl/n,(P[len(P)//2] if P else 999)]
pc=lambda x:f"{round(100*x):3d}%"
if __name__=='__main__':
    def stats(tr,lab):
        R=[(t['pts']-2*COMM/PV)/t['r']*t.get('w',1) for t in tr]; g=sum(x for x in R if x>0); l=-sum(x for x in R if x<=0)
        print(f"{lab:6s} n{len(tr)} ({len(tr)/4.8:.0f}/yr) PF{g/l:.2f} totR{sum(R):+.1f}")
    for nm,tr in (('V4+',V4),('D2',D2),('PIN',PIN),('H2',H2)): stats(tr,nm)
    for names in (['H2'],['V4','H2'],['V4','D2','PIN'],['V4','H2','PIN'],['V4','D2','PIN','H2'],['V4','D2','H2']):
        S=sched(names)
        for f in (.5,.65,.8):
            Dv=ev(S,f,20220301,20241231); Tt=ev(S,f,20250101,20260601)
            print(f"{'+'.join(names):16s} f{f} | DEV pass<=10/20/40/60d "+' '.join(pc(x) for x in Dv[:4])+f" fail {pc(Dv[4])} med {Dv[5]} | TEST "+' '.join(pc(x) for x in Tt[:4])+f" fail {pc(Tt[4])} med {Tt[5]}")
