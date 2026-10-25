"""Sizing for fastest pass. JJ Simon's maths: cost per funded account = eval fee / pass rate; judge by passes and speed, not equity.
Lucid Flex 50K: fee $69, $3,000 target, $2,000 EOD trailing max loss, 50% consistency."""
import sys; sys.path.insert(0, '.')
exec(open('combo_tdp.py').read().split('def attempt')[0].split('# overlap')[0])
def attempt(trs_by_day, start, f, dll, horizon=250):
    bal = 50000.; peak = 50000.; best = 0.; n = 0
    for d in DAYS:
        if d < start: continue
        n += 1; mll = min(peak - 2000, 50000); cush = bal - mll
        dp = size_day([dict(t) for t in trs_by_day.get(d, [])], cush, 'updated', f=f, dll=dll, slipx=8.0)
        bal += dp; best = max(best, dp)
        if bal <= mll: return 'F', n
        peak = max(peak, bal)
        if bal - 50000 >= 3000 and best <= .5 * (bal - 50000): return 'P', n
        if n >= horizon: return 'O', n
    return 'O', n
FEE = 69
print(f"{'period':8s} {'version':26s} {'f':>4s} {'cap':>5s}  pass<=10d  <=20d  <=40d  fail-before-pass  median days  fee per funded acct")
for lab, a, z in (('2022-24', 20220301, 20241231), ('2025-26', 20250101, 20261023)):
    sts = [d for d in DAYS if a <= d <= z][::3]
    for m in ('Playbook only', 'Playbook + TDP (full size)'):
        for f in (.65, .8, 1.0):
            for dll in (1100, 1500, 2000):
                R = [attempt(byd[m], s, f, dll) for s in sts]; n = len(R); P = sorted(x[1] for x in R if x[0] == 'P'); F_ = sum(x[0] == 'F' for x in R) / n
                pe = len(P) / n
                print(f"{lab:8s} {m:26s} {f:4.2f} {dll:5d}  {100*sum(x<=10 for x in P)/n:7.0f}%  {100*sum(x<=20 for x in P)/n:4.0f}%  {100*sum(x<=40 for x in P)/n:4.0f}%  {100*F_:12.0f}%  {P[len(P)//2] if P else '-':>10}  ${FEE/(pe or 1e-9):6.0f}")
