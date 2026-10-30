"""Fetch MNQ 1-minute bars (all hours) for a date range from Databento and write data/live/mnq_1m_<start>_<end>.csv.gz
Usage: DATABENTO_API_KEY=... python scripts/fetch_range_1m.py 2026-10-20 2026-10-31"""
import os, sys, databento as db
s,e=sys.argv[1],sys.argv[2]
c=db.Historical(os.environ['DATABENTO_API_KEY'])
df=c.timeseries.get_range(dataset='GLBX.MDP3',schema='ohlcv-1m',symbols=['MNQ.v.0'],stype_in='continuous',start=s,end=e).to_df()
df=df[['open','high','low','close','volume']]
os.makedirs('data/live',exist_ok=True); p=f'data/live/mnq_1m_{s}_{e}.csv.gz'
df.to_csv(p,compression='gzip'); print(p,len(df),df.index.min(),df.index.max())
