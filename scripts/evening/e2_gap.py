"""Q2. Weeknight gap / pullback analog of the Sunday Gap Pullback.
gap17 = 18:00 open - 17:00 close (the 1-hour halt), gap16 = 18:00 open - 16:00 RTH close.
Styles: (P) pullback limit in the gap direction at k x gap back toward the reference, fill by 19:30, stop s ADR, exit 20:00;
(F) fade at 18:05 toward the reference (target = reference); (G) follow the gap at 18:05.
Baseline: the same rule on a pseudo-gap at later times (price at T vs price 1h or 2h earlier, no halt)."""
import itertools
from ev_common import *
out = Out('/home/claude/mnq-quant/scripts/evening/out_e2.txt')
WEEK = (1, 2, 3, 4)

def gap_of(e, d, ref, sh):
    """returns (open, reference price) for the real evening (sh=0) or the shifted pseudo-gap"""
    O, H, L, C = ETH[d]
    if sh == 0:
        return e['o18'], (e['c17'] if ref == 17 else e['c16'])
    back = 12 if ref == 17 else 24
    return O[sh], C[sh - back - 1] if ref == 16 else C[sh - back - 1]

def pull(ref=17, minA=.05, k=.5, stop=.15, R=None, dows=WEEK, sh=0, fill_by=18, maxA=9):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if sh and not full(d, sh - 25, sh + 24): continue
        o, rp = gap_of(e, d, ref, sh); g = o - rp
        if abs(g) < minA * a or abs(g) > maxA * a: continue
        s = 1 if g > 0 else -1
        t = lim(d, s, o - s * k * abs(g), sh, sh + fill_by - 1, stop * a, R * stop * a if R else None, kx=sh + 24)
        if t: tr.append(t)
    return tr

def fade(ref=17, minA=.05, stop=.15, dows=WEEK, sh=0, tgt_ref=True, k0=1):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if sh and not full(d, sh - 25, sh + 24): continue
        o, rp = gap_of(e, d, ref, sh); g = o - rp
        if abs(g) < minA * a: continue
        s = -1 if g > 0 else 1
        t = mkt(d, s, sh + k0, stop * a, None, sh + 24, tgt_px=rp if tgt_ref else None)
        if t: tr.append(t)
    return tr

def follow(ref=17, minA=.05, stop=.15, dows=WEEK, sh=0, k0=1):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if sh and not full(d, sh - 25, sh + 24): continue
        o, rp = gap_of(e, d, ref, sh); g = o - rp
        if abs(g) < minA * a: continue
        t = mkt(d, 1 if g > 0 else -1, sh + k0, stop * a, None, sh + 24)
        if t: tr.append(t)
    return tr

# base rates
import statistics as S
for ref in (17, 16):
    g = [abs((EV[d]['o18'] - (EV[d]['c17'] if ref == 17 else EV[d]['c16'])) / EV[d]['adr']) for d in keys(WEEK)]
    out(f"weeknight gap vs {ref}:00 close: n {len(g)}, median {S.median(g)*100:.1f}% ADR, 75th {sorted(g)[int(.75*len(g))]*100:.1f}%, 90th {sorted(g)[int(.9*len(g))]*100:.1f}%")
g = [abs((EV[d]['o18'] - EV[d]['c17']) / EV[d]['adr']) for d in keys((0,))]
out(f"Sunday gap vs Friday 17:00 close: n {len(g)}, median {S.median(g)*100:.1f}% ADR")

out('\n## SGP replication on this engine (Sunday evenings, gap vs Friday 17:00, half-gap limit, fill by 19:30, stop 0.15, exit 20:00)\n'); out(HEAD)
out(md('SGP as specified', pull(17, .05, .5, .15, None, dows=(0,))))
for minA, k, sp in itertools.product((.03, .05, .08), (.375, .5, .625), (.12, .15, .2)):
    out(md(f'SGP nb gap>={minA} k{k} stop{sp}', pull(17, minA, k, sp, None, dows=(0,))))
pool = []
for sh in SHIFTS:
    pool += pull(17, .05, .5, .15, None, dows=(0,), sh=sh)
out(md('SGP baseline: pseudo-gap (1h move) at shifted Sunday-night times, pooled', pool))
out(md('SGP rule on weeknights instead (Mon-Thu)', pull(17, .05, .5, .15, None)))

for ref in (17, 16):
    out(f'\n## Weeknight pullback (P), gap vs {ref}:00 close, Mon-Thu evenings\n'); out(HEAD)
    best = []
    mins = (.02, .05, .1, .2) if ref == 17 else (.05, .1, .2, .3)
    for minA, k, sp, R in itertools.product(mins, (.25, .5, .75, 1.0), (.1, .15, .2), (None, 2)):
        tr = pull(ref, minA, k, sp, R)
        out(md(f'gap>={minA} k{k} stop{sp} tgt {R}R', tr))
        best.append((passes(tr), tr, (minA, k, sp, R)))
    out(f"cells passing (n>=40 each period, PF>=1.15 both): {sum(b[0] for b in best)} of {len(best)}")
    out(f'\n## Weeknight fade (F) and follow (G) at 18:05, gap vs {ref}:00\n'); out(HEAD)
    for minA, sp in itertools.product(mins, (.1, .15, .2, .3)):
        out(md(f'FADE to ref gap>={minA} stop{sp}', fade(ref, minA, sp)))
        out(md(f'FOLLOW gap>={minA} stop{sp}', follow(ref, minA, sp)))
    out('\nshifted pseudo-gap baselines (pooled over 6 later windows)\n'); out(HEAD)
    m0 = mins[1]
    for lab, fn, kw in (('P k0.5 stop0.15', pull, dict(k=.5, stop=.15)), ('FADE stop0.15', fade, dict(stop=.15)), ('FOLLOW stop0.15', follow, dict(stop=.15))):
        pool = []
        for sh in SHIFTS: pool += fn(ref, m0, sh=sh, **kw)
        out(md(f'{lab} gap>={m0} REAL', fn(ref, m0, **kw)))
        out(md(f'{lab} gap>={m0} BASELINE pooled', pool))
