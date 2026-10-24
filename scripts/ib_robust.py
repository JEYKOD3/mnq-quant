import sys; sys.argv=['x']
exec(open('/home/claude/mnq-quant/scripts/ib_converged.py').read().split("if __name__")[0])
import collections
B=dict(trig='ib',loc=True,tgt='2r')
print('BASE 15m', stats(run(15,**B)))
print('\n-- timeframe neighbours'); 
for tf in (10,20,30): print(f'{tf}m', stats(run(tf,**B)))
print('\n-- cost'); 
for cst in (2,4,5,6):
    COST=cst; print(f'cost {cst}', stats(run(15,**B)))
COST=3.0
print('\n-- target R')
for t in (1.0,1.5,2.5,3.0): print('tR',t, stats(run(15,tR=t,**B)))
print('\n-- location threshold')
for x in (0.5,0.75,1.25,1.5): print('locR',x, stats(run(15,locR=x,**B)))
print('\n-- EMA length / slope')
for e_ in (10,15,30,50): print('ema',e_, stats(run(15,emaL=e_,**B)))
for sl_ in (3,10): print('slope',sl_, stats(run(15,slope=sl_,**B)))
print('\n-- stop buffer')
for b in (0.25,3,5): print('buf',b, stats(run(15,buf=b,**B)))
print('\n-- max wait bars')
for w in (2,4,8): print('wait',w, stats(run(15,maxwait=w,**B)))
o=run(15,**B)
print('\n-- by entry hour / direction')
log=[]; run(15,log=log,**B)
h=collections.defaultdict(list)
for d,et,pos,ent,stp,tp,hit,pts in log: h[et//60].append((d,et,pts,0))
for k in sorted(h): print(f'{k}h', stats(h[k]))
dd=collections.defaultdict(list)
for d,et,pos,ent,stp,tp,hit,pts in log: dd['long' if pos==1 else 'short'].append((d,et,pts,0))
for k in dd: print(k, stats(dd[k]))
ex=collections.Counter('stop' if hit==stp else 'tgt' if hit==tp else 'eod' for d,et,pos,ent,stp,tp,hit,pts in log); print(ex)
# drawdown and green days
eq=0; pk=0; mdd=0
for x in o: eq+=x[2]*2; pk=max(pk,eq); mdd=max(mdd,pk-eq)
print(f'max DD 1 MNQ ${mdd:.0f}, total ${eq:.0f}')
