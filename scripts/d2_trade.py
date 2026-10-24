import json, collections
L=[l for l in open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/v4live/data/raw/mnq_rth_5m.txt').read().split('\n') if l]
feat=json.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/v4live/scripts/dayfeat.json'))
def v4(f):
    if not f or f['pdRel']>1.2: return 0
    G=abs(f['gap'])>=.6; D=abs(f['orDir'])>=.6
    if not(G or D): return 0
    return (1 if f['gap']>0 else -1) if G else (1 if f['orDir']>0 else -1)
days=[]
for ln in L:
    p=ln.split('|'); d=p[0]; b=[]
    for x in p[1:]:
        t,o,h,l,c=x.split(','); t=int(t); b.append((t,int(o)/4,int(h)/4,int(l)/4,int(c)/4))
    days.append((d,b))
COST=3.0; dr=[]
def run(th=0.4, at=1030, stopMode='open', tR=None, hold=None, onlyOff=False, minStop=10, maxStop=None, log=None):
    out=[]; dr=[]
    for k,(d,b) in enumerate(days):
        if k==0 or len(b)<70 or b[0][0]!=930: 
            if k>0 and days[k-1][1]: pass
            continue
        pb=days[k-1][1]; pdh=max(x[2] for x in pb); pdl=min(x[3] for x in pb)
        adr = sum(dr[-10:])/10 if len(dr)>=10 else pdh-pdl
        dr.append(pdh-pdl)
        if d<'20220101': continue
        if onlyOff and v4(feat.get(d)): continue
        o=b[0][1]
        idx=[i for i,x in enumerate(b) if x[0]+5==at or (x[0]%100==55 and x[0]+45==at)]
        if not idx: continue
        i=idx[0]; e=b[i][4]; mv=(e-o)/adr
        if abs(mv)<th: continue
        s=1 if mv>0 else -1
        if stopMode=='open': stp=o
        elif stopMode=='half': stp=e-s*abs(e-o)/2
        else: stp=e-s*stopMode*adr
        r=abs(e-stp)
        if r<minStop: stp=e-s*minStop; r=minStop
        if maxStop and r>maxStop: continue
        tp = e+s*tR*r if tR else None
        x=None; why='close'
        for j in range(i+1,len(b)):
            t,oo,h,l,c=b[j]
            if (s==1 and l<=stp) or (s==-1 and h>=stp): x=stp; why='stop'; break
            if tp and ((s==1 and h>=tp) or (s==-1 and l<=tp)): x=tp; why='tgt'; break
            if hold and (j-i)*5>=hold: x=c; why='time'; break
            if t>=1555: x=c; break
        if x is None: x=b[-1][4]
        pts=(x-e)*s-COST
        out.append((d,pts,r,why))
        if log is not None: log.append((d,s,e,stp,tp,x,why,pts,r))
    return out
def st(o,lab):
    if not o: return lab+' n=0'
    yrs=collections.defaultdict(list)
    for d,p,r,w in o: yrs[d[:4]].append(p/r)
    pf=lambda v:(sum(x for x in v if x>0)/-sum(x for x in v if x<=0)) if any(x<=0 for x in v) else 9.9
    R=[p/r for d,p,r,w in o]
    eq=0;pk=0;dd=0
    for x in R: eq+=x; pk=max(pk,eq); dd=max(dd,pk-eq)
    ex=collections.Counter(w for *_,w in o)
    return f"{lab:46s} n={len(o):4d} ({len(o)/4.8:3.0f}/yr) win {100*sum(x>0 for x in R)/len(R):3.0f}% PF {pf(R):.2f} avgR {sum(R)/len(R):+.2f} totR {sum(R):+6.1f} maxDD {dd:4.1f}R risk {sum(r for *_,r,_ in o)/len(o):4.0f}pt | "+' '.join(f"{y[2:]}:{pf(v):.2f}" for y,v in sorted(yrs.items()))+f" | {dict(ex)}"
if __name__=='__main__':
    for off in (False,True):
        print('\n=== ', 'ONLY V4-OFF DAYS' if off else 'ALL DAYS')
        for th in (0.3,0.4,0.5):
            for sm,tR,hold in (('open',None,None),('open',1,None),('open',1.5,None),('open',1,60),('open',None,60),('half',None,None),('half',1.5,60),(0.25,None,None)):
                print(st(run(th,1030,sm,tR,hold,off),f"th{th} stop={sm} tgt={tR}R hold={hold}"))
