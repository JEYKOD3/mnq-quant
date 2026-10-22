# RESTORE (server wiped? start here)
1. git clone https://github.com/JEYKOD3/mnq-quant /home/claude/mnq-quant
2. bash /home/claude/mnq-quant/scripts/restore.sh   (unzips data, deps, sqlite, smoke test)
3. Read knowledge/INDEX.md -> knowledge/RULES.md (rule registry, statuses, results)
4. Project docs (claude.ai Project "Trading Strategy") hold the human-readable reports; repo holds everything runnable.

What is where
- data/raw/*.gz          Databento MNQ/MES 5m continuous 2021-10..2026-10, MNQ RTH 1m, MNQ ETH 5m (restore.sh unzips)
- data/features/         day_features.json (gap/orDir/pdRel/committed/bias per day)
- data/transcripts/      51 Wade YouTube transcripts (raw captions)
- knowledge/             RULES.md registry + condensed sources (Wade doc, per-video notes, 3 research files, book notes)
- engine/js, engine/py   backtest engines (engine.js = Eval Lab engine with simORB/simRT2/simFB/simKL; mnqbt.py/rep.py python replica)
- strategies/pine        TradingView Pine: ORB Retest V2/V3/V4 Adaptive, ORB V2 Adaptive, Failed Break V1, VWAP V1 (+ older MNQSCALP versions)
- strategies/moomoo      Mai Language ports (parked)
- lab/                   Eval Lab artifact source (index.html + engine.js); published at https://claude.ai/artifact/Bs81vGM7DhwWVmXHTTHi29
- scripts/               research scripts (greenday_lab*.py = day-type/green-day tests; orb26/fb26/markov/etc = earlier variants), label_today.js, day_report.js, fetch_day.py
- archive/               older project docs, wade per-batch notes, scratch scripts, moomoo V4 source
- docs/research          measured results (GREENDAY_LAB_2026-10-21.md etc), docs/rulebook/RULEBOOK.md
- journal/daily          daily labels/journal (GitHub Action .github/workflows/daily.yml needs DATABENTO_API_KEY secret)
Not in repo (copyright): book PDFs. Notes of them are in knowledge/book/.
