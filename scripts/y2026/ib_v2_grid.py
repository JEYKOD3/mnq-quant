import json, itertools, ib_v2 as M
res = []
for tf, k, cap, dayf, rnd in itertools.product((1, 5), (0, .75, 1, 1.5), (1, 1.5, 2, 3), ('none', 'outside', 'eff'), (False, True)):
    if k == 0 and rnd: continue          # rnd only matters with a level target
    tr = M.ib(tf=tf, k=k, cap=cap, dayf=dayf, rnd=rnd)
    row = dict(tf=tf, k=k, cap=cap, dayf=dayf, rnd=rnd, **{b: M.stats(tr, a, z, 2.0 if tf == 1 else 4.0) for b, (a, z) in M.BL.items()})
    res.append(row)
json.dump(res, open('ib_v2_grid.json', 'w'), indent=0)
ok = [r for r in res if all(r[b]['pf'] > 1 and r[b]['n'] >= 40 for b in ('IS', 'VAL', 'Y26'))]
print('variants', len(res), 'pass all 3', len(ok))
for r in sorted(res, key=lambda r: -r['IS']['pf'])[:15]:
    print(r['tf'], r['k'], r['cap'], r['dayf'], r['rnd'], *[(r[b]['n'], r[b]['pf'], r[b]['avgR']) for b in ('IS', 'VAL', 'Y26')])
