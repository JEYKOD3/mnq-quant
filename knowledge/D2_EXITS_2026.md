# D2 exits redesign, 2026 focus (Oct 25 2026)

Goal: D2 must not hold into the afternoon. Find the fastest exit that keeps D2 useful inside the team eval, chosen on 2026 + 2025 (closest regime twin), checked on 2022, stress-tested on 2023-24 (calm years).

## Recommended D2 rules (update TradingView before 10:30 ET)

1. **Filter:** skip CPI and FOMC days (unchanged).
2. **Signal:** at the 10:29 1m bar close, move = (close - RTH open) / ADR10. Trade only if |move| >= **0.60** (was 0.50).
3. **Entry:** market at 10:30, in the direction of the move.
4. **Stop:** opening price minus 1 tick for longs (plus 1 tick for shorts), unchanged. Bracket SL in ticks = round(|entry - open| / 0.25) + 1. In 2026 the stop was median 272 pts (1,086 ticks), range 137 to 567 pts.
5. **Target:** none. No breakeven, no trailing.
6. **Exit:** hard flat at **13:15 ET** (market, at the close of the 13:14 bar). Was 15:00.
7. **Size:** unchanged (65% of room, shared $1,100 budget, half size when against the daily trend).

Pine changes: `d2Th` input 0.5 -> 0.6, and the time exit `mnt >= 900` -> `mnt >= 795` (labels "15:00" -> "13:15").

## Why this rule

- **Fast exits fail.** Every time cap of 30 to 120 minutes loses money on 2025 and most other years (60 min cap: 2026 -$1,897, PF 0.63). R targets (0.75 to 2R), breakeven at +0.5R/+1R, 0.5R trails and 5m-bar trails all cut the winners. D2 is a slow trend-day hold, and its stop is huge (0.6 ADR or more), so 1R is rarely reached before lunch.
- **The edge is time in the trade before early afternoon.** Hard exits from 13:00 to 14:00 form a flat plateau inside the team eval. 13:15 sits on it and is the earliest stable point.
- **The 0.6 threshold helps the team, not D2 alone.** Fewer, cleaner D2 days leave budget for V4+ and TDP. At 1 MNQ, D2 gives up the 13:15-15:00 drift in 2023-25. In the team eval (40% consistency), the pass rate rises in 2025, 2022 and 2023-24, and is level with the old rule in 2026 once the stop-day rule is on.
- **Pullback entries look great on 2026 only.** A 0.1 ADR limit or a 5m pullback entry wins in 2026 but loses in 2022-25 (PF 0.6 to 0.9), so they are rejected as overfit.
- **The first-hour share supports the earlier exit only partly.** Exiting at 12:00-12:30 is worse than 13:15 in 2025 and 2026. The move needs until early afternoon to play out.

## Table: D2 at 1 MNQ (net $ / PF, costs in)

| Rule | 2022 | 2023 | 2024 | 2025 | 2026 YTD | 2026 n, win, avg hold, max DD |
|---|---|---|---|---|---|---|
| OLD 0.5 ADR, exit 15:00 | 2,310 / 1.82 | 1,599 / 1.90 | 924 / 1.22 | 1,508 / 1.28 | 1,507 / 1.21 | 50, 50%, 241 min, $1,571 |
| **NEW 0.6 ADR, exit 13:15** | 1,485 / 2.00 | 549 / 1.64 | -76 / 0.97 | 44 / 1.01 | **2,608 / 1.73** | 36, 50%, 162 min, $985 |
| ALT 0.5 ADR, exit 13:30 | 1,249 / 1.46 | 928 / 1.54 | 900 / 1.29 | 893 / 1.18 | 1,461 / 1.24 | 50, 54%, 166 min, $1,270 |
| 0.5 ADR, 60 min cap | -467 / 0.81 | 169 / 1.12 | 78 / 1.03 | -705 / 0.81 | -1,897 / 0.63 | 50, 42%, 59 min, $2,266 |
| 0.5 ADR, 1R target, flat 14:00 | 1,349 / 1.46 | 1,289 / 1.71 | 971 / 1.24 | 1,566 / 1.30 | 178 / 1.03 | 50, 50%, 181 min, $1,147 |

## Table: team eval contribution (other 5 strategies on live rules)

Rolling start every trading day (every 2nd day for 2022 and 2023-24). Pass within 40 trading days / fail. Lucid Flex: $3,000 target, $2,000 EOD trailing loss locking at $50,100, 40% consistency, engine sizing, +8 pt stop slippage convention. Same-minute signals are sized in Pine script order (NEWS, V4+, D2, TDP, Pinball, H2).

| Rule | 2026 | 2025 | 2022 | 2023-24 | 2026 + stop-day | 2025 + stop-day | 2026 at 50% cons. |
|---|---|---|---|---|---|---|---|
| OLD exit 15:00 | 37% / 0.5% | 36% / 0% | 42% / 0.9% | 30% / 3.9% | 41% / 0% | 34% / 0% | 43% |
| **NEW 0.6, exit 13:15** | 33% / 2.4% | **42% / 0%** | **48% / 0.9%** | **32% / 0.8%** | 40% / 0% | **44% / 0%** | 41% |
| ALT 0.5, exit 13:30 | 31% / 0.5% | 35% / 0% | 42% / 0.9% | 28% / 8.9% | 37% / 0% | 35% / 0% | 42% |
| 0.5, 60 min cap | 31% / 0.5% | 39% / 0% | 40% / 0.9% | 28% / 4.3% | 36% / 0% | 44% / 0% | 37% |
| No D2 at all | 32% / 2.4% | 34% / 0% | 42% / 0% | 32% / 4.3% | 40% / 0% | 35% / 0% | 34% |

- **2026 alone:** the new D2 is 4 points behind the old one without the stop-day rule, and even (40% vs 41%) with it. The 2.4% fails in 2026 also show up with no D2 at all, so they come from the other strategies (late-September cluster).
- **Primary window (2026 + 2025):** new 75 vs old 73 without the stop-day rule, 84 vs 75 with it. It is better in 2022 and 2023-24 too, with fewer fails in the calm years.
- **With the other strategies also moved to "nothing open after 15:00"** (see BACKTEST_2026_YTD.md), the full new team beats the old team in 2026 as well: 43% vs 41% with the stop-day rule.

## Caveats

- The 2026 sample is small: 36 D2 trades. The plateau (13:00 to 14:00 exits, 0.55 to 0.65 thresholds) matters more than the exact 13:15 cell.
- ALT (0.5 ADR, 13:30) is the safer choice for D2's own P&L, positive in all five years. It is weaker in the eval and had 8% fails in 2023-24.
- Scripts: `scripts/y2026/d2_grid.py` (6,913 configs), `d2_team.py`, `d2_exit_time.py`, `d2_scan2.py`, `d2_final.py`; results in `d2_grid.json`, `d2_scan2.json`, `d2_final.json`.
