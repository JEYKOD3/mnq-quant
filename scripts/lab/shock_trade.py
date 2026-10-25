"""Unexpected news (no scheduled release): a shock bar = 1m range >= K x median of the last 30 bars and >= M x ADR, 10:00-15:00.
JJ Simon's drift trade: trade WITH the jump, no fixed target, wide stop, exit when a 1m candle closes against the structure.
Variants: entry at shock close / after the first consolidation breakout; also the opposite (fade back to the pre-shock price)."""
import sys, collections, statistics as st, csv
sys.path.insert(0, '.')
from rules2 import D, DB, F, PV, COMM, T
EVT = collections.defaultdict(set)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EVT[int(r['date'])].add((r['event'], int(r['time_et'])))
def pf(v):
    g = sum(x for x in v if x > 0); l = -sum(x for x in v if x <= 0); return g / l if l else 9.9
def run(K=4, M=.06, mode='drift', entry='close', exitm='struct', stopm='bar', t0=600, t1=900, maxhold=120):
    out = []
    for d in D:
        b = DB[d]; f = F.get(d)
        if not f: continue
        adr = f['adr']; rg = [x[2] - x[3] for x in b]
        sched = {tm // 100 * 60 + tm % 100 for e, tm in EVT.get(d, ())}
        i = 30
        while i < len(b) - 2:
            m, o, h, l, c = b[i]
            if not (t0 <= m <= t1) or any(abs(m - s) <= 5 for s in sched): i += 1; continue
            med = st.median(rg[i - 30:i])
            if not (rg[i] >= K * med and rg[i] >= M * adr and abs(c - o) >= .5 * rg[i]): i += 1; continue
            s = 1 if c > o else -1
            pre = o
            if mode == 'fade': s = -s
            j = i + 1
            if entry == 'consol':  # wait up to 10 bars for 3 bars inside the shock bar's range, then a close beyond them in the jump direction
                jd = None
                for k in range(i + 3, min(i + 15, len(b) - 1)):
                    box = b[k - 2:k + 1]; bh = max(x[2] for x in box); bl = min(x[3] for x in box)
                    if bh - bl <= .6 * rg[i]:
                        for q in range(k + 1, min(k + 10, len(b) - 1)):
                            if (s > 0 and b[q][4] > bh) or (s < 0 and b[q][4] < bl): jd = q + 1; break
                        break
                if jd is None: i += 1; continue
                j = jd
            e = b[j][1] + s * T
            if mode == 'fade':
                stp = (h if s < 0 else l) + s * -1 * T * 4 if False else (e - s * rg[i])
                tgt = pre
            else:
                stp = (l - T) if s > 0 else (h + T)
                if stopm == 'adr': stp = e - s * .25 * adr
                tgt = None
            r = abs(e - stp)
            if r < 5: i += 1; continue
            res = None
            for k in range(j, len(b)):
                mk, ok, hk, lk, ck = b[k]
                if (s > 0 and lk <= stp) or (s < 0 and hk >= stp): res = (stp - s * T - e) * s; break
                if tgt is not None and ((s > 0 and hk >= tgt) or (s < 0 and lk <= tgt)): res = (tgt - e) * s; break
                if exitm == 'struct' and k > j and ((s > 0 and ck < b[k - 1][3]) or (s < 0 and ck > b[k - 1][2])): res = (ck - e) * s; break
                if exitm == 'struct2' and k > j + 1 and ((s > 0 and ck < min(b[k - 1][3], b[k - 2][3])) or (s < 0 and ck > max(b[k - 1][2], b[k - 2][2]))): res = (ck - e) * s; break
                if mk >= 955 or mk - b[j][0] >= maxhold: res = (ck - e) * s; break
            if res is None: res = (b[-1][4] - e) * s
            out.append(dict(d=d, net=res * PV - 2 * COMM, R=res / r, m=m))
            i = k + 1
        # next day
    return out
def rep(lab, tr):
    o = []
    for a, z in ((0, 20241231), (20250101, 99999999)):
        v = [t['net'] for t in tr if a <= t['d'] <= z]
        o.append(f"n{len(v):4d} win {sum(x>0 for x in v)/max(1,len(v)):.0%} PF {pf(v):.2f} avgR {sum(t['R'] for t in tr if a<=t['d']<=z)/max(1,len(v)):+.2f}")
    print(f"  {lab:60s} 22-24 {o[0]:36s} | 25-26 {o[1]}")
for K, M in ((4, .06), (5, .08), (6, .1)):
    print(f'shock = range >= {K}x and >= {int(M*100)}% ADR')
    rep('drift: enter at shock close, stop shock bar, exit 1 bar structure', run(K, M))
    rep('drift: ... exit 2-bar structure', run(K, M, exitm='struct2'))
    rep('drift: ... stop 0.25 ADR, exit 2-bar structure', run(K, M, exitm='struct2', stopm='adr'))
    rep('drift: after first consolidation, exit 2-bar structure', run(K, M, entry='consol', exitm='struct2'))
    rep('drift: hold 60 min (no structure exit)', run(K, M, exitm='none', maxhold=60))
    rep('fade: back to pre-shock price, stop = shock range', run(K, M, mode='fade', exitm='none', maxhold=60))
