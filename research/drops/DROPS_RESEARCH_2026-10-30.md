# Predicting MNQ drops (2026-10-30)

Question: can we tell when a big drop is coming, and stop getting stopped out by pullbacks?
Data: MNQ 5m all hours and 1m RTH, 2021-10 to 2026-10-20. Train before 2025, test 2025-26. This week's bars were not available (Databento key in GitHub secrets rejected: auth_invalid_username_in_basic_auth).

## Entry ideas tested (all about break-even)
| Idea | Trades | PF all | PF train | PF test |
|---|---|---|---|---|
| Downtrend pullback-break short (5m, stop above pullback high, 2R) | 8,569 | 0.98 | ~0.96 | ~1.0 (2026: 1.11) |
| Jey's EMA break -> retest -> continue (1m, EMA20/9, 1-2R, 40 variants) | 2,800-13,500 | 0.98-1.04 | 1.00-1.07 | 0.95-1.00 |
| Sell the bounce at 0.75-1.5 ATR above a fresh low (5m, 36 variants) | ~6,000 | 0.92-0.995 | <1 | best 1.025 |
None of the precursor features (pullback depth, pullback volume vs leg volume, pullback length, EMA/VWAP tag, distance below EMA) separated winners from losers. A big drop cannot be called in advance from these patterns.

## What is solid: bounce sizes (pullback_size.py)
In a falling market (5m EMA21 slope < -0.5 ATR over 30 min, close below it), after a fresh 5m low:
- 89% made another new low within 4h (uptrend mirror: 91% new high).
- Bounce before that new low: median 1.0 ATR(5m), 80% < 1.9 ATR, 90% < 2.8 ATR. In 2026 points: median 26, 80% 56, 90% 85 (5m ATR ~27).
- Odds of a new low once the bounce reached k ATR: 0.5: 87%, 1: 79%, 1.5: 70%, 2: 60%, 2.5: 51%, 3: 43%.
Meaning: a 15-25 pt stop sits inside normal noise. Stops need ~2 ATR (55 pts in 2026) with fewer contracts, and a bounce past 2.5 ATR means the trend is fading.

## Built
Playbook banner line 3, "bounce meter": live bounce/dip size in points and ATR, new low/high odds, normal-bounce stop distance, warning at 2.5 ATR. Informational, not an entry signal.

## Update with Oct 16-30 data (MNQZ6 1m from Databento, week_drops.py)
- 44 drops of >= 4 x 5m ATR within 1 hour in 2 weeks (about 3 per day, 70-290 pts).
- Only 13 of 44 started with price already below the 5m EMA21; most started while the chart still looked fine (above the EMA, flat slope). Waiting for "downtrend confirmed" means missing the start.
- Pre-drop conditions were ordinary: the hour before ranged about 2.5-4 ATR, volume near normal. No squeeze or volume tell.
- Timing clusters: 7:00-10:45 ET (8:30 data, 9:30 open; drop volume 4-8x normal), 15:00-16:00 ET, and 19:45-21:00 ET.
- Bounce sizes matched the 5-year stats: median 0.97 ATR (30 pts), 80% < 2.0 ATR (67 pts), 90% < 3.1 ATR (103 pts).
- This period trended harder: after a 3 ATR bounce, 64% still made a new low (5-year: 43%). The bounce meter's 2.5 ATR warning reworded to "trend weakening: no new shorts until it rolls over".
