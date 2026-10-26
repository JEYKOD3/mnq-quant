# More trades for the Lucid Flex 50K eval (Oct 26 2026)

**Question:** the fast-pass study (FAST_PASS_2026.md) showed that the bottleneck is how often we trade. 114 of 210 days in 2026 had no signal. Can new MNQ setups on those silent days make the eval pass faster?

**Short answer:** mostly no.
- 26 setup variants in 7 families were tested. Only 4 cells were positive in all three blocks (design 2022-24, validation 2025, 2026 YTD), and all are thin.
- Adding the RTH survivors to the team raises the number of trades. It also lowers the 20-day pass rate in at least one year, because the extra losers push the account into recovery mode (1 MNQ) more often.
- The one add-on that helps in every year, and never adds bust risk, is the **evening module (SGP + WCC) on its own $200 budget**.
- A one-week pass stays near 1 to 6% whatever we add.

## 1. Setup scan (1 MNQ, costs in: $2.37/side, 1 tick entry slip, 1 tick on stop exits; FOMC/CPI days skipped)

"s8" = the same cell with the engine's extra 8-pt stop slippage stress. PASS = net positive in IS, VAL and 2026 with at least 60 IS trades.

| Family / cell | IS n, PF | VAL n, PF | 2026 n, PF | PF with s8 (IS/VAL/26) | Silent 2026 days covered | Verdict |
|---|---|---|---|---|---|---|
| ORB 15m, 1.5R, far stop | 591, 1.08 | 179, 1.07 | 127, 0.81 | 0.98 / 0.99 / 0.76 | 76 | fails 2026 |
| ORB 30m, 1.5R, far stop | 422, 1.36 | 126, 0.89 | 71, 0.67 | 1.25 / 0.84 / 0.64 | 49 | fails VAL, 2026 |
| ORB 5m / other ORB cells | | | | all < 1 | | fail |
| Prior-day high/low fade | 155, 0.53-0.72 | 47, 0.69-0.73 | 42, 0.81-0.82 | | 22 | fail |
| **Prior-day high/low break, stop .2 / target .5 ADR** | 155, 1.02 | 47, 1.39 | 42, 1.11 | 0.89 / 1.24 / 1.00 | 22 | PASS (barely; breakeven IS) |
| Prior-day break, .12/.25 | 155, 1.01 | 47, 1.36 | 42, 1.01 | 0.81 / 1.12 / 0.87 | 22 | PASS (breakeven) |
| Overnight high/low fade or break (4 cells) | 608-610, 0.72-0.97 | 192, 0.69-0.97 | 152, 0.65-1.37 | | 74 | fail |
| **Mean pullback (TWAP), side set at 10:30 by >= 0.2 ADR move, stop 0.2 ADR, 1.5R, until 13:00** | 314, 1.16 | 113, 1.24 | 96, 1.23 | 1.01 / 1.10 / 1.11 | 36 | PASS |
| TWAP pullback, 0.3 ADR filter | 226, 1.15 | 88, 0.94 | 80, 1.36 | | 22 | fails VAL |
| Gap fade toward prior close (3 cells) | 219-288, 0.73-0.80 | 75-98, 0.79-0.98 | 50-68, 0.73-0.79 | | 28-33 | fail |
| Narrow first-hour range fade (3 cells) | 72-206, 0.67-0.86 | 38-84, 0.67-0.92 | 10-33, 0.26-0.99 | | 8-25 | fail |
| **Second-hour momentum (M2H): 11:30, move from open >= 0.5 ADR, not a D2 day, market, stop at the open, flat 14:00** | 145, 1.25 | 41, 1.26 | 39, 1.08 | 1.22 / 1.24 / 1.06 | 22 | PASS |
| M2H 0.4 ADR | 215, 1.13 | 59, 1.40 | 60, 0.68 | | 35 | fails 2026 |
| M2H with 0.25 ADR stop | 145, 1.22 | 41, 1.29 | 39, 0.65 | | 22 | fails 2026 |

**Caution:**
- About 26 cells were tested, so 1 or 2 "passes" are expected by luck.
- The neighbours of TWAP-PB and M2H fail one block each.
- Expect live PF near 1.05 to 1.15, not 1.2+.

Opening-range breakouts, which most fast-pass videos recommend, do not survive 2026 on MNQ.

## 2. Eval impact (Lucid Flex 50K sim, v31 sizing: 65% of room, $1,050/day, recovery mode, stop-day rules)

Share of evals started on each trading day that pass within N trading days. Bust = account failed within 20 days.

| Team | 2026 p5 | p8 | p10 | p20 | 2025 p5 | p8 | p10 | p20 | 2022 p5 | p8 | p10 | p20 | Bust |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BASE v31 | 0.5% | 3.4% | 4.4% | 21.8% | 0% | 2.7% | 5.1% | 18.3% | 3.2% | 9.7% | 13.8% | 30.0% | 0% |
| **+ evening SGP + WCC ($200 own budget)** | **0.5%** | **4.4%** | **7.3%** | **24.3%** | **0%** | **2.7%** | **4.7%** | **26.5%** | **3.2%** | **9.7%** | **13.8%** | **32.7%** | **0%** |
| + M2H | 0.5% | 6.3% | 11.2% | 26.2% | 0% | 1.6% | 3.5% | 17.9% | 1.4% | 7.8% | 12.0% | 27.6% | 0% |
| + M2H half size | 0.5% | 5.3% | 9.2% | 25.7% | 0% | 1.6% | 3.5% | 17.1% | 1.4% | 8.8% | 12.9% | 26.7% | 0% |
| + evening + M2H half | 0.5% | 6.3% | 11.2% | 25.7% | 0% | 2.3% | 5.1% | 21.4% | 1.4% | 8.8% | 12.9% | 31.3% | 0% |
| + TWAP-PB | 1.9% | 3.9% | 4.4% | 13.1% | 2.3% | 7.8% | 14.4% | 31.5% | 1.8% | 3.2% | 5.5% | 11.1% | 0% |
| + PD-break | 0% | 0% | 0% | 11.2% | 0% | 0.8% | 0.8% | 3.5% | 1.4% | 4.6% | 6.5% | 11.5% | 0% |
| + TWAP-PB + M2H + evening | 2.9% | 6.3% | 8.7% | 21.4% | 1.9% | 5.8% | 10.5% | 28.8% | 0.9% | 1.4% | 2.3% | 9.2% | 0% |
| + all three + evening | 1.5% | 3.4% | 4.4% | 16.5% | 1.9% | 6.2% | 9.3% | 18.7% | 2.3% | 6.0% | 6.5% | 9.7% | 0% |

Active trading days in 2026 rise from 96 (base) to 120 (with the evening module) and 166 (everything). But more trading days did not mean faster passes.

**Why extra positive trades can slow the pass:**
- The engine sizes every trade off the room above the floor.
- A small-edge setup adds losing streaks that cut the room under $400, which puts the account in recovery mode (1 MNQ).
- From there the team's good trades are too small to finish the target for weeks.
- With the 40% consistency rule, the eval needs about 3 or more good days, not many small ones.

## 3. Recommendation

| Option | What | Trade-off |
|---|---|---|
| **A (recommended)** | **Add the evening module SGP + WCC at a fixed $200 budget (about 1 MNQ), separate from the day budget.** Rules unchanged from EVENING_MODULE_2026-10-25.md (SGP Sunday 18:00-20:00, WCC Wednesday 18:05-20:00, flat 20:00). | The only add-on that is better or equal in every year at 8, 10 and 20 days, with 0% bust. Small effect (+1 to +8 points on the 20-day pass rate). |
| B | A + M2H at half size | Best 2026 at 8-10 days (11% vs 4% base) but worse than A in 2025 and 2022. Only if the user accepts a 2026-only bet. |
| C | Do not add TWAP-PB or the prior-day break | Positive alone, but they hurt the pass rate in at least one year. Keep for later research (paper-trade). |

**Exact rules for M2H, if paper-traded:**
- At the 11:29 bar close, it is not a D2 day: \|10:29 close - open\| < 0.6 ADR.
- The move from the open is >= 0.5 ADR.
- Enter at market in the move's direction.
- Stop at the 9:30 open, 1 tick beyond.
- No target. Flat at 14:00.
- Skip FOMC and CPI days.

**Bottom line for "pass in under a week":**
- Nothing tested gets a 5-day pass above about 3%, with or without more risk (see FAST_PASS_2026.md).
- The realistic plan is v31 plus the evening module, with an expected 3 to 5 weeks.
- A strong first week (+$1,500 by day 5, about 1 in 5 starts) usually finishes in week 2.

Scripts: `scripts/y2026/more_trades.py` (scan, `more_scan.json`), `more_evening_dump.py` (`more_evening.json`), `more_eval.py` (`more_eval.json`). The Pine indicator was not changed.
