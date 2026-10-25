"""Step 0b: his reversion trade with his entry signals, one account, NY 9:30-11:00.
Fair = 9:30 open (or 9:29 close). Signal toward fair: displacement (body > prev body, close beyond prev wick, prev opposite colour)
or break of structure (close beyond latest unbroken 3-candle swing). Entry next bar open; stop 25, target 38 (or fair price);
room rule: |entry-fair| >= 0.8*38. Max 4 trades/session, stop after 3 losses in a row, one position at a time. Costs: 2.37/side + 1 tick."""
import sys, collections
sys.path.insert(0,'/home/claude/mnq-quant/scripts/lab')
from core import load
days=load(); T=.25; PV=2.0; COMM=2.37
eth={}
for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
    p=ln.strip().split('|')
    if len(p)<50: continue
    for x in p[1:]:
        t,o,h,l,c=x.split(',')
        if t=='925': eth[int(p[0])]=int(c)/4
def run(fair='open', sig='both', stop=25, tgt=38, room=.8, maxtr=4, maxloss=3, t1=660, tgt_mode='fixed'):
    tr=[]
    for d,b in days:
        if d<20220101 or b[0][0]!=570: continue
        F=b[0][1] if fair=='open' else eth.get(d)
        if F is None: continue
        n=0; losses=0; i=2; sw_hi=[]; sw_lo=[]
        while i<len(b)-1:
            m,o,h,l,c=b[i]
            if m>=t1 or n>=maxtr or losses>=maxloss: break
            # confirm swing at i-1
            if b[i-1][3]<b[i-2][3] and b[i-1][3]<b[i][3]: sw_lo.append(b[i-1][3])
            if b[i-1][2]>b[i-2][2] and b[i-1][2]>b[i][2]: sw_hi.append(b[i-1][2])
            po,ph,pl,pc=b[i-1][1],b[i-1][2],b[i-1][3],b[i-1][4]
            s=0
            if c>F and c<o:  # above fair, short signal
                disp = abs(c-o)>abs(pc-po) and c<pl and pc>po
                bos = bool(sw_lo) and c<sw_lo[-1] and b[i-1][4]>=sw_lo[-1]
                if (sig in('both','disp') and disp) or (sig in('both','bos') and bos): s=-1
            elif c<F and c>o:
                disp = abs(c-o)>abs(pc-po) and c>ph and pc<po
                bos = bool(sw_hi) and c>sw_hi[-1] and b[i-1][4]<=sw_hi[-1]
                if (sig in('both','disp') and disp) or (sig in('both','bos') and bos): s=1
            if s:
                e=b[i+1][1]+s*T; dist=(F-e)*s
                tg = tgt if tgt_mode=='fixed' else dist
                if dist>=room*tgt and tg>0:
                    stp=e-s*stop; tp=e+s*tg; res=None
                    for j in range(i+1,len(b)):
                        mj,oj,hj,lj,cj=b[j]
                        if (s>0 and lj<=stp) or (s<0 and hj>=stp): res=((stp-s*T)-e)*s; break
                        if (s>0 and hj>=tp) or (s<0 and lj<=tp): res=tg; break
                        if mj>=955: res=(cj-e)*s; break
                    if res is None: res=(b[-1][4]-e)*s
                    net=res*PV-2*COMM
                    tr.append((d,s,net,res)); n+=1
                    losses = losses+1 if net<0 else 0
                    i=j+1; sw_hi=[]; sw_lo=[]; continue
            i+=1
    return tr
def rep(lab,tr):
    def pf(v):
        g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
    a=[x[2] for x in tr if x[0]<=20241231]; z=[x[2] for x in tr if x[0]>20241231]; al=[x[2] for x in tr]
    w=sum(x>0 for x in al)/len(al)
    yrs=' '.join(f"{y%100}:{pf([x[2] for x in tr if x[0]//10000==y]):.2f}" for y in range(2022,2027))
    print(f"{lab:46s} trades {len(al):5d} ({len(al)/4.8:4.0f}/yr) win {w:4.0%}  PF {pf(al):.2f} (22-24 {pf(a):.2f} | 25-26 {pf(z):.2f})  $ per MNQ {sum(al):+7.0f} | {yrs}")
print("Break-even win rate for 38/25 after costs is about 41%.\n")
for fair in ('open','c929'):
    for sig in ('both','disp','bos'):
        rep(f"fair={fair:4s} signal={sig:4s} 25/38", run(fair,sig))
rep("fair=open both, target = fair price, stop 25", run('open','both',tgt_mode='fair'))
rep("fair=open both, 50/76 (his wider variant)", run('open','both',stop=50,tgt=76))
rep("fair=open both, 25/38, no loss/trade limits", run('open','both',maxtr=99,maxloss=99))
