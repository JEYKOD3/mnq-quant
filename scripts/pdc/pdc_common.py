"""PDC magnet test core (2026-10-26). Is the prior RTH close (PDC, 16:00) a magnet / fair price?
Bars: MNQ ETH 5m from scripts/sessions/common.py. Session key d runs 18:00 (slot 0) -> 16:55; 9:30 = slot 186, 16:00 = slot 264.
PDC = close of the 15:55 bar of the prior key. ADR = mean of the prior 10 RTH ranges (no lookahead).
Placebo levels (same tests, same session):
  MIR   mirror: same distance from the window start price, on the other side (2*S - PDC). Exact null for "nearby level".
  P15   prior day 15:00 price (open of the 15:00 bar): a real recent price, not a close.
  O2    RTH open of 2 sessions ago: an older real price.
  SHIFT PDC +0.25 ADR and PDC -0.25 ADR (two fake lines that move with PDC).
Costs: 2 x 2.37 commission + 1 tick slippage per side (0.5 pt round turn), $2/pt. Stop beats target in the same bar.
Periods: IS 2022-2024, OOS 2025-2026, 2026 YTD (data ends 2026-10-20)."""
import sys
sys.path.insert(0, '/home/claude/mnq-quant/scripts/sessions')
from common import ETH, KEYS, adr_of, full, sim, _t, PV, COMM, SLIP_PTS
T = 0.25
RTH_A, RTH_Z = 186, 264

def _build():
    out = {}
    for i, d in enumerate(KEYS):
        if d < 20220101 or i < 2: continue
        p, pp = KEYS[i - 1], KEYS[i - 2]
        if not (full(d, 0, RTH_Z) and full(p, RTH_A, RTH_Z) and full(pp, RTH_A, RTH_A + 1)): continue
        a = adr_of(d)
        if not a: continue
        Op, Hp, Lp, Cp = ETH[p]
        out[d] = dict(d=d, adr=a, pdc=Cp[RTH_Z - 1], p15=Op[252], o2=ETH[pp][0][RTH_A])
    return out
S = _build()
SK = sorted(S)

def levels(d, s0):
    """all levels for a window whose start price is s0. returns list of (name, level)."""
    e = S[d]; a = e['adr']; P = e['pdc']
    return [('PDC', P), ('MIR', 2 * s0 - P), ('P15', e['p15']), ('O2', e['o2']), ('SHIFT', P + .25 * a), ('SHIFT', P - .25 * a)]

NAMES = ['PDC', 'MIR', 'P15', 'O2', 'SHIFT']

def first_touch(d, lvl, a, z):
    O, H, L, C = ETH[d]
    for k in range(a, z):
        if L[k] <= lvl <= H[k]: return k
    return None

def period(d):
    return 'IS' if d < 20250101 else 'OOS'

PERIODS = [('2022-24', lambda d: d < 20250101), ('2025-26', lambda d: d >= 20250101), ('2026 YTD', lambda d: d >= 20260101)]

def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x < 0)
    return g / l if l else (9.99 if g else 0)

def tstats(tr):
    if not tr: return None
    n = [t['net'] for t in tr]
    return dict(n=len(n), win=sum(x > 0 for x in n) / len(n), pf=pf(n), avg=sum(n) / len(n), tot=sum(n))

def tcell(tr):
    s = tstats(tr)
    return '0 | - | - | -' if not s else f"{s['n']} | {s['win']:.0%} | {s['pf']:.2f} | {s['avg']:+.1f}"

def trow(name, tr):
    cells = [tcell([t for t in tr if f(t['d'])]) for _, f in PERIODS]
    return f"| {name} | " + ' | '.join(cells) + ' |'

THEAD = ("| Test | IS n | IS win | IS PF | IS $/tr | OOS n | OOS win | OOS PF | OOS $/tr | 2026 n | 2026 win | 2026 PF | 2026 $/tr |\n"
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|")

def limit_trade(d, side, level, k_from, k_last, stop_d, tgt_d, hold, kmax):
    """limit at level, fill on first bar in [k_from, k_last] trading 1 tick through (fill at better of open/level).
    stop checked on the fill bar (conservative), target from next bar; time exit after `hold` bars (capped at kmax)."""
    O, H, L, C = ETH[d]
    for k in range(k_from, k_last + 1):
        if (side > 0 and L[k] <= level - T) or (side < 0 and H[k] >= level + T):
            e = min(O[k], level) if side > 0 else max(O[k], level)
            st = e - side * stop_d; tg = e + side * tgt_d
            kx = min(k + 1 + hold, kmax)
            if (side > 0 and L[k] <= st) or (side < 0 and H[k] >= st): t = _t(d, side, e, st, k, 'stop')
            elif k + 1 >= kx: t = _t(d, side, e, C[k], kx, 'time')
            else: t = sim(d, side, k + 1, e, st, tg, kx)
            t['e'] = e; t['k0'] = k
            return t
    return None
