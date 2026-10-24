import sys; sys.path.insert(0,'.')
from regime import *
def rel(t):
    r=reg.get(t['d']); 
    if not r: return None
    if r['trend']=='mixed': return 'mixed'
    return 'with' if (r['trend']=='up')==(t['side']>0) else 'against'
def show(lab,tr):
    D_=summary(tr,20220101,20241231); T_=summary(tr,20250101,20261231)
    print(f"{lab:46s} DEV n{D_['n']:3d} PF{D_['pf']:5.2f} avgR{D_['avgR']:+.2f} | TEST n{T_['n']:3d} PF{T_['pf']:5.2f} avgR{T_['avgR']:+.2f} | {yearly(tr)}")
for k in ('V4_1m_2R','V4_1m_close','V4_5m_2R','D2_1030_4l_close','D2_1030_o_1500','D2_1130_l_close'):
    tr=[t for t in TR[k] if t['d'] in reg]
    show(k+' all',tr)
    for cat in ('with','mixed','against'): show(f'   {cat}',[t for t in tr if rel(t)==cat])
    show('   with+mixed (skip against)',[t for t in tr if rel(t)!='against'])
    show('   skip FOMC day',[t for t in tr if not reg[t['d']]['fomc']])
# alternative trend defs robustness for V4: SMA10/SMA20 only / 5-day return sign
import statistics
def trend_alt(d,kind):
    i=D.index(d); c1=C[D[i-1]]
    if kind=='sma20': s=sum(C[x] for x in D[i-20:i])/20; return 1 if c1>s else -1
    if kind=='sma50': s=sum(C[x] for x in D[i-50:i])/50; return 1 if c1>s else -1
    if kind=='r5': return 1 if C[D[i-1]]>C[D[i-6]] else -1
    if kind=='r20': return 1 if C[D[i-1]]>C[D[i-21]] else -1
for kind in ('sma20','sma50','r5','r20'):
    tr=[t for t in TR['V4_1m_2R'] if t['d'] in reg]
    show(f'V4_1m_2R with {kind}',[t for t in tr if trend_alt(t['d'],kind)==t['side']])
    show(f'V4_1m_2R against {kind}',[t for t in tr if trend_alt(t['d'],kind)!=t['side']])
print('--- D2 with/against r5 and sma20')
for k in ('D2_1030_4l_close','D2_1030_o_1500','D2_1130_l_close'):
    tr=[t for t in TR[k] if t['d'] in reg]
    for kind in ('r5','sma20'):
        show(f'{k} with {kind}',[t for t in tr if trend_alt(t['d'],kind)==t['side']])
        show(f'{k} against {kind}',[t for t in tr if trend_alt(t['d'],kind)!=t['side']])
