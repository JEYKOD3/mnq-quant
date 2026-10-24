import pickle, sys, collections
sys.path.insert(0,'.'); from core import *
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb'))
TR=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/trades.pkl','rb'))
FOMC={20220126,20220316,20220504,20220615,20220727,20220921,20221102,20221214,20230201,20230322,20230503,20230614,20230726,20230920,20231101,20231213,
20240131,20240320,20240501,20240612,20240731,20240918,20241107,20241218,20250129,20250319,20250507,20250618,20250730,20250917,20251029,20251210,
20260128,20260318,20260429,20260617,20260729,20260916}
D=[d for d,_ in days]; C={d:b[-1][4] for d,b in days}; RNG={d:max(x[2] for x in b)-min(x[3] for x in b) for d,b in days}
reg={}
for i,d in enumerate(D):
    if i<60: continue
    prev=D[i-20:i]; sma20=sum(C[x] for x in prev)/20; sma50=sum(C[x] for x in D[i-50:i])/50
    c1=C[D[i-1]]; r5=(c1/C[D[i-6]]-1)*100
    adr20=sum(RNG[x] for x in prev)/20; adr100=sum(RNG[x] for x in D[i-100:i])/100 if i>=100 else adr20
    reg[d]=dict(trend='up' if c1>sma20 and sma20>sma50 else ('down' if c1<sma20 and sma20<sma50 else 'mixed'),
                r5=r5, vol='highvol' if adr20>1.2*adr100 else ('lowvol' if adr20<0.85*adr100 else 'normvol'),
                fomc=d in FOMC, postfomc=D[i-1] in FOMC)
def grp(k,key,lab):
    g=collections.defaultdict(list)
    for t in TR[k]:
        if t['d'] in reg: g[key(t)].append(t)
    print(f'  {lab:22s}'+' | '.join(f"{a}: n{len(v)} PF{summary(v)['pf']:.2f} avgR{summary(v)['avgR']:+.2f}" for a,v in sorted(g.items())))
for k in ('V4_1m_2R','D2_1030_4l_close','D2_1030_o_1500'):
    print(k)
    grp(k,lambda t: reg[t['d']]['trend'],'daily trend (20/50)')
    grp(k,lambda t: ('with' if (reg[t['d']]['trend']=='up')==(t['side']>0) else 'against') if reg[t['d']]['trend']!='mixed' else 'mixed','trade vs daily trend')
    grp(k,lambda t: reg[t['d']]['vol'],'volatility regime')
    grp(k,lambda t: 'FOMC day' if reg[t['d']]['fomc'] else ('day after' if reg[t['d']]['postfomc'] else 'other'),'FOMC')
    grp(k,lambda t: 'r5<-3%' if reg[t['d']]['r5']<-3 else ('r5>3%' if reg[t['d']]['r5']>3 else 'flat'),'prior 5-day return')
# current regime (last day in data)
last=D[-1]; i=len(D)-1
print('last day in 1m data',last, reg.get(last))
