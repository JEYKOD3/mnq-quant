import sys, pickle, itertools; sys.path.insert(0,'.')
from hir import orb5, TRD, days, F
from core import SLIP, T, PV, COMM, summary
TR=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/trades.pkl','rb'))
from regime import FOMC
DAYS=[d for d,_ in days if d>=20220301]
def norm(t,side_key='side'):
    return dict(d=t['d'],side=t.get('side',t.get('s')),r=t['r'],pts=t['pts'],why=t['why'])
S={}
S['V4']=[norm(t) for t in TR['V4_1m_2R']]
S['D2']=[norm(t) for t in TR['D2_1030_o_1500'] if t['d'] not in FOMC]
S['ORB15']=[norm(t) for t in orb5(15,'adr',.15,None,'none')]
S['ORB5']=[norm(t) for t in orb5(5,'adr',.1,None,'none')]
for k in S: S[k]={t['d']:t for t in S[k]}
def w_of(k,t,wts):
    tr=TRD[t['d']][0]; aligned= tr==t['side']
    return wts[k][0] if aligned else wts[k][1]
def attempt(wts,start,f,dll=1100,slipx=8.0,horizon=250,order=('ORB5','ORB15','V4','D2')):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for k in order:
            t=S[k].get(d)
            if not t: continue
            w=w_of(k,t,wts)
            if w<=0: continue
            rc=(t['r']+SLIP*T)*PV+2*COMM; pts=t['pts']-(slipx if t['why']=='stop' else 0); pc=pts*PV-2*COMM
            budget=min(w*f*cush, f*cush-used, dll-used)
            q=min(40,int(budget//rc))
            if q<1 and w>=1 and rc<0.9*(cush-used) and rc<dll-used: q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=0.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def ev(wts,f,a,z,step=2):
    st=[d for d in DAYS if a<=d<=z][::step]; R=[attempt(wts,s,f) for s in st]; n=len(R)
    P=sorted(r[1] for r in R if r[0]=='P'); Fl=sum(r[0]=='F' for r in R)
    return dict(p10=sum(x<=10 for x in P)/n,p20=sum(x<=20 for x in P)/n,p40=sum(x<=40 for x in P)/n,p60=sum(x<=60 for x in P)/n,fail=Fl/n,med=(P[len(P)//2] if P else 999),pall=len(P)/n)
if __name__=='__main__':
    opts={'V4':[(0,0),(1,0),(1,.5),(1,1)],'D2':[(0,0),(1,.5),(1,1)],'ORB15':[(0,0),(.5,0),(1,0),(.5,.5)],'ORB5':[(0,0),(.5,0),(1,0)]}
    res=[]
    for combo in itertools.product(*opts.values()):
        wts=dict(zip(opts.keys(),combo))
        if all(w==(0,0) for w in combo): continue
        for f in (.5,.8):
            Dv=ev(wts,f,20220301,20241231,step=3)
            res.append((Dv['p40']-2*Dv['fail'],wts,f,Dv))
    res.sort(key=lambda r:-r[0])
    pc=lambda x:f"{round(100*x):3d}%"
    print('top portfolios by DEV score (pass<=40d - 2*fail); then TEST')
    for sc,wts,f,Dv in res[:15]:
        Tt=ev(wts,f,20250101,20260601,step=2)
        print(' '.join(f"{k}{v[0]:.1f}/{v[1]:.1f}" for k,v in wts.items()),f"f{f}",'| DEV p10/20/40/60',pc(Dv['p10']),pc(Dv['p20']),pc(Dv['p40']),pc(Dv['p60']),'fail',pc(Dv['fail']),'med',Dv['med'],
              '| TEST',pc(Tt['p10']),pc(Tt['p20']),pc(Tt['p40']),pc(Tt['p60']),'fail',pc(Tt['fail']),'med',Tt['med'],'all',pc(Tt['pall']))
    pickle.dump(res,open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/portfolio.pkl','wb'))
