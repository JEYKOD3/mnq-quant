import sys; sys.path.insert(0,'.')
exec(open('evalv4plus.py').read().split("import portfolio")[0])
import portfolio
pc=lambda x:f"{round(100*x):3d}%"
for v4k in ('V4','V4p_.4.4_1.5_2R','V4p_.4.4_none_2R','V4p_.4.5_1.5_2R'):
    for d2w in ((1,.5),(1,1)):
        for f in (.5,.65,.8,1.0):
            wts={v4k:(1,0),'D2b':d2w}; order=(v4k,'D2b')
            def ev2(a,z,step):
                st=[d for d in DAYS if a<=d<=z][::step]; R=[portfolio.attempt(wts,s,f,order=order) for s in st]; n=len(R)
                P=sorted(r[1] for r in R if r[0]=='P'); Fl=sum(r[0]=='F' for r in R)
                return [sum(x<=k for x in P)/n for k in (10,20,40,60)]+[Fl/n,(P[len(P)//2] if P else 999),len(P)/n]
            Dv=ev2(20220301,20241231,2); Tt=ev2(20250101,20260601,2)
            print(f"{v4k:18s} D2 {d2w} f{f} | DEV p10/20/40/60 "+' '.join(pc(x) for x in Dv[:4])+f" fail {pc(Dv[4])} med {Dv[5]} all {pc(Dv[6])} | TEST "+' '.join(pc(x) for x in Tt[:4])+f" fail {pc(Tt[4])} med {Tt[5]} all {pc(Tt[6])}")
