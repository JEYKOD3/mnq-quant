"""Inside bar, converged version from 3 sources (LPA, Jhunjhunwala, generic PDF) + friend variants.
MNQ RTH 1m data -> 1/5/15m. Cost 3 pts round trip. $2/pt per MNQ.
Box = mother bar (MB) range, one or more inside bars; alive until a bar CLOSES beyond the opposite side.
Trend: EMA21 slope(6) + close on right side, checked when the inside bar forms.
Trigger variants: close beyond MB (conv), full body beyond MB (friend), touch MB (stop order), close beyond IB (ib).
Location filter: skip if S/R (in-day swing 3/3, PDH/PDL/PDC, OR15 H/L) closer than 1R in trade direction.
Target: next S/R in [1R,3R] else 2R ('sr'), or fixed 2R ('2r'). Stop: other side of MB (IB for ib trigger) +1pt.
"""
import sys, collections
RAW = '/home/claude/mnq-quant/data/raw/mnq_rth_1m.txt'
COST = 3.0
days = []
for line in open(RAW):
    p = line.strip().split('|'); d = p[0]
    if d < '20211201': continue
    bars = []
    for x in p[1:]:
        t, o, h, l, c = x.split(',')
        t = int(t); bars.append((t // 100 * 60 + t % 100, int(o) / 4, int(h) / 4, int(l) / 4, int(c) / 4))
    days.append((d, bars))

def agg(bars, tf):
    g = collections.OrderedDict()
    for b in bars:
        k = 570 + (b[0] - 570) // tf * tf
        if k not in g: g[k] = [k, b[1], b[2], b[3], b[4]]
        else:
            a = g[k]; a[2] = max(a[2], b[2]); a[3] = min(a[3], b[3]); a[4] = b[4]
    return [tuple(v) for v in g.values()]

def run(tf, trig='conv', loc=True, tgt='sr', maxwait=None, locR=1.0, tR=2.0, emaL=21, slope=6, buf=1.0, first=575, last=930, flat=955, log=None):
    kk = 2 / (emaL + 1); e = None; out = []; pd = None; EH = []
    for d, raw in days:
        B = agg(raw, tf); n = len(B)
        off = len(EH)
        for b in B:
            e = b[4] if e is None else e + kk * (b[4] - e); EH.append(e)
        ema = EH; 
        orh = max(b[2] for b in raw if b[0] < 585); orl = min(b[3] for b in raw if b[0] < 585)
        swH, swL = [], []; box = None; pos = 0; piv = 3
        for i in range(1, n):
            t, o, h, l, c = B[i]
            j = i - piv
            if j - piv >= 0:
                if B[j][2] == max(x[2] for x in B[j - piv:j + piv + 1]): swH.append(B[j][2])
                if B[j][3] == min(x[3] for x in B[j - piv:j + piv + 1]): swL.append(B[j][3])
            if pos:
                hit = None
                if pos == 1:
                    if l <= stp: hit = stp
                    elif h >= tp: hit = tp
                else:
                    if h >= stp: hit = stp
                    elif l <= tp: hit = tp
                if hit is None and (t >= flat or i == n - 1): hit = c
                if hit is not None:
                    pts = (hit - ent) * pos - COST
                    out.append((d, et, pts, R))
                    if log is not None: log.append((d, et, pos, ent, stp, tp, hit, pts))
                    pos = 0
                continue
            # box management
            if box:
                mh, ml, ih, il, dr, bi = box
                if maxwait and i - bi > maxwait: box = None
                elif dr == 1 and c < ml or dr == -1 and c > mh: box = None
                else:
                    lvl_hi = ih if trig == 'ib' else mh; lvl_lo = il if trig == 'ib' else ml
                    if trig in ('conv', 'ib'): go = c > lvl_hi if dr == 1 else c < lvl_lo
                    elif trig == 'body': go = min(o, c) > mh if dr == 1 else max(o, c) < ml
                    else: go = h > mh if dr == 1 else l < ml  # touch
                    if go and first <= t <= last:
                        if trig == 'touch': entry = max(o, mh + .25) if dr == 1 else min(o, ml - .25)
                        else: entry = c
                        sl = (il - buf if dr == 1 else ih + buf) if trig == 'ib' else (ml - buf if dr == 1 else mh + buf)
                        r = (entry - sl) * dr
                        box = None
                        if r <= 0: continue
                        if dr == 1:
                            lv = sorted(x for x in swH + [pd[0], pd[1], pd[2], orh, orl] if x > entry)
                        else:
                            lv = sorted((x for x in swL + [pd[0], pd[1], pd[2], orh, orl] if x < entry), reverse=True)
                        if loc and lv and abs(lv[0] - entry) < locR * r: continue
                        if tgt == 'sr':
                            z = [x for x in lv if r <= abs(x - entry) <= 3 * r]
                            tpp = (z[0] - .25 * dr) if z else entry + tR * r * dr
                        else: tpp = entry + tR * r * dr
                        pos, ent, stp, tp, R, et = dr, entry, sl, tpp, r, t
                        if trig == 'touch':  # same-bar stop check
                            if (dr == 1 and l <= sl) or (dr == -1 and h >= sl):
                                out.append((d, et, -r - COST, R)); pos = 0
                        continue
                    if h <= mh and l >= ml: box = (mh, ml, min(ih, h) if False else ih, il, dr, bi)
                    continue
            # new pattern: bar i inside bar i-1
            m = B[i - 1]
            if h <= m[2] and l >= m[3] and m[2] > m[3] and off + i >= 60:
                dr = 1 if (ema[off+i] > ema[off+i - slope] and c > ema[off+i]) else (-1 if (ema[off+i] < ema[off+i - slope] and c < ema[off+i]) else 0)
                if dr and pd: box = (m[2], m[3], h, l, dr, i)
        pd = (max(b[2] for b in raw), min(b[3] for b in raw), raw[-1][4])
    return out

def stats(o):
    if not o: return 'n=0'
    w = sum(x[2] for x in o if x[2] > 0); ls = -sum(x[2] for x in o if x[2] <= 0)
    yrs = collections.defaultdict(list)
    for x in o: yrs[x[0][:4]].append(x[2])
    def pf(v):
        a = sum(y for y in v if y > 0); b = -sum(y for y in v if y <= 0); return a / b if b else 9.99
    ny = len(set(x[0][:4] for x in o))
    return (f"n={len(o):5d} ({len(o)/4.9:5.0f}/yr) WR {100*sum(x[2]>0 for x in o)/len(o):4.1f}% PF {w/ls if ls else 9:4.2f} "
            f"avg {sum(x[2] for x in o)/len(o):+5.2f}pt  risk {sum(x[3] for x in o)/len(o):5.1f}pt  $/MNQ {2*sum(x[2] for x in o):+8.0f} | "
            + ' '.join(f"{y[2:]}:{pf(v):.2f}" for y, v in sorted(yrs.items())))

if __name__ == '__main__':
    print(f"days {days[0][0]}..{days[-1][0]} ({len(days)})  cost {COST}pt RT")
    for tf in (1, 5, 15):
        print(f"\n=== {tf}m ===")
        for trig in ('conv', 'body', 'touch', 'ib'):
            for loc in (True, False):
                for tg in ('sr', '2r'):
                    print(f"{trig:5s} loc={'Y' if loc else 'N'} tgt={tg}: " + stats(run(tf, trig, loc, tg)))
