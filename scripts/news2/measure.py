"""Task 2: behaviour around each red folder vs clean days at the same clock time (ETH 5m, ADR units).
Run: python3 measure.py > ../../knowledge/src/red_folder_measure.txt"""
from common import *
EVS = ['CPI', 'PPI', 'NFP', 'GDP', 'PCE', 'RETAIL', 'CLAIMS', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'TESTIMONY', 'JACKSON', 'FOMC', 'FOMC_PC', 'FOMC_MIN']
CLOSE = m18(1555)
def sgn(x): return 1 if x > 0 else -1 if x < 0 else 0
def metr(d, hhmm):
    b, ix = eb(d); k = m18(hhmm); A = adr(d)
    if not A or k not in ix or (k - 5) not in ix or (k - 60) not in ix or CLOSE not in ix: return None
    F = b[ix[k - 5]][4]
    def px(x):
        kk = min(k + x - 5, CLOSE); return b[ix[kk]][4] if kk in ix else None
    r = {x: px(x) for x in (5, 15, 30, 60, 120)}
    if None in r.values(): return None
    r = {x: (v - F) / A for x, v in r.items()}; r['close'] = (b[ix[CLOSE]][4] - F) / A
    w15 = b[ix[k]:ix[k] + 3]
    ex = max(max(x[2] for x in w15) - F, F - min(x[3] for x in w15)) / A
    touch = {}
    for lab, end in ((60, k + 60), (120, k + 120), ('close', CLOSE + 5)):
        touch[lab] = any(x[3] <= F <= x[2] for x in b[ix[k] + 3:] if x[0] < end)
    rth_open = b[ix[m18(930)]][1] if m18(930) in ix else None
    on = ((b[ix[m18(930)]][1] if k > m18(930) else F) - b[0][1]) / A
    morning = (F - rth_open) / A if (rth_open is not None and k > m18(930)) else None
    nd = next_day(d); nxt = None
    if nd and nd in RTH: nb = RTH[nd]; nxt = (nb[-1][4] - nb[0][1]) / (adr(nd) or A)
    # second move (FOMC style): 0-30 min vs 30 min -> close, and 30-60 vs 60 -> close
    s1 = r[30]; s2 = r['close'] - r[30]; s3 = r[60] - r[30]; s4 = r['close'] - r[60]
    return dict(d=d, F=F, A=A, pre=(F - b[ix[k - 60]][1]) / A, r=r, ex=ex, touch=touch, on=on, morning=morning, nxt=nxt, s1=s1, s2=s2, s3=s3, s4=s4)
def pct(v): v = list(v); return f"{sum(v) / len(v):4.0%}" if v else '  - '
def med(v): v = list(v); return st.median(v) if v else 0
def summary(rows):
    o = {}
    o['n'] = len(rows)
    for x in (5, 15, 30): o[f'm{x}'] = med(abs(t['r'][x]) for t in rows)
    o['ex15'] = med(t['ex'] for t in rows); o['pre'] = med(abs(t['pre']) for t in rows)
    o['pre_agree30'] = pct(sgn(t['pre']) == sgn(t['r'][30]) for t in rows if t['pre'] and t['r'][30])
    for x in (30, 60, 120, 'close'):
        o[f'same{x}'] = pct(t['r'][x] * sgn(t['r'][15]) > 0 for t in rows if t['r'][15])
        o[f'ext{x}'] = pct(t['r'][x] * sgn(t['r'][15]) > abs(t['r'][15]) for t in rows if t['r'][15])
    for x in (60, 120, 'close'): o[f'touch{x}'] = pct(t['touch'][x] for t in rows)
    o['al_on'] = pct(sgn(t['on']) == sgn(t['r']['close']) for t in rows if t['on'] and t['r']['close'])
    o['al_morn'] = pct(sgn(t['morning']) == sgn(t['r']['close']) for t in rows if t['morning'])
    o['nxt_rev'] = pct(sgn(t['nxt']) != sgn(t['r']['close']) for t in rows if t['nxt'] is not None and t['nxt'] and t['r']['close'])
    o['nxt_abs'] = med(abs(t['nxt']) for t in rows if t['nxt'] is not None)
    o['second'] = pct(sgn(t['s2']) == sgn(t['s1']) for t in rows if t['s1'] and t['s2'])
    o['second60'] = pct(sgn(t['s4']) == sgn(t['s3']) for t in rows if t['s3'] and t['s4'])
    o['closeabs'] = med(abs(t['r']['close']) for t in rows)
    return o
def pure(d, ev, hhmm):
    return not any(e != ev and e in MAJOR and t == hhmm for e, t in EXT[d].items())
if __name__ == '__main__':
    BASE = {}
    for hh in ('0830', '1000', '1400', '1430'):
        BASE[hh] = [m for m in (metr(d, hh) for d in clean_days(hh)) if m]
    H = ('event', 'time', 'n', 'pure', '|5m|', '|15m|', '|30m|', 'x15', 'pre60', 'pre=30', 's30', 's60', 's120', 'sCl', 'e60', 'eCl', 'F60', 'F120', 'FCl', 'al_on', 'al_mo', 'nxRev', 'nx|', '2nd', 'cl|')
    print('Columns: |Xm| median abs move T..T+X in ADR (x = vs clean days same time); x15 median max excursion in first 15m; pre60 median |drift| T-60..T;')
    print('pre=30: % pre-drift sign = 30m reaction sign; sX: % still on the 15m-spike side at +X; eX: % beyond the 15m level; FX: % that traded back to the pre-release price')
    print('after the first 15 minutes, by +X; al_on: % close-vs-F direction = overnight (18:00->9:30 or ->8:30) direction; al_mo: same vs 9:30->T morning move;')
    print('nxRev: % next RTH day (open->close) opposite to the event move (close - F); nx|: median |next day| ADR; 2nd: % (30m->close) same sign as (0->30m); cl|: median |close - F| ADR\n')
    print(' '.join(f'{h:>6s}' for h in H))
    def line(lab, hh, rows, base, npure=''):
        o = summary(rows); bo = summary(base) if base else None
        rel = lambda k: f"{o[k]:.3f}" + (f"({o[k] / bo[k]:.1f}x)" if bo and bo[k] else '')
        print(f"{lab:>9s} {hh:>5s} {o['n']:4d} {str(npure):>4s} {rel('m5'):>11s} {rel('m15'):>11s} {rel('m30'):>11s} {o['ex15']:.3f} {o['pre']:.3f} {o['pre_agree30']} "
              f"{o['same30']} {o['same60']} {o['same120']} {o['sameclose']} {o['ext60']} {o['extclose']} {o['touch60']} {o['touch120']} {o['touchclose']} "
              f"{o['al_on']} {o['al_morn']} {o['nxt_rev']} {o['nxt_abs']:.2f} {o['second']} {o['closeabs']:.2f}")
    for hh in BASE: line('CLEAN', hh, BASE[hh], None)
    print()
    for ev in EVS:
        rows = []; np_ = 0; hh0 = None
        for d, hh in event_days(ev):
            if ev == 'CLAIMS' and any(e in MAJOR and t == '0830' for e, t in EXT[d].items()): continue   # claims-only Thursdays
            m = metr(d, hh)
            if m: m['hh'] = hh; m['pure'] = pure(d, ev, hh); rows.append(m)
        for hh in sorted(set(t['hh'] for t in rows)):
            rr = [t for t in rows if t['hh'] == hh]
            line(ev, hh, rr, BASE.get(hh), sum(t['pure'] for t in rr))
        if ev in ('GDP', 'PCE', 'RETAIL', 'JOLTS', 'ISM_MFG', 'ISM_SRV'):
            rr = [t for t in rows if t['pure']]
            if len(rr) >= 8 and len(rr) < len(rows): line(ev + '*', rr[0]['hh'], rr, BASE.get(rr[0]['hh']), len(rr))
        for p in ('IS', 'OOS'):
            rr = [t for t in rows if per(t['d']) == p]
            if ev in ('FOMC', 'FOMC_PC', 'CPI', 'NFP', 'PPI') and rr: line(f'{ev[:6]}.{p}', rr[0]['hh'], rr, BASE.get(rr[0]['hh']))
    print('\n* = pure subset: no other major release at the same minute (GDP with PCE etc. removed)')
    # FOMC detail
    print('\nFOMC detail (14:00 statement): sign agreement of moves')
    rows = [m for m in (metr(d, '1400') for d, _ in event_days('FOMC')) if m]
    def agree(a, b): v = [sgn(a(t)) == sgn(b(t)) for t in rows if a(t) and b(t)]; return f"{sum(v)}/{len(v)} = {sum(v) / len(v):.0%}"
    print('  14:00-14:30 vs 14:30-close        ', agree(lambda t: t['r'][30], lambda t: t['r']['close'] - t['r'][30]))
    print('  14:00-14:30 vs 14:30-15:00        ', agree(lambda t: t['r'][30], lambda t: t['r'][60] - t['r'][30]))
    print('  14:30-15:00 vs 15:00-close        ', agree(lambda t: t['r'][60] - t['r'][30], lambda t: t['r']['close'] - t['r'][60]))
    print('  14:00-15:00 vs 15:00-close        ', agree(lambda t: t['r'][60], lambda t: t['r']['close'] - t['r'][60]))
    print('  14:00-14:05 vs 14:05-close        ', agree(lambda t: t['r'][5], lambda t: t['r']['close'] - t['r'][5]))
    print('  14:00-close vs next day open-close', agree(lambda t: t['r']['close'], lambda t: t['nxt']))
    print('  9:30-14:00 vs 14:00-close         ', agree(lambda t: t['morning'], lambda t: t['r']['close']))
    bb = [m for m in BASE['1400']]
    v = [sgn(t['r']['close']) == sgn(t['nxt']) for t in bb if t['nxt'] and t['r']['close']]
    print(f'  baseline: 14:00-close vs next day on clean days {sum(v)}/{len(v)} = {sum(v) / len(v):.0%}')
    v = [sgn(t['r'][30]) == sgn(t['r']['close'] - t['r'][30]) for t in bb if t['r'][30] and t['r']['close'] - t['r'][30]]
    print(f'  baseline: 14:00-14:30 vs 14:30-close on clean days {sum(v)}/{len(v)} = {sum(v) / len(v):.0%}')
    print('\nFOMC per meeting (ADR units): date, r5, r30, r60, close, next day, touched-F-by-close')
    for t in rows:
        print(f"  {t['d']} {t['r'][5]:+.2f} {t['r'][30]:+.2f} {t['r'][60]:+.2f} {t['r']['close']:+.2f} nxt {t['nxt'] if t['nxt'] is None else round(t['nxt'], 2)} F:{int(t['touch']['close'])}")
