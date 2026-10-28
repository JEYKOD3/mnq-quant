# Monte Carlo: running 3 Lucid Flex 50K evals (50% consistency) on the ORB retest signal.
# Trade R values bootstrapped from research/ib/regime_trades.pkl (5y MNQ, 1m-managed ORB retest).
import numpy as np, pandas as pd
rng=np.random.default_rng(7)
d=pd.read_pickle('../ib/regime_trades.pkl'); o=d[d.s=='ORB']
R_all=o.R.values; R_test=o[o.test].R.values
P_TRADE=len(o)/1255          # ORB signals per day (~0.76)
DAYS=60; N=20000

# accounts: (start profit, best day, floor)
START=[(1559,1559,48000+1559-0),(1573,1573,48000+1573),(0,0,48000)]
# floors after today's close: EOD 51,559 -> 49,559 etc.
START=[(1559,1559,49559),(1573,1573,49573),(0,0,48000)]

def run(R, risk, mode):
    passed=np.zeros((N,3),bool); failed=np.zeros((N,3),bool); dpass=np.full((N,3),np.nan)
    for n in range(N):
        prof=[s[0] for s in START]; best=[s[1] for s in START]; floor=[s[2] for s in START]; peak=[50000+s[0] for s in START]
        alive=[True]*3; k=0
        for day in range(DAYS):
            if not any(alive): break
            if rng.random()>P_TRADE: continue
            r=rng.choice(R); k+=1
            for a in range(3):
                if not alive[a]: continue
                if mode=='rotate' and (k%3)!=a: continue
                if mode=='rotate2' and a==2 and k%2==0: continue   # new acct skips every other signal
                pnl=r*risk[a]
                # day cap: never let today's profit move the target
                tgt=max(3000,2*best[a]); need=tgt-prof[a]
                cap=best[a] if best[a]>0 else 1500
                pnl=min(pnl,cap, need if need>0 else pnl)  # take profit early at exact need (bracket set to need)
                prof[a]+=pnl; best[a]=max(best[a],pnl)
                bal=50000+prof[a]
                if bal<=floor[a]: alive[a]=False; failed[n,a]=True; continue
                peak[a]=max(peak[a],bal); floor[a]=min(peak[a]-2000,50100)
                if prof[a]>=3000 and best[a]<=0.5*prof[a]:
                    alive[a]=False; passed[n,a]=True; dpass[n,a]=day+1
    return passed,failed,dpass

res=[]
for label,R in [('all 5y',R_all),('test only',R_test)]:
    for name,risk,mode in [
        ('A copy all, $400 risk',[400,400,400],'copy'),
        ('B copy all, $200 risk',[200,200,200],'copy'),
        ('C copy, $400 old / $200 new',[400,400,200],'copy'),
        ('D rotate signals (1 acct per trade), $400',[400,400,400],'rotate'),
        ('E copy all, $800 risk',[800,800,800],'copy'),
    ]:
        p,f,dp=run(R,risk,mode)
        res.append(dict(data=label,plan=name,
            pass_0002=p[:,0].mean(),pass_0003=p[:,1].mean(),pass_new=p[:,2].mean(),
            avg_funded=p.sum(1).mean(),p_any_fail=f.any(1).mean(),p_all3_fail=f.all(1).mean(),
            p_2plus_funded=(p.sum(1)>=2).mean(),
            med_days_old=np.nanmedian(dp[:,:2]),med_days_new=np.nanmedian(dp[:,2])))
df=pd.DataFrame(res); pd.set_option('display.width',250)
print(f"ORB trades/day {P_TRADE:.2f}, mean R all {R_all.mean():.3f}, test {R_test.mean():.3f}")
print(df.round(3).to_string(index=False))
df.to_csv('multi_acct_results.csv',index=False)
