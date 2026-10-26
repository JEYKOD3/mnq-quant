"""Session pattern mining core (2026-10-25). MNQ ETH 5m bars, one session per key date (18:00 prior evening -> 16:55).
Slot index k = minutes-from-18:00 // 5 (0 = 18:00, 108 = 03:00, 186 = 09:30, 264 = 16:00, 275 = 16:55).
Costs per round turn, 1 MNQ: 2 x 2.37 commission + 1 tick slippage per side (0.5 pt = $1). $2 per point.
IS = 2022-2024, OOS = 2025-2026."""
import json, csv, datetime, collections, math
R = '/home/claude/mnq-quant'
PV = 2.0; COMM = 2.37; SLIP_PTS = 0.5          # total slippage per round turn in points
NS = 276

def slot(hhmm):
    m = (hhmm // 100 * 60 + hhmm % 100 - 1080) % 1440
    return m // 5

def _load():
    S = {}
    for ln in open(R + '/data/raw/mnq_eth_5m.txt'):
        p = ln.strip().split('|')
        if len(p) < 50: continue
        O = [None] * NS; H = [None] * NS; L = [None] * NS; C = [None] * NS
        for x in p[1:]:
            f = x.split(','); hm = int(f[0]); k = slot(hm)
            if k >= NS: continue
            O[k], H[k], L[k], C[k] = (int(v) / 4 for v in f[1:5])
        S[int(p[0])] = (O, H, L, C)
    return S

ETH = _load()
KEYS = sorted(ETH)
def _adr():
    # ADR = mean of the prior 10 RTH (9:30-16:00) ranges, known before the session starts (no lookahead)
    out = {}; rngs = []
    a, z = (930 - 1080) % 1440 // 5 + 0, None
    for d in KEYS:
        O, H, L, C = ETH[d]
        if len(rngs) >= 10: out[d] = sum(rngs[-10:]) / 10
        hs = [x for x in H[186:264] if x is not None]; ls = [x for x in L[186:264] if x is not None]
        if len(hs) >= 60: rngs.append(max(hs) - min(ls))
    return out
ADR = _adr()
MACRO = collections.defaultdict(set)
for r in csv.DictReader(open(R + '/data/macro_dates.csv')): MACRO[int(r['date'])].add((r['event'], r['time_et']))

def wd(d): return datetime.date(d // 10000, d // 100 % 100, d % 100).weekday()
def full(d, a=0, z=NS):
    O = ETH[d][0]
    return all(O[k] is not None for k in range(a, z))

def adr_of(d):
    if d in ADR: return ADR[d]
    prev = [k for k in ADR if k < d]
    return ADR[max(prev)] if prev else None

def prev_key(d):
    i = KEYS.index(d)
    return KEYS[i - 1] if i else None

def rth_hlc(d):
    """prior-day reference levels: RTH 9:30-16:00 high, low, close (16:00 = close of 15:55 bar)"""
    O, H, L, C = ETH[d]; a, z = slot(930), slot(1600)
    if not full(d, a, z): return None
    return max(H[a:z]), min(L[a:z]), C[z - 1]

def hi_lo(d, a, z):
    O, H, L, C = ETH[d]
    return max(H[a:z]), min(L[a:z])

def sim(d, side, k0, entry, stop, tgt, kx):
    """enter at `entry` during bar k0 (market at bar open, or limit/stop fill inside bar k0). Walk bars k0..kx-1;
    stop beats target inside the same bar (conservative). Time exit at open of bar kx (close of kx-1).
    stop/tgt are absolute prices or None. returns dict with gross pts, net $, exit slot, reason."""
    O, H, L, C = ETH[d]
    for k in range(k0, kx):
        if H[k] is None: continue
        if stop is not None and ((side > 0 and L[k] <= stop) or (side < 0 and H[k] >= stop)):
            px = stop
            if k > k0 and ((side > 0 and O[k] < stop) or (side < 0 and O[k] > stop)): px = O[k]   # gap through stop
            return _t(d, side, entry, px, k, 'stop')
        if tgt is not None and ((side > 0 and H[k] >= tgt) or (side < 0 and L[k] <= tgt)):
            return _t(d, side, entry, tgt, k, 'tgt')
    k = kx - 1
    while C[k] is None: k -= 1
    return _t(d, side, entry, C[k], kx, 'time')

def _t(d, side, e, x, k, why):
    pts = (x - e) * side - SLIP_PTS
    return dict(d=d, side=side, pts=pts, net=pts * PV - 2 * COMM, xk=k, why=why)

def stats(tr):
    if not tr: return dict(n=0)
    nets = [t['net'] for t in tr]
    gw = sum(x for x in nets if x > 0); gl = -sum(x for x in nets if x < 0)
    eq = 0; pk = 0; dd = 0
    for t in sorted(tr, key=lambda t: t['d']):
        eq += t['net']; pk = max(pk, eq); dd = max(dd, pk - eq)
    yrs = (max(t['d'] for t in tr) // 10000 - min(t['d'] for t in tr) // 10000) + 1
    return dict(n=len(tr), win=sum(x > 0 for x in nets) / len(nets), avgpts=sum(t['pts'] for t in tr) / len(tr),
                avg=sum(nets) / len(nets), pf=gw / gl if gl else float('inf'), tot=sum(nets), dd=dd)

def split(tr):
    return [t for t in tr if 20220101 <= t['d'] < 20250101], [t for t in tr if t['d'] >= 20250101]

def years_pos(tr):
    y = collections.defaultdict(float)
    for t in tr: y[t['d'] // 10000] += t['net']
    return ''.join('+' if y[k] > 0 else '-' for k in sorted(y))

OOS_YEARS = 1 + 9.8 / 12     # 2025-01-01 .. 2026-10-20
def row(name, tr):
    a, b = split(tr); A = stats(a); B = stats(b)
    def f(s):
        if not s['n']: return 'n 0'
        return f"n {s['n']:4d} win {s['win']:.0%} avg {s['avgpts']:+6.1f}pt PF {s['pf']:.2f} tot ${s['tot']:+8.0f} dd ${s['dd']:.0f}"
    return f"{name:44s} IS {f(A)} | OOS {f(B)} | yrs {years_pos(tr)}"

def md_row(name, tr):
    a, b = split(tr); A = stats(a); B = stats(b)
    def f(s):
        if not s['n']: return '0 | - | - | - | -'
        return f"{s['n']} | {s['win']:.0%} | {s['avgpts']:+.1f} | {s['pf']:.2f} | {s['dd']:.0f}"
    return f"| {name} | {f(A)} | {f(B)} | {years_pos(tr)} |"

MD_HEAD = "| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |\n|---|---|---|---|---|---|---|---|---|---|---|---|"

def sessions(a_hhmm=1800, z_hhmm=1655, need_adr=True, start=20220101):
    """yield keys with full bars over [a, z) slots and an ADR"""
    a, z = slot(a_hhmm), slot(z_hhmm) + 1
    for d in KEYS:
        if d < start: continue
        if not full(d, a, z): continue
        if need_adr and not adr_of(d): continue
        yield d
