"""Evening module core (2026-10-25). Window = 18:00-20:00 ET (slots 0..23 of a session key; slot 24 = 20:00).
Session key d = date the session ends, so the evening of calendar date X (Sun-Thu) is key d = next trading day.
Prior RTH = previous key p (Friday for a Sunday evening). Costs from sessions/common.py:
2 x $2.37 commission + 0.5 pt round-turn slippage (1 tick per side), $2/pt.
Periods: IS 2022-2024, OOS 2025-2026, plus a separate 2026 YTD column (data ends 2026-10-20)."""
import sys, csv, datetime, collections
sys.path.insert(0, '/home/claude/mnq-quant/scripts/sessions')
from common import ETH, KEYS, ADR, adr_of, full, wd, slot, sim, _t, PV, COMM, SLIP_PTS, R
from zoneinfo import ZoneInfo
T = 0.25
NY = ZoneInfo('America/New_York')
EARN = collections.defaultdict(set)
for r in csv.DictReader(open(R + '/data/earnings_megacap.csv')): EARN[int(r['date'])].add(r['symbol'])
DOWN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu']        # evening label from key weekday (Mon key = Sunday evening)

def _date(d): return datetime.date(d // 10000, d // 100 % 100, d % 100)

def _build():
    out = {}
    for i, d in enumerate(KEYS):
        if d < 20220101 or i == 0: continue
        if not full(d, 0, 24): continue
        a = adr_of(d)
        if not a: continue
        p = KEYS[i - 1]
        if not full(p, 186, 264): continue          # need a full prior RTH (skips half days)
        Op, Hp, Lp, Cp = ETH[p]
        k = 275
        while Cp[k] is None: k -= 1
        c17 = Cp[k]
        ed = _date(d) - datetime.timedelta(1)      # calendar date of the evening
        exp_prev = _date(d) - datetime.timedelta(3 if wd(d) == 0 else 1)
        dst = datetime.datetime(ed.year, ed.month, ed.day, 19, tzinfo=NY).utcoffset().total_seconds() == -4 * 3600
        O = ETH[d][0]
        out[d] = dict(d=d, p=p, dow=wd(d), lab=DOWN[wd(d)], adr=a, o18=O[0],
                      rth_o=Op[186], c16=Cp[263], o15=Op[252], c17=c17, rthH=max(Hp[186:264]), rthL=min(Lp[186:264]),
                      holiday=_date(p) != exp_prev, dst=dst, earn=EARN.get(int(ed.strftime('%Y%m%d')), set()) if wd(d) else set())
    return out
EV = _build()
EVK = sorted(EV)

def mkt(d, side, k0, stop_d=None, tgt_d=None, kx=24, stop_px=None, tgt_px=None):
    """market entry at bar k0 open; stop/target as distances in points (or absolute prices)."""
    O = ETH[d][0]
    if O[k0] is None: return None
    e = O[k0]
    st = stop_px if stop_px is not None else (e - side * stop_d if stop_d else None)
    tg = tgt_px if tgt_px is not None else (e + side * tgt_d if tgt_d else None)
    if tg is not None and (tg - e) * side <= 0: return None
    if st is not None and (e - st) * side <= 0: return None
    t = sim(d, side, k0, e, st, tg, kx); t['e'] = e; t['k0'] = k0
    return t

def lim(d, side, level, k_from, k_last, stop_d, tgt_d=None, kx=24, tgt_px=None):
    """limit buy (side>0) at level: fills on the first bar in [k_from, k_last] that trades 1 tick through it
    (fill at the better of open and level). Stop checked on the fill bar (conservative), target from the next bar."""
    O, H, L, C = ETH[d]
    for k in range(k_from, k_last + 1):
        if H[k] is None: continue
        if (side > 0 and L[k] <= level - T) or (side < 0 and H[k] >= level + T):
            e = min(O[k], level) if side > 0 else max(O[k], level)
            st = e - side * stop_d
            tg = tgt_px if tgt_px is not None else (e + side * tgt_d if tgt_d else None)
            if (side > 0 and L[k] <= st) or (side < 0 and H[k] >= st):
                t = _t(d, side, e, st, k, 'stop')
            elif k + 1 >= kx:
                t = _t(d, side, e, C[k], kx, 'time')
            else:
                t = sim(d, side, k + 1, e, st, tg, kx)
            t['e'] = e; t['k0'] = k
            return t
    return None

def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x < 0)
    return g / l if l else (9.99 if g else 0)

def st(tr):
    if not tr: return None
    n = [t['net'] for t in tr]
    eq = pk = dd = 0
    for x in n: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    return dict(n=len(n), win=sum(x > 0 for x in n) / len(n), pf=pf(n), avg=sum(n) / len(n), tot=sum(n), dd=dd)

def parts(tr):
    tr = sorted(tr, key=lambda t: t['d'])
    return ([t for t in tr if t['d'] < 20250101], [t for t in tr if t['d'] >= 20250101], [t for t in tr if t['d'] >= 20260101])

def yrs(tr):
    y = collections.defaultdict(float)
    for t in tr: y[t['d'] // 10000] += t['net']
    return ''.join('+' if y.get(k, 0) > 0 else '-' for k in range(2022, 2027))

def cell(s):
    return '0 | - | - | -' if not s else f"{s['n']} | {s['win']:.0%} | {s['pf']:.2f} | {s['avg']:+.1f}"

HEAD = "| Test | IS n | IS win | IS PF | IS $/tr | OOS n | OOS win | OOS PF | OOS $/tr | 2026 n | 2026 win | 2026 PF | 2026 $/tr | all maxDD$ | years |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"

def md(name, tr):
    a, b, c = parts(tr); s = st(tr)
    return f"| {name} | {cell(st(a))} | {cell(st(b))} | {cell(st(c))} | {s['dd']:.0f} | {yrs(tr)} |" if s else f"| {name} | no trades |"

def passes(tr, n_min=40, pf_min=1.15):
    a, b, c = parts(tr); A, B = st(a), st(b)
    return bool(A and B and A['n'] >= n_min and B['n'] >= n_min and A['pf'] >= pf_min and B['pf'] >= pf_min)

def keys(dows=(0, 1, 2, 3, 4), earn=None, holiday=False):
    for d in EVK:
        e = EV[d]
        if e['dow'] not in dows: continue
        if not holiday and e['holiday']: continue
        if earn is True and not e['earn']: continue
        if earn is False and e['earn']: continue
        yield d

SHIFTS = (24, 48, 72, 96, 120, 144)   # baseline windows start 20:00, 22:00, 00:00, 02:00, 04:00, 06:00
def full_at(d, a, z): return full(d, a, z)

class Out:
    def __init__(self, path): self.f = open(path, 'w')
    def __call__(self, *a):
        s = ' '.join(str(x) for x in a); print(s); self.f.write(s + '\n')
