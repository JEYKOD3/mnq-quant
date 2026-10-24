"""Friend's exact inside bar (his voice notes 2026-10-24), on MNQ ETH 5m data.
Bias: H4, H1, M15 trend, majority 2 of 3 (completed HTF bars only, no lookahead).
  trend def 'ema': close>EMA21 & EMA rising over 3 bars (mirror down)
  trend def 'ms' : market structure, last swing high>prev & last swing low>prev (pivot 2/2) (mirror down)
Execution TF (5m default): bar i inside bar i-1 -> box = mother bar. Alive until a bar closes beyond the opposite side (or maxwait).
Trigger: FULL BODY beyond the box in bias direction. Entry at that close.
Stop: other side of the box. Target 1R (his bot) or 2R (his manual). Both hit same bar -> stop.
Cost 3 pts RT. Reports R both gross (like his Telegram report) and net of cost.
"""
import collections, sys
RAW = '/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'
COST = 3.0
bars = []  # (dayidx, date, t_hhmm_minutes, o,h,l,c, sess_off)
for di, line in enumerate(open(RAW)):
    p = line.strip().split('|')
    if len(p) < 2: continue
    d = p[0]
    for x in p[1:]:
        t, o, h, l, c = x.split(',')
        t = int(t); m = t // 100 * 60 + t % 100
        off = (m - 1080) % 1440
        bars.append((di, d, m, int(o) / 4, int(h) / 4, int(l) / 4, int(c) / 4, off))

def build(tfmin):
    """aggregate into HTF bars keyed by (day, off//tf). returns list of [key,o,h,l,c] and per-5m-bar index of LAST COMPLETED htf bar"""
    out = []; idx = []; cur = None
    for b in bars:
        k = (b[0], b[7] // tfmin)
        if cur is None or k != cur[0]:
            if cur is not None: out.append(cur)
            cur = [k, b[3], b[4], b[5], b[6]]
        else:
            cur[2] = max(cur[2], b[4]); cur[3] = min(cur[3], b[5]); cur[4] = b[6]
        # completed if this 5m bar is the last of its bucket: bucket end = (k+1)*tf ; bar end = off+5
        if b[7] + 5 >= (k[1] + 1) * tfmin:
            out.append(cur); cur = None; idx.append(len(out) - 1)
        else:
            idx.append(len(out) - 1)  # last completed (previous) bar
    return out, idx

def trend_series(H, kind):
    n = len(H); tr = [0] * n
    if kind == 'ema':
        e = None; E = []
        for b in H:
            e = b[4] if e is None else e + 2 / 22 * (b[4] - e); E.append(e)
        for i in range(3, n):
            if H[i][4] > E[i] and E[i] > E[i - 3]: tr[i] = 1
            elif H[i][4] < E[i] and E[i] < E[i - 3]: tr[i] = -1
    else:
        sh, sl = [], []; p = 2
        for i in range(n):
            j = i - p  # pivot confirmed at i
            if j >= p:
                if H[j][2] == max(x[2] for x in H[j - p:j + p + 1]): sh.append(H[j][2])
                if H[j][3] == min(x[3] for x in H[j - p:j + p + 1]): sl.append(H[j][3])
            if len(sh) >= 2 and len(sl) >= 2:
                if sh[-1] > sh[-2] and sl[-1] > sl[-2]: tr[i] = 1
                elif sh[-1] < sh[-2] and sl[-1] < sl[-2]: tr[i] = -1
    return tr

CACHE = {}
def bias_at(kind, need=2):
    key = (kind, need)
    if key in CACHE: return CACHE[key]
    per = []
    for tf in (240, 60, 15):
        H, idx = build(tf); tr = trend_series(H, kind)
        per.append([tr[j] if j >= 0 else 0 for j in idx])
    out = []
    for a, b, c in zip(*per):
        s = a + b + c; up = (a == 1) + (b == 1) + (c == 1); dn = (a == -1) + (b == -1) + (c == -1)
        out.append(1 if up >= need else (-1 if dn >= need else 0))
    CACHE[key] = out
    return out

def exec_bars(tf):
    if tf == 5: return [(i, b) for i, b in enumerate(bars)]
    out = []; cur = None
    for i, b in enumerate(bars):
        k = (b[0], b[7] // tf)
        if cur is None or cur[0] != k:
            if cur: out.append((cur[1], cur[2]))
            cur = [k, i, list(b)]
        else:
            c = cur[2]; c[4] = max(c[4], b[4]); c[5] = min(c[5], b[5]); c[6] = b[6]; cur[1] = i
    out.append((cur[1], cur[2]))
    return out  # index = last 5m bar inside (bias known at its close)

def run(kind='ema', need=2, tf=5, tR=1.0, sess='rth', maxwait=None, body=True, log=None):
    bias = bias_at(kind, need); X = exec_bars(tf)
    win = {'rth': (570, 955), 'ny_am': (570, 690), 'london': (180, 570), 'all': (0, 1440)}[sess]
    flat = 955 if sess in ('rth', 'ny_am') else 1015
    out = []; pos = 0; box = None
    for k in range(1, len(X)):
        bi, b = X[k]; di, d, m, o, h, l, c, off = b
        if pos:
            hit = None
            if pos == 1:
                if l <= stp: hit = stp
                elif h >= tp: hit = tp
            else:
                if h >= stp: hit = stp
                elif l <= tp: hit = tp
            if hit is None and (m >= flat and m < 1080 or X[k - 1][1][0] != di and False): hit = c
            if hit is None and k + 1 < len(X) and X[k + 1][1][0] != di: hit = c
            if hit is not None:
                g = (hit - ent) * pos / R; out.append((d, et, g, (hit - ent) * pos - COST, R))
                if log is not None: log.append((d, et, pos, ent, stp, tp, hit))
                pos = 0
            continue
        pb = X[k - 1][1]
        if pb[0] != di: box = None
        inwin = win[0] <= m < win[1] if sess != 'london' else (m >= 180 and m < 570)
        if box:
            mh, ml, dr, kb = box
            if maxwait and k - kb > maxwait: box = None
            elif (dr == 1 and c < ml) or (dr == -1 and c > mh): box = None
            else:
                go = (min(o, c) > mh if dr == 1 else max(o, c) < ml) if body else (c > mh if dr == 1 else c < ml)
                if go:
                    box = None
                    if inwin and bias[bi] == dr:
                        r = (c - ml) if dr == 1 else (mh - c)
                        if r > 0:
                            pos, ent, stp, R, et = dr, c, (ml if dr == 1 else mh), r, (d, m)
                            tp = c + tR * r * dr
                    continue
                continue
        if h <= pb[4] and l >= pb[5] and pb[4] > pb[5]:
            dr = bias[bi]
            if dr: box = (pb[4], pb[5], dr, k)
    return out

def stats(o, label=''):
    if not o: return label + ' n=0'
    yrs = collections.defaultdict(list)
    for x in o: yrs[x[0][:4]].append(x[3])
    def pf(v):
        a = sum(y for y in v if y > 0); b = -sum(y for y in v if y <= 0); return a / b if b else 9.99
    days = len(set(x[0] for x in o))
    gw = sum(1 for x in o if x[2] > 0)
    netR = sum(x[3] / x[4] for x in o)
    return (f"{label} n={len(o):5d} ({len(o)/days:.1f}/active day) WR {100*gw/len(o):4.1f}% grossR {sum(x[2] for x in o):+7.1f} "
            f"netR {netR:+7.1f} PF(net) {pf([x[3] for x in o]):4.2f} risk {sum(x[4] for x in o)/len(o):5.1f}pt $/MNQ {2*sum(x[3] for x in o):+7.0f} | "
            + ' '.join(f"{y[2:]}:{pf(v):.2f}" for y, v in sorted(yrs.items())))

if __name__ == '__main__':
    print(f"{len(bars)} 5m bars {bars[0][1]}..{bars[-1][1]}")
    for kind in ('ema', 'ms'):
        for sess in ('rth', 'london', 'all'):
            for tR in (1.0, 2.0):
                for tf in (5, 15):
                    print(stats(run(kind, 2, tf, tR, sess), f"{kind:3s} {sess:6s} {tf:2d}m tgt {tR:.0f}R"))
