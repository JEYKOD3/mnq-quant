"""Backtest of the online 'eval pass' shortlist (knowledge/PASS_STRATEGIES_CATALOG.md, Oct 26 2026) + the friend's mother candle
(1m 9:30-10:30, 5m pre-open 9:00-9:30) + the trend-filtered ORB (S4).
Data: RTH 1m (common.DB, 9:30-16:00), ETH 5m (mnq_eth_5m.txt, 18:00-16:55; no 1m before 9:30), 5m continuous with volume (VWAP, EMA200, HTF).
Costs: 2.37/side, 1 tick entry slip, 1 tick stop slip (walk), plus 'slip8' column = extra 8 pt on stop exits (engine convention).
Blocks: IS 2022-2024 (design / tuning, max 2 params), VAL 2025, 2026 YTD. Survivor = net > 0 in all three blocks and n_IS >= 60.
Usage: python3 pass_tested.py scan -> pass_scan.json ; python3 pass_tested.py eval -> pass_eval.json"""
import os, sys, json, collections, statistics, bisect, gzip, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
from common import walk, mk, D, DB, F, EV, SLIP, T, COMM, PV
HERE = os.path.dirname(os.path.abspath(__file__))
BLK = {'IS': (20220101, 20241231), 'VAL': (20250101, 20251231), '2026': (20260101, 20261231)}
NY = ZoneInfo('America/New_York')

# ---------- ETH 5m per session date: m = minutes from midnight of d (evening part negative) ----------
ETH = {}
for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
    p = ln.strip().split('|')
    if len(p) < 2: continue
    bars = []
    for x in p[1:]:
        t, o, h, l, c = x.split(','); t = int(t); m = t // 100 * 60 + t % 100
        if t >= 1800: m -= 1440
        bars.append((m, int(o) / 4, int(h) / 4, int(l) / 4, int(c) / 4))
    ETH[int(p[0])] = bars

# ---------- 5m continuous with volume ----------
C5 = []   # (epoch_end, d, m_start, o, h, l, c, v)
with gzip.open('/home/claude/mnq-quant/data/raw/MNQ_5m_cont.csv.gz', 'rt') as fh:
    next(fh)
    for ln in fh:
        t, o, h, l, c, v = ln.split(','); t = int(t)
        dt = datetime.datetime.fromtimestamp(t, NY)
        C5.append((t + 300, int(dt.strftime('%Y%m%d')), dt.hour * 60 + dt.minute, float(o), float(h), float(l), float(c), float(v)))
def ema_series(vals, n):
    k = 2 / (n + 1); out = []; e = None
    for x in vals: e = x if e is None else e + k * (x - e); out.append(e)
    return out
E200 = ema_series([x[6] for x in C5], 200)
C5END = [x[0] for x in C5]
def htf(tf):
    """completed tf-minute bars: (end_epoch list, close list, ema21 list)"""
    g = collections.OrderedDict()
    for x in C5:
        k = (x[0] - 300) // (tf * 60)
        g[k] = x[6]
    ks = list(g.keys()); cl = list(g.values()); em = ema_series(cl, 21)
    return [(k + 1) * tf * 60 for k in ks], cl, em
HTF = {tf: htf(tf) for tf in (15, 60, 240)}
def epoch(d, m):
    y, mo, dd = d // 10000, d // 100 % 100, d % 100
    return int(datetime.datetime(y, mo, dd, tzinfo=NY).timestamp()) + m * 60
def bias(d, m):
    """majority of 15m/1h/4h: close of last completed bar vs its EMA21. +1 / -1 / 0"""
    e = epoch(d, m); s = 0
    for tf, (ends, cl, em) in HTF.items():
        i = bisect.bisect_right(ends, e) - 1
        if i < 0: return 0
        s += 1 if cl[i] > em[i] else -1
    return 1 if s >= 2 else -1 if s <= -2 else 0
def vwap_ema(d, m):
    """at minute m (RTH): last completed 5m bar close, session VWAP from 9:30, EMA200(5m continuous)."""
    e = epoch(d, m); i = bisect.bisect_right(C5END, e) - 1
    if i < 0 or C5[i][1] != d or C5[i][2] < 570: return None
    pv = vv = 0.0; j = i
    while j >= 0 and C5[j][1] == d and C5[j][2] >= 570:
        tp = (C5[j][4] + C5[j][5] + C5[j][6]) / 3; pv += tp * C5[j][7]; vv += C5[j][7]; j -= 1
    if vv <= 0: return None
    return C5[i][6], pv / vv, E200[i]

def fw(name, d, b, i, s, eP, stp, tgt, tend, **kw):
    """enter during bar i at eP (bar i may still hit stop; target needs close beyond), then walk from i+1."""
    m, o, h, l, c = b[i]
    if (s > 0 and l <= stp) or (s < 0 and h >= stp): return mk(d, name, s, m, eP, stp, i, stp - s * SLIP * T, 'stop', None, b)
    if tgt is not None and ((s > 0 and c >= tgt) or (s < 0 and c <= tgt)): return mk(d, name, s, m, eP, stp, i, tgt, 'target', None, b)
    xi, xP, why, rf = walk(b, i + 1, s, eP, stp, tgt, tend, **kw)
    return mk(d, name, s, m, eP, stp, xi, xP, why, rf, b)
def fw_next(name, d, b, i, s, stp, tgt, tend, **kw):
    """market entry at the open of bar i (+slip), walk from i (stop/target on the entry bar count)."""
    eP = b[i][1] + s * SLIP * T
    xi, xP, why, rf = walk(b, i, s, eP, stp, tgt, tend, **kw)
    return mk(d, name, s, b[i][0], eP, stp, xi, xP, why, rf, b)
def agg5(b):
    g = collections.OrderedDict()
    for m, o, h, l, c in b:
        k = m - (m - 570) % 5
        if k not in g: g[k] = [k, o, h, l, c]
        else: a = g[k]; a[2] = max(a[2], h); a[3] = min(a[3], l); a[4] = c
    return [tuple(v) for v in g.values()]
def idx_at(b, m):
    for i, x in enumerate(b):
        if x[0] >= m: return i
    return None

# ---------- SL1 ORB15 50% target ----------
def sl1(tgtm=.5, wmax=.008, cap=50, last=660):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 60 or b[0][0] != 570: continue
        R = [x for x in b if x[0] < 585]; hi = max(x[2] for x in R); lo = min(x[3] for x in R); W = hi - lo
        if W > wmax * b[0][1] or W < 10: continue
        b5 = agg5(b)
        for k, (m, o, h, l, c) in enumerate(b5):
            if m < 585 or m + 5 > last: continue
            s = 1 if c > hi else -1 if c < lo else 0
            if not s: continue
            i = idx_at(b, m + 5)
            if i is None: break
            eP = b[i][1] + s * SLIP * T
            stp = (lo - T) if s > 0 else (hi + T)
            if abs(eP - stp) > min(W, cap): stp = eP - s * min(W, cap)
            tgt = eP + s * tgtm * W
            xi, xP, why, rf = walk(b, i, s, eP, stp, tgt, 955)
            out.append(mk(d, 'SL1', s, b[i][0], eP, stp, xi, xP, why, rf, b)); break
    return out

# ---------- SL2 IB 25% retrace continuation ----------
def sl2(ret=.25, tgtmode='pdh'):
    out = []
    for d in D:
        b = DB[d]; f = F.get(d)
        if not f or len(b) < 120 or b[0][0] != 570 or not f.get('pdh'): continue
        pdh, pdl = f['pdh'], f['pdl']; op = b[0][1]
        if not (pdl < op < pdh): continue
        ib = [x for x in b if x[0] < 630]; H = max(x[2] for x in ib); L = min(x[3] for x in ib); W = H - L
        c1029 = ib[-1][4]; s = 1 if c1029 > op else -1 if c1029 < op else 0
        if not s or W < 8: continue
        lvl = H if s > 0 else L
        E = lvl - s * ret * W; stp = lvl - s * .5 * W - s * T; inv = lvl - s * .5 * W
        broke = None
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 630: continue
            if broke is None:
                if m >= 780: break
                if (s > 0 and h > H) or (s < 0 and l < L): broke = i
                continue
            if m >= 840: break
            if (s > 0 and l <= E - T) or (s < 0 and h >= E + T):
                r = abs(E - stp)
                if tgtmode == 'pdh':
                    pt = pdh if s > 0 else pdl
                    tgt = pt if (pt - E) * s >= r else E + s * 2 * r
                else: tgt = E + s * float(tgtmode) * r
                out.append(fw('SL2', d, b, i, s, E, stp, tgt, 955)); break
            if (s > 0 and l < inv) or (s < 0 and h > inv): break
    return out

# ---------- hour-9 range incl. pre-open 5m ----------
def h9(d):
    e = [x for x in ETH.get(d, []) if 540 <= x[0] < 570]; r = [x for x in DB[d] if x[0] < 600]
    if len(e) < 6 or len(r) < 30: return None
    return max([x[2] for x in e + r]), min([x[3] for x in e + r])

# ---------- SL3 9:00 hour sweep fade 10-11 ----------
def sl3(tgtmode='opp', rmax=40):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 150 or b[0][0] != 570: continue
        hl = h9(d)
        if not hl: continue
        H9, L9 = hl; sw = None; hh = -1e9; ll = 1e9
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 600: continue
            if m >= 660: break
            hh = max(hh, h); ll = min(ll, l)
            if sw is None:
                if h > H9 and l < L9: break
                if h > H9: sw = (1, i)
                elif l < L9: sw = (-1, i)
            if sw is not None:
                side, i0 = sw
                if i - i0 > 5: sw = None; continue
                if (side > 0 and c < H9) or (side < 0 and c > L9):
                    s = -side; eP = c + s * SLIP * T
                    stp = (hh + T) if s < 0 else (ll - T); r = abs(eP - stp)
                    tgt = (L9 if s < 0 else H9) if tgtmode == 'opp' else ((H9 + L9) / 2 if tgtmode == 'mid' else eP + s * 2 * r)
                    if r > rmax or r <= 0 or (tgt - eP) * s < r: break
                    xi, xP, why, rf = walk(b, i + 1, s, eP, stp, tgt, 719)
                    out.append(mk(d, 'SL3', s, m, eP, stp, xi, xP, why, rf, b)); break
    return out

# ---------- SL4 Asia sweep reversal in London (5m) ----------
NEWS830 = {'NFP', 'CPI', 'PPI'}
def walk5(b, i0, s, eP, stp, tgt, tend):
    for j in range(i0, len(b)):
        m, o, h, l, c = b[j]
        if (s > 0 and l <= stp) or (s < 0 and h >= stp): return j, stp - s * SLIP * T, 'stop'
        if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)): return j, tgt, 'target'
        if m >= tend: return j, o, 'time exit'
    return len(b) - 1, b[-1][4], 'time exit'
def sl4(tgtmode='opp', rmax=40):
    out = []
    for d in D:
        if NEWS830 & EV.get(d, set()): continue
        b = ETH.get(d)
        if not b: continue
        asia = [x for x in b if -240 <= x[0] < 0]
        if len(asia) < 40: continue
        AH = max(x[2] for x in asia); AL = min(x[3] for x in asia)
        sh = sl_ = False; hh = -1e9; ll = 1e9
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 120: continue
            if m >= 300: break
            hh = max(hh, h); ll = min(ll, l)
            if h > AH: sh = True
            if l < AL: sl_ = True
            if sh and sl_: break
            s = -1 if (sh and c < AH) else 1 if (sl_ and c > AL) else 0
            if not s or i + 1 >= len(b): continue
            eP = b[i + 1][1] + s * SLIP * T
            stp = hh + 2 if s < 0 else ll - 2; r = abs(eP - stp)
            tgt = (AL if s < 0 else AH) if tgtmode == 'opp' else ((AH + AL) / 2 if tgtmode == 'mid' else eP + s * 2 * r)
            if r > rmax or r <= 0 or (tgt - eP) * s < r: break
            xi, xP, why = walk5(b, i + 1, s, eP, stp, tgt, 565)
            out.append(dict(d=d, strat='SL4', side=s, eT=b[i + 1][0], eP=eP, stp=stp, xT=b[xi][0] + 5, xP=xP, why=why, r=r, pts=(xP - eP) * s, be=None, w=1.0)); break
    return out

# ---------- SL5 hourly sweep back to hour open ----------
def sl5(minleg=10, cap=25, hours=(600, 660, 780, 840)):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 380 or b[0][0] != 570: continue
        nday = 0
        for hs in hours:
            if nday >= 3: break
            if hs == 600:
                hl = h9(d)
                if not hl: continue
                Ph, Pl = hl
            else:
                pr = [x for x in b if hs - 60 <= x[0] < hs]
                if len(pr) < 50: continue
                Ph = max(x[2] for x in pr); Pl = min(x[3] for x in pr)
            cur = [(i, x) for i, x in enumerate(b) if hs <= x[0] < hs + 60]
            if len(cur) < 50: continue
            Oh = cur[0][1][1]
            if not (Pl < Oh < Ph): continue
            side = 0; ext = None
            for i, (m, o, h, l, c) in cur:
                if not side:
                    if h > Ph and l < Pl: break
                    if h > Ph: side = 1; ext = h
                    elif l < Pl: side = -1; ext = l
                    if not side: continue
                ext = max(ext, h) if side > 0 else min(ext, l)
                if (side > 0 and c < Ph) or (side < 0 and c > Pl):
                    s = -side
                    if (Ph - Oh if side > 0 else Oh - Pl) < minleg: break
                    eP = c + s * SLIP * T; stp = ext + T if s < 0 else ext - T; r = abs(eP - stp)
                    if r > cap or r <= 0 or (Oh - eP) * s <= 0: break
                    xi, xP, why, rf = walk(b, i + 1, s, eP, stp, Oh, hs + 59)
                    out.append(mk(d, 'SL5', s, m, eP, stp, xi, xP, why, rf, b)); nday += 1; break
    return out

# ---------- SL6 VWAP + EMA200 side, 1m FVG limit, 15/15, BE ----------
def sl6(stopp=15., tgtp=15., be=8., gapmin=2.):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 120 or b[0][0] != 570: continue
        n = 0; won = False; busy_until = -1
        for j in range(2, len(b)):
            m = b[j][0]
            if m < 602: continue
            if m > 655 or n >= 2 or won: break
            if j <= busy_until: continue
            ve = vwap_ema(d, m + 1)
            if not ve: continue
            c5, vw, e2 = ve; s = 1 if (c5 > vw and c5 > e2) else -1 if (c5 < vw and c5 < e2) else 0
            if not s: continue
            a, mid, z = b[j - 2], b[j - 1], b[j]
            body = abs(mid[4] - mid[1]); rng = mid[2] - mid[3]
            if rng <= 0 or body < .6 * rng: continue
            if s > 0 and z[3] > a[2] and z[3] - a[2] >= gapmin and mid[4] > mid[1]: E = a[2]
            elif s < 0 and z[2] < a[3] and a[3] - z[2] >= gapmin and mid[4] < mid[1]: E = a[3]
            else: continue
            for k in range(j + 1, min(j + 11, len(b))):
                mm, o, h, l, c = b[k]
                if (s > 0 and l <= E - T) or (s < 0 and h >= E + T):
                    stp = E - s * stopp; tgt = E + s * tgtp
                    t = fw('SL6', d, b, k, s, E, stp, tgt, 690, be_R=be / stopp, be_off=1.0)
                    out.append(t); n += 1; won = t['pts'] > 0
                    busy_until = idx_at(b, t['xT']) or len(b); break
    return out

def s_any(c): return 0   # before 9:30 the open filter does not apply -> no trade for pre-open variants
# ---------- friend's mother candle ----------
TRIG = 'body'
MCMODE = 'one'   # 'one' = first trade only; 'win' = keep trading the setup after losses, stop after the first win (max 4/day)
def wmode(fn):
    def g():
        global MCMODE
        MCMODE = 'win'
        try: return fn()
        finally: MCMODE = 'one'
    return g
def trig(mode, fn):
    def g():
        global TRIG
        TRIG = mode
        try: return fn()
        finally: TRIG = 'body'
    return g
def mc_scan(b, s_win, e_win, tgtR, bf, d, name, tend=955, maxone=True):
    """mother bar + >=1 inside bars; box alive until a close beyond the opposite side; trigger = full body beyond MB in bias dir."""
    out = []
    i = 0
    while i < len(b) - 2:
        mb = b[i]
        if b[i + 1][2] <= mb[2] and b[i + 1][3] >= mb[3]:
            H, L = mb[2], mb[3]; k = i + 2; bside = None
            while k < len(b):
                m, o, h, l, c = b[k]
                if m >= e_win: break
                lo_b, hi_b = min(o, c), max(o, c)
                if TRIG == 'close': up = c > H; dn = c < L
                else: up = lo_b > H; dn = hi_b < L
                if bside is None and (c > H or c < L) and not (up or dn):
                    bside = 1 if c > H else -1; k += 1; continue      # first close beyond: box still alive on that side
                if bside is not None and ((bside > 0 and c < L) or (bside < 0 and c > H)): break   # close beyond the opposite side kills it
                if bside is not None and ((bside > 0 and dn) or (bside < 0 and up)): up = dn = False
                if up or dn:
                    s = 1 if up else -1
                    if m >= s_win and (bf is None or bf(m, c) == s):
                        eP = c + s * SLIP * T; stp = (L - T) if s > 0 else (H + T); r = abs(eP - stp)
                        if r > 0:
                            xi, xP, why, rf = walk(b, k + 1, s, eP, stp, eP + s * tgtR * r, tend)
                            out.append(mk(d, name, s, m, eP, stp, xi, xP, why, rf, b))
                            if MCMODE == 'one' or (MCMODE == 'win' and out[-1]['pts'] > 0) or len(out) >= 4: return out
                            i = xi; break
                    break
                k += 1
        i += 1
    return out
def mc1(tgtR=1., biasf=False, s_win=570, e_win=630):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 60 or b[0][0] != 570: continue
        bf = (lambda m, c, d=d: bias(d, m)) if biasf == True else (lambda m, c, o0=DB[d][0][1]: (1 if c > o0 else -1) if m >= 570 else s_any(c)) if biasf == 'open' else None
        out += mc_scan(b, s_win, e_win, tgtR, bf, d, f'MC1m')
    return out
def mc5pre(tgtR=1., biasf=False):
    """5m pre-open box (ETH 5m 8:00-9:25) breakout 9:00-9:30, then walked on 5m ETH to 9:25 and 1m RTH after."""
    out = []
    for d in D:
        e = [x for x in ETH.get(d, []) if 480 <= x[0] < 570]; r = DB[d]
        if len(e) < 12 or not r or r[0][0] != 570: continue
        b = e + r
        bf = (lambda m, c, d=d: bias(d, m)) if biasf == True else (lambda m, c, o0=DB[d][0][1]: (1 if c > o0 else -1) if m >= 570 else s_any(c)) if biasf == 'open' else None
        out += mc_scan(b, 540, 570, tgtR, bf, d, 'MC5pre')
    return out
def mc5(tgtR=1., biasf=False):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 60 or b[0][0] != 570: continue
        b5 = agg5(b)
        bf = (lambda m, c, d=d: bias(d, m)) if biasf == True else (lambda m, c, o0=DB[d][0][1]: (1 if c > o0 else -1) if m >= 570 else s_any(c)) if biasf == 'open' else None
        t = mc_scan(b5, 570, 630, tgtR, bf, d, 'MC5')
        # re-walk on 1m for honest exits (skip overlaps; in 'win' mode stop after the first 1m-walk win)
        lastx = -1
        for x in t:
            i = idx_at(b, x['eT'] + 5)
            if i is None or b[i][0] < lastx: continue
            if out and out[-1]['d'] == d and MCMODE == 'win' and out[-1]['pts'] > 0: break
            xi, xP, why, rf = walk(b, i, x['side'], x['eP'], x['stp'], x['eP'] + x['side'] * tgtR * x['r'], 955)
            out.append(mk(d, 'MC5', x['side'], b[i][0], x['eP'], x['stp'], xi, xP, why, rf, b)); lastx = out[-1]['xT']
    return out

# ---------- S4 trend-filtered ORB ----------
CL = {d: DB[d][-1][4] for d in D if DB[d]}
def sma_prior(d, n):
    i = D.index(d)
    if i < n: return None
    return statistics.mean(CL[x] for x in D[i - n:i])
_SMA = {}
def s4(orm=15, rr=2., n=200, cap=37.5):
    out = []
    for d in D:
        b = DB[d]
        if len(b) < 60 or b[0][0] != 570: continue
        key = (d, n)
        if key not in _SMA: _SMA[key] = sma_prior(d, n)
        sm = _SMA[key]
        if sm is None: continue
        s = 1 if b[0][1] > sm else -1
        R = [x for x in b if x[0] < 570 + orm]; hi = max(x[2] for x in R); lo = min(x[3] for x in R)
        for i, (m, o, h, l, c) in enumerate(b):
            if m < 570 + orm or m > 900: continue
            if (s > 0 and h >= hi + T) or (s < 0 and l <= lo - T):
                lvl = hi + T if s > 0 else lo - T
                eP = (max(o, lvl) if s > 0 else min(o, lvl)) + s * SLIP * T
                stp = (lo - T) if s > 0 else (hi + T)
                if abs(eP - stp) > cap: stp = eP - s * cap
                out.append(fw(f'S4', d, b, i, s, eP, stp, eP + s * rr * abs(eP - stp), 955)); break
    return out

FAM = {
    # rules as written
    'SL1 as written (.5W, .8%, cap50)': lambda: sl1(),
    'SL1 tgt .33W': lambda: sl1(tgtm=.33), 'SL1 tgt .75W': lambda: sl1(tgtm=.75), 'SL1 tgt 1.0W': lambda: sl1(tgtm=1.0),
    'SL1 W<.5%': lambda: sl1(wmax=.005), 'SL1 W<1.0%': lambda: sl1(wmax=.010), 'SL1 cap30': lambda: sl1(cap=30), 'SL1 cap75': lambda: sl1(cap=75),
    'SL2 as written (PDH else 2R)': lambda: sl2(), 'SL2 tgt 1R': lambda: sl2(tgtmode='1'), 'SL2 tgt 2R': lambda: sl2(tgtmode='2'),
    'SL2 retrace .33': lambda: sl2(ret=.33), 'SL2 retrace .15': lambda: sl2(ret=.15),
    'SL3 as written (opp side)': lambda: sl3(), 'SL3 tgt mid': lambda: sl3('mid'), 'SL3 tgt 2R': lambda: sl3('2r'), 'SL3 rmax 25': lambda: sl3(rmax=25),
    'SL4 as written (opp side)': lambda: sl4(), 'SL4 tgt mid': lambda: sl4('mid'), 'SL4 tgt 2R': lambda: sl4('2r'), 'SL4 rmax 25': lambda: sl4(rmax=25),
    'SL5 as written (10 pt leg, cap25)': lambda: sl5(), 'SL5 leg 20': lambda: sl5(minleg=20), 'SL5 cap 15': lambda: sl5(cap=15),
    'SL5 all RTH hours': lambda: sl5(hours=(600, 660, 720, 780, 840, 900)),
    'SL6 as written (15/15, BE+8)': lambda: sl6(), 'SL6 BE+5': lambda: sl6(be=5), 'SL6 BE+10': lambda: sl6(be=10), 'SL6 no BE': lambda: sl6(be=99),
    'SL6 gap>=4': lambda: sl6(gapmin=4), 'SL6 20/20': lambda: sl6(20, 20, 10),
    'MC 1m 9:30-10:30 1R': lambda: mc1(1.), 'MC 1m 9:30-10:30 2R': lambda: mc1(2.),
    'MC 1m 9:30-10:30 1R HTF bias': lambda: mc1(1., True), 'MC 1m 9:30-10:30 2R HTF bias': lambda: mc1(2., True),
    'MC 1m 9:30-9:45 1R HTF bias': lambda: mc1(1., True, 570, 585),
    'MC 5m pre-open 9:00-9:30 1R': lambda: mc5pre(1.), 'MC 5m pre-open 2R': lambda: mc5pre(2.),
    'MC 5m pre-open 1R HTF bias': lambda: mc5pre(1., True), 'MC 5m pre-open 2R HTF bias': lambda: mc5pre(2., True),
    'MC 5m 9:30-10:30 1R HTF bias': lambda: mc5(1., True), 'MC 5m 9:30-10:30 2R HTF bias': lambda: mc5(2., True),
    'MC 1m 9:30-10:30 1R close-trigger': trig('close', lambda: mc1(1.)), 'MC 1m 9:30-10:30 1R close-trigger HTF bias': trig('close', lambda: mc1(1., True)),
    'MC 5m pre-open 1R close-trigger': trig('close', lambda: mc5pre(1.)), 'MC 5m 9:30-10:30 1R close-trigger HTF bias': trig('close', lambda: mc5(1., True)),
    'MC 5m 9:30-10:30 1R': lambda: mc5(1.),
    'MCW 1m 9:30-10:30 1R stop-after-win': wmode(lambda: mc1(1.)), 'MCW 1m 9:30-10:30 1R stop-after-win HTF bias': wmode(lambda: mc1(1., True)),
    'MCW 1m 9:30-11:30 1R stop-after-win': wmode(lambda: mc1(1., False, 570, 690)), 'MCW 1m 9:30-11:30 1R stop-after-win HTF bias': wmode(lambda: mc1(1., True, 570, 690)),
    'MCW 1m 9:30-10:30 2R stop-after-win (cmp)': wmode(lambda: mc1(2.)),
    'MCW 5m pre-open 1R stop-after-win': wmode(lambda: mc5pre(1.)), 'MCW 5m pre-open 1R stop-after-win HTF bias': wmode(lambda: mc5pre(1., True)),
    'MCW 5m 9:30-10:30 1R stop-after-win': wmode(lambda: mc5(1.)), 'MCW 5m 9:30-10:30 1R stop-after-win HTF bias': wmode(lambda: mc5(1., True)),
    'MCW 5m 9:30-10:30 2R stop-after-win HTF bias (cmp)': wmode(lambda: mc5(2., True)),
    'MCW 1m 9:30-10:30 1R stop-after-win OPEN bias': wmode(lambda: mc1(1., 'open')), 'MCW 1m 9:30-11:30 1R stop-after-win OPEN bias': wmode(lambda: mc1(1., 'open', 570, 690)),
    'MCW 1m 9:30-10:30 2R stop-after-win OPEN bias (cmp)': wmode(lambda: mc1(2., 'open')),
    'MCW 5m 9:30-10:30 1R stop-after-win OPEN bias': wmode(lambda: mc5(1., 'open')), 'MCW 5m 9:30-10:30 2R stop-after-win OPEN bias (cmp)': wmode(lambda: mc5(2., 'open')),
    'S4 trend ORB15 2R SMA200': lambda: s4(), 'S4 ORB15 1.5R': lambda: s4(rr=1.5), 'S4 ORB15 3R': lambda: s4(rr=3.),
    'S4 ORB30 2R': lambda: s4(orm=30), 'S4 ORB15 2R SMA150': lambda: s4(n=150), 'S4 ORB15 2R cap50': lambda: s4(cap=50),
}

def net1(t, stopx=0.0): return (t['pts'] - (stopx if t['why'] in CM.STOPWHY else 0)) * PV - 2 * COMM
def stats(tr, a, z, stopx=0.0):
    v = [net1(t, stopx) for t in tr if a <= t['d'] <= z]
    if not v: return dict(n=0, net=0, pf=0, wr=0, avgR=0)
    g = sum(x for x in v if x > 0); L = -sum(x for x in v if x < 0)
    rr = [net1(t, stopx) / (t['r'] * PV + 2 * COMM) for t in tr if a <= t['d'] <= z and t['r'] > 0]
    return dict(n=len(v), net=round(sum(v)), pf=round(g / L, 2) if L else 99, wr=round(sum(x > 0 for x in v) / len(v), 2),
                avgR=round(statistics.mean(rr), 3), avg_risk_pts=round(statistics.mean(t['r'] for t in tr if a <= t['d'] <= z), 1))
def years(tr, stopx=0.0):
    return {y: stats(tr, y * 10000 + 101, y * 10000 + 1231, stopx) for y in range(2022, 2027)}

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if mode == 'scan':
        out = {}; CACHE = {}
        only = sys.argv[2] if len(sys.argv) > 2 else None
        for nm, fn in FAM.items():
            if only and only not in nm: continue
            tr = fn(); CACHE[nm] = tr; row = {}
            for k, (a, z) in BLK.items(): row[k] = stats(tr, a, z); row[k + '_slip8'] = stats(tr, a, z, 8.0)
            row['years'] = years(tr)
            row['pass'] = all(row[k]['net'] > 0 for k in BLK) and row['IS']['n'] >= 60
            row['pass_slip8'] = all(row[k + '_slip8']['net'] > 0 for k in BLK) and row['IS']['n'] >= 60
            out[nm] = row
            print(f"{nm:34s} " + ' | '.join(f"{k} n{row[k]['n']} wr{row[k]['wr']} pf{row[k]['pf']} R{row[k]['avgR']} ${row[k]['net']} (s8 pf{row[k + '_slip8']['pf']})" for k in BLK) + (' PASS' if row['pass'] else '') + (' S8' if row['pass_slip8'] else ''), flush=True)
        json.dump(out, open(os.path.join(HERE, 'pass_scan.json'), 'w'), indent=1)
        json.dump({k: v for k, v in CACHE.items()}, open(os.path.join(HERE, 'pass_trades.json'), 'w'))
