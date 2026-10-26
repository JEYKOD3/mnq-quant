"""Fetch mega-cap earnings report dates (2022-01 .. 2026-10) from the Nasdaq earnings calendar API.
All nine names report after the 16:00 close, so the report date's evening (18:00 reopen) is the post-earnings evening.
Output: data/earnings_megacap.csv (date,symbol,time)."""
import json, datetime, urllib.request, concurrent.futures as cf, csv
SYM = {'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AVGO', 'NFLX'}
def get(d):
    u = f"https://api.nasdaq.com/api/calendar/earnings?date={d.isoformat()}"
    for _ in range(3):
        try:
            r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
            j = json.load(urllib.request.urlopen(r, timeout=30))
            rows = (j.get('data') or {}).get('rows') or []
            return [(d.strftime('%Y%m%d'), x['symbol'], x.get('time', '')) for x in rows if x['symbol'] in SYM]
        except Exception as e: err = e
    print('fail', d, err); return []
days = []; d = datetime.date(2022, 1, 1)
while d <= datetime.date(2026, 10, 24):
    if d.weekday() < 5: days.append(d)
    d += datetime.timedelta(1)
out = []
with cf.ThreadPoolExecutor(8) as ex:
    for v in ex.map(get, days): out += v
out.sort()
w = csv.writer(open('/home/claude/mnq-quant/data/earnings_megacap.csv', 'w')); w.writerow(['date', 'symbol', 'time']); w.writerows(out)
print(len(out), 'rows')
