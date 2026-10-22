"""Build db/mnq.sqlite from data/raw (run from repo root): python db/load.py"""
import sqlite3, gzip, json, datetime as dt, zoneinfo, os, csv
NY=zoneinfo.ZoneInfo('America/New_York'); R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con=sqlite3.connect(os.path.join(R,'db','mnq.sqlite')); con.executescript(open(os.path.join(R,'db','schema.sql')).read())
for sym in ('MNQ','MES'):
    rows=[]
    with gzip.open(os.path.join(R,'data','raw',f'{sym}_5m_cont.csv.gz'),'rt') as f:
        rd=csv.reader(f); next(rd)
        for t,o,h,l,c,v in rd: rows.append((sym,int(t),float(o),float(h),float(l),float(c),float(v)))
    con.executemany('INSERT OR REPLACE INTO bars_5m VALUES (?,?,?,?,?,?,?)',rows); print(sym,'5m bars',len(rows))
rows=[]
with gzip.open(os.path.join(R,'data','raw','mnq_rth_1m.txt.gz'),'rt') as f:
    for ln in f:
        p=ln.strip().split('|'); d=int(p[0])
        for q in p[1:]:
            hm,o,h,l,c=q.split(','); hm=int(hm)
            t=int(dt.datetime(d//10000,d//100%100,d%100,hm//100,hm%100,tzinfo=NY).timestamp())
            rows.append(('MNQ',t,int(o)/4,int(h)/4,int(l)/4,int(c)/4))
con.executemany('INSERT OR REPLACE INTO bars_1m VALUES (?,?,?,?,?,?)',rows); print('MNQ 1m bars',len(rows))
F=json.load(open(os.path.join(R,'data','features','day_features.json')))
con.executemany('INSERT OR REPLACE INTO day_features (d,gap,or_dir,pd_rel,committed,bias) VALUES (?,?,?,?,?,?)',[(int(d),f['gap'],f['orDir'],f['pdRel'],f['committed'],f['bias']) for d,f in F.items()])
con.commit(); print('day_features',len(F)); con.close()
