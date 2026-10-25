"""Trend-day continuation, entered on a pullback after 10:30 (Oct 25 2026).
Day filter at 10:30: first-hour efficiency |close10:29 - open| / first-hour range >= E, and price outside the prior-day range in that direction.
Entry modes (long shown; short mirrored):
  'retrace': limit buy at dayHigh - k * firstHourRange (day high updates while waiting)
  'resume' : after a retrace of k * FHR from the high, buy when a 5m bar closes above the prior 5m bar high (next 1m open)
  'retest' : limit buy at the prior-day high (the broken level) + 0
Stop: 'pb' = below the pullback low (lowest low since the high) - buf; 'adr' = entry - a * ADR; 'mid' = first-hour midpoint.
Exits: target R multiple, max hold minutes, optional half off at 1R + breakeven, flat 15:55. One trade per day.
Costs: 2.37/side + 1 tick slip on entry and stops (limit fills assume price trades 1 tick through)."""
from base import *
T = .25; PV = 2; COMM = 2.37
DD = []
for d, b in DAYS:
    if d not in FEAT or len(b) < 380 or b[59][0] != 629: continue
    f = FEAT[d]; o = b[0][1]
    h1 = max(x[2] for x in b[:60]); l1 = min(x[3] for x in b[:60]); p = b[59][4]
    eff = abs(p - o) / ((h1 - l1) or 1)
    s = 1 if p > o else -1
    out = (p > f['pdh']) if s > 0 else (p < f['pdl'])
    DD.append((d, b, f, s, eff, out, h1, l1))
def run(E=.6, need_out=True, mode='retrace', k=.33, stop='pb', a=.25, buf=.05, R=1.5, hold=120, half=False, tend=780, minR=10):
    tr = []
    for d, b, f, s, eff, out, h1, l1 in DD:
        if eff < E or (need_out and not out): continue
        adr = f['adr']; fhr = h1 - l1
        ext = h1 if s > 0 else l1     # running extreme in the trend direction
        pbx = None                    # pullback extreme (lowest low since the extreme, for longs)
        armed = False; e = None
        for i in range(60, len(b)):
            m, o, h, l, c = b[i]
            if m >= tend: break
            if mode == 'retrace':
                lvl = ext - s * k * fhr
                if (s > 0 and l <= lvl - T) or (s < 0 and h >= lvl + T):
                    e = min(o, lvl) if s > 0 else max(o, lvl); ei = i; pbx = l if s > 0 else h; break
            elif mode == 'retest':
                lvl = f['pdh'] if s > 0 else f['pdl']
                if (s > 0 and l <= lvl - T) or (s < 0 and h >= lvl + T):
                    e = min(o, lvl) if s > 0 else max(o, lvl); ei = i; pbx = l if s > 0 else h; break
            elif mode == 'resume':
                pbx = l if pbx is None else (min(pbx, l) if s > 0 else max(pbx, h))
                if (ext - pbx) * s >= k * fhr: armed = True
                # 5m bar closes at minutes ending in 4/9
                if armed and (m - 570) % 5 == 4 and i >= 9:
                    cur = b[i - 4:i + 1]; prv = b[i - 9:i - 4]
                    ch = cur[-1][4]; ph = max(x[2] for x in prv); pl = min(x[3] for x in prv)
                    if (s > 0 and ch > ph) or (s < 0 and ch < pl):
                        if i + 1 < len(b): e = b[i + 1][1] + s * T; ei = i + 1; break
            # update extreme after checking entry
            if (s > 0 and h > ext) or (s < 0 and l < ext):
                ext = h if s > 0 else l; pbx = None; armed = False
        if e is None: continue
        if stop == 'pb':
            # pullback extreme: lowest low between the last extreme and entry bar
            stp = (pbx if pbx is not None else e) - s * buf * adr
            if mode == 'retrace' or mode == 'retest': stp = e - s * max(buf * adr, 0)  # for limits, pbx is unknown yet: use buffer below entry
        elif stop == 'adr': stp = e - s * a * adr
        else: stp = (h1 + l1) / 2
        r = (e - stp) * s
        if r < minR: stp = e - s * minR; r = minR
        tgt = e + s * R * r if R else None
        pts = 0; q = 1.0; be = False; st_ = stp; res = None
        for j in range(ei, len(b)):
            m, o, h, l, c = b[j]
            if j == ei and mode != 'resume':
                # limit fill bar: only allow the stop/target check if the bar's extreme came after the fill (unknown) -> check stop only
                if (s > 0 and l <= st_) or (s < 0 and h >= st_): res = q * ((st_ - s * T - e) * s); break
                continue
            if (s > 0 and l <= st_) or (s < 0 and h >= st_):
                res = pts + q * ((st_ - (0 if be else s * T) - e) * s); why = 'breakeven' if be else 'stop'; break
            if half and not be and ((s > 0 and h >= e + s * r) or (s < 0 and l <= e - r)) and not ((s > 0 and h >= e + s * r) and False):
                pts += .5 * r; q = .5; be = True; st_ = e
            if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)):
                res = pts + q * R * r; why = 'target'; break
            if m >= min(955, b[ei][0] + hold):
                res = pts + q * (c - e) * s; why = 'time exit'; break
        if res is None: res = pts + q * (b[-1][4] - e) * s; why = 'time exit'; j = len(b) - 1
        tr.append(dict(d=d, net=res * PV - 2 * COMM, R=res / r, risk=r, em=b[ei][0], s=s, eP=e, stp=stp, xT=b[j][0], pts=res, why=why))
    return tr
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def st(tr):
    A = [t['net'] for t in tr if t['d'] <= 20241231]; Z = [t['net'] for t in tr if t['d'] > 20241231]
    yr = {y: pf([t['net'] for t in tr if t['d'] // 10000 == y]) for y in range(2022, 2027)}
    return dict(nA=len(A), nZ=len(Z), pfA=pf(A), pfZ=pf(Z), win=round(sum(x > 0 for x in A + Z) / max(1, len(A + Z)), 2),
                avgR=round(sum(t['R'] for t in tr) / max(1, len(tr)), 2), yr=yr, yrs=sum(v > 1 for v in yr.values()))
