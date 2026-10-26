"""Q6: setups proposed by the web research (knowledge/RESEARCH_OFF_HOURS_MNQ.md), tested with the same engine and costs.
M1 last-half-hour momentum, M2 Zarattini noise-area 14:00-16:00, L3 London continuation 08:05-11:00 (+ shifted-window baseline),
L2 Asia sweep-and-reclaim 02:00-05:00 (+ shifted-window baseline), A1/L1 sell-off evening/overnight long, M3 post-lunch long.
Run: python3 q6_research.py > out_q6.txt"""
import statistics as st
from common import *
from q2_tests import P, prev_rth

START = 20211101          # include late 2021 so the "2021+" split is visible per year

def days(): return list(sessions(start=START))
def per_year(tr):
    y = collections.defaultdict(list)
    for t in tr: y[t['d'] // 10000].append(t)
    return '  '.join(f"{k}: n{len(v)} PF {stats(v)['pf']:.2f} ${stats(v)['tot']:+.0f}" for k, v in sorted(y.items()))
def show(name, tr, yearly=False):
    tr = [t for t in tr if t['d'] >= 20220101] if not yearly else tr
    print(row(name, [t for t in tr if t['d'] >= 20220101]))
    if yearly: print('    ' + per_year(tr))

# ---------- M1 last-half-hour momentum (Baltussen) ----------
def m1(thr=0.15, stopk=0.12, variant=''):
    out = []
    for d in days():
        r = prev_rth(d)
        if not r: continue
        O, H, L, C = ETH[d]; adr = adr_of(d)
        R = P(d, 1530) - r[2]
        if abs(R) < thr * adr: continue
        s = 1 if R > 0 else -1
        if variant == 'gao' and (P(d, 1000) - P(d, 930, 'o')) * (P(d, 1530) - P(d, 1500, 'o')) <= 0: continue
        if variant == 'gamma':
            a, z = slot(930), slot(1530)
            if max(H[a:z]) - min(L[a:z]) < 1.0 * adr: continue
        k = slot(1530); e = O[k]
        out.append(sim(d, s, k, e, e - s * stopk * adr if stopk else None, None, slot(1600)))
    return out

# ---------- M2 Zarattini noise area, 14:00-16:00 only ----------
CHECK = (1400, 1430, 1500, 1530)
def m2(use_twap=True, checks=CHECK, lookback=14):
    out = []; hist = collections.defaultdict(list)   # slot -> list of |C/O930 - 1| from prior days
    for d in days():
        O, H, L, C = ETH[d]; r = prev_rth(d); k930 = slot(930)
        sig = {t: (st.mean(hist[t][-lookback:]) if len(hist[t]) >= lookback else None) for t in checks}
        if r and all(v is not None for v in sig.values()):
            op = O[k930]; pc = r[2]
            pos = 0; e = None; k_in = None
            acc = 0; nb = 0
            for k in range(k930, slot(1555) + 1):
                acc += (H[k] + L[k] + C[k]) / 3; nb += 1
                tw = acc / nb
                t_end = (k + 1) * 5 + 1080; hhmm = (t_end // 60 % 24) * 100 + t_end % 60   # clock at bar close
                if pos:
                    up = max(op, pc) * (1 + sig_cur); lo = min(op, pc) * (1 - sig_cur)
                    stp = (max(up, tw) if use_twap else up) if pos > 0 else (min(lo, tw) if use_twap else lo)
                    if (pos > 0 and C[k] < stp) or (pos < 0 and C[k] > stp):
                        if k + 1 < NS:
                            out.append(_close(d, pos, e, O[k + 1], k + 1)); pos = 0
                if not pos and hhmm in sig and hhmm != 1600:
                    sg = sig[hhmm]; up = max(op, pc) * (1 + sg); lo = min(op, pc) * (1 - sg)
                    s = 1 if C[k] > up else -1 if C[k] < lo else 0
                    if s: pos = s; e = O[k + 1]; sig_cur = sg
            if pos: out.append(_close(d, pos, e, C[slot(1600) - 1], slot(1600)))
        for t in checks:
            if full(d, k930, slot(t)): hist[t].append(abs(C[slot(t) - 1] / O[k930] - 1))
    return out
def _close(d, s, e, x, k):
    pts = (x - e) * s - SLIP_PTS
    return dict(d=d, side=s, pts=pts, net=pts * PV - 2 * COMM, xk=k, why='trail')

# ---------- L3 London pattern continuation (generic windows for the baseline) ----------
def l3(a0=2000, shift_h=0, hold_h=3, lo_room=0.04, hi_room=0.25):
    out = []
    base = slot(a0) + shift_h * 12
    aA, aZ, lZ = base, base + 72, base + 144          # range 6h, "London" 6h
    kx = lZ + 1 + hold_h * 12 - 1                        # entry at lZ+1 (08:05), exit after hold
    if kx > NS: return out
    for d in days():
        O, H, L, C = ETH[d]; adr = adr_of(d)
        AH, AL = max(H[aA:aZ]), min(L[aA:aZ]); LH, LL = max(H[aZ:lZ]), min(L[aZ:lZ]); mid = (LH + LL) / 2
        px = C[lZ]                                      # close of the 08:00 bar (known at 08:05)
        up = LH > AH and LL >= AL; dn = LL < AL and LH <= AH
        if up and px > mid: s, tg = 1, LH + .25
        elif dn and px < mid: s, tg = -1, LL - .25
        else: continue
        e = O[lZ + 1]; dist = (tg - e) * s
        if dist < lo_room * adr or dist > hi_room * adr: continue
        out.append(sim(d, s, lZ + 1, e, e - s * dist, tg, kx))
    return out

# ---------- L2 Asia sweep and reclaim (generic windows for the baseline) ----------
def l2(a0=2000, shift_h=0, ext_k=0.02, stop_k=0.02, win_h=3, exit_h=6):
    out = []
    base = slot(a0) + shift_h * 12
    aA, aZ = base, base + 72; wZ = aZ + win_h * 12; kx = aZ + exit_h * 12
    if kx > NS: return out
    for d in days():
        O, H, L, C = ETH[d]; adr = adr_of(d)
        AH, AL = max(H[aA:aZ]), min(L[aA:aZ]); mid = (AH + AL) / 2
        done = False
        for k in range(aZ, wZ):
            for side, lvl in ((-1, AH), (1, AL)):
                hit = H[k] >= AH + ext_k * adr if side < 0 else L[k] <= AL - ext_k * adr
                if not hit: continue
                ext = H[k] if side < 0 else L[k]
                for j in range(k, min(k + 3, wZ)):
                    ext = max(ext, H[j]) if side < 0 else min(ext, L[j])
                    back = C[j] < AH if side < 0 else C[j] > AL
                    if back:
                        e = O[j + 1]; stop = ext - side * stop_k * adr
                        t1, t2 = mid, (AL if side < 0 else AH)
                        if (t1 - e) * side <= 1: break
                        a = sim(d, side, j + 1, e, stop, t1, kx); b = sim(d, side, j + 1, e, stop, t2, kx)
                        out.append(dict(d=d, side=side, pts=(a['pts'] + b['pts']) / 2, net=(a['net'] + b['net']) / 2, xk=b['xk'], why=a['why'] + '/' + b['why']))
                        break
                done = True; break
            if done: break
    return out

# ---------- A1 / L1 sell-off evening or overnight long ----------
def a1(entry=1805, stopk=0.30, exit_=330, need_day_down=True, top_adr=False):
    out = []; adrs = []
    for d in days():
        p = prev_key(d); adr = adr_of(d); adrs.append(adr)
        if not p or not full(p, slot(930), slot(1600)): continue
        Op, Hp, Lp, Cp = ETH[p]
        last_hr = Cp[slot(1600) - 1] - Op[slot(1500)]; day = Cp[slot(1600) - 1] - Op[slot(930)]
        if last_hr > -0.15 * adr: continue
        if need_day_down and day >= 0: continue
        if top_adr and len(adrs) > 60 and adr < sorted(adrs[-250:])[int(len(adrs[-250:]) * 2 / 3)]: continue
        k = slot(entry); e = ETH[d][0][k]
        out.append(sim(d, 1, k, e, e - stopk * adr, None, slot(exit_)))
    return out

# ---------- M3 post-lunch long ----------
def m3(variant=''):
    out = []
    for d in days():
        O, H, L, C = ETH[d]; adr = adr_of(d)
        r11 = P(d, 1200) - P(d, 1100, 'o')
        if variant == 'b' and r11 >= 0: continue
        k = slot(1200); e = O[k]
        out.append(sim(d, 1, k, e, e - 0.2 * adr, None, slot(1400)))
        if variant == 'c':
            k1 = slot(1100); e1 = O[k1]
            out.append(sim(d, -1, k1, e1, e1 + 0.2 * adr, None, slot(1200)))
    return out

if __name__ == '__main__':
    print('== R1 / M1 last-half-hour momentum: 15:30 entry, sign of prior close -> 15:30, exit 15:59 (close of 15:55 bar) ==')
    for thr in (0.15, 0.3):
        for sk in (0.12, None):
            show(f"M1 thr{thr} stop{sk}", m1(thr, sk))
    show('M1b Gao filter thr0.15 stop0.12', m1(0.15, 0.12, 'gao'))
    show('M1c day range >= 1 ADR thr0.15 stop0.12', m1(0.15, 0.12, 'gamma'))
    show('M1 thr0 (always) stop0.12', m1(0.0, 0.12))
    print('\n== R2 / M2 Zarattini noise area 14:00-16:00, trail max(upper, RTH TWAP), checks 14:00/14:30/15:00/15:30 ==')
    show('M2 trail band+TWAP', m2(True), True)
    show('M2 trail band only', m2(False))
    show('M2 only 14:00 check', m2(True, (1400,)))
    print('\n== R3 / L3 London partial up/down continuation, entry 08:05, 1:1 to London extreme, exit 11:00 ==')
    tr = l3(); show('L3 as specified (range 20:00-02:00, London 02:00-08:00)', tr, True)
    show('L3 no room filter', l3(lo_room=0, hi_room=99))
    print('  baseline: identical rule on 6h+6h windows shifted through the session (same geometry, other clocks)')
    base = []
    for sh in (-2, -1, 1, 2, 3, 4, 5, 6):
        t = l3(shift_h=sh)
        if t: base += t; show(f"   shift {sh:+d}h (range starts {(20 + sh) % 24:02d}:00)", t)
    show('   pooled baseline', base)
    print('\n== R4 / L2 Asia range sweep (>= 0.02 ADR) and reclaim within 3 bars, 02:00-05:00, T1 mid / T2 far side, exit 08:00 ==')
    show('L2 as specified', l2(), True)
    show('L2 ext 0 (any trade beyond)', l2(ext_k=0))
    base = []
    for sh in (-2, -1, 1, 2, 3, 4, 5, 6, 7, 8):
        t = l2(shift_h=sh)
        if t: base += t; show(f"   shift {sh:+d}h (range starts {(20 + sh) % 24:02d}:00)", t)
    show('   pooled baseline', base)
    print('\n== R5 / A1, L1 after a weak 15:00-16:00 hour (<= -0.15 ADR), long overnight, exit 03:30 (per-year incl. late 2021) ==')
    show('A1 day down too, long 18:05 stop0.30', a1(1805, .30, 330, True), True)
    show('A1 last hour only, long 18:05 stop0.30', a1(1805, .30, 330, False), True)
    show('A1b day down too, long 01:30 stop0.20', a1(130, .20, 330, True), True)
    show('L1 last hour only, long 01:30 stop0.20', a1(130, .20, 330, False), True)
    show('A1c top-tercile ADR, long 18:05 stop0.30', a1(1805, .30, 330, True, True), True)
    show('L1 top-tercile ADR, long 01:30 stop0.20', a1(130, .20, 330, False, True), True)
    tr = a1(1805, .30, 330, True); print('    2021 only:', stats([t for t in tr if t['d'] < 20220101]))
    print('\n== R6 / M3 post-lunch long 12:00-14:00, stop 0.20 ADR ==')
    show('M3 long 12:00-14:00', m3(), True)
    show('M3b only if 11:00-12:00 down', m3('b'), True)
    show('M3c plus 11:00-12:00 short leg', m3('c'))
