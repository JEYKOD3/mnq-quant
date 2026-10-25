import itertools, json
from td import run, st
res = []
for E, mode, k, (stop, a), R, hold, half, tend in itertools.product(
        [.5, .6, .7], ['retrace', 'resume'], [.2, .33, .5], [('adr', .15), ('adr', .25), ('adr', .4), ('mid', 0), ('pb', 0)],
        [1, 1.5, 2, None], [60, 120, 999], [False, True], [720, 840]):
    if stop == 'pb' and mode != 'resume': continue
    if R is None and hold == 60 and half: continue
    c = dict(E=E, mode=mode, k=k, stop=stop, a=a, buf=.03, R=R, hold=hold, half=half, tend=tend)
    s = st(run(**c)); res.append(dict(cfg=c, **s))
json.dump(res, open('td_grid.json', 'w'))
print(len(res))
