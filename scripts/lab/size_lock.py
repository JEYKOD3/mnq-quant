import sys; sys.path.insert(0, '.')
exec(open('size_speed.py').read().split('FEE = 69')[0])
def size_lock(trs, cush, f, dll, lock):
    out = []
    for t in trs:
        realized = sum(u['netq'] for u in out if u['xT'] <= t['eT'])
        if lock and realized >= lock: continue
        out.append(t); size_day(out, cush, 'updated', f=f, dll=dll, slipx=8.0)
    return sum(u['netq'] for u in out)
def attempt2(byday, start, f, dll, lock, horizon=250):
    bal = 50000.; peak = 50000.; best = 0.; n = 0
    for d in DAYS:
        if d < start: continue
        n += 1; mll = min(peak - 2000, 50000); cush = bal - mll
        dp = size_lock([dict(t) for t in byday.get(d, [])], cush, f, dll, lock)
        bal += dp; best = max(best, dp)
        if bal <= mll: return 'F', n
        peak = max(peak, bal)
        if bal - 50000 >= 3000 and best <= .5 * (bal - 50000): return 'P', n
        if n >= horizon: return 'O', n
    return 'O', n
print(f"{'period':8s} {'f':>4s} {'cap':>5s} {'lock':>5s}  <=10d  <=20d  <=40d  ever  fail  median  fee/funded")
for lab, a, z in (('2022-24', 20220301, 20241231), ('2025-26', 20250101, 20261023)):
    sts = [d for d in DAYS if a <= d <= z][::3]
    for f, dll in ((.65, 1100), (.65, 1500), (.8, 1500), (1.0, 1500)):
        for lock in (0, 1450, 1000, 750):
            R = [attempt2(byd['Playbook + TDP (full size)'], s, f, dll, lock) for s in sts]; n = len(R)
            P = sorted(x[1] for x in R if x[0] == 'P'); pe = len(P) / n
            print(f"{lab:8s} {f:4.2f} {dll:5d} {lock:5d}  {100*sum(x<=10 for x in P)/n:4.0f}%  {100*sum(x<=20 for x in P)/n:4.0f}%  {100*sum(x<=40 for x in P)/n:4.0f}%  {100*pe:3.0f}%  {100*sum(x[0]=='F' for x in R)/n:3.0f}%  {P[len(P)//2] if P else '-':>5}   ${69/(pe or 1e-9):4.0f}")
