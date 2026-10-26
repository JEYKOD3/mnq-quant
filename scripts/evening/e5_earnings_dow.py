"""Q5. Post-earnings evenings (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AVGO, NFLX report after the 16:00 close) vs normal evenings.
Q6. Day-of-week effects in 18:00-20:00 (evening label: Sun = Monday session key ... Thu = Friday key)."""
import statistics as S
from ev_common import *
out = Out('/home/claude/mnq-quant/scripts/evening/out_e5.txt')
ALL = (0, 1, 2, 3, 4); WEEK = (1, 2, 3, 4)

def cont16(thr=.05, stop=.2, fade=False, dows=WEEK, earn=None, dst=None, k0=1):
    tr = []
    for d in keys(dows, earn=earn):
        e = EV[d]; a = e['adr']
        if dst is not None and e['dst'] != dst: continue
        x = e['o18'] - e['c16']
        if abs(x) < thr * a or x == 0: continue
        s = (1 if x > 0 else -1) * (-1 if fade else 1)
        t = mkt(d, s, k0, stop * a, None, 24)
        if t: tr.append(t)
    return tr

def post(thr=.05, stop=.2, fade=False, earn=None):
    tr = []
    for d in keys(WEEK, earn=earn):
        e = EV[d]; a = e['adr']; x = e['c17'] - e['c16']
        if abs(x) < thr * a or x == 0: continue
        s = (1 if x > 0 else -1) * (-1 if fade else 1)
        t = mkt(d, s, 1, stop * a, None, 24)
        if t: tr.append(t)
    return tr

def drift(side, dows=ALL, earn=None, dst=None, k0=0, kx=24):
    tr = []
    for d in keys(dows, earn=earn):
        if dst is not None and EV[d]['dst'] != dst: continue
        t = mkt(d, side, k0, None, None, kx)
        if t: tr.append(t)
    return tr

def s2t(dows=ALL, earn=None):
    tr = []
    for d in keys(dows, earn=earn):
        e = EV[d]; a = e['adr']
        if e['c16'] - e['o15'] <= -.15 * a and e['c16'] < e['rth_o']:
            t = mkt(d, 1, 1, .3 * a, None, 24)
            if t: tr.append(t)
    return tr

out('## Q5 descriptive: earnings evenings vs normal Mon-Thu evenings\n')
out('| Set | n | median 16:00-17:00 abs move %ADR | median abs gap 18:00 vs 16:00 %ADR | median 18:00-20:00 range %ADR | median abs 18:00->20:00 move %ADR |')
out('|---|---|---|---|---|---|')
for lab, ev in (('earnings evenings', True), ('normal evenings', False)):
    r = []
    for d in keys(WEEK, earn=ev):
        e = EV[d]; O, H, L, C = ETH[d]; a = e['adr']
        r.append((abs(e['c17'] - e['c16']) / a, abs(e['o18'] - e['c16']) / a, (max(H[:24]) - min(L[:24])) / a, abs(C[23] - O[0]) / a))
    out(f"| {lab} | {len(r)} | " + ' | '.join(f"{S.median(x[i] for x in r)*100:.1f}" for i in range(4)) + ' |')
cnt = collections.Counter()
for d in keys(WEEK, earn=True): cnt[len(EV[d]['earn'])] += 1
out(f"\nearnings evenings by number of mega-caps reporting that night: {dict(sorted(cnt.items()))}\n")
out(HEAD)
for lab, ev in (('EARN', True), ('NORMAL', False)):
    out(md(f'{lab} CONT 16:00->18:00 change >= 0.05, stop 0.2, 18:05-20:00', cont16(earn=ev)))
    out(md(f'{lab} CONT 16:00->18:00 change >= 0.05, EDT only', cont16(earn=ev, dst=True)))
    out(md(f'{lab} FADE 16:00->18:00 change >= 0.05, stop 0.2', cont16(fade=True, earn=ev)))
    for thr in (.05, .1, .2):
        out(md(f'{lab} CONT post-close 16-17 move >= {thr}', post(thr, earn=ev)))
        out(md(f'{lab} FADE post-close 16-17 move >= {thr}', post(thr, fade=True, earn=ev)))
    out(md(f'{lab} long 18:00->20:00 no stop', drift(1, WEEK, earn=ev)))
    out(md(f'{lab} S2 trunc (sell-off long 18:05-20:00)', s2t(WEEK, earn=ev)))

out('\n## Q6 day-of-week, 18:00-20:00\n')
out('| Evening | n | mean 18:00->20:00 %ADR | up% | t | median range %ADR | IS mean %ADR | OOS mean %ADR | 2026 mean %ADR |')
out('|---|---|---|---|---|---|---|---|---|')
for dw in range(5):
    m = []; rg = []; per = collections.defaultdict(list)
    for d in keys((dw,)):
        e = EV[d]; O, H, L, C = ETH[d]; a = e['adr']
        x = (C[23] - O[0]) / a; m.append(x); rg.append((max(H[:24]) - min(L[:24])) / a)
        per['IS' if d < 20250101 else 'OOS'].append(x)
        if d >= 20260101: per['26'].append(x)
    sd = S.pstdev(m); t = S.mean(m) / (sd / len(m) ** .5)
    out(f"| {DOWN[dw]} | {len(m)} | {S.mean(m)*100:+.1f} | {sum(x > 0 for x in m)/len(m):.0%} | {t:+.1f} | {S.median(rg)*100:.1f} | {S.mean(per['IS'])*100:+.1f} | {S.mean(per['OOS'])*100:+.1f} | {S.mean(per['26'])*100:+.1f} |")
out('\n' + HEAD)
for dw in range(5):
    out(md(f'{DOWN[dw]} long 18:00->20:00 no stop', drift(1, (dw,))))
    out(md(f'{DOWN[dw]} short 18:00->20:00 no stop', drift(-1, (dw,))))
    if dw:
        out(md(f'{DOWN[dw]} CONT 16:00 change >= 0.05 stop 0.2', cont16(dows=(dw,))))
        out(md(f'{DOWN[dw]} CONT 16:00 change >= 0.05 stop 0.2 EDT', cont16(dows=(dw,), dst=True)))
