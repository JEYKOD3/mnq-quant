"""PDC magnet test: touch frequency, gap fill, dwell, first-touch reaction, mechanical trades. All vs placebo levels.
Run: python3 scripts/pdc/pdc_test.py  -> writes scripts/pdc/out_pdc.md"""
import statistics as st, collections, math
from pdc_common import *
OUT = open('/home/claude/mnq-quant/scripts/pdc/out_pdc.md', 'w')
def out(*a):
    s = ' '.join(str(x) for x in a); print(s); OUT.write(s + '\n')

WIN = {'ON': (0, RTH_A), 'RTH': (RTH_A, RTH_Z)}
BK = [(0, .1), (.1, .25), (.25, .5), (.5, 1), (1, 99)]
def bname(b): return f"{b[0]:.2f}-{b[1]:.2f}" if b[1] < 99 else f">{b[0]:.0f}"
def bof(x):
    for b in BK:
        if b[0] <= x < b[1]: return b
def pct(v): return f"{100 * sum(v) / len(v):.0f}%" if v else '-'
def mean(v): return sum(v) / len(v) if v else float('nan')

# ---------- 1. touch frequency ----------
rec = collections.defaultdict(list)   # (win, name) -> list of dict
for d in SK:
    O, H, L, C = ETH[d]; a_ = S[d]['adr']
    for w, (a, z) in WIN.items():
        s0 = O[a]
        for nm, lv in levels(d, s0):
            k = first_touch(d, lv, a, z)
            rec[(w, nm)].append(dict(d=d, dist=abs(s0 - lv) / a_, k=k, t=None if k is None else (k - a) * 5, s=1 if s0 > lv else -1, lv=lv))

out('# 1. Touch frequency (window start price vs level, distance in ADR)\n')
for w in WIN:
    out(f"\n## {w} window ({'18:00-09:30, start = 18:00 open' if w == 'ON' else '09:30-16:00, start = 09:30 open'})\n")
    out("| Period | Dist ADR | PDC n | PDC touch | MIR touch | PDC-MIR pp (+/-2se) | P15 touch (n) | O2 touch (n) | SHIFT touch (n) | med min PDC / MIR |")
    out("|---|---|---|---|---|---|---|---|---|---|")
    for pn, pf_ in PERIODS:
        for b in BK:
            sel = {nm: [r for r in rec[(w, nm)] if pf_(r['d']) and bof(r['dist']) == b] for nm in NAMES}
            P = [r['k'] is not None for r in sel['PDC']]; M = [r['k'] is not None for r in sel['MIR']]
            if not P: continue
            pp = 100 * (mean(P) - mean(M)); se = 100 * math.sqrt((mean(P) * (1 - mean(P)) + mean(M) * (1 - mean(M))) / len(P))
            def oth(nm):
                v = [r['k'] is not None for r in sel[nm]]
                return f"{pct(v)} ({len(v)})"
            tp = [r['t'] for r in sel['PDC'] if r['t'] is not None]; tm = [r['t'] for r in sel['MIR'] if r['t'] is not None]
            out(f"| {pn} | {bname(b)} | {len(P)} | {pct(P)} | {pct(M)} | {pp:+.0f} (+/-{2 * se:.0f}) | {oth('P15')} | {oth('O2')} | {oth('SHIFT')} | "
                f"{st.median(tp) if tp else '-'} / {st.median(tm) if tm else '-'} |")

# ---------- 2. gap fill ----------
out('\n# 2. Gap fill at the RTH open (9:30 open vs level)\n')
out("| Period | Gap ADR | Dir | n | PDC fill 10:00 | 11:00 | close | MIR fill 10:00 | 11:00 | close |")
out("|---|---|---|---|---|---|---|---|---|---|")
cut = {'10:00': 192, '11:00': 198, 'close': 264}
for pn, pf_ in PERIODS:
    for b in BK[:4] + [(1, 99)]:
        for dr, dn in ((1, 'up'), (-1, 'down')):
            rp = [r for r in rec[('RTH', 'PDC')] if pf_(r['d']) and bof(r['dist']) == b and r['s'] == dr]
            rm = [r for r in rec[('RTH', 'MIR')] if pf_(r['d']) and bof(r['dist']) == b and r['s'] == -dr]  # mirror of same days
            if len(rp) < 5: continue
            f = lambda rr, c: pct([r['k'] is not None and r['k'] < c for r in rr])
            out(f"| {pn} | {bname(b)} | {dn} | {len(rp)} | {f(rp, 192)} | {f(rp, 198)} | {f(rp, 264)} | {f(rm, 192)} | {f(rm, 198)} | {f(rm, 264)} |")
out("\nGap direction pooled, all levels (each bucketed by its own distance from the 9:30 open), fill by 11:00 / by close:\n")
out("| Period | Dist ADR | PDC | MIR | P15 | O2 | SHIFT |")
out("|---|---|---|---|---|---|---|")
for pn, pf_ in PERIODS:
    for b in BK:
        cells = []
        for nm in NAMES:
            rr = [r for r in rec[('RTH', nm)] if pf_(r['d']) and bof(r['dist']) == b]
            cells.append(f"{pct([r['k'] is not None and r['k'] < 198 for r in rr])} / {pct([r['k'] is not None for r in rr])} ({len(rr)})")
        out(f"| {pn} | {bname(b)} | " + ' | '.join(cells) + ' |')

# ---------- 3. dwell ----------
out('\n# 3. Dwell: share of 5m closes within 0.05 ADR of the level\n')
out("A = all sessions. B = sessions whose start is within 0.25 ADR of that level. C = the 12 bars (60 min) after the first touch: share of closes in the band and mean number of side switches of the close.\n")
out("| Window | Period | Level | A dwell | B n | B dwell | C n | C dwell | C switches |")
out("|---|---|---|---|---|---|---|---|---|")
for w, (a, z) in WIN.items():
    for pn, pf_ in PERIODS:
        for nm in NAMES:
            A = []; B = []; Cd = []; Cs = []
            for r in rec[(w, nm)]:
                if not pf_(r['d']): continue
                O, H, L, C = ETH[r['d']]; band = .05 * S[r['d']]['adr']; lv = r['lv']
                fr = sum(abs(C[k] - lv) <= band for k in range(a, z)) / (z - a)
                A.append(fr)
                if r['dist'] <= .25: B.append(fr)
                k = r['k']
                if k is not None and r['dist'] >= .05 and k + 12 < z:
                    xs = [C[j] for j in range(k + 1, k + 13)]
                    Cd.append(sum(abs(x - lv) <= band for x in xs) / 12)
                    sg = [1 if x > lv else -1 for x in [C[k]] + xs]
                    Cs.append(sum(sg[i] != sg[i - 1] for i in range(1, len(sg))))
            out(f"| {w} | {pn} | {nm} | {100 * mean(A):.1f}% | {len(B)} | {100 * mean(B):.1f}% | {len(Cd)} | {100 * mean(Cd):.1f}% | {mean(Cs):.2f} |")

# ---------- 4. first-touch reaction ----------
out('\n# 4. Reaction on first touch (start at least 0.05 ADR away)\n')
out("Approach side = side price came from. Rej30/Rej60 = close 30/60 min after the touch bar is back on the approach side. "
    "Mean60 = signed close at +60 min in ADR (positive = bounce). Race = bounce +0.1 ADR before through -0.1 ADR (touch bar can only count as through; ties 0.5).\n")
out("| Window | Period | Level | n | Rej30 | Rej60 | Mean60 ADR | Race win |")
out("|---|---|---|---|---|---|---|---|")
for w, (a, z) in WIN.items():
    zz = z if w == 'ON' else 252   # need 12 bars after the touch inside the RTH
    for pn, pf_ in PERIODS:
        for nm in NAMES:
            r30 = []; r60 = []; m60 = []; race = []
            for r in rec[(w, nm)]:
                k = r['k']
                if not pf_(r['d']) or k is None or r['dist'] < .05 or k >= zz: continue
                O, H, L, C = ETH[r['d']]; ad = S[r['d']]['adr']; s = r['s']; lv = r['lv']
                r30.append((C[k + 6] - lv) * s > 0); r60.append((C[k + 12] - lv) * s > 0); m60.append((C[k + 12] - lv) * s / ad)
                up, dn = lv + s * .1 * ad, lv - s * .1 * ad
                if (s > 0 and L[k] <= dn) or (s < 0 and H[k] >= dn): race.append(0); continue
                res = .5
                for j in range(k + 1, k + 13):
                    hb = (H[j] >= up) if s > 0 else (L[j] <= up)
                    ht = (L[j] <= dn) if s > 0 else (H[j] >= dn)
                    if hb and ht: res = .5; break
                    if hb: res = 1; break
                    if ht: res = 0; break
                race.append(res)
            out(f"| {w} | {pn} | {nm} | {len(r60)} | {pct(r30)} | {pct(r60)} | {mean(m60):+.3f} | {100 * mean(race):.0f}% |")

# ---------- 5. mechanical tests ----------
out('\n# 5. Mechanical tests (1 MNQ, costs in)\n')
def fade930(nm, lo=.1, hi=.6, stop=.25, kx=198):
    tr = []
    for d in SK:
        O = ETH[d][0]; ad = S[d]['adr']; s0 = O[RTH_A]
        for n2, lv in levels(d, s0):
            if n2 != nm: continue
            g = (s0 - lv) / ad
            if not (lo <= abs(g) <= hi): continue
            side = -1 if g > 0 else 1
            tr.append(sim(d, side, RTH_A, s0, s0 - side * stop * ad, lv, kx))
    return tr
out("## 5a. 9:30 market fade toward the level, target = level, stop 0.25 ADR, exit 11:00, |gap| 0.1-0.6 ADR\n")
out("MIR = trade toward the mirror level, i.e. follow the gap with the same target distance.\n")
out(THEAD)
for nm in NAMES: out(trow(f"5a {nm}", fade930(nm)))
for lo, hi, sp in ((.1, .3, .25), (.3, .6, .25), (.1, .6, .15), (.1, .6, .4)):
    out(trow(f"5a PDC gap {lo}-{hi} stop {sp}", fade930('PDC', lo, hi, sp)))
    out(trow(f"5a MIR gap {lo}-{hi} stop {sp}", fade930('MIR', lo, hi, sp)))

def touch_trade(nm, w, stop, tgt, hold=12):
    a, z = WIN[w]
    k_from, k_last, kmax = (a + 1, 174, RTH_A) if w == 'ON' else (a + 1, 252, RTH_Z)
    tr = []
    for d in SK:
        O = ETH[d][0]; ad = S[d]['adr']; s0 = O[a]
        for n2, lv in levels(d, s0):
            if n2 != nm or abs(s0 - lv) < .05 * ad: continue
            side = 1 if s0 > lv else -1   # came from above -> buy the touch
            t = limit_trade(d, side, lv, k_from, k_last, stop * ad, tgt * ad, hold, kmax)
            if t: tr.append(t)
    return tr
out("\n## 5b. First-touch rejection: limit at the level on the approach side (start >= 0.05 ADR away), time exit 60 min\n")
out("RTH touches 9:35-15:00, ON touches 18:05-08:30 (exit by 9:30).\n")
out(THEAD)
for w in ('RTH', 'ON'):
    for sp, tg in ((.1, .1), (.1, .2), (.15, .3)):
        for nm in NAMES: out(trow(f"5b {w} {nm} stop {sp} tgt {tg}", touch_trade(nm, w, sp, tg)))

def evening(nm, lo=.05, hi=.3, stop=.2, k0=0):
    tr = []
    for d in SK:
        O = ETH[d][0]; ad = S[d]['adr']; s0 = O[0]
        for n2, lv in levels(d, s0):
            if n2 != nm: continue
            g = (O[k0] - lv) / ad
            if not (lo <= abs(g) <= hi): continue
            side = -1 if g > 0 else 1
            tr.append(sim(d, side, k0, O[k0], O[k0] - side * stop * ad, lv, 24))
    return tr
out("\n## 5c. Evening 18:00 market fade toward the level, target = level, exit 20:00, 0.05-0.3 ADR away\n")
out("MIR here = follow the 16:00 -> 18:00 change with the same target distance.\n")
out(THEAD)
for sp in (.15, .2, .3):
    for nm in NAMES: out(trow(f"5c {nm} stop {sp}", evening(nm, stop=sp)))
out(trow("5c PDC stop 0.2 entry 18:05", evening('PDC', stop=.2, k0=1)))
out(trow("5c MIR stop 0.2 entry 18:05", evening('MIR', stop=.2, k0=1)))
OUT.close()

# ---------- 6. Sunday evenings and far gaps (pooled 2022-2026) ----------
import datetime
OUT = open('/home/claude/mnq-quant/scripts/pdc/out_pdc.md', 'a')
out('\n# 6. Extra checks, pooled 2022-2026\n')
out("Sunday night = sessions whose key is a Monday (Friday 16:00 close is the PDC). ON window 18:00-09:30. Dwell = share of 5m closes within 0.05 ADR, all sessions.\n")
out("| Slice | Level | n | touch | touch if start <0.25 ADR (n) | dwell all | dwell first 3h (18:00-21:00) |")
out("|---|---|---|---|---|---|---|")
def wdk(d): return datetime.date(d // 10000, d // 100 % 100, d % 100).weekday()
for sl, fd in (('Sunday', lambda d: wdk(d) == 0), ('Mon-Thu nights', lambda d: wdk(d) != 0)):
    for nm in NAMES:
        rr = [r for r in rec[('ON', nm)] if fd(r['d'])]
        near = [r['k'] is not None for r in rr if r['dist'] < .25]
        dw = []; dw3 = []
        for r in rr:
            C = ETH[r['d']][3]; band = .05 * S[r['d']]['adr']
            dw.append(sum(abs(C[k] - r['lv']) <= band for k in range(0, RTH_A)) / RTH_A)
            dw3.append(sum(abs(C[k] - r['lv']) <= band for k in range(0, 36)) / 36)
        out(f"| {sl} | {nm} | {len(rr)} | {pct([r['k'] is not None for r in rr])} | {pct(near)} ({len(near)}) | {100 * mean(dw):.1f}% | {100 * mean(dw3):.1f}% |")
out("\nRTH open at least 0.5 ADR from the level, touched by the close:\n")
out("| Level | n | touch by close | +/-2se |")
out("|---|---|---|---|")
for nm in NAMES:
    v = [r['k'] is not None for r in rec[('RTH', nm)] if r['dist'] >= .5]
    p = mean(v); out(f"| {nm} | {len(v)} | {100 * p:.0f}% | {200 * math.sqrt(p * (1 - p) / len(v)):.0f} |")
OUT.close()
