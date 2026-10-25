from base import *
# Q3: at the first touch of a level during RTH, does price break through by X or bounce back by X first? (chance = 50%)
def levels(d, b, prev):
    f = FEAT[d]; L = {}
    L['prior day high'] = f['pdh']; L['prior day low'] = f['pdl']; L['prior day close'] = f['pdc']
    on = overnight(d)
    if on: L['overnight high'], L['overnight low'] = on
    L['opening range 30m high'] = max(x[2] for x in b[:30]); L['opening range 30m low'] = min(x[3] for x in b[:30])
    L['9:30 open'] = b[0][1]
    L['round 100'] = None
    return L
res = collections.defaultdict(lambda: {'A': [0, 0], 'Z': [0, 0]})
for d, b in DAYS:
    if d not in FEAT or len(b) < 380: continue
    adr = FEAT[d]['adr']
    for X in (.08, .15):
        x = X * adr
        L = levels(d, b, None)
        # VWAP touch handled separately below
        for nm, lv in L.items():
            if lv is None: continue
            start = 30 if 'opening range' in nm else 1
            # side the price comes from: price before the touch
            p0 = b[start - 1][4]
            if abs(p0 - lv) < 2: continue
            fromb = p0 < lv  # approaching from below
            t = None
            for i in range(start, len(b)):
                m, o, h, l, c = b[i]
                if t is None:
                    if (fromb and h >= lv) or (not fromb and l <= lv): t = i
                    else: continue
                brk = (h >= lv + x) if fromb else (l <= lv - x)
                bnc = (l <= lv - x) if fromb else (h >= lv + x)
                if brk and bnc: break
                if brk or bnc:
                    tm = 'open-11' if b[t][0] < 660 else '11-14' if b[t][0] < 840 else '14-16'
                    for key in ((nm, X, 'all'), (nm, X, tm)):
                        r = res[key][per(d)]; r[0] += bnc; r[1] += 1
                    break
    # VWAP: first touch after 10:00 from either side
    pv = v = 0; vw = []
    for m, o, h, l, c in b:
        tp = (h + l + c) / 3; pv += tp; v += 1; vw.append(pv / v)  # no volume in file: time-weighted average price
print('Q3. First touch of each level: % of times price bounced back X before breaking through X (50% = coin flip)')
for nm in ['prior day high', 'prior day low', 'prior day close', 'overnight high', 'overnight low', 'opening range 30m high', 'opening range 30m low', '9:30 open']:
    for X in (.08, .15):
        r = res[(nm, X, 'all')]
        if not r['A'][1]: continue
        sub = '  '.join(f"{tm}: {res[(nm,X,tm)]['A'][0]/max(1,res[(nm,X,tm)]['A'][1]):.0%}/{res[(nm,X,tm)]['Z'][0]/max(1,res[(nm,X,tm)]['Z'][1]):.0%}" for tm in ('open-11', '11-14', '14-16'))
        print(f"  {nm:24s} X={int(X*100):2d}% ADR  bounce 22-24 {r['A'][0]/r['A'][1]:.0%} (n{r['A'][1]}) | 25-26 {r['Z'][0]/r['Z'][1]:.0%} (n{r['Z'][1]})   by time A/Z: {sub}")
