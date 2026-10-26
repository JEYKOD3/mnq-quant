"""Q3. Does the 15:00-16:00 move, the full RTH day move, the 16:00-17:00 post-close move, or the 16:00 -> 18:00 change
continue in the first 2 evening hours? And does price revert to the 16:00 close (fair price idea)?
Entry market at 18:05 (slot 1), exit 20:00, stop grid. Baseline: same signal built from the 2h/1h before a later time."""
import itertools
from ev_common import *
out = Out('/home/claude/mnq-quant/scripts/evening/out_e3.txt')
WEEK = (1, 2, 3, 4); ALL = (0, 1, 2, 3, 4)

def sig(e, kind):
    return dict(lh=e['c16'] - e['o15'], day=e['c16'] - e['rth_o'], post=e['c17'] - e['c16'], g16=e['o18'] - e['c16'],
                g17=e['o18'] - e['c17'])[kind]

def cont(kind, thr, stop, fade=False, dows=WEEK, k0=1, kx=24, tgt_ref=False, maxthr=99, dst=None):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        x = sig(e, kind)
        if abs(x) < thr * a or x == 0 or abs(x) >= maxthr * a: continue
        s = (1 if x > 0 else -1) * (-1 if fade else 1)
        tp = e['c16'] if tgt_ref else None
        t = mkt(d, s, k0, stop * a if stop else None, None, kx, tgt_px=tp)
        if t: tr.append(t)
    return tr

def shifted(kind, thr, stop, fade=False, dows=WEEK):
    """pseudo-signal at later time T = slot sh: 'lh' -> move over the hour ending 2h before T, 'day' -> 6.5h move ending 2h before T,
    'post' -> hour ending 1h before T, 'g16' -> 2h move ending at T. Trade T+5m -> T+2h."""
    span = dict(lh=(36, 24), day=(102, 24), post=(24, 12), g16=(24, 0), g17=(12, 0))[kind]
    tr = []
    for sh in SHIFTS:
        for d in keys(dows):
            e = EV[d]; a = e['adr']; O, H, L, C = ETH[d]
            a0, a1 = sh - span[0], sh - span[1]
            if a0 < 0 or not full(d, max(a0, 0), sh + 24): continue
            x = (O[sh] if a1 == sh else C[a1 - 1]) - O[a0]
            if abs(x) < thr * a or x == 0: continue
            s = (1 if x > 0 else -1) * (-1 if fade else 1)
            t = mkt(d, s, sh + 1, stop * a if stop else None, None, sh + 24)
            if t: tr.append(t)
    return tr

for kind, thrs in (('lh', (0, .1, .2, .3)), ('day', (0, .25, .5, .75)), ('post', (0, .03, .05, .1)), ('g16', (0, .05, .1, .2))):
    for dows, dl in ((WEEK, 'Mon-Thu'), (ALL, 'Sun-Thu')):
        out(f'\n## signal {kind}, {dl} evenings, entry 18:05, exit 20:00\n'); out(HEAD)
        for thr, sp, fd in itertools.product(thrs, (.15, .2, .3, None), (False, True)):
            out(md(f"{'FADE' if fd else 'CONT'} {kind} >= {thr} ADR stop {sp}", cont(kind, thr, sp, fd, dows)))
    out(f'\n### baseline for {kind} (pseudo-signal at 6 later times, pooled), stop 0.2\n'); out(HEAD)
    for thr in thrs[:3]:
        out(md(f'CONT {kind} >= {thr} REAL', cont(kind, thr, .2)))
        out(md(f'CONT {kind} >= {thr} BASELINE', shifted(kind, thr, .2)))
        out(md(f'FADE {kind} >= {thr} REAL', cont(kind, thr, .2, True)))
        out(md(f'FADE {kind} >= {thr} BASELINE', shifted(kind, thr, .2, True)))

out('\n## Reversion to the 16:00 close (target = 16:00 close), fade the 16:00->18:00 change at 18:05\n'); out(HEAD)
for thr, sp in itertools.product((.05, .1, .15, .2, .3), (.15, .2, .3)):
    out(md(f'revert to 16:00 close, abs g16 >= {thr}, stop {sp}', cont('g16', thr, sp, True, ALL, tgt_ref=True)))

out('\n## g16 continuation: entry time / exit time / band checks (stop 0.2, Mon-Thu)\n'); out(HEAD)
for k0 in (0, 1, 3, 6, 12):
    out(md(f'CONT g16>=0.05 entry slot {k0}', cont('g16', .05, .2, k0=k0)))
for kx in (6, 12, 18, 24):
    out(md(f'CONT g16>=0.05 exit slot {kx}', cont('g16', .05, .2, kx=kx)))
for lo, hi in ((0, .05), (.05, .1), (.1, .2), (.2, .4), (.4, 9)):
    out(md(f'CONT g16 band {lo}-{hi}', cont('g16', lo, .2, maxthr=hi)))
for lo, hi in ((0, .03), (.03, .06), (.06, .1), (.1, 9)):
    out(md(f'CONT post band {lo}-{hi}', cont('post', lo, .2, maxthr=hi)))
out(md('CONT g16>=0.05 longs only', [t for t in cont('g16', .05, .2) if t['side'] > 0]))
out(md('CONT g16>=0.05 shorts only', [t for t in cont('g16', .05, .2) if t['side'] < 0]))
out(md('CONT g16>=0.05 DST (EDT)', cont('g16', .05, .2, dst=True)))
out(md('CONT g16>=0.05 EST', cont('g16', .05, .2, dst=False)))

out('\n## g16 continuation by DST and exit time (Tokyo opens 20:00 EDT / 19:00 EST)\n'); out(HEAD)
for dst in (True, False):
    for kx in (6, 12, 18, 24):
        out(md(f"CONT g16>=0.05 {'EDT' if dst else 'EST'} exit {18 + kx*5//60}:{kx*5%60:02d}", cont('g16', .05, .2, kx=kx, dst=dst)))
for dst in (True, False):
    for k0, kx in ((12, 24), (18, 24), (6, 12), (1, 12)):
        out(md(f"CONT g16>=0.05 {'EDT' if dst else 'EST'} {18 + k0*5//60}:{k0*5%60:02d}->{18 + kx*5//60}:{kx*5%60:02d}", cont('g16', .05, .2, k0=k0, kx=kx, dst=dst)))
for dst in (True, False):
    out(md(f"CONT g16>=0.05 Sun-Thu {'EDT' if dst else 'EST'}", cont('g16', .05, .2, dows=ALL, dst=dst)))
    out(md(f"CONT day>=0.5 {'EDT' if dst else 'EST'}", cont('day', .5, .2, dst=dst)))
    out(md(f"CONT post>=0.05 {'EDT' if dst else 'EST'}", cont('post', .05, .2, dst=dst)))
