# Mulham "Math of Winning in Prop Firms" framework applied to Jey's candidate strategies on Lucid Flex 50K.
# 1 Account ($2,000 real room, +3,000 before -2,000)  2 Edge (expectancy, win rate, payoff)  3 Size (pass odds by risk)
# 4 Rules (layers: static DD -> EOD trailing -> daily rules -> 50% consistency)  5 Real return (payouts - all fees)
import pickle, numpy as np, pandas as pd
rng=np.random.default_rng(7)
alld=[l.split('|')[0] for l in open('../../data/raw/mnq_rth_1m.txt')]
pb={}
for d,r in pickle.load(open('../drops/pb618_R_by_day.pkl','rb')): pb.setdefault(d,[]).append(r)
PB=[pb.get(d,[]) for d in alld]
orb=pd.read_pickle('../ib/regime_trades.pkl'); orbR=orb[orb.s=='ORB'].R.values-1/30   # R already net of fee in usd; keep R, small cost haircut
p_orb=len(orbR)/len(alld)
def day_pool(kind):
    if kind=='pullback': return lambda: PB[rng.integers(len(PB))]
    if kind=='orb': return lambda: ([rng.choice(orbR)] if rng.random()<p_orb else [])
    if kind=='orb+pullback': return lambda: (([rng.choice(orbR)] if rng.random()<p_orb else [])+PB[rng.integers(len(PB))])
FEE=130.20
def eval_sim(kind,risk,trailing=True,daily=True,consistency=True,N=20000,maxdays=60):
    draw=day_pool(kind); P=F=0; days=[]
    for _ in range(N):
        bal=peak=50000; floor=48000; best=0
        for day in range(maxdays):
            pnl=0; losses=0
            for k,r in enumerate(draw()[:3]):
                pnl+=r*risk; losses+=r<0
                if daily and (losses>=2 or pnl<=-400): break
                if pnl<=-1200: break            # Lucid soft DLL
            bal+=pnl; prof=bal-50000
            if bal<=floor: F+=1; break
            best=max(best,pnl); peak=max(peak,bal)
            if trailing: floor=50100 if peak>52100 else min(peak-2000,50100)
            if prof>=3000 and (not consistency or best<=0.5*prof): P+=1; days.append(day+1); break
    return P/N,F/N,(np.median(days) if days else np.nan)
def funded_sim(kind,risk,N=10000,maxdays=120):
    # Lucid Flex funded: EOD trailing 2,000 (locks 50,100 above 52,100); payout cycle = 5 days with >= $150 and positive cycle;
    # request 50% of profit, min 500, max 2,000; 90% to trader; MLL -> 50,100 after a request; max 5 payouts. Jey keeps the same day rules.
    draw=day_pool(kind); tot=[]; npay=[]
    for _ in range(N):
        bal=peak=50000; floor=48000; qd=0; cyc0=bal; got=0; n=0
        for day in range(maxdays):
            pnl=0; losses=0
            for r in draw()[:3]:
                pnl+=r*risk; losses+=r<0
                if losses>=2 or pnl<=-400: break
            bal+=pnl
            if bal<=floor: break
            if pnl>=150: qd+=1
            peak=max(peak,bal); floor=max(floor,50100 if peak>52100 else min(peak-2000,50100))
            prof=bal-50000
            if qd>=5 and bal>cyc0 and prof>0:
                req=min(0.5*prof,2000)
                if req>=500 and bal-req>50100+400:      # keep at least one bad day of cushion above the locked floor
                    got+=0.9*req; n+=1; bal-=req; floor=50100; qd=0; cyc0=bal
                    if n>=5: break
        tot.append(got); npay.append(n)
    return np.mean(tot), np.mean(np.array(npay)>0), np.mean(npay)
def edge(R):
    R=np.asarray(R); w=R[R>0]; l=R[R<=0]
    return dict(trades=len(R),win=round(len(w)/len(R),3),avg_win_R=round(w.mean(),2),avg_loss_R=round(l.mean(),2),expectancy_R=round(R.mean(),3),
                PF=round(w.sum()/-l.sum(),2),p4_losses_in_row=round((1-len(w)/len(R))**4,3))
def max_streak(R,n=120,N=5000):
    out=[]
    for _ in range(N):
        s=rng.choice(R,n); m=c=0
        for r in s: c=c+1 if r<=0 else 0; m=max(m,c)
        out.append(m)
    return int(np.median(out)),int(np.percentile(out,90))
allPB=np.concatenate([np.array(x) for x in PB if x])
print('== 2. EDGE ==')
for name,R in [('Pullback 61.8',allPB),('ORB retest',orbR)]:
    e=edge(R); ms=max_streak(R); print(name,e,'| longest losing streak in 120 trades: median',ms[0],'90th pct',ms[1])
# Jey Oct 30 (from Tradovate export): 31 trades, 24 wins avg $124, 7 losses avg -$659 (incl. 1 scratch), commissions ~$408
print("Jey Oct 30 manual: win 77%, avg win $124, avg loss $659 -> expectancy per trade",round(0.774*124-0.226*659,1),'$ before ~$13 commissions/trade')
print('\n== 3. SIZE: pass odds by risk per trade (60 trading days, all Lucid rules + Jey day rules) ==')
rows=[]
for kind in ['pullback','orb','orb+pullback']:
    for risk in (150,200,250,300,400,500):
        p,f,md=eval_sim(kind,risk); rows.append(dict(strategy=kind,risk=risk,pass_pct=round(100*p,1),fail_pct=round(100*f,1),unfinished=round(100*(1-p-f),1),median_days=md))
S=pd.DataFrame(rows); print(S.to_string(index=False))
print('\n== 4. RULES: how each layer changes the pass rate (orb+pullback, $300) ==')
for lab,kw in [('only a static -2,000 floor',dict(trailing=False,daily=False,consistency=False)),('+ EOD trailing drawdown',dict(trailing=True,daily=False,consistency=False)),
               ('+ Jey day rules (2 losses / -$400)',dict(trailing=True,daily=True,consistency=False)),('+ 50% consistency (= Lucid Flex)',dict(trailing=True,daily=True,consistency=True))]:
    p,f,md=eval_sim('orb+pullback',300,**kw); print(f'  {lab:40s} pass {100*p:5.1f}%  fail {100*f:5.1f}%  median days {md}')
print('\n== 5. REAL RETURN per eval bought (fee $130.20) ==')
for kind in ['pullback','orb+pullback']:
    for risk in (200,300,400):
        p,f,md=eval_sim(kind,risk,N=8000)
        pay,anypay,npay=funded_sim(kind,risk,N=4000)
        print(f'  {kind:13s} ${risk}: pass {100*p:4.1f}% | funded acct: avg paid to you ${pay:,.0f}, gets >=1 payout {100*anypay:.0f}%, avg payouts {npay:.1f} | per eval bought: ${p*pay-FEE:,.0f}')
S.to_csv('size_table.csv',index=False)
