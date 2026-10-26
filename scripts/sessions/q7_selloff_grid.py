"""Q7: neighbourhood grid for the sell-off overnight long (A1 / A1b from q6). Threshold x entry x stop x exit."""
from common import *
from q6_research import days, per_year
from q2_tests import P
def a1g(thr=0.15, entry=1805, stopk=0.30, exit_=330, need_day_down=True, mirror=False):
    out = []
    for d in days():
        p = prev_key(d); adr = adr_of(d)
        if not p or not full(p, slot(930), slot(1600)): continue
        Op, Hp, Lp, Cp = ETH[p]
        lh = Cp[slot(1600) - 1] - Op[slot(1500)]; day = Cp[slot(1600) - 1] - Op[slot(930)]
        s = 1
        if mirror: lh, day, s = -lh, -day, -1          # strong rally last hour -> short overnight
        if lh > -thr * adr or (need_day_down and day >= 0): continue
        k = slot(entry); e = ETH[d][0][k]
        out.append(sim(d, s, k, e, e - s * stopk * adr if stopk else None, None, slot(exit_)))
    return out
def r(name, tr): print(row(name, [t for t in tr if t['d'] >= 20220101]))
if __name__ == '__main__':
    for thr in (0.1, 0.15, 0.2, 0.25):
        for ent, sk in ((1805, .3), (1805, None), (2000, .3), (0, .25), (130, .2), (130, None)):
            for ex in (330, 600, 925):
                if ent == 130 and ex == 925: continue
                r(f"thr{thr} in{ent:04d} stop{sk} x{ex:04d}", a1g(thr, ent, sk, ex))
    print('\n-- day-down filter off / mirror (short after a strong rally hour) --')
    for thr in (0.15, 0.25):
        r(f"no day filter thr{thr} 18:05 stop.3 x3:30", a1g(thr, 1805, .3, 330, False))
        r(f"MIRROR short thr{thr} 18:05 stop.3 x3:30", a1g(thr, 1805, .3, 330, True, True))
        r(f"MIRROR short thr{thr} 01:30 stop.2 x3:30", a1g(thr, 130, .2, 330, True, True))
    print('\n-- full stats, chosen cells --')
    for nm, tr in (('A1 18:05 thr0.15 stop0.30 x3:30', a1g()), ('A1b 01:30 thr0.15 stop0.20 x3:30', a1g(0.15, 130, .2, 330))):
        tr = [t for t in tr if t['d'] >= 20220101]; s = stats(tr)
        print(nm, f"n {s['n']} trades/yr {s['n'] / 4.74:.0f} win {s['win']:.0%} avg {s['avgpts']:+.1f}pt ${s['avg']:+.1f} PF {s['pf']:.2f} maxDD ${s['dd']:.0f} tot ${s['tot']:.0f}", dict(collections.Counter(t['why'] for t in tr)))
        print('   ', per_year(tr))
