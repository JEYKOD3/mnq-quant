"""Task 3: simple mechanical ideas per red folder. 1 MNQ, net of 2x2.37 commission + 1 tick entry slip + 1 tick stop slip.
IS = 2022-2024, OOS = 2025-2026. Every rule is also run on CLEAN days at the same clock time as a control.
Run: python3 trades.py > ../../knowledge/src/red_folder_trades.txt"""
from common import *
from measure import EVS
CLOSE = m18(1555)
def sgn(x): return 1 if x > 0 else -1 if x < 0 else 0
def sim(b, i, s, S, tg, flat):
    e = b[i][1] + s * T
    r = walk(b, i, s, e, S, tg if tg else 1e9, None, flat)
    return r['pts'] * PV - 2 * COMM, r
def days_for(ev):
    out = []
    for d, hh in event_days(ev):
        if ev == 'CLAIMS' and any(e in MAJOR and t == '0830' for e, t in EXT[d].items()): continue
        out.append((d, hh))
    return out
def rule_fade15(d, hh, k=.10, rr=1.0, hold=120):
    """at T+15: if the 15m move is >= k ADR, fade it: target the pre-release price F, stop = rr x distance, flat at T+hold"""
    b, ix = eb(d); K = m18(hh); A = adr(d)
    if not A or any(x not in ix for x in (K - 5, K + 10, K + 15)): return None
    F = b[ix[K - 5]][4]; p = b[ix[K + 10]][4]; mv = p - F
    if abs(mv) < k * A: return None
    s = -sgn(mv); i = ix[K + 15]; dist = abs(b[i][1] - F)
    if dist < 8: return None
    return sim(b, i, s, max(8, rr * dist), dist, min(K + hold, CLOSE))[0]
def rule_follow(d, hh, w=30, k=.10, stopk=.25, hold=None, fade=False, tgtR=None):
    """at T+w: follow (or fade) the T..T+w move if >= k ADR; stop stopk ADR; exit at close (or after `hold` min)"""
    b, ix = eb(d); K = m18(hh); A = adr(d)
    if not A or any(x not in ix for x in (K - 5, K + w - 5, K + w)): return None
    F = b[ix[K - 5]][4]; mv = b[ix[K + w - 5]][4] - F
    if abs(mv) < k * A: return None
    s = sgn(mv) * (-1 if fade else 1); S = max(8, round(stopk * A * 4) / 4)
    return sim(b, ix[K + w], s, S, tgtR * S if tgtR else None, min(K + w + hold, CLOSE) if hold else CLOSE)[0]
def rule_predrift(d, hh, k=.08, hold=30, stopk=.2):
    """at T: follow the T-60..T drift for `hold` minutes"""
    b, ix = eb(d); K = m18(hh); A = adr(d)
    if not A or any(x not in ix for x in (K - 60, K - 5, K)): return None
    mv = b[ix[K - 5]][4] - b[ix[K - 60]][1]
    if abs(mv) < k * A: return None
    S = max(8, round(stopk * A * 4) / 4)
    return sim(b, ix[K], sgn(mv), S, None, min(K + hold, CLOSE))[0]
def rule_morning(d, hh, k=.2, stopk=.3):
    """at T (10:00/14:00 events): trade in the direction of the 9:30->T move, exit at close"""
    b, ix = eb(d); K = m18(hh); A = adr(d); o = m18(930)
    if not A or K <= o + 5 or any(x not in ix for x in (o, K - 5, K)): return None
    mv = b[ix[K - 5]][4] - b[ix[o]][1]
    if abs(mv) < k * A: return None
    S = max(8, round(stopk * A * 4) / 4)
    return sim(b, ix[K], sgn(mv), S, None, CLOSE)[0]
def rule_nextday(d, hh, fade=True, stopk=.5, k=.2):
    """next RTH day: at 9:30 open trade against (fade=True) or with the event move (close - F), stop stopk ADR, exit 15:55"""
    b, ix = eb(d); K = m18(hh); A = adr(d)
    if not A or (K - 5) not in ix or CLOSE not in ix: return None
    mv = b[ix[CLOSE]][4] - b[ix[K - 5]][4]
    if abs(mv) < k * A: return None
    nd = next_day(d)
    if not nd or nd not in RTH: return None
    nb = RTH[nd]; A2 = adr(nd) or A; s = sgn(mv) * (-1 if fade else 1); S = max(8, round(stopk * A2 * 4) / 4)
    return sim(nb, 0, s, S, None, 955)[0]
RULES = [
    ('fade15 k.10 tgt=F stop=1x', lambda d, h: rule_fade15(d, h, .10, 1.0)),
    ('fade15 k.05 tgt=F stop=1x', lambda d, h: rule_fade15(d, h, .05, 1.0)),
    ('fade15 k.10 tgt=F stop=0.5x', lambda d, h: rule_fade15(d, h, .10, .5)),
    ('follow30 k.10 stop.25 ->close', lambda d, h: rule_follow(d, h, 30, .10, .25)),
    ('follow30 k.10 stop.25 2R', lambda d, h: rule_follow(d, h, 30, .10, .25, tgtR=2)),
    ('fade30 k.10 stop.25 ->close', lambda d, h: rule_follow(d, h, 30, .10, .25, fade=True)),
    ('follow60 k.10 stop.25 ->close', lambda d, h: rule_follow(d, h, 60, .10, .25)),
    ('fade60 k.10 stop.25 ->close', lambda d, h: rule_follow(d, h, 60, .10, .25, fade=True)),
    ('follow5 k.05 stop.20 hold60', lambda d, h: rule_follow(d, h, 5, .05, .20, hold=60)),
    ('predrift k.08 hold30', lambda d, h: rule_predrift(d, h)),
    ('morning-trend at T ->close', lambda d, h: rule_morning(d, h)),
    ('next day fade event move', lambda d, h: rule_nextday(d, h, True)),
    ('next day follow event move', lambda d, h: rule_nextday(d, h, False)),
]
if __name__ == '__main__':
    print(__doc__)
    for ev in EVS + ['CLEAN0830', 'CLEAN1000', 'CLEAN1400', 'CLEAN1430']:
        DD = [(d, ev[5:]) for d in clean_days(ev[5:])] if ev.startswith('CLEAN') else days_for(ev)
        print(f'\n== {ev}  ({len(DD)} days)')
        for lab, f in RULES:
            tr = []
            for d, hh in DD:
                v = f(d, hh)
                if v is not None: tr.append(dict(d=d, net=v))
            if tr: print(f'  {lab:32s} {fmt(tstats(tr))}')
