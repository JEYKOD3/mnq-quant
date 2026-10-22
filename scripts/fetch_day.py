"""Fetch today's (or a given day's) MNQ RTH 1-minute bars from Databento, aggregate to 5m, and write/replace that day in data/live/mnq_rth_5m_live.txt
Usage: DATABENTO_API_KEY=... python scripts/fetch_day.py [YYYYMMDD] [--until HHMM]   (run from repo root)
Format matches data/raw/mnq_rth_5m.txt: YYYYMMDD|hhmm,o,h,l,c|...  prices in quarter points (x4)."""
import os, sys, datetime as dt, zoneinfo, collections
NY=zoneinfo.ZoneInfo('America/New_York'); R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args=[a for a in sys.argv[1:] if not a.startswith('--')]; until=1600
if '--until' in sys.argv: until=int(sys.argv[sys.argv.index('--until')+1])
day=dt.datetime.strptime(args[0],'%Y%m%d').date() if args else dt.datetime.now(NY).date()
import databento as db
client=db.Historical(os.environ['DATABENTO_API_KEY'])
start=dt.datetime(day.year,day.month,day.day,9,30,tzinfo=NY); end=dt.datetime(day.year,day.month,day.day,until//100,until%100,tzinfo=NY)
data=client.timeseries.get_range(dataset='GLBX.MDP3',schema='ohlcv-1m',symbols=['MNQ.v.0'],stype_in='continuous',start=start,end=end)
df=data.to_df()
if df.empty: print('no bars for',day); sys.exit(2)
agg=collections.OrderedDict()
for ts,row in df.iterrows():
    t=ts.tz_convert(NY); hm=t.hour*100+(t.minute//5)*5
    o,h,l,c=float(row['open']),float(row['high']),float(row['low']),float(row['close'])
    if hm in agg: a=agg[hm]; agg[hm]=[a[0],max(a[1],h),min(a[2],l),c]
    else: agg[hm]=[o,h,l,c]
line=f"{day:%Y%m%d}|"+'|'.join(f"{hm},{int(round(v[0]*4))},{int(round(v[1]*4))},{int(round(v[2]*4))},{int(round(v[3]*4))}" for hm,v in agg.items())
p=os.path.join(R,'data','live','mnq_rth_5m_live.txt'); lines=[]
if os.path.exists(p): lines=[l for l in open(p).read().splitlines() if l and not l.startswith(f"{day:%Y%m%d}|")]
lines.append(line); open(p,'w').write('\n'.join(lines)+'\n'); print(f"{day} {len(agg)} 5m bars written (through {until})")
