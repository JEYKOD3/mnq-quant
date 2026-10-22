import pickle, itertools, multiprocessing as mp, datetime as dt, json, sys
from mnqbt import run; from db5 import B; from rep import report, line, score
SP='../data/cache/'
rows=pickle.load(open(SP+'mnq26.pkl','rb'))
A0,A1,B0,B1=dt.date(2026,1,1),dt.date(2026,5,31),dt.date(2026,6,1),dt.date(2026,10,20)
SETUPS={'V10 (SE+LH+BP)':{}, 'SE only':dict(useLHHL=False,useBP=False), 'LH only':dict(useSE=False,useBP=False), 'BP only':dict(useSE=False,useLHHL=False),
        'SE+LH':dict(useBP=False), 'LH+BP':dict(useSE=False), 'SE+F2':dict(useLHHL=False,useBP=False,useF2=True), 'V10+F2':dict(useF2=True)}
SESS={'full session':{}, 'RTH 10:00-15:30':dict(noNew=((1530,2400),(0,1000)),flatWin=(1555,1800)), 'NY 9:30-12:00':dict(noNew=((1200,2400),(0,930)),flatWin=(1555,1800)),
      'London+NY 4:00-12:00':dict(noNew=((1200,2400),(0,400)),flatWin=(1555,1800)), 'Evening 18:00-24:00':dict(noNew=((0,1800),),flatWin=(1640,1800))}
EXITS={'tp1 1R run 3R key':{}, 'tp1 1R run 2R':dict(runnerR=2,useKeyTgt=False), 'tp1 1.5R run 3R':dict(tp1R=1.5), 'single 2R':dict(tp1R=2.0,tp1Frac=1.0,runnerR=2.0,useKeyTgt=False)}
FILT={'atr1.5+htf15':{}, 'no filters':dict(maxAtrRatio=99,htfMin=0), 'htf15 only':dict(maxAtrRatio=99)}
G=[(s,se,e,f) for s in SETUPS for se in SESS for e in EXITS for f in FILT]
def job(g):
    s,se,e,f=g; kk={**B,'dayProfitUSD':0,'maxTrades':5,**SETUPS[s],**SESS[se],**EXITS[e],**FILT[f]}
    tr,daily,net=run(rows,**kk)
    T=[dict(sess=t['sess'],pnl=float(t['pnl']),id=t['id'],side=t['side'],etime=int(t['etime']),reason=t['reason']) for t in tr]
    return g,T
if __name__=='__main__':
    with mp.Pool(2) as p: res=p.map(job,G,chunksize=4)
    out=[]
    for g,T in res:
        RA,RB,RT=report(T,A0,A1),report(T,B0,B1),report(T,A0,B1)
        out.append(dict(g=g,A=RA,B=RB,T=RT,sc=min(score(RA),score(RB))))
    pickle.dump(res,open(SP+'wade26_trades.pkl','wb')); json.dump(out,open(SP+'wade26.json','w'))
    out.sort(key=lambda x:-x['sc'])
    print('variants',len(out),'| both halves profitable:',sum(1 for o in out if o['A']['net']>0 and o['B']['net']>0),'| green days >= 55% in both:',sum(1 for o in out if o['A']['g']>=.55*(o['A']['g']+o['A']['r']) and o['B']['g']>=.55*(o['B']['g']+o['B']['r'])))
    for o in out[:12]:
        print(' | '.join(o['g'])); print('   Jan-May', line(o['A'])); print('   Jun-Oct', line(o['B']))
