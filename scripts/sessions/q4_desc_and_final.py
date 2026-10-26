"""Q4: descriptive base rates (sweeps, persistence) + lunch-range break + final candidate stats (per year, trades/yr, max DD).
Run: python3 q4_desc_and_final.py > out_q4.txt"""
from common import *
from q2_tests import P, cond_hold, sig_day, night_rev, sig_prev_rth_day, sig_win, is_mon, prev_rth

def pct(x): return f"{x:.0%}"
def per(f):
    A = [d for d in sessions() if d < 20250101]; B = [d for d in sessions() if d >= 20250101]
    return f(A), f(B)

def desc():
    print('== D1 Asia range (20:00-02:00) vs London (03:00-06:00) ==')
    def f(days):
        sw = 0; both = 0; back_mid = 0; n = 0; brk_hold = 0
        for d in days:
            O, H, L, C = ETH[d]; a, z = slot(2000), slot(200); la, lz = slot(300), slot(600)
            AH, AL = max(H[a:z]), min(L[a:z]); mid = (AH + AL) / 2
            if max(H[z:la]) > AH or min(L[z:la]) < AL: continue
            n += 1
            uh = max(H[la:lz]) > AH; dl = min(L[la:lz]) < AL
            if uh or dl: sw += 1
            if uh and dl: both += 1
            if uh != dl:
                first = next(k for k in range(la, lz) if H[k] > AH or L[k] < AL)
                tm = next((k for k in range(first + 1, slot(925)) if L[k] <= mid <= H[k]), None)
                back_mid += tm is not None
                brk_hold += (C[slot(925) - 1] > AH) if uh else (C[slot(925) - 1] < AL)
        one = sw - both
        return f"days {n}: London takes a side {pct(sw / n)}, both sides {pct(both / n)}; one-side sweeps that revisit Asia mid by 9:25 {pct(back_mid / max(one, 1))}, still beyond the swept side at 9:25 {pct(brk_hold / max(one, 1))}"
    a, b = per(f); print('IS ', a); print('OOS', b)
    print('\n== D2 sign agreement: overnight (18:00-9:30) vs RTH windows ==')
    def g(days, w):
        s = [((P(d, 930) - ETH[d][0][0]) * (P(d, w[1]) - P(d, w[0], 'o'))) > 0 for d in days]
        return pct(sum(s) / len(s))
    for w in ((930, 1600), (930, 1000), (1200, 1555), (1400, 1555)):
        a, b = per(lambda days: g(days, w)); print(f"ON same sign as {w[0]}-{w[1]}: IS {a} OOS {b}")
    print('\n== D3 sign agreement: morning 9:30->12:00 vs 12:00->15:55, and 9:30->13:00 vs 13:00->15:55 ==')
    for t in (1200, 1300):
        def h(days):
            s = [((P(d, t) - P(d, 930, 'o')) * (P(d, 1555) - P(d, t, 'o'))) > 0 for d in days]
            return pct(sum(s) / len(s))
        a, b = per(h); print(f"9:30->{t} vs {t}->15:55 same sign: IS {a} OOS {b}")
    print('\n== D4 prior-day RTH high/low touched overnight (18:00-9:25), when 18:00 opens inside prior range ==')
    def k(days):
        n = t = brk = 0
        for d in days:
            r = prev_rth(d)
            if not r: continue
            PH, PL, _ = r; O, H, L, C = ETH[d]; adr = adr_of(d)
            if not (PL < O[0] < PH): continue
            n += 1; z = slot(925)
            hit = next((j for j in range(0, z) if H[j] >= PH or L[j] <= PL), None)
            if hit is None: continue
            t += 1
            up = H[hit] >= PH
            ext = max(H[hit:z]) - PH if up else PL - min(L[hit:z])
            brk += ext >= 0.15 * adr
        return f"days {n}: touch {pct(t / n)}, of touches extend >= 0.15 ADR beyond {pct(brk / max(t, 1))}"
    a, b = per(k); print('IS ', a); print('OOS', b)

def lunch_break(dir_filter=True, stop='mid', exit_=1555, a_=1200, z_=1400):
    out = []
    for d in sessions():
        O, H, L, C = ETH[d]; a, z = slot(a_), slot(z_); adr = adr_of(d)
        hi, lo = max(H[a:z]), min(L[a:z]); mid = (hi + lo) / 2
        day = C[z - 1] - O[slot(930)]
        for k in range(z, slot(exit_) - 1):
            s = 1 if C[k] > hi else -1 if C[k] < lo else 0
            if not s: continue
            if dir_filter and s * day <= 0: break
            e = O[k + 1]; st = mid if stop == 'mid' else (lo if s > 0 else hi)
            if (e - st) * s <= 0: break
            out.append(sim(d, s, k + 1, e, st, None, slot(exit_))); break
    return out

def full_stats(name, tr):
    a, b = split(tr); S = stats(tr)
    yrs = {}
    for t in tr: yrs.setdefault(t['d'] // 10000, []).append(t)
    tpy = len(tr) / (len(list(sessions())) / 252)
    print(f"\n### {name}")
    print(row('IS/OOS', tr))
    print(f"all: n {S['n']} trades/yr {tpy:.0f} win {S['win']:.0%} avg {S['avgpts']:+.1f}pt ${S['avg']:+.1f}/trade PF {S['pf']:.2f} maxDD ${S['dd']:.0f} tot ${S['tot']:.0f}")
    for y, v in sorted(yrs.items()):
        s = stats(v); print(f"  {y}: n {s['n']} win {s['win']:.0%} PF {s['pf']:.2f} tot ${s['tot']:+.0f} dd ${s['dd']:.0f}")
    whys = collections.Counter(t['why'] for t in tr); print('  exits', dict(whys))

if __name__ == '__main__':
    desc()
    print('\n== lunch range (12:00-14:00) break after 14:00 ==')
    for df in (True, False):
        for stp in ('mid', 'opp'):
            print(row(f"lunch break dirfilter={df} stop={stp}", lunch_break(df, stp)))
    for a_, z_ in ((1200, 1300), (1230, 1400), (1300, 1400)):
        print(row(f"range {a_}-{z_} break, dir filter, stop mid", lunch_break(True, 'mid', 1555, a_, z_)))
    print('\n================ FINAL CANDIDATES ================')
    full_stats('S1 afternoon continuation 12:30 thr0.2 stop0.25 ADR', cond_hold(sig_day(1230), 1230, 1555, 0.2, 'cont', None, 0.25))
    full_stats('S1b afternoon continuation 13:00 thr0.2 no stop', cond_hold(sig_day(1300), 1300, 1555, 0.2, 'cont'))
    full_stats('S1c afternoon continuation 13:00 thr0.2 stop0.25 ADR', cond_hold(sig_day(1300), 1300, 1555, 0.2, 'cont', None, 0.25))
    full_stats('S2 lunch-range break with day direction', lunch_break(True, 'mid'))
    full_stats('S3 midnight TWAP stretch fade k0.3 stop0.15 x6:00', night_rev((0, 300), 0.3, 0.15, 'twap', 600))
    full_stats('W1 prior RTH big day (>=0.75 ADR) faded overnight 18:00-9:25 stop0.3', cond_hold(sig_prev_rth_day, 1800, 925, 0.75, 'rev', None, 0.3))
    full_stats('W2 long Tue-night (Wed key) 18:00-9:25', cond_hold(lambda d: 1, 1800, 925, 0, 'cont', lambda d: wd(d) == 2))

def on_agree(t):
    return lambda d: (P(d, 930) - ETH[d][0][0]) * (P(d, t) - P(d, 930, 'o')) > 0
if __name__ == '__main__':
    full_stats('S1* afternoon continuation 13:00 thr0.15 stop0.35 ADR (chosen)', cond_hold(sig_day(1300), 1300, 1555, 0.15, 'cont', None, 0.35))
    full_stats('S1A* same + overnight agrees with morning', cond_hold(sig_day(1300), 1300, 1555, 0.15, 'cont', on_agree(1300), 0.35))
    full_stats('S3* midnight TWAP stretch fade k0.3 stop0.15 x4:00', night_rev((0, 300), 0.3, 0.15, 'twap', 400))
