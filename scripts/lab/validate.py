import pickle, time, sys
sys.path.insert(0,'.')
from core import *
t0=time.time(); days=load(); F=features(days)
pickle.dump((days,F),open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','wb'))
print('loaded',len(days),'days',round(time.time()-t0,1),'s')
import json
fj=json.load(open('/home/claude/mnq-quant/scripts/dayfeat.json'))
mism=[d for d in F if str(d) in fj and (abs(F[d]['gap']-fj[str(d)]['gap'])>0.011 or abs(F[d]['orDir']-fj[str(d)]['orDir'])>0.011)]
print('feature mismatches vs dayfeat.json:',len(mism), mism[:5])
for tf in (5,1):
    tr=v4_trades(days,F,tf=tf,tgtR=2.0)
    print(f'V4 {tf}m 2R hold-close:',summary(tr,20220101),'yrs',yearly(tr))
