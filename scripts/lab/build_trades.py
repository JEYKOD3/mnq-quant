import pickle, sys; sys.path.insert(0,'.')
from core import *
from cont import cont, days, F
TR={}
TR['V4_1m_2R']=v4_trades(days,F,tf=1,tgtR=2)
TR['V4_1m_close']=v4_trades(days,F,tf=1,tgtR=None)
TR['V4_1m_1500']=v4_trades(days,F,tf=1,tgtR=None,flat=900)
TR['V4_1m_2R_1500']=v4_trades(days,F,tf=1,tgtR=2,flat=900)
TR['V4_5m_2R']=v4_trades(days,F,tf=5,tgtR=2)
TR['D2_1030_o_1500']=cont(630,.5,stop='open',flat=900)
TR['D2_1030_l_1500']=cont(630,.5,stop='lod',flat=900)
TR['D2_1100_l_close']=cont(660,.5,stop='lod',flat=955)
TR['D2_1130_l_close']=cont(690,.5,stop='lod',flat=955)
TR['D2_1030_4l_close']=cont(630,.4,stop='lod',flat=955)
for k,v in TR.items():
    v=[t for t in v if t['d']>=20220101]; TR[k]=v
    print(k, summary(v), yearly(v))
pickle.dump(TR,open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/trades.pkl','wb'))
# overlap stats
v4d={t['d']:t['side'] for t in TR['V4_1m_2R']}; d2=TR['D2_1030_o_1500']
same=sum(1 for t in d2 if t['d'] in v4d and v4d[t['d']]==t['side']); opp=sum(1 for t in d2 if t['d'] in v4d and v4d[t['d']]!=t['side'])
print('D2 1030 trades',len(d2),'on V4 days same dir',same,'opposite',opp,'D2-only days',len(d2)-same-opp, '| V4 days',len(v4d))
