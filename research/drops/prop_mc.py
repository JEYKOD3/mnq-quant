# Lucid Flex 50K eval Monte Carlo with the Pullback 61.8 trade results (5y RTH, R per trade incl. 1 pt cost).
# Rules: start 50,000; EOD trailing floor = peak EOD - 2,000 (locks at 50,100 once an EOD close > 52,100); target +3,000;
# 50% consistency (best day <= 50% of total profit); DLL 1,200 (soft). Jey's day rules: stop after 2 losses or -$400; optional profit stop.
import pickle, numpy as np, pandas as pd
rows=pickle.load(open('pb618_R_by_day.pkl','rb'))
days={}
for d,r in rows: days.setdefault(d,[]).append(r)
alld=[l.split('|')[0] for l in open('../../data/raw/mnq_rth_1m.txt')]
pool=[days.get(d,[]) for d in alld]
rng=np.random.default_rng(1)
def run(risk,profit_stop=None,max_trades=3,N=20000,maxdays=60):
    passed=failed=0; dpass=[]
    for _ in range(N):
        bal=50000; peak=50000; floor=48000; best=0; prof=0
        for day in range(maxdays):
            trades=pool[rng.integers(len(pool))]; pnl=0; losses=0
            for k,r in enumerate(trades[:max_trades]):
                pnl+=r*risk
                if r<0: losses+=1
                if losses>=2 or pnl<=-400 or pnl<=-1200: break
                if profit_stop and pnl>=profit_stop: break
            bal+=pnl; prof=bal-50000
            if bal<=floor: failed+=1; break
            best=max(best,pnl)
            if bal>peak: peak=bal
            floor=min(peak-2000,50100) if peak<=52100 else 50100
            if prof>=3000 and best<=0.5*prof: passed+=1; dpass.append(day+1); break
    return passed/N, failed/N, (np.median(dpass) if dpass else np.nan)
out=[]
for risk in (100,150,200,300,400,500,750):
    for ps in (None,800,1200):
        p,f,md=run(risk,ps)
        out.append(dict(risk_per_trade=risk,profit_stop=ps or 'none',pass_pct=round(p*100,1),fail_pct=round(f*100,1),still_going_after_60d=round((1-p-f)*100,1),median_days_to_pass=md))
R=pd.DataFrame(out); pd.set_option('display.width',200); print(R.to_string(index=False)); R.to_csv('prop_mc.csv',index=False)
