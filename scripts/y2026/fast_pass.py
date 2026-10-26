"""Fast-pass study for the Lucid Flex 50K eval (Oct 26 2026).
Sequential rolling evals: every trading day of a year is a start, the eval then runs on the real following days.
Lucid Flex 50K: target $3,000, EOD trailing $2,000 floor capped at 50,100, best day <= 40% of total profit at the pass,
$1,200 daily loss limit (soft: flattened, day over), max 40 MNQ. Intraday floor breach uses the 1m path (prop_sim.day_path).
SYM=MES env: same strategies run on MES (5m bars expanded to 1m: open, open, high/low, close, close), PV $5, NEWS off.
Usage: python3 fast_pass.py [grid|fail|mes] ; writes JSON next to this file."""
import os, sys, json, collections, statistics
SYM = os.environ.get('SYM', 'MNQ')
L = '/home/claude/mnq-quant/scripts/lab'
for p in (L, '/home/claude/mnq-quant/scripts/discover', '/home/claude/mnq-quant/scripts/fair', os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path: sys.path.insert(0, p)
if SYM == 'MES':
    import core
    core.PV = 5.0
    def _mes(path=None):
        days = []
        for ln in open('/home/claude/mnq-quant/data/raw/mes_rth_5m.txt'):
            p = ln.strip().split('|')
            if len(p) < 2: continue
            b = []
            for x in p[1:]:
                t, o, h, l, c = x.split(','); t = int(t); m = t // 100 * 60 + t % 100
                o, h, l, c = int(o) / 4, int(h) / 4, int(l) / 4, int(c) / 4
                mid = (h, l) if c >= o else (h, l)
                b += [(m, o, max(o, o), min(o, o), o), (m + 1, o, o, o, o), (m + 2, o, h, l, c), (m + 3, c, c, c, c), (m + 4, c, c, c, c)]
            days.append((int(p[0]), b))
        return days
    core.load = _mes
from prop_sim import *                     # rulesets/common/rules2 (D, DB, PV ...), day_path
import prop_sim as PS
import common as CM
PVX = 5.0 if SYM == 'MES' else 2.0
SLIPX = 2.0 if SYM == 'MES' else 8.0      # coded extra slip on stop exits, points (MNQ 8 pts ~ MES 2 pts)
LAST = 20261020 if SYM == 'MES' else 99999999

def build_trades():
    if SYM == 'MES':
        tr = CM.v4(flat=900) + CM.d2(th=.6, flat=795) + CM.tdp(tgtR=1.5, flat=900) + CM.pinball(tgtR=2, cap=180, flat=900) + CM.h2(tgtR=2, flat=900)
    else:
        tr = CM.news() + CM.v4(flat=900) + CM.d2(th=.6, flat=795) + CM.tdp(tgtR=1.5, flat=900) + CM.pinball(tgtR=2, cap=180, flat=900) + CM.h2(tgtR=2, flat=900)
    tr = [t for t in tr if t['d'] <= LAST]
    tr.sort(key=lambda t: (t['d'], t['eT'], PRI.get(t['strat'], 9)))
    return tr

COMMX = COMM
def risk1(t): return (t['r'] + SLIP * T + SLIPX) * PVX + 2 * COMMX

def size_plan(trs, cush, P, dayn, prof0, best0, target=3000., cons=.4):
    """returns sized list. P keys: f, budget (list by day index or number), maxq, strats, sd, pcap (stop new entries once day realized >= pcap),
    fixed (contracts per trade, overrides room sizing), rec (recovery 1-lot when room<400), guard (q*risk1 <= room-100)."""
    bud = P['budget']; bud = bud[min(dayn - 1, len(bud) - 1)] if isinstance(bud, (list, tuple)) else bud
    f = P.get('f', .65); maxq = P.get('maxq', 40); sd = P.get('sd', 3); pcap = P.get('pcap'); fixed = P.get('fixed')
    done = []
    for t in trs:
        if P.get('strats') and t['strat'] not in P['strats']: continue
        if P.get('skipev') and t.get('evday'): continue
        cl = [u for u in done if u['xT'] <= t['eT']]
        rl = -sum(min(0, u['netq']) for u in cl); rp = sum(u['netq'] for u in cl); nl = sum(u['netq'] < 0 for u in cl)
        passed = prof0 + rp >= target and max(best0, rp) <= cons * (prof0 + rp)
        room = cush + rp
        stop = rl >= bud - 150 or (sd and nl >= sd) or passed or (pcap is not None and rp >= pcap)
        rc = (t['r'] + SLIP * T) * PVX + 2 * COMMX
        pts = t['pts'] - (SLIPX if t['why'] in STOPWHY else 0)
        pc = pts * PVX - 2 * COMMX
        used = 0; openr = 0
        for u in done:
            if u['q'] == 0: continue
            if u['xT'] <= t['eT']: used += max(0, -u['netq'])
            elif u['be'] is not None and u['be'] <= t['eT']: pass
            else: used += u['q'] * u['rc']; openr += u['q'] * risk1(u)
        q = 0
        if not stop:
            live = room - openr
            if room < 400:
                if P.get('rec', True) and risk1(t) <= live - 100: q = 1
            else:
                if fixed: q = max(1, int(fixed * t['w'] + .5))
                elif P.get('riskd'):
                    rd = P['riskd'] + P.get('grow', 0) * max(0, prof0 + rp)
                    rd = min(rd, bud - used)
                    q = int(t['w'] * rd // rc) if rd > 0 else 0
                    if q < 1 and P.get('min1', True) and t['w'] >= 1 and rc < bud - used: q = 1
                else:
                    b = min(t['w'] * f * cush, f * cush - used, bud - used); q = int(b // rc) if b > 0 else 0
                    if q < 1 and t['w'] >= 1 and rc < .9 * (cush - used) and rc < bud - used: q = 1
                q = min(q, maxq)
                if P.get('guard', True):
                    while q > 0 and q * risk1(t) > live - 100: q -= 1
                # never let a single trade's worst case break the Lucid DLL together with today's losses
                while q > 0 and rl + q * risk1(t) > 1200: q -= 1
        u = dict(t); u['q'] = q; u['rc'] = rc; u['pc'] = pc; u['netq'] = q * pc
        done.append(u)
    return done

def lucid_day(trs, bal, floor, P, dayn, prof0, best0):
    done = size_plan(trs, bal - floor, P, dayn, prof0, best0)
    PS.PV = PVX
    lo, hi = day_path(done)
    dp = sum(t['netq'] for t in done)
    if lo is None: return 0.0, 'ok', done
    hit = np.nonzero(lo <= -1200)[0]
    if len(hit): lo = lo[:hit[0] + 1]; dp = -1200.0
    if np.any(bal + lo <= floor): return float(lo.min()), 'fail', done
    return dp, 'ok', done

def eval_seq(byd, seq, P, H=20, keep=False):
    bal = 50000.; peak = 50000.; best = 0.; worst = 0.; log = []
    for n, d in enumerate(seq[:H], 1):
        floor = min(peak - 2000, 50100)
        dp, st, done = lucid_day(byd.get(d, []), bal, floor, P, n, bal - 50000, best)
        if keep: log.append((d, round(dp), [(t['strat'], t['q'], round(t['netq'])) for t in done if t['q']]))
        if st == 'fail': return dict(res='F', n=n, worst=round(bal + dp - 50000), log=log)
        bal += dp; best = max(best, dp); worst = min(worst, bal - 50000)
        if bal <= floor: return dict(res='F', n=n, worst=round(worst), log=log)
        peak = max(peak, bal); prof = bal - 50000
        if prof >= 3000 and best <= .4 * prof: return dict(res='P', n=n, worst=round(worst), log=log)
    return dict(res='O', n=len(seq[:H]), worst=round(worst), log=log, end=round(bal - 50000), cons_block=bal - 50000 >= 3000)

def roll(byd, P, a, z, H=20, keep=False):
    days = [d for d in D if d <= LAST and d >= 20220301]
    starts = [i for i, d in enumerate(days) if a <= d <= z]
    R = []
    for i in starts:
        seq = days[i:]
        if len(seq) < 5: continue
        r = eval_seq(byd, seq, P, H, keep); r['start'] = days[i]; r['avail'] = len(seq); R.append(r)
    return R

def summ(R):
    n = len(R)
    def pin(k): return round(sum(r['res'] == 'P' and r['n'] <= k for r in R) / n, 3)
    P_ = [r['n'] for r in R if r['res'] == 'P']
    return dict(n=n, p5=pin(5), p8=pin(8), p10=pin(10), p20=pin(20), bust20=round(sum(r['res'] == 'F' for r in R) / n, 3),
                bust8=round(sum(r['res'] == 'F' and r['n'] <= 8 for r in R) / n, 3),
                med=statistics.median(P_) if P_ else None, worst=min(r['worst'] for r in R),
                consblk=round(sum(r['res'] == 'O' and r.get('cons_block') for r in R) / n, 3))

YEARS = {'2026': (20260101, 20261231), '2025': (20250101, 20251231), '2022': (20220301, 20221231)}

if __name__ == '__main__':
    tr = build_trades(); byd = byday(tr)
    print(SYM, 'trades', len(tr), collections.Counter(t['strat'] for t in tr if t['d'] >= 20260101), flush=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'grid'
    from fast_plans import plans_for
    out = {}
    for name, P in plans_for(mode):
        row = {}
        for y, (a, z) in YEARS.items(): row[y] = summ(roll(byd, P, a, z))
        out[name] = dict(P=P, **row)
        print(f"{name:28s}", ' | '.join(f"{y}: p5 {row[y]['p5']:.2f} p8 {row[y]['p8']:.2f} p20 {row[y]['p20']:.2f} bust {row[y]['bust20']:.2f} med {row[y]['med']} worst {row[y]['worst']}" for y in YEARS), flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'fast_{mode}_{SYM}.json'), 'w'), indent=1, default=str)
