"""Q3: neighbourhood checks around the few Q2 families that were not dead (avoid picking a lucky single cell).
Run: python3 q3_refine.py > out_q3.txt"""
from common import *
from q2_tests import P, cond_hold, sig_day, night_rev, prev_rth, sig_prev_rth_day, sig_win, is_mon

def clv_filter(t, lo):
    """location of price at time t inside the 9:30..t range, measured in the direction of the day: 1 = at the extreme"""
    def f(d):
        O, H, L, C = ETH[d]; a, z = slot(930), slot(t)
        hi, lw = max(H[a:z]), min(L[a:z]); c = C[z - 1]; op = O[a]
        if hi == lw: return False
        loc = (c - lw) / (hi - lw)
        return (loc if c > op else 1 - loc) >= lo
    return f

def sma_trend(n=20):
    """+1 if prior RTH close is above the mean of the prior n RTH closes, else -1 (known before 18:00)"""
    closes = {}
    for d in KEYS:
        r = rth_hlc(d)
        if r: closes[d] = r[2]
    ks = sorted(closes); out = {}
    for i in range(n, len(ks) - 1):
        m = sum(closes[k] for k in ks[i - n + 1:i + 1]) / n
        out[ks[i + 1]] = 1 if closes[ks[i]] > m else -1
    return out
TR = sma_trend(20)

if __name__ == '__main__':
    print('== F/E afternoon continuation: entry time x threshold x stop (signal = 9:30 open -> entry, exit 15:55) ==')
    for t in (1200, 1230, 1300, 1330, 1400, 1430):
        for thr in (0, 0.2, 0.4):
            for sk in (None, 0.25):
                print(row(f"cont {t} thr{thr} stop{sk}", cond_hold(sig_day(t), t, 1555, thr, 'cont', None, sk)))
    print('\n== afternoon continuation + location filter (price in outer part of the day range in the day direction) ==')
    for t in (1200, 1300, 1400):
        for lo in (0.5, 0.7, 0.8):
            print(row(f"cont {t} loc>={lo}", cond_hold(sig_day(t), t, 1555, 0, 'cont', clv_filter(t, lo))))
    print('\n== afternoon continuation by year (12:00, thr0) ==')
    tr = cond_hold(sig_day(1200), 1200, 1555, 0)
    for y in range(2022, 2027): print(y, stats([x for x in tr if x['d'] // 10000 == y]))
    print('\n== trend filter (prior close vs 20d SMA of RTH closes) for night holds ==')
    for a, z in ((1800, 925), (1800, 300), (300, 925), (2000, 300), (1800, 2000)):
        for m in ('cont', 'rev'):
            print(row(f"{m} SMA20 {a}-{z}", cond_hold(lambda d: TR.get(d), a, z, 0, m)))
        print(row(f"long only when SMA up {a}-{z}", cond_hold(lambda d: 1 if TR.get(d) == 1 else None, a, z)))
        print(row(f"long always {a}-{z}", cond_hold(lambda d: 1, a, z)))
    print('\n== C fade to TWAP after midnight: k grid ==')
    for k in (0.2, 0.25, 0.3, 0.35, 0.4):
        for sk in (0.1, 0.15, 0.25):
            print(row(f"fade twap 0-3 k{k} stop{sk} x4:00", night_rev((0, 300), k, sk, 'twap', 400)))
            print(row(f"fade twap 0-3 k{k} stop{sk} x6:00", night_rev((0, 300), k, sk, 'twap', 600)))
    print('\n== J prior RTH day direction reversed overnight (18:00-9:25), threshold grid ==')
    for thr in (0, 0.25, 0.5, 0.75, 1.0):
        for sk in (None, 0.3):
            print(row(f"rev prevRTH thr{thr} stop{sk}", cond_hold(sig_prev_rth_day, 1800, 925, thr, 'rev', None, sk)))
    print('\n== I Sunday: first 2h direction reversed 20:00-03:00 ==')
    for thr in (0, .05, .1, .2):
        print(row(f"rev Sun 18-20 thr{thr} 20:00-03:00", cond_hold(sig_win(1800, 2000), 2000, 300, thr, 'rev', is_mon)))
