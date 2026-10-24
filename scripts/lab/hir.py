"""High-R family. Generic: entry at time/trigger, stop small, exit EOD / target kR / trailing. Report R distribution."""
import pickle, sys, collections
sys.path.insert(0,'.'); from core import *
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb'))
D=[d for d,_ in days]; C={d:b[-1][4] for d,b in days}
def trend(d,kind='sma20'):
    i=D.index(d)
    if i<21: return 0
    if kind=='sma20': s=sum(C[x] for x in D[i-20:i])/20; return 1 if C[D[i-1]]>s else -1
    if kind=='r5': return 1 if C[D[i-1]]>C[D[i-6]] else -1
TRD={d:(trend(d,'sma20'),trend(d,'r5')) for d in D}
def rstats(tr,lab):
    if not tr: print(lab,'n=0'); return
    R=[t['Rn'] for t in tr]; W=[r for r in R if r>0]
    gp=sum(W); gl=-sum(r for r in R if r<=0)
    def pf(a,z):
        v=[t['Rn'] for t in tr if a<=t['d']<=z]; g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return (g/l if l else 9.9),len(v)
    dv=pf(20220101,20241231); tv=pf(20250101,20261231)
    eq=pk=dd=0
    for r in R: eq+=r; pk=max(pk,eq); dd=max(dd,pk-eq)
    hold=sum(t['hold'] for t in tr)/len(tr)
    big=sum(r>=5 for r in R)
    print(f"{lab:58s} n{len(tr):4d} wr{100*len(W)/len(R):3.0f}% avgW {sum(W)/max(1,len(W)):4.1f}R maxW {max(R):5.1f}R  >=5R:{big:3d} PF{gp/gl if gl else 9.9:5.2f} DEV{dv[0]:5.2f} TEST{tv[0]:5.2f} avgR{sum(R)/len(R):+.2f} totR{sum(R):+6.0f} DD{dd:5.1f} hold{hold:4.0f}m")
def run_trade(b,i,s,eP,stp,tgtR=None,flat=955,trailR=None):
    r=abs(eP-stp); tgt=eP+s*tgtR*r if tgtR else None
    best=eP; mae=0
    for j in range(i,len(b)):
        tm,o,h,l,c=b[j]
        if (s>0 and l<=stp) or (s<0 and h>=stp): return j,stp-s*SLIP*T,'stop'
        if tgt is not None and ((s>0 and h>=tgt) or (s<0 and l<=tgt)): return j,tgt,'tgt'
        if tm>=flat: return j,c,'close'
        if trailR:
            best=max(best,h) if s>0 else min(best,l)
            if abs(best-eP)>=trailR[0]*r:   # activate trail
                ns=best-s*trailR[1]*r
                stp=max(stp,ns) if s>0 else min(stp,ns)
    return len(b)-1,b[-1][4],'close'
def mk(d,b,i,s,eP,stp,**kw):
    r=abs(eP-stp)
    if r<=0: return None
    j,x,why=run_trade(b,i,s,eP,stp,**kw)
    pts=(x-eP)*s
    return dict(d=d,s=s,r=r,pts=pts,R=pts/r,Rn=(pts-2*COMM/PV)/r,why=why,hold=b[j][0]-b[i-1][0] if i>0 else 0,eT=b[i-1][0] if i>0 else 570)
def orb5(orm=5, stopmode='bar', sfrac=.1, tgtR=None, flt='none', minstop=4, trailR=None):
    """direction of first orm-minute candle; enter at next bar open; stop = opposite extreme of OR candle (bar) or sfrac*ADR"""
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101 or len(b)<300: continue
        n=orm; o=b[0][1]; c=b[n-1][4]; hi=max(x[2] for x in b[:n]); lo=min(x[3] for x in b[:n])
        if c==o: continue
        s=1 if c>o else -1
        t20,t5=TRD[d]
        if flt=='sma20' and s!=t20: continue
        if flt=='r5' and s!=t5: continue
        if flt=='v4' and v4bias(f)!=s: continue
        eP=b[n][1]+s*SLIP*T
        stp=(lo-T if s>0 else hi+T) if stopmode=='bar' else eP-s*sfrac*f['adr']
        if abs(eP-stp)<minstop: stp=eP-s*minstop
        t=mk(d,b,n,s,eP,stp,tgtR=tgtR,trailR=trailR)
        if t: out.append(t)
    return out
if __name__=='__main__':
    for orm in (5,15):
        for sm,sf in (('bar',0),('adr',.05),('adr',.1),('adr',.15)):
            for tg in (None,10,5):
                for flt in ('none','sma20','r5'):
                    rstats(orb5(orm,sm,sf,tg,flt),f"ORB{orm} stop {sm}{sf or ''} tgt {tg or 'EOD'} filter {flt}")
