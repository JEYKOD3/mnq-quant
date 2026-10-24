import sys, collections; sys.path.insert(0,'.')
exec(open('evalv4plus.py').read().split("import portfolio")[0])
from core import summary, yearly
def stream(k,wts):
    out=[]
    for d,t in sorted(S[k].items()):
        if d<20220101 or d not in TRD: continue
        al=TRD[d][0]==t['side']; w=wts[0] if al else wts[1]
        if w>0: out.append(dict(d=d,side=t['side'],r=t['r'],pts=t['pts'],R=t['pts']/t['r'],why=t['why'],al=al,w=w))
    return out
for k,w in (('V4p_.4.4_none_2R',(1,0)),('D2b',(1,1)),('D2b',(1,0))):
    tr=stream(k,w); print(k,w,summary(tr),yearly(tr),'per yr',round(len(tr)/4.8),'exits',collections.Counter(t['why'] for t in tr))
    # longest losing streak
    ls=m=0
    for t in tr:
        if t['R']<=0: ls+=1; m=max(m,ls)
        else: ls=0
    print('   longest losing streak',m,' avg stop pts',round(sum(t['r'] for t in tr)/len(tr)))
both=sorted(stream('V4p_.4.4_none_2R',(1,0))+stream('D2b',(1,1)),key=lambda t:t['d'])
days_=collections.defaultdict(float)
for t in both: days_[t['d']]+=t['R']*t['w']
v=list(days_.values()); print('combined trading days',len(v),'per yr',round(len(v)/4.8),'green days',sum(x>0 for x in v),'red',sum(x<=0 for x in v),'avg day R',round(sum(v)/len(v),2))
mo=collections.defaultdict(float)
for d,x in days_.items(): mo[d//100]+=x
print('months green',sum(x>0 for x in mo.values()),'of',len(mo))
