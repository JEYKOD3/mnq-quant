"""Fair price reversion in the overnight sessions on 5m ETH bars (he trades quiet sessions on 5m).
Minutes are counted from 18:00 ET (0 = 18:00, 120 = 20:00, 540 = 03:00)."""
from fp import ETH, signals, walk, stats, T, PV, COMM
SESS = {'6pm': (0, 90), 'asia': (120, 210), 'london': (540, 630)}
def bars(d):
    e = ETH[d]; out = []
    for hm, (o, h, l, c) in e.items():
        m = (hm // 100 * 60 + hm % 100 - 1080) % 1440
        out.append((m, o, h, l, c))
    return sorted(out)
def run(sess='london', fair='own', sig='either', stop=25, tgt=38, tgt_mode='fixed', room=.8, maxtr=4, maxloss=3, hold=60, be=False):
    out = []
    a, z = SESS[sess]
    for d in sorted(ETH):
        if d < 20220101: continue
        b = bars(d)
        if len(b) < 250 or b[0][0] != 0: continue
        idx = {x[0]: i for i, x in enumerate(b)}
        if a not in idx: continue
        F = b[idx[a]][1] if fair == 'own' else b[0][1]   # 'own' = this session's open, else 6 PM open
        n = 0; losses = 0; busy = -1
        for i in range(idx[a] + 2, len(b) - 1):
            m = b[i][0]
            if m >= z or n >= maxtr or losses >= maxloss: break
            if m < busy: continue
            s, ext = signals(b, F, i, sig)
            if not s: continue
            e = b[i + 1][1] + s * T; dist = (F - e) * s
            tg = tgt if tgt_mode == 'fixed' else dist
            if tgt_mode == 'fixed' and dist < room * tgt: continue
            if tg <= 2: continue
            r = walk(b, i + 1, s, e, stop, tg, F if be else None, z + hold)
            r.update(d=d, side=s, kind='rev', R=r['pts'] / stop, net=r['pts'] * PV - 2 * COMM, dist=dist)
            out.append(r); n += 1; losses = losses + 1 if r['net'] < 0 else 0; busy = r['xm']
    return out
if __name__ == '__main__':
    import itertools
    for sess, fair, sig, (S, Tg, md) in itertools.product(['6pm', 'asia', 'london'], ['own', '6pm'], ['either', 'bos', 'disp'],
                                                          [(10, 15, 'fixed'), (15, 23, 'fixed'), (25, 38, 'fixed'), (25, 25, 'fixed'), (15, 0, 'fair'), (25, 0, 'fair')]):
        if sess == '6pm' and fair == '6pm': continue
        s = stats(run(sess, fair, sig, S, Tg or 38, md))
        if s['n']: print(f"{sess:6s} fair={fair:4s} {sig:6s} {S}/{Tg or 'fair'}  n {s['n']:5d} win {s['win']:.0%} PF {s['pf']:.2f} (22-24 {s['pfA']:.2f} | 25-26 {s['pfZ']:.2f}) yrs>1: {s['yrs_pos']}", flush=True)
