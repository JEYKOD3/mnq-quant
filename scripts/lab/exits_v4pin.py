"""Exit variants for V4+ and Pinball (asked 2026-10-25 after reviewing Oct 22 trades). 1m management, costs incl."""
import sys; sys.path.insert(0,'.')
from core import *
import pros as P
days=P.days; DB=P.DB; F=P.F; TRD=P.TRD
def walk(b,i0,s,eP,stp0,rule):
    r=abs(eP-stp0); stp=stp0; mfe=0; ext=eP; pb=False; pbx=None; half=None
    tgtR=rule.get('tgt'); cap=rule.get('cap'); t0=b[i0-1][0]
    g5=None  # current 5m bucket (start,o,h,l,c)
    done5=[]
    for j in range(i0,len(b)):
        m,o,h,l,c=b[j]
        if (s>0 and l<=stp) or (s<0 and h>=stp):
            x=stp-s*SLIP*T if stp==stp0 else stp
            p=(x-eP)*s; return (p if half is None else (p+half)/2),'stop',m-t0
        mfe=max(mfe,(h-eP) if s>0 else (eP-l))
        if rule.get('half') and half is None and mfe>=rule['half']*r:
            half=rule['half']*r; stp=eP if (s>0 and stp<eP) or (s<0 and stp>eP) else stp
        tg=eP+s*tgtR*r if tgtR else None
        if tg is not None and ((s>0 and h>=tg) or (s<0 and l<=tg)):
            p=tgtR*r; return (p if half is None else (p+half)/2),'tgt',m-t0
        if rule.get('pb') and pbx is not None and ((s>0 and h>=pbx) or (s<0 and l<=pbx)):
            p=(pbx-eP)*s; return p,'pbx',m-t0
        if m>=955 or (cap and m-t0>=cap):
            p=(c-eP)*s; return (p if half is None else (p+half)/2),'time',m-t0
        if rule.get('be') and mfe>=rule['be']*r: 
            nb=eP+s*1.25
            stp=max(stp,nb) if s>0 else min(stp,nb)
        # 5m buckets for swing trail / pullback rule
        k=570+(m-570)//5*5
        if g5 is None or g5[0]!=k:
            if g5 is not None: done5.append(g5)
            g5=[k,o,h,l,c]
        else: g5[2]=max(g5[2],h); g5[3]=min(g5[3],l); g5[4]=c
        if (m+1)%5==0:
            done5.append(g5); g5=None
            last=done5[-1]
            ext=max(ext,max(x[2] for x in done5)) if s>0 else min(ext,min(x[3] for x in done5))
            if rule.get('trail') and mfe>=rule['trail']*r and len(done5)>=2:
                nv=min(x[3] for x in done5[-2:])-T if s>0 else max(x[2] for x in done5[-2:])+T
                stp=max(stp,nv) if s>0 else min(stp,nv)
            if rule.get('pb') and mfe>=rule['pb']*r and not pb:
                if (s>0 and last[4]<last[1]) or (s<0 and last[4]>last[1]):
                    pb=True; pbx=ext   # take profit when price gets back to the pre-pullback extreme
                    nv=last[3]-T if s>0 else last[2]+T
                    stp=max(stp,nv) if s>0 else min(stp,nv)
    return (b[-1][4]-eP)*s,'close',b[-1][0]-t0
# --- entries
v4=[]
for t in v4_trades(days,F,tf=1,tgtR=2,bias=lambda f: v4bias(f,.4,.4,0)):
    if TRD.get(t['d'],(0,))[0]!=t['side']: continue
    b=DB[t['d']]; i=[k for k,x in enumerate(b) if x[0]==t['eT']][0]
    if (t['side']>0 and b[i][3]<=t['stp']) or (t['side']<0 and b[i][2]>=t['stp']): v4.append((t['d'],b,None,t['side'],t['eP'],t['stp'],0)); continue
    v4.append((t['d'],b,i+1,t['side'],t['eP'],t['stp'],0))
pin=[]
closes=[P.DAILY[x][3] for x in P.D]
for k,d in enumerate(P.D):
    if d<20220101 or k<5: continue
    ch=[closes[j]-closes[j-1] for j in range(k-3,k)]; up=sum(x for x in ch if x>0); dn=-sum(x for x in ch if x<0)
    rs=100 if dn==0 else 100-100/(1+up/dn); s=1 if rs<30 else (-1 if rs>70 else 0)
    if not s or TRD[d][0]!=s: continue
    b=DB[d]; IB=[x for x in b if x[0]<630]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB); f=F.get(d)
    for i,(m,o,h,l,c) in enumerate(b):
        if m<630 or m>900: continue
        lvl=hi+T if s>0 else lo-T
        if (s>0 and h>=lvl) or (s<0 and l<=lvl):
            eP=(max(o,lvl) if s>0 else min(o,lvl))+s*SLIP*T; stp=lo-T if s>0 else hi+T
            stretch=(eP-b[0][1])*s/f['adr'] if f else 0
            pin.append((d,b,i+1 if not((s>0 and l<=stp) or (s<0 and h>=stp)) else None,s,eP,stp,stretch)); break
def test(lab,E,rule,flt=None):
    R=[];P_=[];H=[]
    for d,b,i,s,eP,stp,st in E:
        if flt and not flt(st): continue
        r=abs(eP-stp)
        if i is None: p,why,hm=(stp-s*SLIP*T-eP)*s,'stop',0
        else: p,why,hm=walk(b,i,s,eP,stp,rule)
        net=p-2*COMM/PV; R.append((d,net/r)); P_.append(net); H.append(hm)
    def pf(v):
        g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
    a=[x for d,x in R if d<=20241231]; z=[x for d,x in R if d>20241231]; allr=[x for d,x in R]
    eq=pk=dd=0
    for x in allr: eq+=x; pk=max(pk,eq); dd=max(dd,pk-eq)
    print(f"{lab:38s} n{len(allr):4d} win {100*sum(x>0 for x in allr)/len(allr):3.0f}%  PF {pf(allr):.2f} (22-24 {pf(a):.2f} | 25-26 {pf(z):.2f})  avg {sum(allr)/len(allr):+.2f}R  total {sum(allr):+6.1f}R  maxDD {dd:4.1f}R  hold {sum(H)/len(H):4.0f}m")
rules=[('2R target, else 15:55 (current)',dict(tgt=2)),('1R target',dict(tgt=1)),('1.5R target',dict(tgt=1.5)),('3R target',dict(tgt=3)),
 ('2R + 60 min cap',dict(tgt=2,cap=60)),('2R + 90 min cap',dict(tgt=2,cap=90)),('2R + breakeven after 1R',dict(tgt=2,be=1)),
 ('2R + trail 5m swing after 1R',dict(tgt=2,trail=1)),('no tgt, trail 5m swing after 1R',dict(trail=1)),
 ('half at 1R, half at 2R (BE)',dict(tgt=2,half=1)),('YOUR RULE: exit at prior low after',dict(tgt=2,pb=1)),
 ('  ...same, armed after 0.5R',dict(tgt=2,pb=.5)),('  ...same, armed after 1.5R',dict(tgt=2,pb=1.5))]
print("=== V4+ (with-trend only), 2022 - Oct 2026 ===")
for lab,ru in rules: test(lab,v4,ru)
print("\n=== PINBALL, 2022 - Oct 2026 ===")
prules=[('no target, exit 15:55 (current)',dict())]+[(l,r) for l,r in rules]+[('1R + 60 min cap',dict(tgt=1,cap=60)),('1.5R + 90 min cap',dict(tgt=1.5,cap=90)),('120 min cap only',dict(cap=120))]
for lab,ru in prules: test(lab,pin,ru)
print("\n=== PINBALL entry filter: how stretched is price at entry (move from open in trade dir, x ADR) ===")
for lo_,hi_ in ((-9,.2),(.2,.35),(.35,.5),(.5,9)): test(f"stretch {lo_}..{hi_}",pin,dict(),lambda st:lo_<=st<hi_)
for lab,ru in (('2R target',dict(tgt=2)),('1.5R target',dict(tgt=1.5))):
    test(f"skip if stretch>=0.5, {lab}",pin,ru,lambda st:st<.5)
