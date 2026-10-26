"""Build data/macro_dates_ext.csv: red-folder US events 2022-2026 (date,event,time_et,approx,source).
Sources (fetched Oct 25 2026):
  FOMC meetings + minutes: federalreserve.gov/monetarypolicy/fomccalendars.htm (official)
  GDP advance, PCE (Personal Income and Outlays): bea.gov/news/archive (official), times: bea.gov/news/schedule
  Retail Sales: census.gov/retail/marts/www/MARTSreleasedates.xlsx (official)
  ISM Manufacturing / Services: rule (1st / 3rd business day, January exceptions) -> approx
  JOLTS: 2025 schedule cross-checked on equalsmoney.com (BLS schedule copy); other years from memory -> approx
  Initial Jobless Claims: every Thursday 8:30, Wednesday when Thursday is a federal holiday -> rule
  Fed Chair semiannual testimony / Jackson Hole: from memory -> approx
approx = 0 official date, 1 rule-based or remembered (could be off by a day, or a release was skipped)."""
import csv, datetime as dt
OUT = '/home/claude/mnq-quant/data/macro_dates_ext.csv'
rows = []
def add(d, ev, t, ap, src): rows.append((d.replace('-', '') if isinstance(d, str) else d.strftime('%Y%m%d'), ev, t, ap, src))
# ---------- FOMC (existing file) + press conference ----------
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')):
    if r['event'] == 'FOMC':
        add(r['date'], 'FOMC', '1400', 0, 'fed'); add(r['date'], 'FOMC_PC', '1430', 0, 'fed')
SEP = {'20220316','20220615','20220921','20221214','20230322','20230614','20230920','20231213','20240320','20240612','20240918',
       '20241218','20250319','20250618','20250917','20251210','20260318','20260617','20260916','20261209'}
for d in SEP: add(d, 'FOMC_SEP', '1400', 0, 'fed')
MIN = ['2022-01-05','2022-02-16','2022-04-06','2022-05-25','2022-07-06','2022-08-17','2022-10-12','2022-11-23','2023-01-04','2023-02-22',
       '2023-04-12','2023-05-24','2023-07-05','2023-08-16','2023-10-11','2023-11-21','2024-01-03','2024-02-21','2024-04-10','2024-05-22',
       '2024-07-03','2024-08-21','2024-10-09','2024-11-26','2025-01-08','2025-02-19','2025-04-09','2025-05-28','2025-07-09','2025-08-20',
       '2025-10-08','2025-11-19','2025-12-30','2026-02-18','2026-04-08','2026-05-20','2026-07-08','2026-08-19','2026-10-07']
for d in MIN: add(d, 'FOMC_MIN', '1400', 0, 'fed')
# ---------- GDP advance (Q3 2025 'initial' estimate replaced the advance after the shutdown) ----------
GDP = ['2022-01-27','2022-04-28','2022-07-28','2022-10-27','2023-01-26','2023-04-27','2023-07-27','2023-10-26','2024-01-25','2024-04-25',
       '2024-07-25','2024-10-30','2025-01-30','2025-04-30','2025-07-30','2025-12-23','2026-02-20','2026-04-30','2026-07-30']
for d in GDP: add(d, 'GDP', '0830', 0, 'bea')
# ---------- PCE (Personal Income and Outlays). 10:00 when it shared the day with a GDP 8:30 release in Apr 2025 ----------
PCE = ['2022-01-28','2022-02-25','2022-03-31','2022-04-29','2022-05-27','2022-06-30','2022-07-29','2022-08-26','2022-09-30','2022-10-28',
       '2022-12-01','2022-12-23','2023-01-27','2023-02-24','2023-03-31','2023-04-28','2023-05-26','2023-06-30','2023-07-28','2023-08-31',
       '2023-09-29','2023-10-27','2023-11-30','2023-12-22','2024-01-26','2024-02-29','2024-03-29','2024-04-26','2024-05-31','2024-06-28',
       '2024-07-26','2024-08-30','2024-09-27','2024-10-31','2024-11-27','2024-12-20','2025-01-31','2025-02-28','2025-03-28','2025-04-30',
       '2025-05-30','2025-06-27','2025-07-31','2025-08-29','2025-09-26','2025-12-05','2026-01-22','2026-02-20','2026-03-13','2026-04-09',
       '2026-04-30','2026-05-28','2026-06-25','2026-07-30','2026-08-26']
for d in PCE:
    if d == '2025-04-30': add(d, 'PCE', '1000', 0, 'bea')
    elif d == '2025-12-05': add(d, 'PCE', '1000', 1, 'bea (post-shutdown catch-up, time unverified)')
    elif d >= '2026-01-01': add(d, 'PCE', '0830', 1, 'bea (combined GDP+PCE day, time from schedule pattern)')
    else: add(d, 'PCE', '0830', 0, 'bea')
# ---------- Retail sales (Census table: day of release by year/month) ----------
RS = {2022: [14,16,16,14,17,15,15,17,15,14,16,15], 2023: [18,15,15,14,16,15,18,15,14,17,15,14], 2024: [17,15,14,15,15,18,16,15,17,17,15,17],
      2025: [16,14,17,16,15,17,17,15,16,None,25,16], 2026: [14,10,6,(1,21),14,17,16,14,16,15,None,None]}
for y, ms in RS.items():
    for m, x in enumerate(ms, 1):
        if x is None: continue
        for dd in (x if isinstance(x, tuple) else (x,)):
            add(dt.date(y, m, dd), 'RETAIL', '0830', 0, 'census')
# ---------- holidays / business days ----------
def nth_wd(y, m, wd, n):
    d = dt.date(y, m, 1); k = 0
    while True:
        if d.weekday() == wd:
            k += 1
            if k == n: return d
        d += dt.timedelta(1)
def last_wd(y, m, wd):
    d = dt.date(y, m + 1, 1) - dt.timedelta(1) if m < 12 else dt.date(y, 12, 31)
    while d.weekday() != wd: d -= dt.timedelta(1)
    return d
def obs(d):
    return d - dt.timedelta(1) if d.weekday() == 5 else d + dt.timedelta(1) if d.weekday() == 6 else d
HOL = set()
for y in range(2021, 2028):
    HOL |= {obs(dt.date(y, 1, 1)), nth_wd(y, 1, 0, 3), nth_wd(y, 2, 0, 3), last_wd(y, 5, 0), obs(dt.date(y, 6, 19)), obs(dt.date(y, 7, 4)),
            nth_wd(y, 9, 0, 1), nth_wd(y, 10, 0, 2), obs(dt.date(y, 11, 11)), nth_wd(y, 11, 3, 4), obs(dt.date(y, 12, 25))}
def bizdays(y, m):
    d = dt.date(y, m, 1); out = []
    while d.month == m:
        if d.weekday() < 5 and d not in HOL: out.append(d)
        d += dt.timedelta(1)
    return out
END = dt.date(2026, 10, 20)
# ---------- ISM ----------
JAN = {2022: ('2022-01-04', '2022-01-06'), 2023: ('2023-01-04', '2023-01-06'), 2024: ('2024-01-03', '2024-01-05'),
       2025: ('2025-01-03', '2025-01-07'), 2026: ('2026-01-05', '2026-01-07')}
for y in range(2022, 2027):
    for m in range(1, 13):
        if dt.date(y, m, 1) > END: break
        if m == 1: a, b = JAN[y]; add(a, 'ISM_MFG', '1000', 1, 'rule'); add(b, 'ISM_SRV', '1000', 1, 'rule'); continue
        bd = bizdays(y, m); add(bd[0], 'ISM_MFG', '1000', 1, 'rule'); add(bd[2], 'ISM_SRV', '1000', 1, 'rule')
# ---------- JOLTS ----------
JOLTS = ['2022-02-01','2022-03-09','2022-03-29','2022-05-03','2022-06-01','2022-07-06','2022-08-02','2022-09-06','2022-10-04','2022-11-01',
         '2022-11-30','2023-01-04','2023-02-01','2023-03-08','2023-04-04','2023-05-02','2023-06-06','2023-07-06','2023-08-01','2023-08-29',
         '2023-10-03','2023-11-01','2023-12-05','2024-01-03','2024-02-06','2024-03-06','2024-04-02','2024-05-01','2024-06-04','2024-07-02',
         '2024-07-30','2024-09-04','2024-10-01','2024-10-29','2024-12-03','2025-01-07','2025-02-04','2025-03-11','2025-04-01','2025-04-29',
         '2025-06-03','2025-07-01','2025-07-29','2025-09-03','2025-09-30','2025-12-09','2026-01-07','2026-02-05','2026-03-10','2026-03-31',
         '2026-05-05','2026-06-02','2026-06-30','2026-08-04','2026-09-01','2026-09-29']
for d in JOLTS: add(d, 'JOLTS', '1000', 0 if d[:4] == '2025' and d < '2025-10' else 1, 'equalsmoney (BLS copy)' if d[:4] == '2025' and d < '2025-10' else 'memory')
# ---------- Initial claims (Thursdays; Wednesday if Thursday is a holiday). Oct-Nov 2025 shutdown weeks flagged ----------
d = dt.date(2022, 1, 6)
while d <= END:
    x = d - dt.timedelta(1) if d in HOL else d
    ap = 1 if dt.date(2025, 10, 1) <= x <= dt.date(2025, 11, 13) else 0
    add(x, 'CLAIMS', '0830', ap, 'rule')
    d += dt.timedelta(7)
# ---------- Fed chair testimony (semiannual) and Jackson Hole ----------
for x in ['2022-01-11','2022-03-02','2022-03-03','2022-06-22','2022-06-23','2023-03-07','2023-03-08','2023-06-21','2023-06-22',
          '2024-03-06','2024-03-07','2024-07-09','2024-07-10','2025-02-11','2025-02-12','2025-06-24','2025-06-25']:
    add(x, 'TESTIMONY', '1000', 1, 'memory')
for x in ['2022-08-26', '2023-08-25', '2024-08-23', '2025-08-22']: add(x, 'JACKSON', '1000', 1, 'memory')
# existing 8:30 core events, so one file has everything
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')):
    if r['event'] in ('CPI', 'PPI', 'NFP'): add(r['date'], r['event'], r['time_et'], 0, 'macro_dates.csv')
rows = sorted(set(r for r in rows if '20220101' <= r[0] <= '20261231'))
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'event', 'time_et', 'approx', 'source']); w.writerows(rows)
import collections
print(len(rows), collections.Counter(r[1] for r in rows))
