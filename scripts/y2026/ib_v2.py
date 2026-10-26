"""Inside-bar breakout v1 (live Pine) vs v2 (key-level targets + room filter), plus trend-day pullback (TPB). Oct 26 2026.
Bars: common.DB (RTH 1m, to 2026-10-23) + today's TV 1m (data/live/mnq_1m_2026-10-26.csv).
HTF trend = close vs EMA21 of the last COMPLETED 15/60/240m bar, 2 of 3 (RTH-only bars: approximation of Pine's ETH HTF).
Costs per MNQ: 2 x 2.37 commission, entry 1 tick against, stop exits 1 tick (walk), optional extra stop slip stress.
All trades flat at 15:59 (Pine IB has no time exit; this is a backtest convention)."""
import os, sys, csv, collections, math, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
T = 0.25; COMM = 2.37; PV = 2.0
ROOT = '/home/claude/mnq-quant'

# ---------- data ----------
DB = dict(C.DB); F = dict(C.F); D = list(C.D)
TODAY = 20261026
rows = list(csv.DictReader(open(f'{ROOT}/data/live/mnq_1m_2026-10-26.csv')))
tb = [(int(r['time_et'][:2]) * 60 + int(r['time_et'][2:]), float(r['o']), float(r['h']), float(r['l']), float(r['c'])) for r in rows]
DB[TODAY] = [b for b in tb if 570 <= b[0] < 960]
pre = [b for b in tb if b[0] < 570]
F[TODAY] = dict(pdh=29325.75, pdl=28986.25, pdc=29122.25, open=DB[TODAY][0][1],
                orh=max(b[2] for b in DB[TODAY][:15]), orl=min(b[3] for b in DB[TODAY][:15]), adr=F[D[-1]]['adr'])
if TODAY not in D: D.append(TODAY)

# overnight high/low (18:00 prior evening .. 9:29) from ETH 5m; today: only 8:15-9:29 TV bars + reported levels unknown -> use pre-open bars
ON = {}
for line in open(f'{ROOT}/data/raw/mnq_eth_5m.txt'):
    p = line.strip().split('|'); d = int(p[0]); hs = []; ls = []
    for x in p[1:]:
        t, o, h, l, c = map(int, x.split(','))
        if t >= 1800 or t < 930: hs.append(h / 4); ls.append(l / 4)
    if hs: ON[d] = (max(hs), min(ls))
ON[TODAY] = (max(b[2] for b in pre), min(b[3] for b in pre))   # partial (8:15-9:29) for today

# ---------- HTF trend (ETH 5m, session-anchored 18:00, like Pine on a 24h chart) ----------
def _eth_bars():
    out = []
    for line in open(f'{ROOT}/data/raw/mnq_eth_5m.txt'):
        p = line.strip().split('|'); d = int(p[0])
        for x in p[1:]:
            t, o, h, l, c = map(int, x.split(','))
            hh, mm = divmod(t, 100); tm = hh * 60 + mm
            sm = tm - 1080 if t >= 1800 else tm + 360
            out.append((d, sm, c / 4))
    return out
_ETH = _eth_bars()
def htf_events(tf):
    """dict d -> sorted list of (start_sm_of_bar, dir) for completed tf bars; dir known for bars starting later."""
    k = 2 / 22; ema = None; ev = collections.defaultdict(list); cur = None
    for d, sm, c in _ETH + [(None, None, None)]:
        g = None if d is None else (d, sm // tf)
        if cur is not None and g != cur[0]:
            (cd, gi), cc = cur[0], cur[1]
            ema = cc if ema is None else ema + k * (cc - ema)
            ev[cd].append((gi * tf, 1 if cc > ema else -1))
        if d is None: break
        cur = (g, c)
    return ev
EV = {tf: htf_events(tf) for tf in (15, 60, 240)}
TODAY_TREND = lambda m: -1 if m < 600 else 1        # today: read off the live chart (IB trend box), ETH file ends Oct 20
def _dir(tf, d, m):
    sm = m + 360; cur_start = sm // tf * tf; last = 0
    for st, dr in EV[tf].get(d, ()):
        if st < cur_start: last = dr
        else: break
    return last
_TC = {}
def trend(d, m):
    if d == TODAY: return TODAY_TREND(m)
    key = (d, m)
    if key not in _TC:
        v = _dir(15, d, m) + _dir(60, d, m) + _dir(240, d, m)
        _TC[key] = 1 if v > 0 else (-1 if v < 0 else 0)
    return _TC[key]

def agg(b, tf):
    if tf == 1: return list(b)
    g = collections.OrderedDict()
    for x in b:
        k = 570 + (x[0] - 570) // tf * tf
        if k not in g: g[k] = [k, x[1], x[2], x[3], x[4]]
        else: a = g[k]; a[2] = max(a[2], x[2]); a[3] = min(a[3], x[3]); a[4] = x[4]
    return [tuple(v) for v in g.values()]

def walk1(b1, m0, s, e, stp, tgt):
    """walk 1m bars with minute >= m0. stop first. flat 15:59 close."""
    for x in b1:
        m, o, h, l, c = x
        if m < m0: continue
        if (s > 0 and l <= stp) or (s < 0 and h >= stp): return m, stp - s * T, 'stop'
        if (s > 0 and h >= tgt) or (s < 0 and l <= tgt): return m, tgt, 'target'
        if m >= 959: return m, c, 'time'
    x = b1[-1]; return x[0], x[4], 'time'

def levels(d, m, b1, rnd):
    f = F[d]; L = [f['pdh'], f['pdl'], f['pdc']]
    if d in ON: L += list(ON[d])
    if m >= 585: L += [f['orh'], f['orl']]
    pr = [x for x in b1 if x[0] < m - 1]
    if pr: L += [max(x[2] for x in pr), min(x[3] for x in pr)]
    return L, rnd

def nearest(L, rnd, e, s):
    c = [x for x in L if (x - e) * s > 2 * T]
    if rnd:
        r = (math.floor(e / 100) + (1 if s > 0 else 0)) * 100
        if (r - e) * s <= 2 * T: r += 100 * s
        c.append(r)
    if not c: return None
    return min(c, key=lambda x: (x - e) * s)

def eff_at(b1, m):
    xs = [x for x in b1 if x[0] < m]
    if not xs: return 0, 0
    o = xs[0][1]; c = xs[-1][4]; hi = max(x[2] for x in xs); lo = min(x[3] for x in xs)
    return (abs(c - o) / (hi - lo) if hi > lo else 0), (1 if c > o else -1)

def ib(tf=1, k=0.0, cap=1.0, dayf='none', rnd=False, a=20220101, z=29991231, expiry=30, last=945, keep=False):
    """k = min room/R (0 = off); cap = max target in R (target = min(level, cap R); cap=1 & k=0 -> v1).
    dayf: none | outside (price outside prior-day range at entry) | eff (after 10:30, first hour eff >= .5 in trade dir)."""
    out = []
    for d in D:
        if d < a or d > z or d not in DB or d not in F: continue
        b1 = DB[d]; b = agg(b1, tf)
        armed = False; busy_until = -1
        fh = None
        for i in range(1, len(b)):
            m, o, h, l, c = b[i]
            mend = m + tf - 1                       # last minute of this bar
            if armed:
                upo = min(o, c) > mbH; dno = max(o, c) < mbL
                if upo or dno:
                    s = 1 if upo else -1; armed = False
                    if 570 <= m and mend < last and mend >= busy_until and s == trend(d, mend):
                        e = c + s * T; stp = (mbL - T) if s > 0 else (mbH + T); r = abs(e - stp)
                        ok = 5 <= r <= (80 if tf == 1 else 120)
                        if ok and dayf == 'outside':
                            f = F[d]; ok = (s > 0 and c > f['pdh']) or (s < 0 and c < f['pdl'])
                        if ok and dayf == 'eff':
                            if mend < 630: ok = False
                            else:
                                ef, dr = eff_at(b1, 630); ok = ef >= .5 and dr == s
                        if ok:
                            L, rr = levels(d, mend, b1, rnd); lv = nearest(L, rr, e, s)
                            room = (abs(lv - e) - T) if lv is not None else 1e9
                            if k > 0 and room < k * r: ok = False
                        if ok:
                            tg = e + s * min(room if k > 0 or cap > 1 else r, cap * r)
                            if cap == 1 and k == 0: tg = e + s * r
                            xm, xp, why = walk1(b1, mend + 1, s, e, stp, tg)
                            pts = (xp - e) * s
                            out.append(dict(d=d, strat='IB', side=s, eT=mend + 1, eP=e, stp=stp, xT=xm + 1, xP=xp, why=why, r=r, pts=pts, be=None, w=1.0, tgR=abs(tg - e) / r))
                            busy_until = xm + 1
                    continue
                if i - mbI > expiry: armed = False
            if not armed and h <= b[i - 1][2] and l >= b[i - 1][3]:
                armed = True; mbH = b[i - 1][2]; mbL = b[i - 1][3]; mbI = i - 1
    return out

def tpb(th=.5, tg='2R', a=20220101, z=29991231, maxn=2, keep=False):
    """trend-day pullback: at 10:30 first-hour eff >= th sets direction. 10:30-14:30 on 5m: bar touches EMA20(5m) and closes
    back beyond it in trend dir with a trend-colored body -> enter at close; stop = 3-bar extreme -1 tick; target 1.5R/2R/'hod'
    (retest of day extreme so far, min 1R); flat 15:59."""
    out = []; ema = None; kk = 2 / 21
    for d in D:
        if d not in DB or d not in F: continue
        b1 = DB[d]; b = agg(b1, 5)
        emas = []
        for x in b:
            ema = x[4] if ema is None else ema + kk * (x[4] - ema); emas.append(ema)
        if d < a or d > z: continue
        ef, s = eff_at(b1, 630)
        if ef < th: continue
        n = 0; busy = -1
        for i in range(3, len(b)):
            m, o, h, l, c = b[i]; mend = m + 4
            if mend < 630 or m >= 870 or mend < busy or n >= maxn: continue
            em = emas[i - 1]
            touch = (l <= em and c > em and c > o) if s > 0 else (h >= em and c < em and c < o)
            if not touch: continue
            e = c + s * T
            stp = (min(x[3] for x in b[i - 2:i + 1]) - T) if s > 0 else (max(x[2] for x in b[i - 2:i + 1]) + T)
            r = abs(e - stp)
            if r < 5 or r > 120: continue
            if tg == 'hod':
                pr = [x for x in b1 if x[0] <= mend]
                ext = max(x[2] for x in pr) if s > 0 else min(x[3] for x in pr)
                tgt = e + s * max(r, abs(ext - e))
            else:
                tgt = e + s * float(tg[:-1]) * r
            xm, xp, why = walk1(b1, mend + 1, s, e, stp, tgt)
            out.append(dict(d=d, strat='TPB', side=s, eT=mend + 1, eP=e, stp=stp, xT=xm + 1, xP=xp, why=why, r=r, pts=(xp - e) * s, be=None, w=1.0))
            n += 1; busy = xm + 1
    return out

def stats(tr, a, z, slipx=0.0):
    v = [((t['pts'] - (slipx if t['why'] == 'stop' else 0)) * PV - 2 * COMM) for t in tr if a <= t['d'] <= z]
    R = [((t['pts'] - (slipx if t['why'] == 'stop' else 0)) - 2 * COMM / PV) / t['r'] for t in tr if a <= t['d'] <= z]
    if not v: return dict(n=0, wr=0, pf=0, avgR=0, net=0)
    gw = sum(x for x in v if x > 0); gl = -sum(x for x in v if x < 0)
    return dict(n=len(v), wr=round(sum(x > 0 for x in v) / len(v), 3), pf=round(gw / gl, 2) if gl else 99, avgR=round(sum(R) / len(R), 3), net=round(sum(v)))
BL = dict(IS=(20220101, 20241231), VAL=(20250101, 20251231), Y26=(20260101, 20261023))
