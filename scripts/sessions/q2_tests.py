"""Q2: mechanical rule families per session window. Every variant run is printed (no hiding of losers).
Run: python3 q2_tests.py > out_q2.txt   (also writes out_q2.md with markdown tables)"""
from common import *

def P(d, hhmm, what='c'):
    """price at clock time: 'c' = close of the bar ending at hhmm, 'o' = open of bar starting at hhmm"""
    O, H, L, C = ETH[d]; k = slot(hhmm)
    return C[k - 1] if what == 'c' else O[k]

# ---------- A. Asia range sweep / break at London ----------
def asia(rng=(2000, 200), win=(300, 600), mode='fade', exit_=800, stopk=None):
    out = []
    a, z = slot(rng[0]), slot(rng[1]); wa, wz = slot(win[0]), slot(win[1]); kx = slot(exit_)
    for d in sessions():
        O, H, L, C = ETH[d]; adr = adr_of(d)
        AH, AL = max(H[a:z]), min(L[a:z]); mid = (AH + AL) / 2; w = AH - AL
        if w <= 0: continue
        ext_h, ext_l = AH, AL
        for k in range(z, wz):
            ext_h = max(ext_h, H[k]); ext_l = min(ext_l, L[k])
            if k < wa:
                if H[k] > AH or L[k] < AL: break          # range already broken before the window: skip the day
                continue
            if mode == 'fade':
                if H[k] > AH and C[k] < AH: s, stop = -1, ext_h + .25
                elif L[k] < AL and C[k] > AL: s, stop = 1, ext_l - .25
                else:
                    if C[k] > AH or C[k] < AL: break     # accepted outside: no fade today
                    continue
                e = O[k + 1]
                if stopk: stop = e - s * stopk * adr
                if (mid - e) * s <= 1 or (stop - e) * s >= 0: break
                out.append(sim(d, s, k + 1, e, stop, mid, kx)); break
            else:
                if C[k] > AH: s = 1
                elif C[k] < AL: s = -1
                else: continue
                e = O[k + 1]; risk = max(stopk * adr if stopk else w / 2, 4)
                out.append(sim(d, s, k + 1, e, e - s * risk, e + s * risk, kx)); break
    return out

# ---------- B. Opening range breakout / fade per session open ----------
def orb(op=1800, orm=30, dur=150, mode='break', tgtR=1.0):
    out = []
    k0 = slot(op); n = orm // 5; kx = k0 + dur // 5
    for d in sessions():
        O, H, L, C = ETH[d]; adr = adr_of(d)
        if kx >= NS: continue
        hi, lo = max(H[k0:k0 + n]), min(L[k0:k0 + n]); w = hi - lo
        if w < 2: continue
        side = 0; ext = None
        for k in range(k0 + n, kx - 1):
            if not side:
                if C[k] > hi: side = 1; ext = H[k]
                elif C[k] < lo: side = -1; ext = L[k]
                else: continue
                if mode == 'break':
                    e = O[k + 1]; stop = lo - .25 if side > 0 else hi + .25
                    risk = (e - stop) * side
                    if risk <= 0: break
                    tg = e + side * tgtR * risk if tgtR else None
                    out.append(sim(d, side, k + 1, e, stop, tg, kx)); break
                continue
            ext = max(ext, H[k]) if side > 0 else min(ext, L[k])
            if (side > 0 and C[k] < hi) or (side < 0 and C[k] > lo):   # failed breakout -> fade back through
                s = -side; e = O[k + 1]; stop = ext + .25 * side
                tg = lo if s < 0 else hi
                if (tg - e) * s <= 1: break
                out.append(sim(d, s, k + 1, e, stop, tg, kx)); break
    return out

# ---------- C. Night reversion to the 18:00 open / running TWAP ----------
def night_rev(win=(2000, 200), k=0.25, stopk=0.15, ref='open', exit_=300, mode='fade'):
    out = []
    wa, wz = slot(win[0]), slot(win[1]); kx = slot(exit_)
    for d in sessions():
        O, H, L, C = ETH[d]; adr = adr_of(d)
        acc = 0; nb = 0
        for kk in range(0, wa): acc += (H[kk] + L[kk] + C[kk]) / 3; nb += 1
        for kk in range(wa, wz):
            F = O[0] if ref == 'open' else acc / nb
            dev = C[kk] - F
            if abs(dev) >= k * adr:
                s = -1 if dev > 0 else 1
                if mode != 'fade': s = -s
                e = O[kk + 1]
                tg = F if mode == 'fade' else e + s * abs(dev)
                out.append(sim(d, s, kk + 1, e, e - s * stopk * adr, tg, kx)); break
            acc += (H[kk] + L[kk] + C[kk]) / 3; nb += 1
    return out

# ---------- D/E/F/H/I/J. conditional directional holds ----------
def cond_hold(sig, t_in, t_out, thr=0.0, mode='cont', days_filter=None, stopk=None):
    """sig(d) -> signed move in points known before t_in. Enter at open of t_in bar, exit close before t_out."""
    out = []
    for d in sessions():
        if days_filter and not days_filter(d): continue
        v = sig(d)
        if v is None: continue
        adr = adr_of(d)
        if abs(v) < thr * adr or v == 0: continue
        s = (1 if v > 0 else -1) * (1 if mode == 'cont' else -1)
        k0 = slot(t_in); kx = slot(t_out) if t_out != 1655 else NS
        e = ETH[d][0][k0]
        out.append(sim(d, s, k0, e, e - s * stopk * adr if stopk else None, None, kx))
    return out

def prev_rth(d):
    p = prev_key(d)
    return rth_hlc(p) if p else None

def sig_on(d): return P(d, 930) - ETH[d][0][0]                         # 18:00 open -> 9:30
def sig_gao(d):                                                           # prior RTH close -> 10:00 (Gao et al.)
    r = prev_rth(d); return P(d, 1000) - r[2] if r else None
def sig_day(t):                                                           # 9:30 open -> t
    return lambda d: P(d, t) - P(d, 930, 'o')
def sig_win(a, b, wa='o'):
    return lambda d: P(d, b) - P(d, a, wa)
def sig_prev_rth_day(d):                                                  # prior RTH open -> close
    p = prev_key(d)
    if not p or not full(p, 186, 264): return None
    return ETH[p][3][263] - ETH[p][0][186]
def is_mon(d): return wd(d) == 0
def no_news(d): return not any(t == '0830' for e, t in MACRO.get(d, ()))

# ---------- G. prior-day RTH high / low overnight ----------
def pdhl(win=(1800, 925), mode='fade', stopk=0.15, tgtk=0.3, exit_=925):
    out = []
    wa, wz = slot(win[0]), slot(win[1]); kx = slot(exit_)
    for d in sessions():
        r = prev_rth(d)
        if not r: continue
        PH, PL, PC = r; adr = adr_of(d)
        O, H, L, C = ETH[d]
        if not (PL < O[wa] < PH): continue
        for k in range(wa, wz):
            th, tl = H[k] >= PH, L[k] <= PL
            if not (th or tl): continue
            if th and tl: break
            lvl, s = (PH, -1) if th else (PL, 1)
            if mode == 'fade':
                e = lvl
                out.append(sim(d, s, k, e, e - s * stopk * adr, e + s * tgtk * adr, kx))
            else:
                s = -s; e = lvl + s * .25
                out.append(sim(d, s, k, e, e - s * stopk * adr, e + s * tgtk * adr, kx))
            break
    return out

TESTS = []
def T(q, name, fn): TESTS.append((q, name, fn))

for rng in ((2000, 200), (1800, 200)):
    for win, ex in (((300, 600), 800), ((200, 600), 800), ((300, 600), 925)):
        for sk in (None, 0.15):
            T('A Asia range swept at London: fade back to Asia mid', f"fade rng{rng[0]}-{rng[1]} win{win[0]}-{win[1]} x{ex} stop={'sweep' if not sk else sk}",
              lambda rng=rng, win=win, ex=ex, sk=sk: asia(rng, win, 'fade', ex, sk))
        T('A2 Asia range broken at London: go with break', f"break rng{rng[0]}-{rng[1]} win{win[0]}-{win[1]} x{ex} 1:1 half-range",
          lambda rng=rng, win=win, ex=ex: asia(rng, win, 'break', ex, None))
for op in (1800, 2000, 2100, 300, 600, 800, 1200, 1400):
    for orm in (15, 30):
        for dur in (120, 240):
            if op in (1200, 1400) and dur == 240: dur = 115 if op == 1400 else 230
            T(f'B ORB {op:04d}', f"break OR{orm} hold{dur} 1R", lambda op=op, orm=orm, dur=dur: orb(op, orm, dur, 'break', 1.0))
            T(f'B ORB {op:04d}', f"break OR{orm} hold{dur} no tgt", lambda op=op, orm=orm, dur=dur: orb(op, orm, dur, 'break', 0))
            T(f'B ORB {op:04d}', f"fade failed break OR{orm} hold{dur}", lambda op=op, orm=orm, dur=dur: orb(op, orm, dur, 'fade'))
for win, ex in (((2000, 200), 300), ((1830, 2400), 200), ((0, 300), 400), ((300, 600), 700)):
    for k in (0.2, 0.3):
        for ref in ('open', 'twap'):
            T('C Night stretch from 18:00 open/TWAP', f"fade {ref} win{win[0]}-{win[1]} k{k} stop.15 x{ex}", lambda win=win, k=k, ref=ref, ex=ex: night_rev(win, k, .15, ref, ex))
            T('C2 Night stretch: go with', f"cont {ref} win{win[0]}-{win[1]} k{k} stop.15 x{ex}", lambda win=win, k=k, ref=ref, ex=ex: night_rev(win, k, .15, ref, ex, 'cont'))
for thr in (0, 0.3):
    for m in ('cont', 'rev'):
        T('D Overnight (18:00-9:30) direction -> afternoon', f"{m} thr{thr} 12:00-15:55", lambda thr=thr, m=m: cond_hold(sig_on, 1200, 1555, thr, m))
        T('D Overnight (18:00-9:30) direction -> afternoon', f"{m} thr{thr} 14:00-15:55", lambda thr=thr, m=m: cond_hold(sig_on, 1400, 1555, thr, m))
        T('E Intraday momentum (last 30 min)', f"{m} Gao prevclose->10:00 thr{thr} 15:30-15:55", lambda thr=thr, m=m: cond_hold(sig_gao, 1530, 1555, thr, m))
        T('E Intraday momentum (last 30 min)', f"{m} 9:30->15:30 thr{thr} 15:30-15:55", lambda thr=thr, m=m: cond_hold(sig_day(1530), 1530, 1555, thr, m))
        T('E Intraday momentum (last 30 min)', f"{m} 9:30->15:00 thr{thr} 15:00-15:55", lambda thr=thr, m=m: cond_hold(sig_day(1500), 1500, 1555, thr, m))
        T('E Intraday momentum (last 30 min)', f"{m} 15:00->15:30 thr{thr} 15:30-15:55", lambda thr=thr, m=m: cond_hold(sig_win(1500, 1530), 1530, 1555, thr / 3, m))
        T('F Midday: morning direction -> 12:00-14:00', f"{m} 9:30->12:00 thr{thr} 12:00-14:00", lambda thr=thr, m=m: cond_hold(sig_day(1200), 1200, 1400, thr, m))
        T('F Midday: morning direction -> 12:00-14:00', f"{m} 9:30->12:00 thr{thr} 12:00-15:55", lambda thr=thr, m=m: cond_hold(sig_day(1200), 1200, 1555, thr, m))
        T('F Midday: morning direction -> 12:00-14:00', f"{m} 9:30->14:00 thr{thr} 14:00-15:55", lambda thr=thr, m=m: cond_hold(sig_day(1400), 1400, 1555, thr, m))
        T('H Pre-market: London direction -> 6:00-9:30', f"{m} 3:00->6:00 thr{thr / 2} 6:00-9:25", lambda thr=thr, m=m: cond_hold(sig_win(300, 600), 600, 925, thr / 2, m))
        T('H Pre-market: overnight -> 8:30-9:30 (no-news days)', f"{m} 18:00->8:30 thr{thr} 8:30-9:25", lambda thr=thr, m=m: cond_hold(sig_win(1800, 830), 830, 925, thr, m, no_news))
        T('H Pre-market: overnight -> 8:30-9:30 (no-news days)', f"{m} 18:00->6:00 thr{thr} 6:00-9:25", lambda thr=thr, m=m: cond_hold(sig_win(1800, 600), 600, 925, thr, m))
        T('I Sunday evening beyond the gap', f"{m} Sun 18:00->20:00 thr{thr / 2} 20:00-03:00", lambda thr=thr, m=m: cond_hold(sig_win(1800, 2000), 2000, 300, thr / 2, m, is_mon))
        T('I Sunday evening beyond the gap', f"{m} Sun 18:00->20:00 thr{thr / 2} 20:00-09:25", lambda thr=thr, m=m: cond_hold(sig_win(1800, 2000), 2000, 925, thr / 2, m, is_mon))
        T('I Sunday evening beyond the gap', f"{m} Sun 18:00->24:00 thr{thr / 2} 00:00-09:25", lambda thr=thr, m=m: cond_hold(sig_win(1800, 0), 0, 925, thr / 2, m, is_mon))
        T('J Prior RTH day direction -> evening', f"{m} prevRTH thr{thr * 2} 18:00-20:00", lambda thr=thr, m=m: cond_hold(sig_prev_rth_day, 1800, 2000, thr * 2, m))
        T('J Prior RTH day direction -> evening', f"{m} prevRTH thr{thr * 2} 18:00-03:00", lambda thr=thr, m=m: cond_hold(sig_prev_rth_day, 1800, 300, thr * 2, m))
        T('J Prior RTH day direction -> evening', f"{m} prevRTH thr{thr * 2} 18:00-09:25", lambda thr=thr, m=m: cond_hold(sig_prev_rth_day, 1800, 925, thr * 2, m))
        T('J2 Last hour -> post-close 16:00-16:55', f"{m} 15:00->16:00 thr{thr / 2} 16:00-16:55", lambda thr=thr, m=m: cond_hold(sig_win(1500, 1600), 1600, 1655, thr / 2, m))
for w in range(5):
    for m in ('cont',):
        T('K Weekday overnight hold (long)', f"long 18:00-09:25 key wd{w}", lambda w=w: cond_hold(lambda d: 1, 1800, 925, 0, 'cont', lambda d: wd(d) == w))
        T('K Weekday overnight hold (long)', f"long 20:00-03:00 key wd{w}", lambda w=w: cond_hold(lambda d: 1, 2000, 300, 0, 'cont', lambda d: wd(d) == w))
for win in ((1800, 300), (300, 925), (1800, 925)):
    for mode in ('fade', 'break'):
        for sk, tk in ((0.1, 0.15), (0.15, 0.3), (0.2, 0.2)):
            T('G Prior-day RTH high/low touched overnight', f"{mode} win{win[0]}-{win[1]} stop{sk} tgt{tk}", lambda win=win, mode=mode, sk=sk, tk=tk: pdhl(win, mode, sk, tk))

if __name__ == '__main__':
    import collections
    md = collections.OrderedDict()
    passed = []
    for q, name, fn in TESTS:
        tr = fn()
        print(f"[{q}] " + row(name, tr), flush=True)
        md.setdefault(q, []).append(md_row(name, tr))
        a, b = split(tr); A, B = stats(a), stats(b)
        if A['n'] >= 60 and B['n'] >= 30 and A['pf'] > 1.15 and B['pf'] > 1.15: passed.append(f"[{q}] {row(name, tr)}")
    print('\n==== passes IS n>=60, OOS n>=30, PF>1.15 both ====')
    for p in passed: print(p)
    with open('/home/claude/mnq-quant/scripts/sessions/out_q2.md', 'w') as f:
        for q, rows in md.items():
            f.write(f"\n#### {q}\n\n{MD_HEAD}\n" + '\n'.join(rows) + '\n')
    print(len(TESTS), 'variants')
