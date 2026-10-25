"""Fair Pricing Theory engine (Oct 25 2026). One account, one position at a time. Prices in points.
Costs: 2.37/side commission + 1 tick slippage on entry and on stops. Bars: RTH 1m (Databento) + ETH 5m for pre-open prices."""
import sys, csv, collections
sys.path.insert(0, '/home/claude/mnq-quant/scripts/lab')
from core import load, agg, features
T = .25; PV = 2.0; COMM = 2.37
DAYS = [(d, b) for d, b in load() if d >= 20211201 and b and b[0][0] == 570]
FEAT = features(DAYS)
DAYS = [(d, b) for d, b in DAYS if d >= 20220101]
EV = collections.defaultdict(set)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')):
    if r['time_et'] == '0830': EV[int(r['date'])].add(r['event'])
ETH = {}
for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
    p = ln.strip().split('|')
    if len(p) < 50: continue
    ETH[int(p[0])] = {int(x.split(',')[0]): tuple(int(v) / 4 for v in x.split(',')[1:]) for x in p[1:]}

def eth_hm(hm):  # 'hhmm' int -> order key for overnight (18:00 = 0)
    m = hm // 100 * 60 + hm % 100
    return (m - 1080) % 1440

def fair_price(d, b, mode):
    e = ETH.get(d, {})
    op = b[0][1]
    news = bool(EV.get(d))
    if mode == 'open': return op
    if mode == 'c929': return e[925][3] if 925 in e else None
    if mode == 'b929': return (e[925][0] + e[925][3]) / 2 if 925 in e else None   # middle of the 9:25-9:30 body
    if mode == 'news': return e[825][3] if news and 825 in e else op            # 8:29 close on 8:30 news days
    if mode == 'news_only': return e[825][3] if news and 825 in e else None
    if mode == 'preopen':  # middle of the 9:00-9:30 range
        xs = [e[k] for k in (900, 905, 910, 915, 920, 925) if k in e]
        return (max(x[1] for x in xs) + min(x[2] for x in xs)) / 2 if len(xs) == 6 else None
    if mode == 'news_back':  # 8:29 price only if the open trades back through it in the first 5 minutes
        if not (news and 825 in e): return op
        F = e[825][3]
        hi = max(x[2] for x in b[:5]); lo = min(x[3] for x in b[:5])
        return F if lo <= F <= hi else op
    raise ValueError(mode)

def overnight_bias(d, b, hours):
    """big-picture reversion bias: opposite of the move over the previous `hours` before 9:30. +1 = look for longs."""
    e = ETH.get(d, {})
    if not e: return 0
    k = [x for x in e if eth_hm(x) <= eth_hm(925)]
    start = 930 - hours * 100
    if start < 0: start += 2400
    ks = min(k, key=lambda x: abs(eth_hm(x) - eth_hm(start)))
    mv = b[0][1] - e[ks][0]
    return -1 if mv > 0 else 1

def signals(bb, F, i, kind):
    """signal on the close of bar i of bb, toward F. returns +1 long, -1 short, 0 none. bb rows (m,o,h,l,c)."""
    m, o, h, l, c = bb[i]; pm, po, ph, pl, pc = bb[i - 1]
    s = 1 if c < F else -1 if c > F else 0
    if not s: return 0, None
    body = abs(c - o); pbody = abs(pc - po)
    col = 1 if c > o else -1 if c < o else 0
    if col != s: return 0, None
    disp = body > pbody and ((c > ph) if s > 0 else (c < pl)) and (pc - po) * s < 0
    # swing points confirmed before bar i: j with wick beyond both neighbours (j+1 <= i-1)
    bos = False; sw = None
    for j in range(i - 2, max(0, i - 30), -1):
        if s < 0 and bb[j][3] < bb[j - 1][3] and bb[j][3] < bb[j + 1][3]: sw = bb[j][3]; break
        if s > 0 and bb[j][2] > bb[j - 1][2] and bb[j][2] > bb[j + 1][2]: sw = bb[j][2]; break
    if sw is not None:
        bos = (c < sw and pc >= sw) if s < 0 else (c > sw and pc <= sw)
    if kind == 'disp': ok = disp
    elif kind == 'bos': ok = bos
    elif kind == 'either': ok = disp or bos
    elif kind == 'aplus': ok = disp and bos
    elif kind == 'disp_nowick':  # $1.2M video: bigger than prior candle, little wick on the close side
        rng = h - l
        wick = (h - c) if s > 0 else (c - l)
        ok = body > pbody and rng > 0 and wick <= .2 * rng and (pc - po) * s < 0
    elif kind == 'two':  # two closes in a row toward fair
        ok = (pc - po) * s > 0 and ((c > ph) if s > 0 else (c < pl))
    elif kind == 'any':
        ok = disp or bos or ((pc - po) * s > 0 and ((c > ph) if s > 0 else (c < pl)))
    else: raise ValueError(kind)
    return (s if ok else 0), (l if s > 0 else h)

AGG = {}
def run(fair='open', tf=1, sig='either', t0=570, t1=660, stop=25, tgt=38, tgt_mode='fixed', room=.8,
        dmin=0, dmax=9999, maxtr=4, maxloss=3, be_at_fair=False, bias=0, news=None, flat=955,
        stop_mode='fixed', adrk=None, cont=False, cont_win=5, skip_first=0, years=None, diag=False, stopbuf=1,
        need_cross=0, max_away=0, gapmax=0, dist_adr=0, wd=None):
    """returns list of trades dict(d, side, net$, pts, R, kind, ...). Sizing: 1 MNQ (R = stop pts)."""
    out = []
    for d, b in DAYS:
        if years and d // 10000 not in years: continue
        if news == 'only' and not EV.get(d): continue
        if news == 'skip' and EV.get(d): continue
        F = fair_price(d, b, fair)
        if F is None: continue
        f = FEAT.get(d)
        adr = f['adr'] if f else 300
        S = stop if stop_mode == 'fixed' else max(25, round(adrk * adr / 4) * 4 / 4)
        TG = tgt if stop_mode == 'fixed' else S * tgt / stop
        if gapmax and f and abs(f['gap']) > gapmax: continue
        if wd is not None and wd != __import__('datetime').date(d // 10000, d // 100 % 100, d % 100).weekday(): continue
        bb = AGG.get((d, tf))
        if bb is None: bb = AGG[(d, tf)] = agg(b, tf)
        # running count of 1m bars that traded through F, and the minute of the last touch
        cross = []; c_ = 0; last = 570
        for x in b:
            if x[3] <= F <= x[2]: c_ += 1; last = x[0]
            cross.append((x[0], c_, last))
        bi = overnight_bias(d, b, bias) if bias else 0
        n = 0; losses = 0; busy_until = -1
        # optional opening continuation: first 1m candle colour, close beyond prior structure in first cont_win minutes
        if cont:
            c1 = b[0]; s = 1 if c1[4] > c1[1] else -1 if c1[4] < c1[1] else 0
            if s and (not bias or s == bi):
                big = abs(c1[4] - c1[1]) > 25
                Sc, Tc = (50, 76) if big else (25, 38)
                for i in range(1, len(b) - 1):
                    if b[i][0] >= 570 + cont_win: break
                    hi = max(x[2] for x in b[:i]); lo = min(x[3] for x in b[:i])
                    if (s > 0 and b[i][4] > hi) or (s < 0 and b[i][4] < lo):
                        r = walk(b, i + 1, s, b[i + 1][1] + s * T, Sc, Tc, None, flat)
                        r.update(d=d, side=s, kind='cont', R=r['pts'] / Sc, net=r['pts'] * PV * (.5 if big else 1) - 2 * COMM * (.5 if big else 1))
                        out.append(r); busy_until = r['xm']; break
        for i in range(2, len(bb) - 1):
            m = bb[i][0] + tf - 1   # close time of bar i
            if m < t0 + tf - 1 or bb[i][0] < t0: continue
            if bb[i][0] >= t1 or n >= maxtr or losses >= maxloss: break
            if m < busy_until: continue
            s, ext = signals(bb, F, i, sig)
            if not s: continue
            if bias and s != bi: continue
            # entry at next 1m bar open after the signal close
            j = next((k for k, x in enumerate(b) if x[0] > m), None)
            if j is None: break
            e = b[j][1] + s * T
            dist = (F - e) * s
            if dist < dmin or dist > dmax: continue
            if dist_adr and dist > dist_adr * adr: continue
            if need_cross and cross[j - 1][1] < need_cross: continue
            if max_away and b[j][0] - cross[j - 1][2] > max_away: continue
            if tgt_mode == 'fixed': tg = TG
            elif tgt_mode == 'fair': tg = dist
            elif tgt_mode == 'fair_r': tg = min(dist, TG)  # fixed target, capped at fair
            else: raise ValueError
            if tgt_mode != 'fair' and dist < room * TG: continue
            if tg <= 2: continue
            Sx = S
            if stop_mode == 'struct': Sx = max(stop, (e - ext) * s + stopbuf)
            r = walk(b, j, s, e, Sx, tg, F if be_at_fair else None, flat)
            r.update(d=d, side=s, kind='rev', R=r['pts'] / Sx, net=r['pts'] * PV - 2 * COMM, dist=dist, em=b[j][0], S=Sx, F=F)
            if diag: r.update(after=after(b, r['xi'], s, e, tg, F, flat))
            out.append(r); n += 1
            losses = losses + 1 if r['net'] < 0 else 0
            busy_until = r['xm']
    return out

def walk(b, j, s, e, S, tg, befair, flat):
    stp = e - s * S; tp = e + s * tg; mfe = 0; mae = 0; bed = False
    for k in range(j, len(b)):
        m, o, h, l, c = b[k]
        adv = (e - l) if s > 0 else (h - e); fav = (h - e) if s > 0 else (e - l)
        if (s > 0 and l <= stp) or (s < 0 and h >= stp):
            px = stp - s * T if not bed else stp
            return dict(pts=(px - e) * s, why='be' if bed else 'stop', xi=k, xm=m, mfe=mfe, mae=max(mae, adv), bars=k - j)
        if (s > 0 and h >= tp) or (s < 0 and l <= tp):
            return dict(pts=tg, why='tgt', xi=k, xm=m, mfe=max(mfe, fav), mae=mae, bars=k - j)
        mfe = max(mfe, fav); mae = max(mae, adv)
        if befair is not None and not bed and ((s > 0 and h >= befair) or (s < 0 and l <= befair)):
            stp = e; bed = True
        if m >= flat:
            return dict(pts=(c - e) * s, why='time', xi=k, xm=m, mfe=mfe, mae=mae, bars=k - j)
    return dict(pts=(b[-1][4] - e) * s, why='time', xi=len(b) - 1, xm=b[-1][0], mfe=mfe, mae=mae, bars=len(b) - j)

def after(b, k, s, e, tg, F, flat):
    """after the exit: did price later reach the old target / the fair price before the close?"""
    hit_t = hit_f = False
    for x in b[k + 1:]:
        if (s > 0 and x[2] >= e + s * tg) or (s < 0 and x[3] <= e + s * tg): hit_t = True
        if (s > 0 and x[2] >= F) or (s < 0 and x[3] <= F): hit_f = True
    return dict(t=hit_t, f=hit_f)

def stats(tr, split=20241231):
    def pf(v):
        g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
    a = [t['net'] for t in tr if t['d'] <= split]; z = [t['net'] for t in tr if t['d'] > split]
    al = a + z
    if not al: return dict(n=0)
    yr = {y: pf([t['net'] for t in tr if t['d'] // 10000 == y]) for y in range(2022, 2027)}
    return dict(n=len(al), win=round(sum(x > 0 for x in al) / len(al), 3), pf=pf(al), pfA=pf(a), pfZ=pf(z),
                nA=len(a), nZ=len(z), usd=round(sum(al)), avgR=round(sum(t['R'] for t in tr) / len(tr), 3), yr=yr,
                yrs_pos=sum(v > 1 for v in yr.values()))
