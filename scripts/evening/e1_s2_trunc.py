"""Q1. S2 sell-off long truncated to 18:00-20:00. Condition: prior RTH closed below its 9:30 open and 15:00-16:00 <= -thr ADR.
Long at 18:05 open, exit 20:00, stop/target grid. Baselines: unconditional long same window, and the same conditional
rule moved to later 2h windows (20-22, 22-24, 00-02, 02-04, 04-06, 06-08)."""
from ev_common import *
out = Out('/home/claude/mnq-quant/scripts/evening/out_e1.txt')

def s2(thr=.15, dayf=True, k0=1, kx=24, stop=.30, tgt=None, cond=True, dows=(0, 1, 2, 3, 4)):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if not full(d, k0, kx): continue
        lh = e['c16'] - e['o15']; dm = e['c16'] - e['rth_o']
        if cond and not (lh <= -thr * a and (dm < 0 or not dayf)): continue
        t = mkt(d, 1, k0, stop * a if stop else None, tgt * a if tgt else None, kx)
        if t: tr.append(t)
    return tr

out('## Q1 S2 truncated to the evening window\n')
out(HEAD)
out(md('S2 original reference: 18:05 -> 03:30, stop 0.30', s2(kx=slot(330))))
out(md('S2 trunc: 18:05 -> 20:00, stop 0.30, no target', s2()))
for sp in (None, .15, .20, .25, .30):
    for tg in (None, .2, .3, .4, .5):
        out(md(f'18:05->20:00 stop {sp} tgt {tg}', s2(stop=sp, tgt=tg)))
out('\n### threshold / filter / entry neighbours (stop 0.30, no target)\n'); out(HEAD)
for thr in (.10, .15, .20, .25):
    for dayf in (True, False):
        out(md(f'thr {thr} dayDown {dayf}', s2(thr=thr, dayf=dayf)))
for k0 in (0, 1, 3, 6):
    out(md(f'entry slot {k0} ({18}:{k0*5:02d})', s2(k0=k0)))
for kx in (12, 18, 24):
    out(md(f'exit {18 + kx*5//60}:{kx*5%60:02d}', s2(kx=kx)))
out('\n### Baselines\n'); out(HEAD)
out(md('unconditional long 18:05->20:00 stop 0.30', s2(cond=False)))
pool = []
for sh in SHIFTS:
    tr = s2(k0=1 + sh, kx=24 + sh); pool += tr
    out(md(f'conditional, window shifted +{sh*5//60}h', tr))
out(md('conditional, pooled shifted windows', pool))
out('\n### by evening day-of-week (stop 0.30)\n'); out(HEAD)
for dw in range(5): out(md(f'{DOWN[dw]} evening', s2(dows=(dw,))))
