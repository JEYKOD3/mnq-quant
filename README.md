# mnq-quant

MNQ (Micro Nasdaq) strategy research and trading system. Private.

## Layout
- `data/raw/` Databento CME GLBX MNQ/MES 5-minute continuous bars 2021-10 to 2026-10 (back-adjusted), RTH 1-minute MNQ, RTH/ETH 5-minute text format (`YYYYMMDD|hhmm,o,h,l,c|...`, prices in quarter points).
- `data/features/day_features.json` per-day features known at 9:45 ET: gap, first-15-min direction, prior-day range ratio, committed flag, bias.
- `engine/js/engine.js` bar-by-bar simulators (ORB break, ORB retest V2, failed break, key-level, Wade 2E) + exits (TP1, BE, trail, levels) + eval simulator. `engine/js/report.js` daily/weekly/monthly scoring.
- `engine/py/mnqbt.py` Wade/V10 price-action engine (Python, full session). `engine/py/rep.py` scoring.
- `strategies/pine/` TradingView strategies. `strategies/moomoo/` Mai Language indicators.
- `scripts/` the research runs (2026 grids, regime tests, plan for the last month).
- `docs/rulebook/RULEBOOK.md` the rules that passed the gate. `docs/research/` findings.
- `journal/` trade journal (to build).

## Setup
```
pip install -r requirements.txt
npm install
gunzip -k data/raw/*.gz
node scripts/featdump.js        # rebuild day features
node scripts/plan.js            # last month, trade by trade
```
Scripts expect to run from `scripts/`.

## Method
Every rule must be positive in 2026 and in 2022-2025 with more green days than red; judged on net P&L, max drawdown, % profitable, profit factor. Walk-forward where parameters are fitted. TradingView check on the last month before anything is traded, then sim.
