-- mnq-quant SQLite schema
CREATE TABLE IF NOT EXISTS bars_5m (sym TEXT, t INTEGER, o REAL, h REAL, l REAL, c REAL, v REAL, PRIMARY KEY(sym,t));
CREATE TABLE IF NOT EXISTS bars_1m (sym TEXT, t INTEGER, o REAL, h REAL, l REAL, c REAL, PRIMARY KEY(sym,t));
CREATE TABLE IF NOT EXISTS day_features (d INTEGER PRIMARY KEY, gap REAL, or_dir REAL, pd_rel REAL, committed INTEGER, bias INTEGER, regime20 INTEGER, adr REAL);
CREATE TABLE IF NOT EXISTS journal (
  id INTEGER PRIMARY KEY AUTOINCREMENT, d INTEGER, playbook TEXT, day_type TEXT, side TEXT, entry_time TEXT, entry REAL, stop REAL, target REAL,
  exit_time TEXT, exit_price REAL, qty INTEGER, pnl REAL, exit_reason TEXT, source TEXT, -- backtest | tradingview | sim | live
  rule_ok INTEGER, note TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS daily_pnl (d INTEGER, source TEXT, pnl REAL, trades INTEGER, PRIMARY KEY(d,source));
