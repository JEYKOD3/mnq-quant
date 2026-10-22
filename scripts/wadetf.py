import pickle, multiprocessing as mp, datetime as dt, json
from mnqbt import run; from db5 import B; from rep import report, line
SP='../data/cache/'
A0,A1,B0,B1=dt.date(2026,1,1),dt.date(2026,5,31),dt.date(2026,6,1),dt.date(2026,10,20)
SETUPS={'V10':{}, 'V10+F2':dict(useF2=True), 'SE+F2':dict(useLHHL=False,useBP=False,useF2=True), 'LH+BP':dict(useSE=False)}
SESS={'RTH 10:00-15:30':dict(noNew=((1530,2400),(0,1000)),flatWin=(1555,1800)), 'NY 9:30-12:00':dict(noNew=((1200,2400),(0,930)),flatWin=(1555,1800))}
EXITS={'tp1 1R run 2R':dict(runnerR=2,useKeyTgt=False), 'tp1 1R run 3R key':{}, 'single 1.5R':dict(tp1R=1.5,tp1Frac=1.0,runnerR=1.5,useKeyTgt=False)}
FILT={'htf15':dict(maxAtrRatio=99,htfMin=15), 'none':dict(maxAtrRatio=99,htfMin=0)}
G=[(tf,s,se,e,f) for tf in (1,2,3) for s in SETUPS for se in SESS for e in EXITS for f in FILT]
def job(g):
    tf,s,se,e,f=g; rows=pickle.load(open(SP+f'mnq26_{tf}m.pkl','rb'))
    kk={**B,'dayProfitUSD':0,'maxTrades':5,'tfMin':tf,'skipLondon':False,'useVwapF':False,**SETUPS[s],**SESS[se],**EXITS[e],**FILT[f]}
    tr,daily,net=run(rows,**kk)
    return g,[dict(sess=t['sess'],pnl=float(t['pnl']),id=t['id'],side=t['side'],etime=int(t['etime']),reason=t['reason']) for t in tr]
if __name__=='__main__':
    with mp.Pool(2) as p: res=p.map(job,G,chunksize=2)
    pickle.dump(res,open(SP+'wadetf_trades.pkl','wb'))
    out=[]
    for g,T in res:
        RA,RB=report(T,A0,A1),report(T,B0,B1); out.append((g,RA,RB))
    gr=lambda R:R['g']/max(1,R['g']+R['r'])
    out.sort(key=lambda x:-(min(gr(x[1]),gr(x[2]))*2+min(x[1]['pf'],x[2]['pf'],3)/3+(1 if x[1]['net']>0 and x[2]['net']>0 else 0)))
    print('variants',len(out),'| both halves positive:',sum(1 for o in out if o[1]['net']>0 and o[2]['net']>0),'| green>=55% both:',sum(1 for o in out if gr(o[1])>=.55 and gr(o[2])>=.55))
    for tf in (1,2,3):
        sub=[o for o in out if o[0][0]==tf]; print(f'  {tf}m: both+ {sum(1 for o in sub if o[1]["net"]>0 and o[2]["net"]>0)}/{len(sub)} avg net A {sum(o[1]["net"] for o in sub)/len(sub):+.0f} B {sum(o[2]["net"] for o in sub)/len(sub):+.0f} avg legs/half {sum(o[1]["n"]+o[2]["n"] for o in sub)/(2*len(sub)):.0f}')
    for g,RA,RB in out[:10]:
        print(f'{g[0]}m | '+' | '.join(g[1:])); print('   Jan-May',line(RA)); print('   Jun-Oct',line(RB))
