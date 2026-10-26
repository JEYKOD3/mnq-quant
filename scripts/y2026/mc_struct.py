"""Friend's mother candle with STRUCTURE stops (Oct 26 2026). Every signal taken (no stop-after-win), 1R target, full-body
breakout beyond the mother bar (MB). After an exit, scanning resumes at the next bar. Box rules as pass_tested.mc_scan.
Stop modes (long shown; short mirrored), all -1 tick beyond the level:
  mb    = MB low (baseline)
  ib    = low of the last inside bar before the trigger
  half  = MB 50% level
  sw2/sw3 = most recent confirmed pivot low (2/2 or 3/3 on the execution TF) below entry, clamped to [min, max] stop
            (stop widened to min if closer; trade skipped if farther than max). Caps: 1m 8-40 pts, 5m 15-80 pts.
  minsw = the closer (smaller risk) of MB side and sw3
TF: 1m boxes on RTH 1m; 5m boxes on 5m RTH bars, exits re-walked on 1m from the bar after the trigger.
Windows: 9:30-15:45 (flat 15:55) and 9:30-11:00. Bias: none / HTF 2-of-3 / 9:30 open.
Costs: walk pays 1 tick entry + 1 tick stop slip, 2.37/side. Stress: +8 pt on stop exits, but +2 pt for 1m trades with stop < 20 pt.
Usage: python3 mc_struct.py scan ; python3 mc_struct.py eval"""
import os, sys, json, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pass_tested as PT
from common import walk, mk, D, DB, SLIP, T, COMM, PV, STOPWHY
HERE = os.path.dirname(os.path.abspath(__file__))
BLK = PT.BLK
CAPS = {1: (8., 40.), 5: (15., 80.)}

def pivots(b, p):
    """lists of (confirm_index, price) for pivot lows and highs with p bars each side."""
    lo, hi = [], []
    for j in range(p, len(b) - p):
        if all(b[j][3] < b[j - q][3] for q in range(1, p + 1)) and all(b[j][3] <= b[j + q][3] for q in range(1, p + 1)): lo.append((j + p, b[j][3]))
        if all(b[j][2] > b[j - q][2] for q in range(1, p + 1)) and all(b[j][2] >= b[j + q][2] for q in range(1, p + 1)): hi.append((j + p, b[j][2]))
    return lo, hi

def swing_stop(piv, k, s, eP):
    lo, hi = piv
    src = lo if s > 0 else hi
    for ci, px in reversed(src):
        if ci > k: continue
        if (s > 0 and px < eP) or (s < 0 and px > eP): return px - s * T
    return None

def stop_for(mode, s, eP, H, L, ibH, ibL, piv, k, tf):
    mn, mx = CAPS[tf]
    if mode == 'mb': return (L - T) if s > 0 else (H + T)
    if mode == 'ib': return (ibL - T) if s > 0 else (ibH + T)
    if mode == 'half': return (H + L) / 2 - s * T
    if mode in ('sw2', 'sw3', 'minsw'):
        sw = swing_stop(piv, k, s, eP)
        if mode == 'minsw':
            mbs = (L - T) if s > 0 else (H + T)
            if sw is None: return mbs
            return sw if abs(eP - sw) < abs(eP - mbs) else mbs
        if sw is None: return None
        r = abs(eP - sw)
        if r > mx: return None
        if r < mn: sw = eP - s * mn
        return sw
    raise ValueError(mode)

def scan(b, e_win, bf, mode, tf, piv, walkb=None, d=None, tend=955, maxn=12):
    """returns list of (k, s, eP, stp) signals honoring 'one position at a time' via exits computed on walkb (1m)."""
    out = []; i = 0
    while i < len(b) - 2 and len(out) < maxn:
        mb = b[i]
        if not (b[i + 1][2] <= mb[2] and b[i + 1][3] >= mb[3]): i += 1; continue
        H, L = mb[2], mb[3]; k = i + 1; ibH, ibL = b[i + 1][2], b[i + 1][3]; k = i + 2; bside = None; nxt = i + 1
        while k < len(b):
            m, o, h, l, c = b[k]
            if m >= e_win: break
            if h <= H and l >= L: ibH, ibL = h, l       # another inside bar: last inside bar wins
            lo_b, hi_b = min(o, c), max(o, c)
            up = lo_b > H; dn = hi_b < L
            if bside is None and (c > H or c < L) and not (up or dn):
                bside = 1 if c > H else -1; k += 1; continue
            if bside is not None and ((bside > 0 and c < L) or (bside < 0 and c > H)): break
            if bside is not None and ((bside > 0 and dn) or (bside < 0 and up)): up = dn = False
            if up or dn:
                s = 1 if up else -1
                if bf is None or bf(m, c) == s:
                    eP = c + s * SLIP * T
                    stp = stop_for(mode, s, eP, H, L, ibH, ibL, piv, k, tf)
                    if stp is not None and (eP - stp) * s > 0:
                        r = abs(eP - stp); tgt = eP + s * r
                        if tf == 1:
                            xi, xP, why, rf = walk(b, k + 1, s, eP, stp, tgt, tend)
                            out.append(mk(d, f'MCS{tf}', s, m, eP, stp, xi, xP, why, rf, b)); nxt = xi + 1
                        else:
                            j = PT.idx_at(walkb, m + 5)
                            if j is None: break
                            xi, xP, why, rf = walk(walkb, j, s, eP, stp, tgt, tend)
                            out.append(mk(d, f'MCS{tf}', s, walkb[j][0], eP, stp, xi, xP, why, rf, walkb))
                            xt = walkb[xi][0]; nxt = next((q for q in range(len(b)) if b[q][0] >= xt), len(b))
                        break
                break
            k += 1
        i = max(i + 1, nxt)
    return out

def run(tf, e_win, biasf, mode):
    out = []
    for d in D:
        b1 = DB[d]
        if len(b1) < 60 or b1[0][0] != 570: continue
        b = b1 if tf == 1 else PT.agg5(b1)
        p = 2 if mode == 'sw2' else 3
        piv = pivots(b, p) if mode in ('sw2', 'sw3', 'minsw') else None
        o0 = b1[0][1]
        bf = (lambda m, c, d=d: PT.bias(d, m)) if biasf == 'htf' else (lambda m, c, o0=o0: 1 if c > o0 else -1) if biasf == 'open' else None
        out += scan(b, e_win, bf, mode, tf, piv, walkb=b1, d=d)
    return out

def net(t, stress=False):
    x = 0.0
    if stress and t['why'] in STOPWHY: x = 2.0 if (t['strat'] == 'MCS1' and t['r'] < 20) else 8.0
    return (t['pts'] - x) * PV - 2 * COMM
def stats(tr, a, z, stress=False):
    v = [net(t, stress) for t in tr if a <= t['d'] <= z]
    if not v: return dict(n=0, net=0, pf=0, wr=0, be_wr=0, risk=0)
    w = [x for x in v if x > 0]; ls = [-x for x in v if x <= 0]
    g, L = sum(w), sum(ls)
    be = (statistics.mean(ls) / (statistics.mean(ls) + statistics.mean(w))) if w and ls else 0
    return dict(n=len(v), net=round(sum(v)), pf=round(g / L, 2) if L else 99, wr=round(len(w) / len(v), 3), be_wr=round(be, 3),
                risk=round(statistics.mean(t['r'] for t in tr if a <= t['d'] <= z), 1))

VARS = []
for tf in (1, 5):
    for wn, ew in (('all', 945), ('am', 660)):
        for mode in ('mb', 'ib', 'half', 'sw2', 'sw3', 'minsw'):
            for bias in (None, 'htf', 'open'):
                VARS.append((f'{tf}m {wn} {mode} {bias or "nobias"}', tf, ew, bias, mode))

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if cmd == 'scan':
        res = {}; trades = {}
        for nm, tf, ew, bias, mode in VARS:
            tr = run(tf, ew, bias, mode); trades[nm] = tr; row = {}
            for k, (a, z) in BLK.items(): row[k] = stats(tr, a, z); row[k + '_s'] = stats(tr, a, z, True)
            row['years'] = {y: stats(tr, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}
            row['pass'] = all(row[k]['net'] > 0 for k in BLK) and row['IS']['n'] >= 60
            row['pass_s'] = all(row[k + '_s']['net'] > 0 for k in BLK) and row['IS']['n'] >= 60
            res[nm] = row
            print(f"{nm:24s} " + ' | '.join(f"{k} n{row[k]['n']} wr{row[k]['wr']} be{row[k]['be_wr']} pf{row[k]['pf']} s{row[k + '_s']['pf']} r{row[k]['risk']}" for k in BLK)
                  + (' PASS' if row['pass'] else '') + (' PASS_S' if row['pass_s'] else ''), flush=True)
        json.dump(res, open(os.path.join(HERE, 'mc_struct_scan.json'), 'w'), indent=1)
        json.dump(trades, open(os.path.join(HERE, 'mc_struct_trades.json'), 'w'))
