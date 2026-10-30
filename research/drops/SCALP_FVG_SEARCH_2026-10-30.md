# Scalp, breakout and Fair Value Gap search (2026-10-30)

Data: MNQ 1m RTH 2021-10..2026-10-20 (5y) + MNQZ6 1m Oct 21-29 (Databento), MNQ 5m all hours. Cost 1 pt per round trip
($1 commission + slippage). Train < 2025, test 2025..2026-10-20, recent = Oct 21-29. One position at a time unless noted.

## 1-minute scalps (scalp_search.py, 576 variants)
EMA9 / EMA20 pullback, 5-bar micro-breakout, VWAP rejection; stops = signal bar, 8 or 15 pts; targets 1-2R; hold 5-10 min;
with/without 15m trend; 9:30-11:00 or all RTH; shorts only or both.
Result: every variant loses after costs. Best PF 0.94 (train and test), median 0.80.

## 5m breakdown momentum and "wait for the bounce, enter on the roll-over" (edge_search.py, 172 variants)
Best PF about 1.0 (1.01 / 1.01, recent 0.8). No edge.

## LuxAlgo Fair Value Gap on 1m (fvg_lab.py, fvg_seq.py)
Descriptive, after the first pullback into a gap (69k gaps):
- Continuation vs fill is a coin flip in every Playbook banner state (continuation 42-50%).
- Age matters: gaps retested within 2 bars continued 57%; 6-15 bars later 32%; 16-60 bars later 20%; > 60 bars 13%.
  An old gap that price comes back to usually fills.
- Bigger gaps hold a little more: > 1 ATR 53%, > 2 ATR 62% (rare).
- Time of day: no effect.
Trading the gap (limit at the middle, stop beyond the far edge + 0.5 ATR, 1.5R):
- A first per-gap run showed PF 1.3; it was a bug (it skipped fills whose bar closed through the gap, a look-ahead).
- Correct one-at-a-time simulation: PF 0.76-0.85 for fresh gaps; 0.99 / 1.06 when allowing older gaps. No edge.
  Banner filter (VWAP side + slope) and 9:30-11:30 window do not fix it (best 0.83 / 0.93).

## What still has an edge (earlier research)
- ORB retest 15m range, body >= 50%, stop other side, 2R, +1R lock: PF 1.19 over 5y (train 1.24, test 1.11), every year > 1.
  Last 10 RTH days: 7 trades, PF 0.77 with the body filter (too few to judge).
- FOMC statement / press conference fade back to the pre-release price (RED_FOLDER_NEWS_STUDY).
