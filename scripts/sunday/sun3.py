"""Sunday 18:00-20:00, three entry styles, exit by 20:00. 5m bars, 1 MNQ, costs in."""
import json, sys, itertools, collections
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair')
from eth_fp import bars
rows = json.load(open('sun_rows.json'))
B = {r['d']: bars(r['d']) for r in rows}
T = .25; PV = 2; COMM = 2.37
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def manage(b, j, s, e, stp, tgt, end):
    for k in range(j, len(b)):
        m, o, h, l, c = b[k]
        if (s > 0 and l <= stp) or (s < 0 and h >= stp): return (stp - s * T - e) * s
        if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)): return (tgt - e) * s
        if m >= end: return (c - e) * s
    return None
def style_follow(r, b, minA, entry_m, stopk, R):
    if abs(r['gapA']) < minA: return None
    s = 1 if r['gap'] > 0 else -1
    idx = {x[0]: j for j, x in enumerate(b)}
    if entry_m not in idx: return None
    j = idx[entry_m]
    if entry_m > 5 and (b[j - 1][4] - r['o']) * s <= 0: return None  # confirmation
    e = b[j][1] + s * T
    stp = e - s * stopk * r['adr']
    return s, j, e, stp, (e + s * R * stopk * r['adr']) if R else None
def style_orb(r, b, rng_m, minA, stopm, R, gapdir):
    w = [x for x in b if x[0] < rng_m]
    hi = max(x[2] for x in w); lo = min(x[3] for x in w)
    if minA and abs(r['gapA']) < minA: return None
    for j in range(len(w), len(b)):
        m, o, h, l, c = b[j]
        if m >= 105: return None
        s = 1 if c > hi else -1 if c < lo else 0
        if not s: continue
        if gapdir and r['gap'] * s <= 0: return None
        if j + 1 >= len(b): return None
        e = b[j + 1][1] + s * T
        stp = ((lo - T) if s > 0 else (hi + T)) if stopm == 'other' else (hi + lo) / 2
        Rr = abs(e - stp)
        if Rr < 4: return None
        return s, j + 1, e, stp, (e + s * R * Rr) if R else None
    return None
def style_pull(r, b, minA, k, stopk, R):
    if abs(r['gapA']) < minA: return None
    s = 1 if r['gap'] > 0 else -1
    lvl = r['o'] - s * k * abs(r['gap'])
    for j in range(1, len(b)):
        m, o, h, l, c = b[j]
        if m >= 90: return None
        if (s > 0 and l <= lvl - T) or (s < 0 and h >= lvl + T):
            e = min(o, lvl) if s > 0 else max(o, lvl)
            stp = e - s * stopk * r['adr']
            # fill bar: stop check only
            if (s > 0 and l <= stp) or (s < 0 and h >= stp): return s, None, e, stp, 'stopped'
            return s, j + 1, e, stp, (e + s * R * stopk * r['adr']) if R else None
    return None
def run(fn, *a, end=120):
    out = []
    for r in rows:
        b = B[r['d']]
        if not b or b[0][0] != 0: continue
        x = fn(r, b, *a)
        if not x: continue
        s, j, e, stp, tgt = x
        Rr = abs(e - stp)
        if tgt == 'stopped': res = (stp - s * T - e) * s
        else:
            res = manage(b, j, s, e, stp, tgt, end)
            if res is None: continue
        out.append((r['d'], res * PV - 2 * COMM, res / Rr))
    return out
res = []
def add(lab, tr):
    if len(tr) < 25: return
    a = [t[1] for t in tr if t[0] <= 20241231]; z = [t[1] for t in tr if t[0] > 20241231]
    res.append((lab, len(tr), round(sum(t[1] > 0 for t in tr) / len(tr), 2), pf([t[1] for t in tr]), pf(a), pf(z), round(sum(t[2] for t in tr) / len(tr), 2),
                {y: pf([t[1] for t in tr if t[0] // 10000 == y]) for y in range(2022, 2027)}))
for minA, em, sk, R in itertools.product((0, .05, .1, .2), (5, 10, 15, 30), (.1, .15, .2, .3), (None, 1, 1.5, 2)):
    add(f"FOLLOW gap>={minA} entry 18:{em:02d} stop {sk} ADR target {R}R", run(style_follow, minA, em, sk, R))
for rm, minA, sm, R, gd in itertools.product((15, 30, 60), (0, .05, .1), ('other', 'mid'), (None, 1, 1.5, 2), (False, True)):
    add(f"RANGE BREAK 18:00-18:{rm if rm<60 else 0:02d}{'' if rm<60 else '(19:00)'} gap>={minA} stop {sm} target {R}R {'gap-dir only' if gd else 'both'}", run(style_orb, rm, minA, sm, R, gd))
for minA, k, sk, R in itertools.product((.05, .1, .2), (.25, .5, .75, 1.0), (.1, .15, .2), (None, 1, 1.5, 2)):
    add(f"PULLBACK gap>={minA} limit at {k} of gap back, stop {sk} ADR target {R}R", run(style_pull, minA, k, sk, R))
json.dump(res, open('sun3.json', 'w'))
print(len(res), 'versions with >=25 trades')
print('PF>1 both periods:', sum(r[4] > 1 and r[5] > 1 for r in res), '| PF>1.2 both:', sum(r[4] > 1.2 and r[5] > 1.2 for r in res))
for fam in ('FOLLOW', 'RANGE', 'PULLBACK'):
    v = [r for r in res if r[0].startswith(fam)]
    print(f"\n{fam}: {len(v)} versions, PF>1 both periods {sum(r[4]>1 and r[5]>1 for r in v)}, median PF {sorted(r[3] for r in v)[len(v)//2]}")
    for r in sorted(v, key=lambda r: -min(r[4], r[5]))[:6]:
        print(f"  {r[0]:72s} n{r[1]:3d} win {r[2]:.0%} PF {r[3]} ({r[4]}|{r[5]}) avgR {r[6]:+} yrs {r[7]}")
