"""Overnight/London setups on MNQ ETH 5m. Session line = 18:00 (prev day) .. 16:55. Times ET (minutes since midnight; overnight bars have m>=1080)."""
import sys, collections; sys.path.insert(0,'.')
from core import T, SLIP, COMM, PV
from hir import TRD
S=[]
for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
    p=ln.strip().split('|')
    if len(p)<50: continue
    b=[]
    for x in p[1:]:
        t,o,h,l,c=x.split(','); t=int(t); m=t//100*60+t%100
        b.append((m,int(o)/4,int(h)/4,int(l)/4,int(c)/4))
    S.append((int(p[0]),b))
def seq(m): return m-1080 if m>=1080 else m+360   # minutes since 18:00
def run(entry_m, rng=(1080,180), stopk='range', sfrac=.15, exit_m=570, tgtR=None, flt='none', minR=4, adr_days=10):
    out=[]; rngs=[]
    for k,(d,b) in enumerate(S):
        if d<20220101: rngs.append(max(x[2] for x in b)-min(x[3] for x in b)); continue
        adr=sum(rngs[-adr_days:])/adr_days if len(rngs)>=adr_days else None
        rngs.append(max(x[2] for x in b)-min(x[3] for x in b))
        if not adr: continue
        A=[x for x in b if seq(rng[0])<=seq(x[0])<seq(rng[1])]
        if len(A)<10: continue
        hi=max(x[2] for x in A); lo=min(x[3] for x in A)
        idx=[i for i,x in enumerate(b) if seq(x[0])>=seq(rng[1])]
        if not idx: continue
        tr=TRD.get(d,(0,0))[0]
        pos=None
        for i in idx:
            m,o,h,l,c=b[i]
            if seq(m)>=seq(exit_m):
                if pos: s,eP,stp,tgt=pos; out.append(((c-eP)*s,abs(eP-stp),'time',d))
                break
            if pos:
                s,eP,stp,tgt=pos
                if (s>0 and l<=stp) or (s<0 and h>=stp): out.append(((stp-s*SLIP*T-eP)*s,abs(eP-stp),'stop',d)); pos=None; break
                if tgt and ((s>0 and h>=tgt) or (s<0 and l<=tgt)): out.append(((tgt-eP)*s,abs(eP-stp),'tgt',d)); pos=None; break
                continue
            if seq(m)>seq(entry_m): continue
            for s,lvl in ((1,hi),(-1,lo)):
                if flt=='trend' and s!=tr: continue
                if (s>0 and h>lvl) or (s<0 and l<lvl):
                    eP=(max(o,lvl+T) if s>0 else min(o,lvl-T))+s*SLIP*T
                    stp=(lo-T if s>0 else hi+T) if stopk=='range' else eP-s*sfrac*adr
                    if abs(eP-stp)<minR: stp=eP-s*minR
                    pos=(s,eP,stp,(eP+s*tgtR*abs(eP-stp)) if tgtR else None)
                    if (s>0 and l<=stp) or (s<0 and h>=stp): out.append(((stp-s*SLIP*T-eP)*s,abs(eP-stp),'stop',d)); pos=None
                    break
            if pos is None and out and out[-1][3]==d: break
    return out
def st(o,lab):
    if not o: print(lab,'n0'); return
    R=[(p-2*COMM/PV)/r for p,r,w,d in o]
    def pf(a,z):
        v=[(p-2*COMM/PV)/r for p,r,w,d in o if a<=d<=z]; g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
    eq=pk=dd=0
    for x in R: eq+=x; pk=max(pk,eq); dd=max(dd,pk-eq)
    yrs=' '.join(f"{y%100}:{pf(y*10000,y*10000+1231):.2f}" for y in range(2022,2027))
    print(f"{lab:60s} n{len(o):4d} wr{100*sum(x>0 for x in R)/len(R):3.0f}% PF{pf(0,99999999):5.2f} DEV{pf(20220101,20241231):5.2f} TEST{pf(20250101,20261231):5.2f} avgR{sum(R)/len(R):+.2f} DD{dd:5.1f} | {yrs}")
if __name__=='__main__':
    # Asia range 18:00-03:00, London breakout 03:00-06:00, exit 09:25
    for flt in ('none','trend'):
        for sk,sf in (('range',0),('adr',.1),('adr',.2)):
            for tg in (None,1,2):
                st(run(360,(1080,180),sk,sf,565,tg,flt),f"London BO: asia range, entry<=6:00, stop {sk}{sf or ''} tgt {tg} exit 9:25 {flt}")
    # overnight range 18:00-09:30 -> break after 09:30 handled by RTH strategies; test pre-market 8:00-9:25 break of 3:00-8:00 range
    for flt in ('none','trend'):
        for sk,sf in (('range',0),('adr',.1)):
            st(run(565,(180,480),sk,sf,630,None,flt),f"Pre-mkt BO: 3:00-8:00 range, entry 8:00-9:25, stop {sk}{sf or ''} exit 10:30 {flt}")
            st(run(565,(180,480),sk,sf,565,None,flt),f"Pre-mkt BO: 3:00-8:00 range, entry 8:00-9:25, stop {sk}{sf or ''} exit 9:25 {flt}")
