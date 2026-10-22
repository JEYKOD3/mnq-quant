#!/usr/bin/env bash
# Rebuild the working server from this repo after a wipe.
# usage: git clone https://github.com/JEYKOD3/mnq-quant /home/claude/mnq-quant && bash /home/claude/mnq-quant/scripts/restore.sh
set -e
R=$(cd "$(dirname "$0")/.." && pwd); cd "$R"
echo "[1/5] unpack Databento data"
for f in data/raw/*.gz; do b="${f%.gz}"; [ -f "$b" ] || gunzip -k "$f"; done
ls -la data/raw/
echo "[2/5] python deps"
pip install -q --break-system-packages pandas numpy databento 2>/dev/null || true
echo "[3/5] node deps"; (npm install --silent 2>/dev/null || true)
echo "[4/5] rebuild sqlite"; [ -f db/load.py ] && python3 db/load.py || true
echo "[5/5] sanity: green-day lab smoke test (2026 only)"
python3 scripts/greenday_lab.py 2026 | head -3
echo "restore done. read knowledge/INDEX.md then knowledge/RULES.md."
