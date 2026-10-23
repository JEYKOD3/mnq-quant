"""Inside-bar box (friend) with STRUCTURE stop and S/R take profit. 5m MNQ.
stop: beyond the nearest swing low/high below/above the box (pivot 3/3 of last 60 bars, or PDL/PDH/OR), + buffer; cap maxStop.
target: nearest S/R zone in trade direction (swing / PDH-PDL-PDC / OR edges) with room >= minRoomR*R; else next; else 1R. cost 3pt."""
import sys,collections,json
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
feat=json.load(open('data/features/day_features.json')); COST=3.0; tick=.25
def v4(d):
    f=feat.get(d)
    if not f or f['pdRel']>1.2: return 0
    G=abs(f['gap'])>=.6; D=abs(f['orDir'])>=.6
    if not(G or D): return 0
    return (1 if f['gap']>0 else -1) if G else (1 if f['orDir']>0 else -1)
def agg(bars,n): return [(bars[i][0],bars[i][1],max(b[2] for b in bars[i:i+n]),min(b[3] for b in bars[i:i+n]),bars[i+n-1][4]) for i in range(0,len(bars)-n+1,n)]
PD={}
prev=None
for d,b in days:
    PD[d]=prev; prev=(max(x[2] for x in b),min(x[3] for x in b),b[-1][4])
def run(d,bars,tf=5,stopMode='struct',bufPts=3,maxStop=80,minStop=10,tgtMode='sr',minRoomR=0.8,maxRoomR=3.0,trend='ema',first=585,last=870,flat=955,maxTr=3,maxWait=6,log=None):
    B=agg(bars,tf); n=len(B); k=2/22; e=None; ema=[]
    for b in B: e=b[4] if e is None else e+k*(b[4]-e); ema.append(e)
    bias=v4(d) if trend=='v4' else 0
    if trend=='v4' and bias==0: return []
    pd=PD[d]; orb=B[:3]; orh=max(x[2] for x in orb); orl=min(x[3] for x in orb)
    swH=[]; swL=[]; trades=[]; pos=0; box=None; ntr=0
    tm=lambda i: f"{(570+i*5)//60}:{(570+i*5)%60:02d}"
    for i in range(2,n):
        t,o,h,l,c=B[i]
        if i>=6:
            j=i-3
            if B[j][2]==max(x[2] for x in B[j-3:j+4]): swH.append(B[j][2])
            if B[j][3]==min(x[3] for x in B[j-3:j+4]): swL.append(B[j][3])
        if pos!=0:
            why=None
            if pos==1:
                if l<=stp: why=('stop',stp)
                elif h>=tgt: why=('target',tgt)
            else:
                if h>=stp: why=('stop',stp)
                elif l<=tgt: why=('target',tgt)
            if not why and t>=flat: why=('close',c)
            if why:
                x=why[1]; p=(x-entry if pos==1 else entry-x)-COST; trades.append(p)
                if log is not None: log.append(f"   {'LONG ' if pos==1 else 'SHORT'} {tm(ei)} @{entry} stop {stp} ({stopWhy}) tgt {tgt} ({tgtWhy}) R={R:.0f} -> {tm(i)} {why[0]} {p:+.0f}")
                pos=0
            if pos!=0: continue
        if t<first or t>last or ntr>=maxTr: continue
        m=B[i-1]; ib=B[i]
        if ib[2]<=m[2] and ib[3]>=m[3] and (m[2]-m[3])>0:
            if trend=='ema': dirn = 1 if (ema[i]>ema[i-6] and c>ema[i]) else (-1 if (ema[i]<ema[i-6] and c<ema[i]) else 0)
            else: dirn=bias
            if dirn!=0: box=(m[2],m[3],dirn,i)
            continue
        if box:
            hi,lo,dirn,bi=box
            if i-bi>maxWait: box=None; continue
            go = (dirn==1 and min(o,c)>hi) or (dirn==-1 and max(o,c)<lo)
            bad = (dirn==1 and max(o,c)<lo) or (dirn==-1 and min(o,c)>hi)
            if bad: box=None; continue
            if not go: continue
            box=None; entry=c; s=dirn
            # ---- stop
            if stopMode=='box': stp=(lo-tick) if s==1 else (hi+tick); stopWhy='box'
            else:
                cands=[]
                if s==1:
                    cands=[('swing',x) for x in swL if x<lo]+([('PDL',pd[1])] if pd and pd[1]<lo else [])+[('ORL',orl)] if orl<lo else [('swing',x) for x in swL if x<lo]+([('PDL',pd[1])] if pd and pd[1]<lo else [])
                    cands=[cd for cd in cands if entry-cd[1]<=maxStop]
                    if cands: stopWhy,lv=max(cands,key=lambda z:z[1]); stp=lv-bufPts
                    else: stp=lo-bufPts; stopWhy='box'
                else:
                    cands=[('swing',x) for x in swH if x>hi]+([('PDH',pd[0])] if pd and pd[0]>hi else [])+([('ORH',orh)] if orh>hi else [])
                    cands=[cd for cd in cands if cd[1]-entry<=maxStop]
                    if cands: stopWhy,lv=min(cands,key=lambda z:z[1]); stp=lv+bufPts
                    else: stp=hi+bufPts; stopWhy='box'
            R=abs(entry-stp)
            if R<minStop: stp=entry-s*minStop; R=minStop
            if R>maxStop: continue
            # ---- target
            if tgtMode=='r1': tgt=entry+s*R; tgtWhy='1R'
            else:
                if s==1: lv=sorted(set([x for x in swH if x>entry]+([pd[0]] if pd and pd[0]>entry else [])+([pd[2]] if pd and pd[2]>entry else [])+([orh] if orh>entry else [])))
                else: lv=sorted(set([x for x in swL if x<entry]+([pd[1]] if pd and pd[1]<entry else [])+([pd[2]] if pd and pd[2]<entry else [])+([orl] if orl<entry else [])),reverse=True)
                pick=None
                for z in lv:
                    room=abs(z-entry)
                    if room>=minRoomR*R and room<=maxRoomR*R: pick=z; break
                if pick is None: tgt=entry+s*R; tgtWhy='1R(no zone)'
                else: tgt=pick-s*tick; tgtWhy='zone'
            pos=s; ei=i; ntr+=1
            if (s==1 and l<=stp) or (s==-1 and h>=stp): trades.append(-R-COST); pos=0
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(d,bars,**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr: y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0)
    print(f'{name:48s} net {tot:+7.0f}pt n={n:5d} win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y[2:]}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
if __name__=='__main__':
    rep('box stop, 1R (friend baseline)',stopMode='box',tgtMode='r1')
    rep('struct stop (swing/PDL/OR), 1R',tgtMode='r1')
    rep('struct stop, S/R target >=0.8R',)
    rep('struct stop, S/R target >=1.0R',minRoomR=1.0)
    rep('struct stop, S/R target >=0.6R (permissive)',minRoomR=0.6)
    rep('struct stop cap 50, S/R >=0.8R',maxStop=50)
    rep('struct stop, S/R >=0.8R, V4 direction only',trend='v4')
    rep('struct stop, S/R >=0.8R, first hour only',last=630)
    rep('struct stop, S/R >=0.8R, 1 trade/day',maxTr=1)
    rep('box stop, S/R target >=0.8R',stopMode='box')
