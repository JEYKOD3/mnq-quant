"""Evening module: final rules, budget sizing, and a Lucid Flex 50K eval simulation alongside the day engine.
Rules (1 trade per evening max, flat by 20:00):
  SGP  Sunday Gap Pullback: Sunday, gap = 18:00 open - Friday 17:00 close, |gap| >= 0.05 ADR; limit in the gap direction at
       half the gap back toward Friday's close, fill by 19:30; stop 0.15 ADR; exit 20:00.
  WCC  Wednesday Close Continuation: Wednesday, x = 18:00 open - Wednesday 16:00 close, |x| >= 0.05 ADR; market at the 18:05 bar
       open in the sign of x; stop 0.20 ADR; exit 20:00.
  Alternatives scored for comparison: G16 (same as WCC but Mon-Thu), G16-EDT (Mon-Thu, only while US daylight time is in force).
Eval: Lucid Flex 50K, EOD trailing $2,000 (mll = min(peakEOD - 2000, 50000)), $3,000 target, best day <= 50% of profit.
Day engine = final defaults 2026-10-25 (rules2.build('current', be=True, v4t=1.25), size_day 'updated', 65% of room, $1,100/day,
8-pt stop slip stress). The evening trade belongs to the next trading day (futures day starts 18:00), so it is added to that
day's P&L and the day engine sizes off the room left after it. Evening stop exits get an extra 2-pt slip stress in the eval."""
import sys, os, math, statistics as S
sys.path.insert(0, '/home/claude/mnq-quant/scripts/evening')
from ev_common import *
out = Out('/home/claude/mnq-quant/scripts/evening/out_e7.txt')

def sgp():
    tr = []
    for d in keys((0,)):
        e = EV[d]; a = e['adr']; g = e['o18'] - e['c17']
        if abs(g) < .05 * a: continue
        s = 1 if g > 0 else -1
        t = lim(d, s, e['o18'] - s * .5 * abs(g), 0, 17, .15 * a, None, 24)
        if t: t['rule'] = 'SGP'; t['rpts'] = .15 * a; tr.append(t)
    return tr

def g16(dows=(3,), dst=None, thr=.05, stop=.2, name='WCC'):
    tr = []
    for d in keys(dows):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        x = e['o18'] - e['c16']
        if abs(x) < thr * a or x == 0: continue
        t = mkt(d, 1 if x > 0 else -1, 1, stop * a, None, 24)
        if t: t['rule'] = name; t['rpts'] = stop * a; tr.append(t)
    return tr

def tstat(tr):
    n = [t['net'] for t in tr]
    return S.mean(n) / (S.pstdev(n) / len(n) ** .5) if len(n) > 2 else 0

RULES = {'SGP': sgp(), 'WCC': g16(), 'G16 Mon-Thu': g16((1, 2, 3, 4), name='G16'), 'G16-EDT Mon-Thu': g16((1, 2, 3, 4), True, name='G16E')}
out('## Final rule stats, 1 MNQ, costs in\n'); out(HEAD)
for k, tr in RULES.items(): out(md(k, tr))
out('\n| Rule | trades/yr | t-stat IS | t-stat OOS | avg stop pts 2026 | avg risk $/MNQ 2026 | per-year PF 2022..2026 |\n|---|---|---|---|---|---|---|')
for k, tr in RULES.items():
    a, b, c = parts(tr)
    yp = []
    for y in range(2022, 2027):
        v = [t['net'] for t in tr if t['d'] // 10000 == y]; yp.append(f"{pf(v):.2f}" if v else '-')
    r26 = [t['rpts'] for t in c] or [0]
    out(f"| {k} | {len(tr)/ (4 + 9.7/12):.0f} | {tstat(a):+.1f} | {tstat(b):+.1f} | {S.mean(r26):.0f} | {S.mean(r26)*PV + 2*COMM + SLIP_PTS*PV:.0f} | {' / '.join(yp)} |")

def rc(t, slip=0.): return (t['rpts'] + SLIP_PTS + slip) * PV + 2 * COMM
def sized(t, budget, cap=None, slip=0.):
    r = rc(t, slip)
    b = budget if cap is None else min(budget, cap)
    q = int(b // r)
    pts = t['pts'] - (slip if t['why'] == 'stop' else 0)
    return q, q * (pts * PV - 2 * COMM)

MODULES = {'A: SGP only': ['SGP'], 'B: SGP + WCC (recommended)': ['SGP', 'WCC'], 'C: SGP + G16 Mon-Thu': ['SGP', 'G16 Mon-Thu'],
           'D: SGP + G16-EDT Mon-Thu': ['SGP', 'G16-EDT Mon-Thu']}
def module_trades(m):
    v = []
    for r in MODULES[m]: v += RULES[r]
    return sorted(v, key=lambda t: t['d'])

out('\n## Module P&L with a fixed evening budget (contracts = floor(budget / risk per MNQ), skip if 0)\n')
out('| Module | budget | trades | skipped (risk > budget) | avg MNQ | 2022 $ | 2023 $ | 2024 $ | 2025 $ | 2026 YTD $ | maxDD $ | worst evening $ | longest losing streak |')
out('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for m in MODULES:
    for B in (200, 300, 400):
        tr = module_trades(m); y = collections.defaultdict(float); eq = pk = dd = 0; worst = 0; qs = []; sk = 0; ls = cur = 0
        for t in tr:
            q, net = sized(t, B)
            if q == 0: sk += 1; continue
            qs.append(q); y[t['d'] // 10000] += net; eq += net; pk = max(pk, eq); dd = max(dd, pk - eq); worst = min(worst, net)
            cur = cur + 1 if net < 0 else 0; ls = max(ls, cur)
        out(f"| {m} | {B} | {len(qs)} | {sk} | {S.mean(qs):.1f} | " + ' | '.join(f"{y[k]:+.0f}" for k in range(2022, 2027)) + f" | {dd:.0f} | {worst:.0f} | {ls} |")

# ---------------- Lucid Flex eval with the day engine ----------------
os.chdir('/home/claude/mnq-quant/scripts/lab'); sys.path.insert(0, '/home/claude/mnq-quant/scripts/lab')
import rules2
DAYTR = rules2.build('current', be=True, v4t=1.25)
byd = collections.defaultdict(list)
for t in DAYTR: byd[t['d']].append(t)
DDAYS = [d for d in rules2.D if d >= 20220301]
evd = {m: {t['d']: t for t in module_trades(m)} for m in MODULES}

def attempt(start, m=None, B=300, cap_frac=.5, end=20261020, ev_slip=2.0):
    bal = 50000.; peak = 50000.; best = 0.; td = 0; evn = 0; evpnl = 0.
    for d in DDAYS:
        if d < start: continue
        if d > end: break
        td += 1; mll = min(peak - 2000, 50000); dp = 0.
        if m and d in evd[m]:
            q, net = sized(evd[m][d], B, cap_frac * (bal - mll), ev_slip)
            if q: dp += net; evn += 1; evpnl += net
            if bal + dp <= mll: return 'F', td, evn, evpnl
        cush = bal + dp - mll
        dp += rules2.size_day([dict(t) for t in byd.get(d, [])], cush, 'updated', f=.65, slipx=8.0)
        bal += dp; best = max(best, dp)
        if bal <= mll: return 'F', td, evn, evpnl
        peak = max(peak, bal)
        if bal - 50000 >= 3000 and best <= .5 * (bal - 50000): return 'P', td, evn, evpnl
    return ('S' if bal - min(peak - 2000, 50000) < 300 else 'O'), td, evn, evpnl

out('\n## Lucid Flex 50K eval alongside the day engine (start on every trading day in the window, run to 2026-10-20)\n')
out('S = stalled: room above the max-loss line under $300 at data end, so no trade fits (a dead account in practice). O = still open with room.')
out('paired columns compare each start with the day-engine-only run from the same day.\n')
out('| Window | Module | budget | attempts | pass % | fail % | stalled % | open % | pass <= 20d | pass <= 40d | median days to pass | passes earlier | passes later | gained a pass | lost a pass | evening trades per attempt |')
out('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for lab, a, z, lastst in (('2025', 20250101, 20251231, 20251231), ('2026 YTD', 20260101, 20261020, 20260915)):
    starts = [d for d in DDAYS if a <= d <= lastst]
    base = [attempt(s) for s in starts]
    for m, B in [(None, 0)] + [(m, B) for m in MODULES for B in (200, 300, 400)]:
        R = [attempt(s, m, B) for s in starts] if m else base
        n = len(R); P = [r[1] for r in R if r[0] == 'P']
        bp = [(x, y) for x, y in zip(base, R)]
        e_ = sum(x[0] == 'P' and y[0] == 'P' and y[1] < x[1] for x, y in bp); l_ = sum(x[0] == 'P' and y[0] == 'P' and y[1] > x[1] for x, y in bp)
        g_ = sum(x[0] != 'P' and y[0] == 'P' for x, y in bp); lo_ = sum(x[0] == 'P' and y[0] != 'P' for x, y in bp)
        pc = lambda k: f"{100*sum(r[0]==k for r in R)/n:.0f}"
        out(f"| {lab} | {m or 'day engine only'} | {B or '-'} | {n} | {pc('P')} | {pc('F')} | {pc('S')} | {pc('O')} | "
            f"{100*sum(x <= 20 for x in P)/n:.0f}% | {100*sum(x <= 40 for x in P)/n:.0f}% | {S.median(P) if P else '-'} | {100*e_/n:.0f}% | {100*l_/n:.0f}% | {100*g_/n:.0f}% | {100*lo_/n:.0f}% | {S.mean(r[2] for r in R):.1f} |")

# 2026 calendar run from Jan 2 for the recommended module
out('\n## One eval started 2026-01-02 and restarted the day after each pass or fail (2026 YTD), day engine only vs module B at $300\n')
for m in (None, 'B: SGP + WCC (recommended)'):
    s = [d for d in DDAYS if d >= 20260102][0]; res = []
    while True:
        r = attempt(s, m, 300)
        res.append((s, r[0], r[1]))
        if r[0] == 'O': break
        i = DDAYS.index(s) + r[1]
        if i >= len(DDAYS) or DDAYS[i] > 20261020: break
        s = DDAYS[i]
    out(f"{m or 'day engine only'}: " + ', '.join(f"{x[0]} {x[1]} in {x[2]}d" for x in res))
