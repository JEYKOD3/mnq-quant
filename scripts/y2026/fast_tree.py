"""Where a BASE v31 eval stands after 5 and 8 trading days (rolling starts), plus 60-day eventual pass."""
import collections, json
from fast_pass import *
from fast_plans import BASE
tr = build_trades(); byd = byday(tr); out = {}
for y, (a, z) in YEARS.items():
    R = roll(byd, BASE, a, z, H=60, keep=True); row = {}
    for k in (5, 8):
        c = collections.Counter()
        for r in R:
            if r['res'] == 'P' and r['n'] <= k: c['passed'] += 1; continue
            if r['res'] == 'F' and r['n'] <= k: c['failed'] += 1; continue
            eq = sum(dp for d, dp, _ in r['log'][:k])
            c['ahead +1500 or more' if eq >= 1500 else 'up 0 to 1500' if eq >= 0 else 'down 0 to -1000' if eq > -1000 else 'down more than -1000 (slow mode)'] += 1
        row[f'day{k}'] = {kk: round(v / len(R), 3) for kk, v in c.items()}
    s = summ([dict(r) for r in R]); P_ = sorted(r['n'] for r in R if r['res'] == 'P')
    row['p60'] = round(len(P_) / len(R), 3); row['p40'] = round(sum(n <= 40 for n in P_) / len(R), 3); row['med'] = P_[len(P_) // 2] if P_ else None
    row['busts60'] = round(sum(r['res'] == 'F' for r in R) / len(R), 3)
    out[y] = row; print(y, row)
json.dump(out, open('fast_tree.json', 'w'), indent=1)
