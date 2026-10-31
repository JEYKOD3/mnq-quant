import numpy as np, pickle, sys
exec(open('fib_causal_lib.py').read())
tf=float(sys.argv[1])
rows=[]
for line in open('../../data/raw/mnq_rth_1m.txt'):
    dd,*bars=line.strip().split('|'); a=np.array([[int(x) for x in b.split(',')] for b in bars],float); a[:,1:]/=4
    for s_,p,rk in sim(a[:,2],a[:,3],a[:,4],slope_of(a[:,4]),60,0.618,tfrac=tf): rows.append((dd,p/rk))
pickle.dump(rows,open(f'pb618_R_tf{tf}.pkl','wb'))
R=np.array([r for _,r in rows]); w=R[R>0]; l=R[R<=0]
print(f'target {tf:.0%} of the way to B: trades {len(R)} win {len(w)/len(R):.3f} avg win {w.mean():.2f}R avg loss {l.mean():.2f}R expectancy {R.mean():.3f}R PF {w.sum()/-l.sum():.2f}')
