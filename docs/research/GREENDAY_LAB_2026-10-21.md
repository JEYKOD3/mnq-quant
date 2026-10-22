# Green-day lab, MNQ RTH 1m (Databento), 2022-01-03 to 2026-10-20, 1,195 days
Cost model: 3 pts per round trip (commission $4.74 + ~2 ticks spread/slip). 1 contract, results in points ($2/pt).
Scripts: scripts/greenday_lab.py, greenday_lab2.py (3m/5m), greenday_lab3.py (early features), greenday_lab4.py (honest labels, persistence).

## A. How much movement exists per day (zigzag swings, 1m)
- Swings >= 25 pts: median 42 per day (p25 26, p75 65). Swings >= 40 pts: median 17 per day (p25 10, p75 29).
- Same count on trend days and range days: range days have as many big swings, just not directional ones.
- Swing starts by hour (>= 40 pts, totals): 9h 5806, 10h 6419, 11h 4008, 12h 2943, 13h 2716, 14h 2925, 15h 2942. The 9:30-11:00 window holds ~45% of all big swings.
- Conclusion: 10-15 trades/day is physically available; the ceiling is not the problem, capture is. At 3 pts friction, 15 trades cost 45 pts/day before any edge.

## B. Executable Wade-lite second entry (H2/L2 at EMA21, 1-tick triggers, stop 1 tick beyond signal bar, min stop 8-10 pts)
All variants lose, every year, every timeframe:
- 1m, 2R target: 1,251 trades (1/day), win 28% (random geometry 33%), PF 0.54, green days 32%. Zero-cost ceiling still PF 0.77.
- 1m, 1R: win 42% (random 50%), PF 0.43. Min target 25 pts: PF 0.57. Day stop / trade cap: no change. First entries added: 3.4 trades/day, PF 0.60.
- 3m: PF 0.47. 5m: PF 0.79 (zero cost 0.95), TREND days +100 pts (13/19 green), RANGE days -624 (12/46).
Why it loses (loser common denominator): (1) RANGE days: the pullback to the EMA is the middle of the range, Wade's own skip rule, and we had no classifier; (2) signal-bar stops on 1m are 8-12 pts, inside the noise, hit rate below random for the geometry; (3) after the first hour, further drift is small (section C), so 2R targets from mid-day pullbacks rarely get reached.
Why winners won: trend days (honest label) only; 5m beats 1m and 3m because the signal bar is big enough for the stop to sit outside noise.

## C. What is knowable at 10:30 that predicts the day (honest labels: TREND2 = close in top/bottom 20% of range, range >= 1 ADR, |open-close| >= 60% of range; RANGE2 = range <= 0.7 ADR or close mid)
Base rates: TREND2 19%, RANGE2 40%.
- Move since open at 10:30 >= 0.5 ADR: P(trend) 36%, P(range) 25% (n=208). < 0.2 ADR: P(trend) 11%, P(range) 51% (n=478). This is the strongest early feature.
- First-hour range < 0.35 ADR: P(range) 66%, P(trend) 7% (n=149). > 0.7 ADR: P(trend) 27%.
- First-15-min direction strength, pullback depth, open outside prior range: weak alone (<= 24% trend).
- Direction persistence (10:30 side vs close): move 0.2-0.4 ADR -> 75% same side; 0.4-0.6 -> 90%; 0.6-1.0 -> 93%. Median further move after 10:30 in that direction: +0.07 / +0.09 / +0.13 ADR (about 20-45 pts). Beyond 1 ADR by 10:30 (n=18): further move negative (exhaustion).
Conclusion: the day's direction is mostly decided in the first hour (this is why ORB V4 Adaptive works and mid-day pullbacks do not). After 10:30 trade only with the 10:30 side, expect modest follow-through, size targets to ~0.1 ADR or trail; skip days with < 0.2 ADR move by 10:30 (range day odds 51%).

## D. Filtered run (5m H2 after 10:30 only on days with move >= 0.4 ADR and shallow pullback): PF 1.14, 67 trades, +160 pts. Positive but thin; 2024 carried it. Not a strategy yet.

## Next tests (in order)
1. Day-type switch at 10:30 using move/ADR and IB/ADR; playbooks per type.
2. Re-run ORB V4 without the gap condition (direction only) and with the 10:30 persistence rule as an add-on entry (first pullback after 10:30 with the 10:30 side, target 0.1 ADR, stop beyond pullback).
3. IB-level retest entry (base rate 71% continuation after retest at 1.1x IB) with 25-pt minimum target.
4. Cost sweep on everything kept (2/3/4/5 pts).
