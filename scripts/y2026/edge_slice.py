"""Edge optimization, stage 2: slice each strategy's 1-contract net R by entry-time features.
Cuts (terciles) are fixed on 2022-2024 trades only. Blocks: IS 2022-24, VAL 2025, OOS 2026.
Then greedy filter search (max 2 filters per strategy) chosen on IS by total R gained, reported on VAL/OOS.
Writes edge_slice.json."""
import os, json, math, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, 'edge_trades.json')))
def blk(d): return 'IS' if d < 20250101 else ('VAL' if d < 20260101 else 'OOS')
NUM = ['gap', 'adrReg', 'pdr', 'onr', 'fhr', 'eT']
CAT = ['withT', 'news', 'wd']
STR = ['NEWS', 'V4+', 'D2', 'TDP', 'Pinball', 'H2', 'SGP', 'WCC']

def st(rs):
    if not rs: return dict(n=0, avg=None, sum=0.0, win=None)
    R = [r['R'] for r in rs]
    return dict(n=len(R), avg=round(sum(R) / len(R), 3), sum=round(sum(R), 2), win=round(sum(x > 0 for x in R) / len(R), 2))

def ok(v): return v is not None and not (isinstance(v, float) and math.isnan(v))

out = {}; tried = collections.Counter()
for s in STR:
    rs = [r for r in rows if r['strat'] == s]
    for r in rs: r['eT_'] = r['eT']
    base = {b: st([r for r in rs if blk(r['d']) == b]) for b in ('IS', 'VAL', 'OOS')}
    sl = {}
    cands = []                                      # (name, predicate keep)
    for f in NUM:
        key = 'eT' if f == 'eT' else f
        isv = sorted(r[key] for r in rs if blk(r['d']) == 'IS' and ok(r.get(key)))
        if len(isv) < 30 or len(set(isv)) < 3: continue
        c1, c2 = isv[len(isv) // 3], isv[2 * len(isv) // 3]
        if c1 == c2: continue
        lab = {}
        for nm, fn in (('low', lambda v: v < c1), ('mid', lambda v: c1 <= v < c2), ('high', lambda v: v >= c2)):
            lab[nm] = {b: st([r for r in rs if blk(r['d']) == b and ok(r.get(key)) and fn(r[key])]) for b in ('IS', 'VAL', 'OOS')}
        sl[f] = dict(cuts=[round(c1, 3), round(c2, 3)], **lab)
        for nm, fn in ((f'{f}>={c1:.3g}', lambda r, k=key, c=c1: not ok(r.get(k)) or r[k] >= c), (f'{f}<{c2:.3g}', lambda r, k=key, c=c2: not ok(r.get(k)) or r[k] < c),
                       (f'{f}>={c2:.3g}', lambda r, k=key, c=c2: not ok(r.get(k)) or r[k] >= c), (f'{f}<{c1:.3g}', lambda r, k=key, c=c1: not ok(r.get(k)) or r[k] < c)):
            cands.append((nm, fn))
    for f in CAT:
        vals = sorted(set(r[f] for r in rs if ok(r.get(f))))
        if len(vals) < 2: continue
        sl[f] = {str(v): {b: st([r for r in rs if blk(r['d']) == b and r.get(f) == v]) for b in ('IS', 'VAL', 'OOS')} for v in vals}
        for v in vals:
            cands.append((f'{f}!={v}', lambda r, k=f, vv=v: r.get(k) != vv))
    # greedy: up to 2 filters, each must add >= 3R on IS and keep >= 60% of IS trades
    keep = list(rs); chosen = []
    for step in range(2):
        best = None
        isb = sum(r['R'] for r in keep if blk(r['d']) == 'IS'); nis = sum(blk(r['d']) == 'IS' for r in rs)
        for nm, fn in cands:
            if any(nm.split('>')[0].split('<')[0].split('!')[0] == c.split('>')[0].split('<')[0].split('!')[0] for c in chosen): continue
            tried[s] += 1
            k2 = [r for r in keep if fn(r)]
            gain = sum(r['R'] for r in k2 if blk(r['d']) == 'IS') - isb
            if sum(blk(r['d']) == 'IS' for r in k2) < .6 * nis: continue
            if gain >= 3 and (best is None or gain > best[0]): best = (gain, nm, fn)
        if best is None: break
        chosen.append(best[1]); keep = [r for r in keep if best[2](r)]
    filt = {b: st([r for r in keep if blk(r['d']) == b]) for b in ('IS', 'VAL', 'OOS')}
    out[s] = dict(base=base, filtered=filt, filters=chosen, tried=tried[s], slices=sl)
    print(f"\n=== {s}: base " + ' | '.join(f"{b} n{base[b]['n']} avg {base[b]['avg']} sum {base[b]['sum']}" for b in base))
    print(f"   filters {chosen} (tried {tried[s]}) -> " + ' | '.join(f"{b} n{filt[b]['n']} avg {filt[b]['avg']} sum {filt[b]['sum']}" for b in filt))
    for f, v in sl.items():
        parts = []
        for k, x in v.items():
            if k == 'cuts': continue
            parts.append(f"{k}: " + '/'.join('-' if x[b]['avg'] is None else f"{x[b]['avg']:+.2f}({x[b]['n']})" for b in ('IS', 'VAL', 'OOS')))
        print(f"   {f:7s} {v.get('cuts', '')} " + ' ; '.join(parts))
json.dump(out, open(os.path.join(HERE, 'edge_slice.json'), 'w'), indent=1)
print('\nvariants tried', sum(tried.values()))
