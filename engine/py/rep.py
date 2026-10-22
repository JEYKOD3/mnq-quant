# daily / weekly / monthly report for a list of trades with 'sess' (date) and 'pnl'
import datetime as dt, collections, math
def report(trs, a, b):
    """trs: trades; a,b: date bounds inclusive. returns dict"""
    T=[t for t in trs if a<=t['sess']<=b]
    day=collections.OrderedDict()
    for t in T: day[t['sess']]=day.get(t['sess'],0)+t['pnl']
    dv=list(day.values()); g=sum(1 for v in dv if v>0); r=len(dv)-g
    wk=collections.OrderedDict()
    for d,v in day.items(): k=d.isocalendar()[:2]; wk[k]=wk.get(k,0)+v
    mo=collections.OrderedDict()
    for d,v in day.items(): k=(d.year,d.month); mo[k]=mo.get(k,0)+v
    n=len(T); w=sum(1 for t in T if t['pnl']>0); gp=sum(t['pnl'] for t in T if t['pnl']>0); gl=-sum(t['pnl'] for t in T if t['pnl']<=0)
    eq=pk=dd=0
    for v in dv: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    return dict(n=n,net=round(sum(dv)),win=round(100*w/max(n,1)),pf=round(gp/gl,2) if gl>0 else 99.0,avgW=round(gp/max(w,1)),avgL=round(gl/max(n-w,1)),
                g=g,r=r,wk=sum(1 for v in wk.values() if v>0),wkn=len(wk),mo=sum(1 for v in mo.values() if v>0),mon=len(mo),
                worstDay=round(min(dv)) if dv else 0,bestDay=round(max(dv)) if dv else 0,dd=round(dd),months={f"{y}-{m:02d}":round(v) for (y,m),v in mo.items()})
def line(R):
    return (f"net {R['net']:+6d} | {R['n']:3d} tr win {R['win']:2d}% PF {R['pf']:4.2f} avgW {R['avgW']} avgL {R['avgL']} | days G/R {R['g']}/{R['r']} "
            f"| weeks+ {R['wk']}/{R['wkn']} | months+ {R['mo']}/{R['mon']} | worst day {R['worstDay']} DD {R['dd']}")
def score(R):
    # what Jey asked for: green most days, weeks, months; then PF
    if R['n']<10: return -9
    return (R['g']/max(1,R['g']+R['r']))*2 + (R['mo']/max(1,R['mon'])) + min(R['pf'],3)/3
