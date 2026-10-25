import json,collections
S='/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/'
J=json.load(open(S+'sepoct2.json'))['updated']
old=json.load(open(S+'dashsep/days.json'))
hm=lambda m:f"{m//60}:{m%60:02d}"
f=lambda x:f"{x:,.2f}".rstrip('0').rstrip('.')
SN={'V4+':'v4','D2':'d2','Pinball':'pin','H2':'h2'}
days=[];trades=[];n=0;cum=0
oldby={d['date']:d for d in old}
import sys; sys.path.insert(0,'.')
for r in J:
    ds=f"{str(r['d'])[:4]}-{str(r['d'])[4:6]}-{str(r['d'])[6:]}"; o=oldby[ds]
    row={k:o[k] for k in ('date','source','trend','adr','gap_adr','first15_adr','open','close','events')}
    row.update(room=round(r['room']),trades=len(r['trades']),pnl_1mnq=round(sum(t['net1'] for t in r['trades'])),pnl_eval=round(r['day']),balance_eval=round(r['bal']))
    cum+=row['pnl_1mnq']; row['cum_1mnq']=cum
    for s,k in SN.items():
        mine=[t for t in r['trades'] if t['strat']==s]
        if mine:
            txt=[]
            for t in mine:
                side='LONG' if t['side']>0 else 'SHORT'
                w={'stop':'stopped','target':'target hit','breakeven':'breakeven stop'}.get(t['why'],t['why'])
                x=f"{side} {hm(t['eT'])} @{f(t['eP'])}, {w} {hm(t['xT'])} @{f(t['xP'])}: {t['pts']:+.2f} pts"
                if t.get('be'): x+=f" (stop to breakeven {hm(t['be'])})"
                if t['q']==0: x+=" (0 contracts: day risk budget used)"
                txt.append(x)
            row[k]=' | '.join(txt)
        else:
            nt=o[k]
            if s=='H2' and 'needs 0.40' in nt:
                v=float(nt.split(': ')[1].split(' ADR')[0]); nt=nt.replace('needs 0.40','needs 0.30')
            if s=='V4+' or s=='D2' or s=='Pinball' or s=='H2':
                if '|' in nt or nt.startswith(('LONG','SHORT')): nt='No trade under the updated rules'
            row[k]=nt
    for t in r['trades']:
        n+=1; side='LONG' if t['side']>0 else 'SHORT'
        trades.append(dict(id=f"U{n:02d}",date=ds,strategy=t['strat'],side=side,entry_time=hm(t['eT']),entry=round(t['eP'],2),stop=round(t['stp'],2),target=round(t['tgt'],2) if t['tgt'] else None,
            exit_time=hm(t['xT']),exit=round(t['xP'],2),exit_reason=t['why'],risk_pts=round(t['r'],2),result_pts=round(t['pts'],2),result_R=round((t['pts']-2*2.37/2)/t['r'],2),pnl_1mnq=round(t['net1']),
            contracts=t['q'],risk_usd=round(t['q']*t['rc']),pnl_eval=round(t['netq']),why=''))
    days.append(row)
# copy "why" from current trades where same trade
cur=json.load(open(S+'dashsep/trades.json')); ck={(t['date'],t['strategy'],t['entry_time']):t['why'] for t in cur}
for t in trades:
    t['why']=ck.get((t['date'],t['strategy'],t['entry_time']),'H2 at the lower 0.30 trend-day threshold' if t['strategy']=='H2' else '')
    if t['strategy']=='H2' and t['why'] and 'trend day' in t['why']: pass
json.dump(days,open(S+'dashsep/days_u.json','w')); json.dump(trades,open(S+'dashsep/trades_u.json','w'))
print(len(days),len(trades),days[-1]['balance_eval'],cum)
for d in days:
    if d['trades']: print(d['date'],d['pnl_eval'],d['v4'][:60],'|',d['h2'][:80])
