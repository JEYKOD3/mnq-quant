"""Research core (2026-10-24): MNQ RTH 1m data + day features + V4 (faithful port of engine simRT2 retest, stop=opp) + D2,
with per-trade diagnostics (MAE/MFE in R, time, context). Prices in points. Costs per contract: comm 2.37/side, slip 1 tick/side.
Data: data/raw/mnq_rth_1m.txt (Databento, through 2026-10-20). Optional extra days in data/live/mnq_rth_5m_live.txt are ignored here.
"""
import collections, os
R = '/home/claude/mnq-quant'
T = 0.25; PV = 2.0; COMM = 2.37; SLIP = 1
def load(path=R + '/data/raw/mnq_rth_1m.txt'):
    days = []
    for ln in open(path):
        p = ln.strip().split('|')
        if len(p) < 2: continue
        b = []
        for x in p[1:]:
            t, o, h, l, c = x.split(','); t = int(t)
            b.append((t // 100 * 60 + t % 100, int(o) / 4, int(h) / 4, int(l) / 4, int(c) / 4))
        days.append((int(p[0]), b))
    return days

def agg(b, tf):
    if tf == 1: return b
    g = collections.OrderedDict()
    for m, o, h, l, c in b:
        k = 570 + (m - 570) // tf * tf
        if k in g:
            a = g[k]; a[2] = max(a[2], h); a[3] = min(a[3], l); a[4] = c
        else: g[k] = [k, o, h, l, c]
    return [tuple(v) for v in g.values()]

def features(days):
    """same definitions as scripts/featdump.js (computed on 5m bars of the day; ADR = mean of prior 10 RTH ranges)"""
    F = {}; dr = []; prev = None
    for d, b in days:
        b5 = agg(b, 5)
        if prev is not None and len(b5) >= 20 and b5[0][0] == 570:
            pb = prev
            pdh = max(x[2] for x in pb); pdl = min(x[3] for x in pb); pdc = pb[-1][4]
            adr = sum(dr[-10:]) / 10 if len(dr) >= 10 else pdh - pdl
            dr.append(pdh - pdl)
            hi = max(x[2] for x in b5[:3]); lo = min(x[3] for x in b5[:3]); op = b5[0][1]
            gap = (op - pdc) / adr; ordir = (b5[2][4] - op) / ((hi - lo) or 1); pdrel = (pdh - pdl) / adr
            F[d] = dict(gap=round(gap, 2), orDir=round(ordir, 2), pdRel=round(pdrel, 2), adr=adr, pdh=pdh, pdl=pdl, pdc=pdc, open=op,
                        orh=hi, orl=lo, orw=(hi - lo) / adr, wd=0)
        if len(b) >= 20: prev = agg(b, 5)
    return F

def v4bias(f, g=.6, dd=.6, pd=1.2):
    if not f or (pd and f['pdRel'] > pd): return 0
    G = abs(f['gap']) >= g; D = abs(f['orDir']) >= dd
    if not (G or D): return 0
    return (1 if f['gap'] > 0 else -1) if G else (1 if f['orDir'] > 0 else -1)

def manage(b, i0, side, eP, stp, tgt, maxhold=0, flat=955, trail=None):
    """walk from bar i0 (entry bar already passed). returns (xi, xP, why, mae, mfe) in points"""
    mae = 0; mfe = 0
    for i in range(i0, len(b)):
        tm, o, h, l, c = b[i]
        if (side > 0 and l <= stp) or (side < 0 and h >= stp):
            mae = max(mae, (eP - l) if side > 0 else (h - eP))
            return i, stp - side * SLIP * T, 'stop', mae, mfe
        mae = max(mae, (eP - l) if side > 0 else (h - eP)); mfe = max(mfe, (h - eP) if side > 0 else (eP - l))
        if tgt is not None and ((side > 0 and h >= tgt) or (side < 0 and l <= tgt)): return i, tgt, 'target', mae, mfe
        if tm >= flat: return i, c, 'close', mae, mfe
        if maxhold and (tm - b[i0][0] + 1) >= maxhold: return i, c, 'time', mae, mfe
        if trail: stp = trail(stp, i, b, side, eP, mfe)
    return len(b) - 1, b[-1][4], 'close', mae, mfe

def v4_trades(days, F, tf=5, tgtR=2.0, maxhold=0, lastEntry=780, stopMode='opp', orMin=15, bias=v4bias, first_only=True,
              sigFrac=.5, minBody=.3, minStop=16, stopFrac=None, flat=955):
    """faithful port of engine simRT2 (retest setup only, stop=opp). Returns list of trade dicts (per 1 contract)."""
    out = []
    for d, b1 in days:
        f = F.get(d); s = bias(f) if f else 0
        if not s: continue
        b = agg(b1, tf)
        if len(b) < 20 or b[0][0] != 570: continue
        n = max(1, round(orMin / tf)); hi = max(x[2] for x in b[:n]); lo = min(x[3] for x in b[:n])
        dr = 0; saw = False; ext = None; pend = None; ntr = 0
        i = n
        while i < len(b):
            tm, o, h, l, c = b[i]
            if pend:
                p = pend; pend = None
                if tm <= lastEntry and ((p['side'] > 0 and h >= p['lvl']) or (p['side'] < 0 and l <= p['lvl'])):
                    side = p['side']; eP = (max(o, p['lvl']) if side > 0 else min(o, p['lvl'])) + side * SLIP * T
                    stp = p['stp']; r = abs(eP - stp); tgt = eP + side * tgtR * r if tgtR else None
                    if (side > 0 and l <= stp) or (side < 0 and h >= stp):
                        xi, xP, why, mae, mfe = i, stp - side * SLIP * T, 'stop', r, 0
                    else:
                        xi, xP, why, mae, mfe = manage(b, i + 1, side, eP, stp, tgt, maxhold, flat)
                        # same-bar MFE/MAE of entry bar
                    pts = (xP - eP) * side
                    out.append(dict(d=d, side=side, eT=tm, eP=eP, stp=stp, r=r, xT=b[xi][0], xP=xP, why=why, pts=pts,
                                    pnl=pts * PV - 2 * COMM, R=pts / r, maeR=mae / r, mfeR=mfe / r, f=f, orw=hi - lo))
                    ntr += 1; dr = 0; saw = False; ext = None
                    if first_only: break
                    i = xi + 1; continue
            if tm >= 955 or tm > lastEntry: i += 1; continue
            mm = (tm // 60 * 100 + tm % 60) % 100
            closes5 = ((mm + tf) % 5) == 0
            rg = h - l
            bull = c > o and rg > 0 and (c - l) >= sigFrac * rg and abs(c - o) >= minBody * rg
            bear = c < o and rg > 0 and (h - c) >= sigFrac * rg and abs(c - o) >= minBody * rg
            inside = lo <= c <= hi
            if closes5 and c > hi:
                if dr != 1: dr = 1; saw = False; ext = None
            elif closes5 and c < lo:
                if dr != -1: dr = -1; saw = False; ext = None
            if inside and dr != 0: dr = 0; saw = False; ext = None
            if dr != 0:
                edge = hi if dr > 0 else lo
                touch = l <= edge if dr > 0 else h >= edge
                if touch:
                    saw = True; ext = (l if ext is None else min(ext, l)) if dr > 0 else (h if ext is None else max(ext, h))
                if saw and not inside and (bull if dr > 0 else bear) and dr == s:
                    lvl = h + T if dr > 0 else l - T
                    if stopMode == 'opp': stp = lo - T if dr > 0 else hi + T
                    elif stopMode == 'mid': stp = (hi + lo) / 2 - dr * T
                    elif stopMode == 'ext': stp = ext - dr * T
                    elif stopMode == 'adr': stp = lvl - dr * stopFrac * f['adr']
                    rr = abs(lvl + dr * SLIP * T - stp)
                    if rr < minStop * T: stp = lvl + dr * SLIP * T - dr * minStop * T
                    pend = dict(side=dr, lvl=lvl, stp=round(stp / T) * T)
            i += 1
    return out

def summary(tr, a=None, z=None, cost_pts=0.0):
    t = [x for x in tr if (a is None or x['d'] >= a) and (z is None or x['d'] <= z)]
    if not t: return dict(n=0, pf=0, wr=0, avgR=0, net=0)
    R_ = [x['R'] - (2 * COMM / PV) / x['r'] - cost_pts / x['r'] for x in t]
    gp = sum(r for r in R_ if r > 0); gl = -sum(r for r in R_ if r <= 0)
    eq = pk = dd = 0
    for r in R_: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    return dict(n=len(t), pf=round(gp / gl, 2) if gl else 9.9, wr=round(100 * sum(r > 0 for r in R_) / len(R_)), avgR=round(sum(R_) / len(R_), 3),
                totR=round(sum(R_), 1), ddR=round(dd, 1))

def yearly(tr):
    return ' '.join(f"{y % 100}:{summary(tr, y * 10000 + 101, y * 10000 + 1231)['pf']:.2f}" for y in range(2022, 2027))
