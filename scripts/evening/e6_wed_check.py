"""Q6 follow-up: the 16:00-close continuation (CONT g16) is concentrated on Wednesday evenings. Check FOMC, earnings, season,
thresholds, stops, entry time, per-year, and a shifted baseline on the same Wednesday sessions."""
import itertools
from ev_common import *
from common import MACRO
out = Out('/home/claude/mnq-quant/scripts/evening/out_e6.txt')
def fomc(e): return any(ev == 'FOMC' for ev, _ in MACRO.get(e['p'], ()))
def macro_names(e): return {ev for ev, _ in MACRO.get(e['p'], ())}
def c16(thr=.05, stop=.2, dows=(3,), k0=1, kx=24, filt=lambda e: True, sh=0, tgt=None):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if not filt(e): continue
        if sh:
            if not full(d, sh - 24, sh + 24): continue
            O = ETH[d][0]; x = O[sh] - O[sh - 24]
        else: x = e['o18'] - e['c16']
        if abs(x) < thr * a or x == 0: continue
        t = mkt(d, 1 if x > 0 else -1, sh + k0, stop * a if stop else None, tgt * a if tgt else None, sh + kx)
        if t: tr.append(t)
    return tr
out(HEAD)
out(md('Wed all', c16()))
out(md('Wed FOMC day evenings', c16(filt=fomc)))
out(md('Wed non-FOMC', c16(filt=lambda e: not fomc(e))))
out(md('Wed non-FOMC non-earnings', c16(filt=lambda e: not fomc(e) and not e['earn'])))
out(md('Wed EDT', c16(filt=lambda e: e['dst'])))
out(md('Wed EST', c16(filt=lambda e: not e['dst'])))
out(md('Wed longs', [t for t in c16() if t['side'] > 0]))
out(md('Wed shorts', [t for t in c16() if t['side'] < 0]))
out(md('Mon+Tue+Thu', c16(dows=(1, 2, 4))))
out(md('Mon+Tue+Thu EDT', c16(dows=(1, 2, 4), filt=lambda e: e['dst'])))
out(md('Mon+Tue+Thu non-earnings', c16(dows=(1, 2, 4), filt=lambda e: not e['earn'])))
out(md('Mon-Thu non-FOMC', c16(dows=(1, 2, 3, 4), filt=lambda e: not fomc(e))))
for thr, sp in itertools.product((0, .03, .05, .08, .1, .15), (.15, .2, .3, None)):
    out(md(f'Wed thr {thr} stop {sp}', c16(thr, sp)))
for k0 in (0, 1, 3, 6, 12):
    out(md(f'Wed entry slot {k0}', c16(k0=k0)))
for kx in (6, 12, 18, 24):
    out(md(f'Wed exit slot {kx}', c16(kx=kx)))
for tg in (.1, .15, .2, .3):
    out(md(f'Wed target {tg} ADR', c16(tgt=tg)))
pool = []
for sh in SHIFTS: pool += c16(sh=sh)
out(md('Wed BASELINE: 2h move into later times, same Wednesday sessions, pooled', pool))
for dw in range(1, 5):
    p = []
    for sh in SHIFTS: p += c16(dows=(dw,), sh=sh)
    out(md(f'{DOWN[dw]} REAL', c16(dows=(dw,))))
    out(md(f'{DOWN[dw]} BASELINE', p))
# which macro events precede Wednesday evenings
cnt = collections.Counter()
for d in keys((3,)):
    for n in macro_names(EV[d]): cnt[n] += 1
out('\nmacro events on the Wednesday before the evening:', dict(cnt))
out('\n### practical exit buffer: flatten at 19:50 / 19:55 instead of 20:00\n'); out(HEAD)
for kx in (22, 23, 24):
    out(md(f'WCC exit at open of slot {kx} ({18 + kx*5//60}:{kx*5%60:02d})', c16(kx=kx)))
out(md('WCC 2025-2026 earnings evenings only', [t for t in c16() if EV[t['d']]['earn']]))
out(md('WCC non-earnings', [t for t in c16() if not EV[t['d']]['earn']]))
