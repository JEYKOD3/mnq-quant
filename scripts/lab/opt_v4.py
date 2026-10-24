import pickle, sys, itertools
sys.path.insert(0,'.'); from core import *
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb'))
def rep(lab,tr):
    D=summary(tr,20220101,20241231); Tt=summary(tr,20250101,20261231); A=summary(tr,20220101)
    print(f"{lab:48s} DEV n{D['n']:3d} PF{D['pf']:5.2f} avgR{D['avgR']:+.2f} | TEST n{Tt['n']:3d} PF{Tt['pf']:5.2f} avgR{Tt['avgR']:+.2f} | ALL ddR{A['ddR']:4.1f} | {yearly(tr)}")
    return D,Tt
for tf in (1,5):
    print(f'\n===== V4 {tf}m =====')
    rep('base opp stop, hold close',v4_trades(days,F,tf=tf,tgtR=None))
    rep('base opp stop, 2R',v4_trades(days,F,tf=tf,tgtR=2))
    for sm,fr in (('mid',None),('ext',None),('adr',.1),('adr',.15),('adr',.2),('adr',.25),('adr',.3)):
        for tg in (None,2,3):
            rep(f'stop {sm}{fr or ""} tgt {tg}',v4_trades(days,F,tf=tf,tgtR=tg,stopMode=sm,stopFrac=fr))
    for fl in (720,780,840,900):
        rep(f'opp stop, flat at {fl//60}:{fl%60:02d}',v4_trades(days,F,tf=tf,tgtR=None,flat=fl))
        rep(f'adr.2 stop, flat at {fl//60}:{fl%60:02d}',v4_trades(days,F,tf=tf,tgtR=None,stopMode='adr',stopFrac=.2,flat=fl))
    for le in (630,660,720):
        rep(f'opp stop hold, lastEntry {le//60}:{le%60:02d}',v4_trades(days,F,tf=tf,tgtR=None,lastEntry=le))
    rep('opp stop hold, multi-trade',v4_trades(days,F,tf=tf,tgtR=None,first_only=False))
    rep('adr.2 hold, multi-trade',v4_trades(days,F,tf=tf,tgtR=None,first_only=False,stopMode='adr',stopFrac=.2))
