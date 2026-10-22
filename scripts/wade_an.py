import pickle, datetime as dt, collections, sys
from rep import report, line
SP='../data/cache/'
res=pickle.load(open(SP+'wade26_trades.pkl','rb'))
A0,A1,B0,B1=dt.date(2026,1,1),dt.date(2026,5,31),dt.date(2026,6,1),dt.date(2026,10,20)
import zoneinfo; NY=zoneinfo.ZoneInfo('America/New_York')
def breakdown(T,a,b,key):
    g=collections.defaultdict(list)
    for t in T:
        if a<=t['sess']<=b: g[key(t)].append(t)
    out=[]
    for k,L in sorted(g.items(), key=lambda kv: -len(kv[1])):
        n=len(L); w=sum(1 for t in L if t['pnl']>0); net=sum(t['pnl'] for t in L)
        out.append(f"{k}: {n} legs win {100*w/n:.0f}% net {net:+.0f}")
    return ' | '.join(out)
which=sys.argv[1:] or ['V10 (SE+LH+BP)|full session|tp1 1R run 3R key|atr1.5+htf15']
for g,T in res:
    if '|'.join(g) not in which: continue
    print('\n###',' | '.join(g))
    for lab,a,b in [('Jan-May',A0,A1),('Jun-Oct',B0,B1)]:
        print(lab, line(report(T,a,b)))
        print('   by setup :',breakdown(T,a,b,lambda t:t['id']))
        print('   by side  :',breakdown(T,a,b,lambda t:'long' if t['side']>0 else 'short'))
        print('   by hour  :',breakdown(T,a,b,lambda t:dt.datetime.fromtimestamp(t['etime'],NY).hour))
        print('   by exit  :',breakdown(T,a,b,lambda t:t['reason']))
