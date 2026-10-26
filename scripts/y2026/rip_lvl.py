"""Two last tests (Oct 26 2026).
A) Friend's mother candle with a STRATEGIC stop: stop 1 tick beyond the nearest strong level behind the entry
   (RTH day low/high so far, PDH/PDL/PDC, overnight high/low, OR15 high/low once formed), min stop 1m 6 pt / 5m 12 pt,
   capped (1m 25|40, 5m 50|80; no level inside the cap -> skip). Target 0.5R / 0.75R / 1R. Every signal, one position
   at a time. Box rules = mc_struct.scan (full-body breakout). 1m and 5m boxes, 9:30-15:45 and 9:30-11:00. Bias none / 9:30 open.
B) Momentum 'rip' continuation. Trigger bar closes in its top/bottom 25% and is a burst:
   r1roll: 1m range >= k x mean range of the prior 20 1m bars (same day, so from 9:50)
   r1tod : 1m range >= k x mean range of the same minute over the prior 20 days
   v5roll: 5m volume >= k x mean volume of the prior 20 5m bars (continuous, incl. overnight)
   v5tod : 5m volume >= k x mean volume of the same 5m slot over the prior 20 days
   k in 2/3/4. Entry next bar open (+1 tick) in burst direction. Trend: none / with 9:30 open / with session VWAP.
   Stop: burst bar extreme or its 50%. Exit: 1R, 2R, trail = stop to prior 1m bar's low/high each bar, or time 15/30/60 min
   (stop only). Windows: entries 9:30-15:30 and 9:30-11:00; flat 15:55. One position at a time, max 6 per day.
Costs: 2.37/side, 1 tick entry + 1 tick stop slip. Stress: +8 pt on stop exits (+2 pt if the stop is under 20 pt).
Blocks IS 2022-24 / VAL 2025 / 2026. Survivor = net > 0 in all blocks (and under stress), n_IS >= 60.
Usage: python3 rip_lvl.py scan ; python3 rip_lvl.py eval"""
import os, sys, json, statistics, collections, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pass_tested as PT
import mc_struct as MS
from common import walk, mk, D, DB, SLIP, T, COMM, PV, STOPWHY
HERE = os.path.dirname(os.path.abspath(__file__))
BLK = PT.BLK
DI = {d: i for i, d in enumerate(D)}

# ---------------- levels ----------------
PREV = {}
for i, d in enumerate(D):
    if i and DB[D[i - 1]]:
        b = DB[D[i - 1]]; PREV[d] = (max(x[2] for x in b), min(x[3] for x in b), b[-1][4])
ONHL = {}
for d in D:
    e = [x for x in PT.ETH.get(d, []) if x[0] < 570]
    if e: ONHL[d] = (max(x[2] for x in e), min(x[3] for x in e))

def lvl_stop(d, b1, m, s, eP, tf, cap):
    """nearest strong level behind entry, from data known before minute m."""
    lv = []
    if d in PREV: lv += list(PREV[d])
    if d in ONHL: lv += list(ONHL[d])
    past = [x for x in b1 if x[0] < m]
    if past: lv += [max(x[2] for x in past), min(x[3] for x in past)]
    if m >= 585:
        orb = [x for x in b1 if x[0] < 585]; lv += [max(x[2] for x in orb), min(x[3] for x in orb)]
    mn = 6. if tf == 1 else 12.
    cand = [v for v in lv if (eP - v) * s >= mn]
    if not cand: return None
    v = max(cand) if s > 0 else min(cand)
    st = v - s * T
    if abs(eP - st) > cap: return None
    return st

def scanA(b, b1, d, e_win, bf, tf, cap, tR, tend=955, maxn=12):
    out = []; i = 0
    while i < len(b) - 2 and len(out) < maxn:
        mb = b[i]
        if not (b[i + 1][2] <= mb[2] and b[i + 1][3] >= mb[3]): i += 1; continue
        H, L = mb[2], mb[3]; k = i + 2; bside = None; nxt = i + 1
        while k < len(b):
            m, o, h, l, c = b[k]
            if m >= e_win: break
            lo_b, hi_b = min(o, c), max(o, c)
            up = lo_b > H; dn = hi_b < L
            if bside is None and (c > H or c < L) and not (up or dn):
                bside = 1 if c > H else -1; k += 1; continue
            if bside is not None and ((bside > 0 and c < L) or (bside < 0 and c > H)): break
            if bside is not None and ((bside > 0 and dn) or (bside < 0 and up)): up = dn = False
            if up or dn:
                s = 1 if up else -1
                if bf is None or bf(m, c) == s:
                    eP = c + s * SLIP * T
                    stp = lvl_stop(d, b1, m + tf, s, eP, tf, cap)
                    if stp is not None:
                        r = abs(eP - stp); tgt = eP + s * tR * r
                        j = PT.idx_at(b1, m + tf)
                        if j is None: break
                        xi, xP, why, rf = walk(b1, j, s, eP, stp, tgt, tend)
                        out.append(mk(d, f'LV{tf}', s, b1[j][0], eP, stp, xi, xP, why, rf, b1))
                        xt = b1[xi][0]; nxt = next((q for q in range(len(b)) if b[q][0] >= xt), len(b))
                break
            k += 1
        i = max(i + 1, nxt)
    return out

def runA(tf, e_win, biasf, cap, tR):
    out = []
    for d in D:
        b1 = DB[d]
        if len(b1) < 60 or b1[0][0] != 570: continue
        b = b1 if tf == 1 else PT.agg5(b1)
        o0 = b1[0][1]
        bf = (lambda m, c, o0=o0: 1 if c > o0 else -1) if biasf == 'open' else None
        out += scanA(b, b1, d, e_win, bf, tf, cap, tR)
    return out

# ---------------- B: rip triggers ----------------
TOD1D = {}   # (d, minute) -> mean range of that minute over prior 20 days
_hist = collections.defaultdict(collections.deque)
for d in D:
    for x in DB[d]:
        q = _hist[x[0]]
        if len(q) >= 20: TOD1D[(d, x[0])] = sum(q) / len(q)
    for x in DB[d]:
        q = _hist[x[0]]; q.append(x[2] - x[3])
        if len(q) > 20: q.popleft()

# tod volume history needs per-day update (one value per slot per day): rebuild properly
_vs = collections.defaultdict(collections.deque); C5D2 = collections.defaultdict(list); _byday = collections.defaultdict(list)
for x in PT.C5: _byday[x[1]].append(x)
_vq = collections.deque()
for d in sorted(_byday):
    for x in _byday[d]:
        _, _, m, o, h, l, c, v = x
        vroll = sum(_vq) / len(_vq) if len(_vq) >= 20 else None
        q = _vs[m]; vtod = sum(q) / len(q) if len(q) >= 20 else None
        if 570 <= m < 960: C5D2[d].append((m, o, h, l, c, v, vroll, vtod))
        _vq.append(v)
        if len(_vq) > 20: _vq.popleft()
    for x in _byday[d]:
        q = _vs[x[2]]; q.append(x[7])
        if len(q) > 20: q.popleft()
C5D = C5D2

import functools
@functools.lru_cache(maxsize=None)
def triggers(d, kind, k, e_win):
    """list of (entry_minute, side, stop_bar_hi, stop_bar_lo) - entry at open of the next bar after the burst."""
    out = []
    if kind in ('r1roll', 'r1tod'):
        b = DB[d]
        for i, (m, o, h, l, c) in enumerate(b):
            if m >= e_win or i + 1 >= len(b): continue
            rg = h - l
            if rg <= 0: continue
            if kind == 'r1roll':
                if i < 20: continue
                base = sum(x[2] - x[3] for x in b[i - 20:i]) / 20
            else:
                base = TOD1D.get((d, m))
                if base is None: continue
            if rg < k * base: continue
            pos = (c - l) / rg
            s = 1 if pos >= .75 else -1 if pos <= .25 else 0
            if s: out.append((m + 1, s, h, l))
    else:
        for (m, o, h, l, c, v, vr, vt) in C5D.get(d, []):
            if m >= e_win: continue
            base = vr if kind == 'v5roll' else vt
            if base is None or base <= 0 or v < k * base: continue
            rg = h - l
            if rg <= 0: continue
            pos = (c - l) / rg
            s = 1 if pos >= .75 else -1 if pos <= .25 else 0
            if s: out.append((m + 5, s, h, l))
    return out

@functools.lru_cache(maxsize=None)
def VW(d, m): return PT.vwap_ema(d, m)

def walk_trail(b, i0, s, eP, stp, tend):
    st = stp
    for j in range(i0, len(b)):
        m, o, h, l, c = b[j]
        if (s > 0 and l <= st) or (s < 0 and h >= st): return j, st - s * SLIP * T, 'stop' if st == stp else 'trail'
        if m >= tend: return j, c, 'time exit'
        x = l - T if s > 0 else h + T
        if (x - st) * s > 0 and (x - c) * s < 0: st = x
    return len(b) - 1, b[-1][4], 'time exit'

def runB(kind, k, trend, stopm, exitm, e_win, maxn=6):
    out = []
    for d in D:
        b1 = DB[d]
        if len(b1) < 60 or b1[0][0] != 570: continue
        o0 = b1[0][1]; busy = 0; n = 0
        for (em, s, H, L) in triggers(d, kind, k, e_win):
            if em < busy or n >= maxn: continue
            j = PT.idx_at(b1, em)
            if j is None or b1[j][0] >= 955: continue
            eP = b1[j][1] + s * SLIP * T
            if trend == 'open' and (1 if eP > o0 else -1) != s: continue
            if trend == 'vwap':
                ve = VW(d, em)
                if ve is None or (1 if eP > ve[1] else -1) != s: continue
            stp = (L - T if s > 0 else H + T) if stopm == 'bar' else ((H + L) / 2 - s * T)
            if (eP - stp) * s <= 0.5: continue
            r = abs(eP - stp)
            if exitm in ('1R', '2R'):
                xi, xP, why, rf = walk(b1, j, s, eP, stp, eP + s * (1 if exitm == '1R' else 2) * r, 955)
            elif exitm == 'trail':
                xi, xP, why = walk_trail(b1, j, s, eP, stp, 955); rf = None
            else:
                xi, xP, why, rf = walk(b1, j, s, eP, stp, None, min(955, em + int(exitm[1:])))
            out.append(mk(d, 'RIP', s, b1[j][0], eP, stp, xi, xP, why, rf, b1))
            busy = b1[xi][0] + 1; n += 1
    return out

def net(t, stress=False):
    x = 0.0
    if stress and t['why'] in STOPWHY: x = 2.0 if t['r'] < 20 else 8.0
    return (t['pts'] - x) * PV - 2 * COMM
def stats(tr, a, z, stress=False):
    v = [net(t, stress) for t in tr if a <= t['d'] <= z]
    if not v: return dict(n=0, net=0, pf=0, wr=0, be_wr=0, risk=0)
    w = [x for x in v if x > 0]; ls = [-x for x in v if x <= 0]
    g, Ls = sum(w), sum(ls)
    be = (statistics.mean(ls) / (statistics.mean(ls) + statistics.mean(w))) if w and ls else 0
    return dict(n=len(v), net=round(sum(v)), pf=round(g / Ls, 2) if Ls else 99, wr=round(len(w) / len(v), 3), be_wr=round(be, 3),
                risk=round(statistics.mean(t['r'] for t in tr if a <= t['d'] <= z), 1))

VA = []
for tf in (1, 5):
    for wn, ew in (('all', 945), ('am', 660)):
        for cap in ((25., 40.) if tf == 1 else (50., 80.)):
            for tR in (.5, .75, 1.):
                for bias in (None, 'open'):
                    VA.append((f'A {tf}m {wn} cap{int(cap)} t{tR} {bias or "nobias"}', ('A', tf, ew, bias, cap, tR)))
VB = []
for kind in ('r1roll', 'r1tod', 'v5roll', 'v5tod'):
    for k in (2, 3, 4):
        for wn, ew in (('all', 930), ('am', 660)):
            for trend in (None, 'open', 'vwap'):
                for stopm in ('bar', 'half'):
                    for exitm in ('1R', '2R', 'trail', 't15', 't30', 't60'):
                        VB.append((f'B {kind} k{k} {wn} {trend or "notrend"} {stopm} {exitm}', ('B', kind, k, trend, stopm, exitm, ew)))

def build(spec):
    if spec[0] == 'A': _, tf, ew, bias, cap, tR = spec; return runA(tf, ew, bias, cap, tR)
    _, kind, k, trend, stopm, exitm, ew = spec; return runB(kind, k, trend, stopm, exitm, ew)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    which = sys.argv[2] if len(sys.argv) > 2 else 'AB'
    if cmd == 'scan':
        res = {}
        kf = sys.argv[3] if len(sys.argv) > 3 else None
        lst = (VA if which == 'A' else []) + ([v for v in VB if kf is None or v[1][1] == kf] if which == 'B' else [])
        for nm, spec in lst:
            tr = build(spec); row = {}
            for kk, (a, z) in BLK.items(): row[kk] = stats(tr, a, z); row[kk + '_s'] = stats(tr, a, z, True)
            row['years'] = {y: stats(tr, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}
            row['pass'] = all(row[kk]['net'] > 0 for kk in BLK) and row['IS']['n'] >= 60
            row['pass_s'] = all(row[kk + '_s']['net'] > 0 for kk in BLK) and row['IS']['n'] >= 60
            res[nm] = row
            print(f"{nm:44s} " + ' | '.join(f"{kk} n{row[kk]['n']} wr{row[kk]['wr']} pf{row[kk]['pf']} s{row[kk + '_s']['pf']}" for kk in BLK)
                  + (' PASS' if row['pass'] else '') + (' PASS_S' if row['pass_s'] else ''), flush=True)
        json.dump(res, open(os.path.join(HERE, f'rip_lvl_scan_{which}{kf or ""}.json'), 'w'), indent=1)
