import json, sys
sys.path.insert(0, '/home/claude/mnq-quant/scripts/fair')
from eth_fp import bars
rows = json.load(open('sun_rows.json'))
T = .25; PV = 2; COMM = 2.37
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return round(g / l, 2) if l else 9.9
def run(minA=.1, entry_m=5, stop='fri', stopA=.15, exit_m=120, tgtR=None, mode='go', confirm=False):
    out = []
    for r in rows:
        if abs(r['gapA']) < minA: continue
        b = bars(r['d']); idx = {x[0]: j for j, x in enumerate(b)}
        s = 1 if r['gap'] > 0 else -1
        if mode == 'fade': s = -s
        if entry_m not in idx: continue
        j = idx[entry_m]
        if confirm:  # first bars must have moved in the trade direction
            if (b[j - 1][4] - r['o']) * s <= 0: continue
        e = b[j][1] + s * T
        stp = (r['fri'] - s * T) if stop == 'fri' and mode == 'go' else e - s * stopA * r['adr']
        if (e - stp) * s <= 4: stp = e - s * stopA * r['adr']
        R = (e - stp) * s
        tgt = e + s * tgtR * R if tgtR else (r['fri'] if mode == 'fade' else None)
        res = None
        for k in range(j, len(b)):
            m, o, h, l, c = b[k]
            if (s > 0 and l <= stp) or (s < 0 and h >= stp): res = (stp - s * T - e) * s; break
            if tgt is not None and ((s > 0 and h >= tgt) or (s < 0 and l <= tgt)): res = (tgt - e) * s; break
            if m >= exit_m: res = (c - e) * s; break
        if res is None: continue
        out.append((r['d'], res * PV - 2 * COMM, res / R))
    return out
def rep(lab, tr):
    a = [t[1] for t in tr if t[0] <= 20241231]; z = [t[1] for t in tr if t[0] > 20241231]
    yrs = ' '.join(f"{y%100}:{pf([t[1] for t in tr if t[0]//10000==y]):.2f}" for y in range(2022, 2027))
    print(f"  {lab:58s} n{len(tr):3d} win {sum(t[1]>0 for t in tr)/max(1,len(tr)):.0%} PF {pf([t[1] for t in tr]):.2f} (22-24 {pf(a):.2f} | 25-26 {pf(z):.2f}) avgR {sum(t[2] for t in tr)/max(1,len(tr)):+.2f} | {yrs}")
print('Gap-and-go: trade in the gap direction (1 MNQ, costs in)')
for minA in (.05, .1, .2):
    for stop, sA in (('fri', .15), ('adr', .1), ('adr', .2)):
        for ex in (60, 120, 240, 930):
            rep(f"gap>={minA} ADR, stop {'Friday close' if stop=='fri' else str(sA)+' ADR'}, exit {ex//60+18 if ex<360 else 'Mon 9:30'}:{ex%60:02d}" if ex < 360 else f"gap>={minA} ADR, stop {'Friday close' if stop=='fri' else str(sA)+' ADR'}, exit Mon 9:30", run(minA, 5, stop, sA, ex))
print('\nWith confirmation (first 5 min already moving with the gap), entry 18:10')
for minA in (.05, .1):
    for ex in (120, 240):
        rep(f"gap>={minA}, confirm, stop Friday close, exit {ex//60+18}:00", run(minA, 10, 'fri', .15, ex, confirm=True))
print('\nGap fade toward Friday close (the classic idea), stop 0.15 ADR')
for minA in (.05, .1, .2):
    rep(f"fade gap>={minA} ADR, target Friday close, exit 20:00", run(minA, 5, 'adr', .15, 120, mode='fade'))
