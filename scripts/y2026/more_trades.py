"""More-trades study (Oct 26 2026). New MNQ RTH setup families, small grids, strict blocks:
design 2022-2024 (IS), validate 2025 (VAL), final 2026 YTD. 1 MNQ costs: 2.37/side + 1 tick entry slip + 1 tick on stop exits
(walk() already slips stops). Report PF/net per block; keep only cells positive in all three blocks with n_IS >= 60.
Usage: python3 more_trades.py scan  -> more_scan.json ; python3 more_trades.py eval -> more_eval.json"""
import os, sys, json, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
from common import walk, mk, D, DB, F, EV, SLIP, T, COMM, PV

BLK = {'IS': (20220101, 20241231), 'VAL': (20250101, 20251231), '2026': (20260101, 20261231)}

def onhl():
    """overnight (18:00 prior evening .. 9:29) high/low per RTH date from the ETH 5m file (keyed by session end date)."""
    out = {}
    for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
        p = ln.strip().split('|')
        if len(p) < 2: continue
        hs = []; ls = []
        for x in p[1:]:
            t, o, h, l, c = x.split(','); t = int(t)
            if t >= 1800 or t < 925: hs.append(int(h) / 4); ls.append(int(l) / 4)
        if hs: out[int(p[0])] = (max(hs), min(ls))
    return out
ON = onhl()

def skipday(d): return bool({'FOMC', 'CPI'} & EV.get(d, set()))

def fill_and_walk(name, d, b, i, s, eP, stp, tgt, tend, **kw):
    m, o, h, l, c = b[i]
    if (s > 0 and l <= stp) or (s < 0 and h >= stp):
        return mk(d, name, s, m, eP, stp, i, stp - s * SLIP * T, 'stop', None, b, **kw)
    if tgt is not None and ((s > 0 and c >= tgt) or (s < 0 and c <= tgt)):
        return mk(d, name, s, m, eP, stp, i, tgt, 'target', None, b, **kw)
    xi, xP, why, rf = walk(b, i + 1, s, eP, stp, tgt, tend)
    return mk(d, name, s, m, eP, stp, xi, xP, why, rf, b, **kw)

# ---------- 1. opening range breakout ----------
def orb(orm=15, tgtR=1.5, stopm='far', last=660, flat=900, a=20220101, z=20991231):
    """first break of the first `orm` minutes range, stop entry 1 tick beyond, until `last`; stop = other side ('far') or OR mid ('mid')."""
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F: continue
        b = DB[d]; f = F[d]; adr = f['adr']
        if not adr: continue
        R = [x for x in b if x[0] < 570 + orm]
        if len(R) < orm: continue
        hi = max(x[2] for x in R); lo = min(x[3] for x in R)
        if hi - lo > .45 * adr or hi - lo < .05 * adr: continue
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 570 + orm or m > last: continue
            up = h >= hi + T; dn = l <= lo - T
            if up and dn: break
            if up or dn:
                s = 1 if up else -1; lvl = hi + T if up else lo - T
                eP = (max(o, lvl) if s > 0 else min(o, lvl)) + s * SLIP * T
                stp = (lo - T if s > 0 else hi + T) if stopm == 'far' else (hi + lo) / 2
                r = abs(eP - stp); tgt = eP + s * tgtR * r
                out.append(fill_and_walk(f'ORB{orm}', d, b, i, s, eP, stp, tgt, flat)); break
    return out

# ---------- 2. prior-day high/low reaction ----------
def pdlvl(mode='fade', stopA=.12, tgtA=.25, first=585, last=720, flat=900, a=20220101, z=20991231):
    """open inside the prior-day range; first touch of PDH or PDL between first..last.
    fade: limit at the level, stop stopA*ADR beyond, target tgtA*ADR back. break: stop entry 1 tick through, stop stopA back, target tgtA."""
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F: continue
        b = DB[d]; f = F[d]; adr = f['adr']; H = f['pdh']; L = f['pdl']; op = f['open']
        if not adr or not H or not (L < op < H): continue
        for i, (m, o, h, l, c) in enumerate(b):
            if m < first:
                if h >= H or l <= L: break        # touched before the window: skip day
                continue
            if m > last: break
            th = h >= H + (T if mode == 'break' else 0); tl = l <= L - (T if mode == 'break' else 0)
            if th and tl: break
            if th or tl:
                lvl = H if th else L
                if mode == 'fade':
                    s = -1 if th else 1
                    eP = (min(o, lvl) if s < 0 else max(o, lvl)) if False else lvl
                    eP = (max(o, lvl) if s < 0 else min(o, lvl)) + s * SLIP * T   # gap-through fills at the open
                else:
                    s = 1 if th else -1
                    eP = (max(o, lvl + T) if s > 0 else min(o, lvl - T)) + s * SLIP * T
                stp = eP - s * stopA * adr; tgt = eP + s * tgtA * adr
                out.append(fill_and_walk(f'PD-{mode}', d, b, i, s, eP, stp, tgt, flat)); break
    return out

# ---------- 3. overnight high/low first test ----------
def onlvl(mode='fade', stopA=.12, tgtA=.25, last=720, flat=900, a=20220101, z=20991231):
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F or d not in ON: continue
        b = DB[d]; f = F[d]; adr = f['adr']; H, L = ON[d]; op = f['open']
        if not adr or not (L < op < H): continue
        for i, (m, o, h, l, c) in enumerate(b):
            if m > last: break
            th = h >= H + (T if mode == 'break' else 0); tl = l <= L - (T if mode == 'break' else 0)
            if th and tl: break
            if th or tl:
                lvl = H if th else L
                if mode == 'fade':
                    s = -1 if th else 1; eP = (max(o, lvl) if s < 0 else min(o, lvl)) + s * SLIP * T
                else:
                    s = 1 if th else -1; eP = (max(o, lvl + T) if s > 0 else min(o, lvl - T)) + s * SLIP * T
                stp = eP - s * stopA * adr; tgt = eP + s * tgtA * adr
                out.append(fill_and_walk(f'ON-{mode}', d, b, i, s, eP, stp, tgt, flat)); break
    return out

# ---------- 4. TWAP pullback on directional days (no volume in the 1m set, so a time-weighted mean) ----------
def twap_pb(th=.3, stopA=.2, tgtR=1.5, first=630, last=780, flat=900, a=20220101, z=20991231):
    """at `first`, |close-open| >= th*ADR sets the side; then the first touch of the running session mean (typical price) = limit entry."""
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F: continue
        b = DB[d]; f = F[d]; adr = f['adr']; op = f['open']
        if not adr: continue
        cum = 0.0; n = 0; s = 0
        for i, (m, o, h, l, c) in enumerate(b):
            mean = cum / n if n else None
            if m == first:
                mv = b[i - 1][4] - op if i else 0
                if abs(mv) < th * adr: break
                s = 1 if mv > 0 else -1
            if s and m > first and m <= last and mean is not None:
                if (s > 0 and l <= mean) or (s < 0 and h >= mean):
                    eP = (min(o, mean) if s > 0 else max(o, mean)) + s * SLIP * T
                    stp = eP - s * stopA * adr; tgt = eP + s * tgtR * stopA * adr
                    out.append(fill_and_walk('TWAP-PB', d, b, i, s, eP, stp, tgt, flat)); break
            if m > last: break
            cum += (h + l + c) / 3; n += 1
    return out

# ---------- 5. gap fade toward the prior close ----------
def gapfade(lo_=.1, hi_=.4, stopx=.5, flat=690, a=20220101, z=20991231):
    """gap vs prior RTH close between lo_ and hi_ ADR: at 9:35 open fade toward pdc. stop = stopx*gap beyond the 9:35 open, target pdc."""
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F: continue
        b = DB[d]; f = F[d]; adr = f['adr']; pdc = f['pdc']; op = f['open']
        if not adr or not pdc: continue
        g = op - pdc
        if not (lo_ * adr <= abs(g) <= hi_ * adr): continue
        i = next((j for j, x in enumerate(b) if x[0] == 575), None)
        if i is None: continue
        s = -1 if g > 0 else 1; eP = b[i][1] + s * SLIP * T
        if (eP - pdc) * s >= 0: continue                    # already filled
        stp = eP - s * stopx * abs(g); tgt = pdc
        out.append(fill_and_walk('GAPFADE', d, b, i, s, eP, stp, tgt, flat))
    return out

# ---------- 6. inside-IB range fade on narrow days ----------
def ibfade(maxw=.35, ext=.0, stopA=.12, flat=840, last=780, a=20220101, z=20991231):
    """first hour range <= maxw*ADR: fade the first touch of IB high/low (+ext*ADR) after 10:30, target IB mid, stop stopA beyond."""
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F: continue
        b = DB[d]; f = F[d]; adr = f['adr']
        if not adr: continue
        IB = [x for x in b if x[0] < 630]
        if len(IB) < 55: continue
        hi = max(x[2] for x in IB); lo = min(x[3] for x in IB)
        if hi - lo > maxw * adr: continue
        H = hi + ext * adr; L = lo - ext * adr; mid = (hi + lo) / 2
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 630: continue
            if m > last: break
            th = h >= H; tl = l <= L
            if th and tl: break
            if th or tl:
                s = -1 if th else 1; lvl = H if th else L
                eP = (max(o, lvl) if s < 0 else min(o, lvl)) + s * SLIP * T
                stp = eP - s * stopA * adr
                out.append(fill_and_walk('IB-FADE', d, b, i, s, eP, stp, mid, flat)); break
    return out

# ---------- 7. second-hour momentum (11:30 continuation, the D2 idea one hour later, only if D2 did not fire) ----------
def m2h(th=.5, at=690, flat=840, stop='open', a=20220101, z=20991231):
    out = []
    for d in D:
        if d < a or d > z or skipday(d) or d not in F: continue
        b = DB[d]; f = F[d]; adr = f['adr']; op = f['open']
        if not adr: continue
        idx = {x[0]: j for j, x in enumerate(b)}
        j0 = idx.get(629); j = idx.get(at - 1)
        if j is None or j0 is None: continue
        if abs(b[j0][4] - op) >= .6 * adr: continue          # D2 day already
        mv = b[j][4] - op
        if abs(mv) < th * adr: continue
        s = 1 if mv > 0 else -1; eP = b[j][4] + s * SLIP * T
        stp = (op - s * T) if stop == 'open' else eP - s * .25 * adr
        if j + 1 >= len(b): continue
        out.append(fill_and_walk('M2H', d, b, j + 1, s, eP, stp, None, flat))
    return out

FAM = {
 'ORB15 1.5R far': lambda: orb(15, 1.5, 'far'), 'ORB15 1R far': lambda: orb(15, 1.0, 'far'), 'ORB15 2R mid': lambda: orb(15, 2.0, 'mid'),
 'ORB30 1.5R far': lambda: orb(30, 1.5, 'far'), 'ORB30 1R mid': lambda: orb(30, 1.0, 'mid'), 'ORB5 2R far': lambda: orb(5, 2.0, 'far'),
 'PD fade .12/.25': lambda: pdlvl('fade', .12, .25), 'PD fade .2/.4': lambda: pdlvl('fade', .2, .4), 'PD break .12/.25': lambda: pdlvl('break', .12, .25),
 'PD break .2/.5': lambda: pdlvl('break', .2, .5),
 'ON fade .12/.25': lambda: onlvl('fade', .12, .25), 'ON fade .2/.4': lambda: onlvl('fade', .2, .4), 'ON break .12/.25': lambda: onlvl('break', .12, .25),
 'ON break .2/.5': lambda: onlvl('break', .2, .5),
 'TWAP-PB .3 1.5R': lambda: twap_pb(.3, .2, 1.5), 'TWAP-PB .2 1.5R': lambda: twap_pb(.2, .2, 1.5), 'TWAP-PB .3 2R s.15': lambda: twap_pb(.3, .15, 2.0),
 'GAPFADE .1-.4 x.5': lambda: gapfade(.1, .4, .5), 'GAPFADE .1-.4 x1': lambda: gapfade(.1, .4, 1.0), 'GAPFADE .05-.25 x1': lambda: gapfade(.05, .25, 1.0),
 'IB-FADE .35': lambda: ibfade(.35), 'IB-FADE .45': lambda: ibfade(.45), 'IB-FADE .35 ext.05': lambda: ibfade(.35, .05),
 'M2H .5 open': lambda: m2h(.5), 'M2H .4 open': lambda: m2h(.4), 'M2H .5 .25ADR': lambda: m2h(.5, stop='adr'),
}

def net1(t, stopx=0.0): return (t['pts'] - (stopx if t['why'] in CM.STOPWHY else 0)) * PV - 2 * COMM

def stats(tr, a, z, stopx=0.0):
    v = [net1(t, stopx) for t in tr if a <= t['d'] <= z]
    if not v: return dict(n=0, net=0, pf=0, wr=0, avgR=0)
    g = sum(x for x in v if x > 0); L = -sum(x for x in v if x < 0)
    rr = [t['pts'] / t['r'] for t in tr if a <= t['d'] <= z and t['r'] > 0]
    return dict(n=len(v), net=round(sum(v)), pf=round(g / L, 2) if L else 99, wr=round(sum(x > 0 for x in v) / len(v), 2), avgR=round(statistics.mean(rr), 3))

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    base = CM.news() + CM.v4(flat=900) + CM.d2(th=.6, flat=795) + CM.tdp(tgtR=1.5, flat=900) + CM.pinball(tgtR=2, cap=180, flat=900) + CM.h2(tgtR=2, flat=900)
    busy = set(t['d'] for t in base)
    if mode == 'scan':
        out = {}
        for nm, fn in FAM.items():
            tr = fn(); row = {}
            for k, (a, z) in BLK.items():
                row[k] = stats(tr, a, z); row[k + '_slip8'] = stats(tr, a, z, 8.0)
            row['silent_share_2026'] = round(sum(t['d'] not in busy for t in tr if t['d'] >= 20260101) / max(1, sum(t['d'] >= 20260101 for t in tr)), 2)
            row['silent_days_2026'] = len(set(t['d'] for t in tr if t['d'] >= 20260101 and t['d'] not in busy))
            ok = all(row[k]['net'] > 0 for k in BLK) and row['IS']['n'] >= 60
            row['pass'] = ok; out[nm] = row
            print(f"{nm:22s} " + ' | '.join(f"{k} n{row[k]['n']} pf{row[k]['pf']} ${row[k]['net']} (s8 pf{row[k + '_slip8']['pf']})" for k in BLK) + f" | silent26 {row['silent_days_2026']}d {'PASS' if ok else ''}", flush=True)
        json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'more_scan.json'), 'w'), indent=1)
