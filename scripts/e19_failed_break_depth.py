"""E19 vs E6: failed breakout of PDH/PDL/OR15 edges, split by poke depth. 1m bars. Poke = bar high > level; failure = within K=3 bars a bar closes back below level. Entry at that close. Stop = poke extreme + 1tk (min 8pt). Target = max(1R, minTgt). One trade per level-side per day, max 3/day. 10:00-14:30. cost 3."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
COST=3.0; tick=.25
prev=None
def run(bars,levels,buckets,tgtR=1.0,minTgt=25,K=3,first=600,last=870,flat=955,maxTr=3,maxStop=60):
    trades=[]; pos=0; used=set(); n=0
    for i,(t,o,h,l,c) in enumerate(bars):
        if pos!=0:
            if pos==1:
                if l<=stp: trades.append((stp-entry-COST,dep)); pos=0
                elif h>=tgt: trades.append((tgt-entry-COST,dep)); pos=0
            else:
                if h>=stp: trades.append((entry-stp-COST,dep)); pos=0
                elif l<=tgt: trades.append((entry-tgt-COST,dep)); pos=0
            if pos!=0 and t>=flat: trades.append(((c-entry if pos==1 else entry-c)-COST,dep)); pos=0
            if pos!=0: continue
        if t<first or t>last or n>=maxTr: continue
        for name,lv in levels.items():
            if lv is None or (name,'up') in used and (name,'dn') in used: continue
            # poke above level then close back below within K bars
            if (name,'up') not in used and h>lv and c<lv:
                # depth = max high over last K bars incl this one above lv
                pk=max(b[2] for b in bars[max(0,i-K+1):i+1]); dep=(pk-lv)
                if dep>0 and dep<=45:
                    e=c; stp=pk+tick; R=stp-e
                    if R<8: stp=e+8; R=8
                    if R<=maxStop:
                        pos=-1; entry=e; tgt=e-max(tgtR*R,minTgt); used.add((name,'up')); n+=1; break
            if (name,'dn') not in used and l<lv and c>lv:
                pk=min(b[3] for b in bars[max(0,i-K+1):i+1]); dep=(lv-pk)
                if dep>0 and dep<=45:
                    e=c; stp=pk-tick; R=e-stp
                    if R<8: stp=e-8; R=8
                    if R<=maxStop:
                        pos=1; entry=e; tgt=e+max(tgtR*R,minTgt); used.add((name,'dn')); n+=1; break
    return trades
def rep(name,**kw):
    global prev
    prev=None; agg=collections.defaultdict(lambda:[0,0,0,0]); byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        or15=[b for b in bars if b[0]<585]
        levels={'PDH':prev[0] if prev else None,'PDL':prev[1] if prev else None,'ORH':max(b[2] for b in or15),'ORL':min(b[3] for b in or15)}
        tr=run(bars,levels,None,**kw)
        for p,dep in tr:
            b = '<=0.5pt' if dep<=0.5 else ('<=2pt' if dep<=2 else ('<=10pt' if dep<=10 else '>10pt'))
            a=agg[b]; a[0]+=p; a[1]+=1; a[2]+=(p>0); a[3]+= (p if p>0 else 0)
            agg['ALL'][0]+=p; agg['ALL'][1]+=1; agg['ALL'][2]+=(p>0); agg['ALL'][3]+=(p if p>0 else 0)
        p=sum(x[0] for x in tr)
        if tr: y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0)
        prev=(max(b[2] for b in bars),min(b[3] for b in bars))
    print(name)
    for b in ['<=0.5pt','<=2pt','<=10pt','>10pt','ALL']:
        a=agg[b]; gl=a[3]-a[0]
        print(f'   poke {b:8s} n={a[1]:4d} win {a[2]/max(a[1],1):.0%} PF {a[3]/max(gl,1):.2f} net {a[0]:+.0f}pt')
    print('   by year:',' '.join(f"{y[2:]}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
rep('E19 1R min25, PDH/PDL/OR15, K=3')
rep('E19 2R min25',tgtR=2)
rep('E19 1R min25 K=1 (same-bar failure)',K=1)
rep('E19 1R no min target',minTgt=0)
