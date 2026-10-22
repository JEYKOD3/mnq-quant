import sys; sys.argv=['x','2022']
exec(open('scripts/greenday_lab.py').read().split('# ---------- A) zigzag')[0])
exec('def ema_series'+open('scripts/greenday_lab.py').read().split('def ema_series')[1].split("report('H2 EMA21 1m, tgt 2R, cost3'")[0])
def agg(bars,n):
    out=[]
    for i in range(0,len(bars)-n+1,n):
        ch=bars[i:i+n]; out.append((ch[0][0],ch[0][1],max(b[2] for b in ch),min(b[3] for b in ch),ch[-1][4]))
    return out
days5=[(d,agg(b,5)) for d,b in days]
days3=[(d,agg(b,3)) for d,b in days]
D=days
days=days5
report('5m H2 EMA21, tgt 2R, cost3',            lambda b: run(b,tgtR=2.0,minStop=10,maxStop=60))
report('5m H2 EMA21, tgt 1R, cost3',            lambda b: run(b,tgtR=1.0,minStop=10,maxStop=60))
report('5m H2 EMA21, tgt 2R, EMA dist 1x range',lambda b: run(b,tgtR=2.0,minStop=10,maxStop=60,emaD=None,sigBody=.2))
report('5m H2 EMA21, 2R, cost0 ceiling',        lambda b: [(x[0]+COST,x[1]) for x in run(b,tgtR=2.0,minStop=10,maxStop=60)])
days=days3
report('3m H2 EMA21, tgt 2R, cost3',            lambda b: run(b,tgtR=2.0,minStop=10,maxStop=50))
