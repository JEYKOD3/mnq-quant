"""Q4. Manual-friendly open patterns inside 18:00-20:00.
(a) first 15/30-min range at 18:00, then a sweep beyond one side and a 5m close back inside before 19:30: fade (and the break-and-go control).
(b) 19:00 / 20:00 behaviour: pre-Tokyo hour (Tokyo opens 20:00 EDT, 19:00 EST); 18:00-19:00 range break/fade at the EST Tokyo open;
    what the 20:00-21:00 hour does after the evening move (why flat by 20:00 matters).
(c) 18:00 open as fair price: fade (or follow) the first extension >= X ADR from the 18:00 open.
Every rule is repeated with its clock moved to later 2h windows (baseline)."""
import itertools
from ev_common import *
out = Out('/home/claude/mnq-quant/scripts/evening/out_e4.txt')
ALL = (0, 1, 2, 3, 4); WEEK = (1, 2, 3, 4)

def sweep(orm=3, depth=.02, stop='ext', tgt='mid', last=18, sh=0, dows=ALL, go=False, dst=None):
    """orm = OR bars (3=15m, 6=30m). sweep = a bar trades >= depth ADR beyond OR high/low; trigger = a later (or same) bar
    closes back inside the OR within 3 bars of the sweep; entry next bar open opposite the sweep (go=True: with the sweep,
    on the first close outside instead). stop 'ext' = sweep extreme + 0.02 ADR, or a fixed ADR fraction."""
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        if not full(d, sh, sh + 24): continue
        O, H, L, C = ETH[d]
        hi = max(H[sh:sh + orm]); lo = min(L[sh:sh + orm]); mid = (hi + lo) / 2
        if hi - lo <= 0: continue
        sw = None
        for k in range(sh + orm, sh + last):
            if go:
                if C[k] > hi or C[k] < lo:
                    s = 1 if C[k] > hi else -1
                    stp = (lo if s > 0 else hi) if stop == 'ext' else None
                    t = mkt(d, s, k + 1, None if stop == 'ext' else stop * a, (hi - lo) if tgt == 'or' else None, sh + 24,
                            stop_px=(stp - s * T) if stop == 'ext' else None)
                    if t: tr.append(t)
                    break
                continue
            if sw is None:
                if H[k] >= hi + depth * a: sw = (-1, k, H[k])
                elif L[k] <= lo - depth * a: sw = (1, k, L[k])
                else: continue
            s, k_sw, ext = sw
            if k - k_sw > 3: break
            ext = max(H[k_sw:k + 1]) if s < 0 else min(L[k_sw:k + 1])
            if (s < 0 and C[k] < hi) or (s > 0 and C[k] > lo):
                stp = ext - s * .02 * a if stop == 'ext' else None
                tp = mid if tgt == 'mid' else (lo if s < 0 else hi) if tgt == 'far' else None
                t = mkt(d, s, k + 1, None if stop == 'ext' else stop * a, None, sh + 24, stop_px=stp, tgt_px=tp)
                if t: tr.append(t)
                break
    return tr

def pre_tokyo(ref='c16', thr=.05, stop=.15, k0=12, kx=24, fade=False, dst=None, dows=ALL, sh=0):
    """signal at the open of bar k0: price (open of k0) minus reference (16:00 close or 18:00 open); trade k0 -> kx."""
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        if not full(d, sh, sh + kx): continue
        O = ETH[d][0]
        if sh:
            refp = O[sh - 24] if ref == 'c16' else O[sh]
        else:
            refp = e['c16'] if ref == 'c16' else e['o18']
        x = O[sh + k0] - refp
        if abs(x) < thr * a or x == 0: continue
        s = (1 if x > 0 else -1) * (-1 if fade else 1)
        t = mkt(d, s, sh + k0, stop * a if stop else None, None, sh + kx)
        if t: tr.append(t)
    return tr

def tokyo_rng(mode='break', stop='other', dst=False, dows=ALL, sh=0, last=21):
    """range 18:00-19:00; 19:00-20:00 first close outside: break = go with it, fade = trade back toward the range (only after a
    close outside and a close back inside)."""
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        if not full(d, sh, sh + 24): continue
        O, H, L, C = ETH[d]
        hi = max(H[sh:sh + 12]); lo = min(L[sh:sh + 12])
        out_s = 0
        for k in range(sh + 12, sh + last):
            if mode == 'break':
                if C[k] > hi or C[k] < lo:
                    s = 1 if C[k] > hi else -1
                    stp = (lo - T) if s > 0 else (hi + T)
                    t = mkt(d, s, k + 1, .15 * a if stop != 'other' else None, None, sh + 24, stop_px=stp if stop == 'other' else None)
                    if t: tr.append(t)
                    break
            else:
                if not out_s and (C[k] > hi or C[k] < lo): out_s = 1 if C[k] > hi else -1; ext = H[k] if out_s > 0 else L[k]; continue
                if out_s:
                    ext = max(ext, H[k]) if out_s > 0 else min(ext, L[k])
                    if (out_s > 0 and C[k] < hi) or (out_s < 0 and C[k] > lo):
                        s = -out_s
                        t = mkt(d, s, k + 1, None, None, sh + 24, stop_px=ext - s * .02 * a, tgt_px=(hi + lo) / 2)
                        if t: tr.append(t)
                        break
    return tr

def fair18(x=.15, stop=.15, fade=True, a_from=3, a_to=18, sh=0, dows=ALL, tgt='open', dst=None):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        if not full(d, sh, sh + 24): continue
        O, H, L, C = ETH[d]; ref = O[sh]
        for k in range(sh + a_from, sh + a_to):
            dv = C[k] - ref
            if abs(dv) >= x * a:
                s = (-1 if dv > 0 else 1) * (1 if fade else -1)
                tp = ref if (fade and tgt == 'open') else None
                t = mkt(d, s, k + 1, stop * a, None, sh + 24, tgt_px=tp)
                if t: tr.append(t)
                break
    return tr

def with_base(name, fn, **kw):
    out(md(name + ' REAL', fn(**kw)))
    pool = []
    for sh in SHIFTS: pool += fn(sh=sh, **kw)
    out(md(name + ' BASELINE pooled', pool))

out('## (a) 18:00 opening range sweep-and-reclaim (fade), entries until 19:30, exit 20:00\n'); out(HEAD)
for orm, dp, sp, tg in itertools.product((3, 6), (.01, .02, .04), ('ext', .1, .15), ('mid', 'far', None)):
    out(md(f'OR{orm*5} sweep>={dp} stop {sp} tgt {tg}', sweep(orm, dp, sp, tg)))
out('\n### controls and baselines\n'); out(HEAD)
for orm in (3, 6):
    with_base(f'OR{orm*5} sweep>=0.02 stop ext tgt mid', sweep, orm=orm, depth=.02, stop='ext', tgt='mid')
    with_base(f'OR{orm*5} break-and-go stop other side, no tgt', sweep, orm=orm, go=True, stop='ext', tgt=None)
    with_base(f'OR{orm*5} break-and-go stop other side, 1:1 OR width', sweep, orm=orm, go=True, stop='ext', tgt='or')

out('\n## (b1) pre-Tokyo hour: signal at 19:00, trade 19:00 -> 20:00\n'); out(HEAD)
for ref, thr, sp, fd, dst in itertools.product(('c16', 'o18'), (0, .05, .1, .15), (.1, .15, None), (False, True), (True, False)):
    out(md(f"{'FADE' if fd else 'CONT'} 19:00 vs {ref} >= {thr} stop {sp} {'EDT' if dst else 'EST'}", pre_tokyo(ref, thr, sp, fade=fd, dst=dst)))
out('\n### pre-Tokyo hour baselines (pooled later windows, both seasons together and split)\n'); out(HEAD)
for ref in ('c16', 'o18'):
    for dst in (None, True, False):
        with_base(f"CONT 19:00 vs {ref} >= 0.05 stop 0.15 {dst}", pre_tokyo, ref=ref, thr=.05, stop=.15, dst=dst)
out('\n### entry-time neighbours, CONT vs 16:00 close >= 0.05, stop 0.15, exit 20:00\n'); out(HEAD)
for dst in (True, False):
    for k0 in (6, 9, 12, 15, 18):
        out(md(f"CONT vs c16 entry {18 + k0*5//60}:{k0*5%60:02d} {'EDT' if dst else 'EST'}", pre_tokyo('c16', .05, .15, k0=k0, dst=dst)))
out('\n## (b2) 18:00-19:00 range at the EST Tokyo open (19:00), trade 19:00-20:00\n'); out(HEAD)
for dst in (False, True):
    for mode in ('break', 'fade'):
        out(md(f"18-19 range {mode} {'EDT' if dst else 'EST'}", tokyo_rng(mode, dst=dst)))
    with_base(f"18-19 range break {'EDT' if dst else 'EST'}", tokyo_rng, mode='break', dst=dst)

out('\n## (b3) what 20:00-21:00 does after the 18:00-20:00 move (information, not a trade for this module)\n')
for dst in (True, False):
    for lo in (0, .1, .2):
        same = n = 0; mv = []
        for d in keys(ALL):
            e = EV[d]
            if e['dst'] != dst or not full(d, 0, 36): continue
            O, H, L, C = ETH[d]; a = e['adr']
            m1 = C[23] - O[0]; m2 = C[35] - C[23]
            if abs(m1) < lo * a: continue
            n += 1; same += (m1 > 0) == (m2 > 0); mv.append(m2 * (1 if m1 > 0 else -1) / a)
        out(f"{'EDT' if dst else 'EST'} |18-20 move| >= {lo} ADR: n {n}, 20-21 continues {same/n:.0%}, mean continuation {sum(mv)/len(mv)*100:+.1f}% ADR")

out('\n## (c) 18:00 open as fair price: first 5m close >= X ADR from the 18:00 open between 18:15 and 19:30\n'); out(HEAD)
for x, sp, fd in itertools.product((.08, .1, .15, .2, .25, .3), (.1, .15, .2), (True, False)):
    out(md(f"{'FADE to open' if fd else 'FOLLOW'} ext>={x} stop {sp}", fair18(x, sp, fd)))
out('\n### baselines\n'); out(HEAD)
for x in (.1, .15, .2):
    with_base(f'FADE to open ext>={x} stop 0.15', fair18, x=x, stop=.15, fade=True)
    with_base(f'FOLLOW ext>={x} stop 0.15', fair18, x=x, stop=.15, fade=False)
for dst in (True, False):
    out(md(f"FOLLOW ext>=0.15 stop 0.15 {'EDT' if dst else 'EST'}", fair18(.15, .15, False, dst=dst)))
    out(md(f"FADE ext>=0.15 stop 0.15 {'EDT' if dst else 'EST'}", fair18(.15, .15, True, dst=dst)))
