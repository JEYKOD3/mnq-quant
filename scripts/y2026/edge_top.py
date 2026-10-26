"""Top-3 single filters per strategy ranked on IS (2022-24) total R gain; their VAL/OOS gain. Validated = gain > 0 in VAL and OOS."""
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, 'edge_trades.json')))
def blk(d): return 'IS' if d < 20250101 else ('VAL' if d < 20260101 else 'OOS')
def ok(v): return v is not None and not (isinstance(v, float) and math.isnan(v))
NUM = ['gap', 'adrReg', 'pdr', 'onr', 'fhr', 'eT']; CAT = ['withT', 'news']
out = {}; n = 0
for s in ['NEWS', 'V4+', 'D2', 'TDP', 'Pinball', 'H2', 'SGP', 'WCC']:
    rs = [r for r in rows if r['strat'] == s]; c = []
    for f in NUM:
        v = sorted(r[f] for r in rs if blk(r['d']) == 'IS' and ok(r.get(f)))
        if len(v) < 30: continue
        for q in (v[len(v) // 3], v[2 * len(v) // 3]):
            c.append((f'skip {f}<{q:.3g}', lambda r, f=f, q=q: ok(r.get(f)) and r[f] < q))
            c.append((f'skip {f}>={q:.3g}', lambda r, f=f, q=q: ok(r.get(f)) and r[f] >= q))
    for f in CAT:
        for val in (0, 1):
            if any(r.get(f) == val for r in rs): c.append((f'skip {f}=={val}', lambda r, f=f, v=val: r.get(f) == v))
    res = []
    for nm, fn in c:
        n += 1
        sk = [r for r in rs if fn(r)]
        nis = sum(blk(r['d']) == 'IS' for r in rs); kis = nis - sum(blk(r['d']) == 'IS' for r in sk)
        if kis < .6 * nis: continue
        g = {b: round(-sum(r['R'] for r in sk if blk(r['d']) == b), 2) for b in ('IS', 'VAL', 'OOS')}
        ns = {b: sum(blk(r['d']) == b for r in sk) for b in ('IS', 'VAL', 'OOS')}
        res.append((nm, g, ns))
    res.sort(key=lambda x: -x[1]['IS'])
    out[s] = [dict(rule=a, gainR=g, skipped=ns, validated=g['VAL'] > 0 and g['OOS'] > 0) for a, g, ns in res[:3]]
    print(f"== {s}")
    for a, g, ns in res[:3]:
        print(f"   {a:22s} gain R IS {g['IS']:+6.2f} VAL {g['VAL']:+6.2f} OOS {g['OOS']:+6.2f}  skipped {ns}  {'VALIDATED' if g['VAL'] > 0 and g['OOS'] > 0 else ''}")
print('rules tried', n)
json.dump(out, open(os.path.join(HERE, 'edge_top.json'), 'w'), indent=1)
