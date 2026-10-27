import gzip, numpy as np
TICK=.25; SLIP=.25
S=[]
for line in gzip.open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt.gz','rt'):
    p=line.strip().split('|'); a=np.array([list(map(int,x.split(','))) for x in p[1:]],float)
    S.append((p[0],a[:,0].astype(int),a[:,1]/4,a[:,2]/4,a[:,3]/4,a[:,4]/4))
def run(start_hhmm, win_min=180, tgt=2.0, body=0.5):
    out=[]; split=int(len(S)*.7)
    for k,(d,hm,o,h,l,c) in enumerate(S):
        # session order: 1800..2359 then 0000..1659 ; build minutes since 18:00
        ms=np.where(hm>=1800,(hm//100-18)*60+hm%100,(hm//100+6)*60+hm%100)
        st=(start_hhmm//100-18)*60+start_hhmm%100 if start_hhmm>=1800 else (start_hhmm//100+6)*60+start_hhmm%100
        idx=np.where((ms>=st)&(ms<st+15))[0]
        if len(idx)<3: continue
        ORH=h[idx].max(); ORL=l[idx].min(); W=ORH-ORL
        if W<=0: continue
        arm=0; tch=False; j0=idx[-1]+1
        for j in range(j0,len(c)):
            if ms[j]>=st+win_min: break
            if arm==0:
                if c[j]>ORH: arm=1; tch=False
                elif c[j]<ORL: arm=-1; tch=False
                continue
            if (arm>0 and c[j]<ORH) or (arm<0 and c[j]>ORL): arm=0; continue
            if (arm>0 and l[j]<=ORH+.1*W) or (arm<0 and h[j]>=ORL-.1*W): tch=True
            rg=h[j]-l[j]; strong=rg>0 and abs(c[j]-o[j])>=body*rg and ((c[j]>o[j]) if arm>0 else (c[j]<o[j]))
            if tch and strong:
                side=arm; e=c[j]; s=ORL-TICK if side>0 else ORH+TICK; r=abs(e-s)
                if r<4: break
                sL=s; tT=e+tgt*side*r; lk=False; x=None
                for i in range(j+1,len(c)):
                    if (l[i]<=sL if side>0 else h[i]>=sL): x=sL-SLIP*side; break
                    if (h[i]>=tT if side>0 else l[i]<=tT): x=tT; break
                    if not lk and ((h[i]-e) if side>0 else (e-l[i]))>=r: lk=True; sL=e+side*r
                    if ms[i]>=st+win_min+240: x=c[i]; break
                if x is None: x=c[-1]
                pts=(x-e)*side; out.append((pts/r, pts*2-1, k>=split, d[:4], r)); break
    a=np.array([x[:3] for x in out],float); y=np.array([x[3] for x in out]); R,U,t=a[:,0],a[:,1],a[:,2]==1
    pf=lambda u: u[u>0].sum()/max(-u[u<=0].sum(),1e-9)
    return f"n{len(R)} win{(U>0).mean()*100:.0f}% avgR{R.mean():+.3f} PF{pf(U):.2f} train{pf(U[~t]):.2f} test{pf(U[t]):.2f} $/day{U.sum()/len(S):+.1f} medRisk{np.median([x[4] for x in out]):.0f}pts | "+' '.join(f"{pf(U[y==yy]):.2f}" for yy in ['2022','2023','2024','2025','2026'])
for nm,hhmm in [('Globex 18:00',1800),('Tokyo 20:00',2000),('London 03:00',300),('NY 09:30',930)]:
    print(f"{nm:13s}", run(hhmm))
