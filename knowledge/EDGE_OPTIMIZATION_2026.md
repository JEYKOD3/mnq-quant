# Edge optimization of the existing strategies (Oct 26 2026)

Question: is the edge of our strategies (NEWS, V4+, D2, TDP, Pinball, H2, evening SGP / WCC) concentrated in conditions we can identify in real time, so that filters, better exits or "A+ only" sizing pass the Lucid Flex 50K eval faster with less risk?

**Answer: no.** The edge is thin and spread evenly. Of the 24 top filters picked on 2022-24, one held up in both 2025 and 2026, about what luck alone gives. The best exit change improves the average trade but lowers the eval pass rate. A+ tilts and A-only plans pass less often. The only change that helps in every year stays the evening module ($200 own budget, see MORE_TRADES_2026.md).

Method: 1 MNQ net R after costs ($2.37/side, 1 tick entry slip, +8 pt stop slip). Design on IS = 2022-24, validate on VAL = 2025, final check OOS = 2026 YTD (to Oct 23). Cuts are terciles fixed on IS. Max 2 filters per strategy. Eval = the Lucid Flex simulator of fast_pass.py (every start day, v31 sizing, $2,000 EOD trail, 40% consistency, $1,200 DLL). Variants tried: 199 single-filter rules (plus a 246-step greedy pass), 89 exit variants, 23 eval plans.

## 1. Where the edge sits (1 lot, average net R per trade, IS / VAL / OOS)

| Strategy | All trades | Pattern in IS | Holds in VAL and OOS? |
|---|---|---|---|
| NEWS | +0.13 / -0.03 / +0.19 | prior-day range > 1.1 ADR loses (-0.31) | no (VAL +0.79 on 2 trades, OOS -0.11) |
| V4+ | +0.13 / +0.24 / +0.24 | first hour > 0.6 ADR loses (-0.24) | no (1 and 4 trades, mixed) |
| D2 | +0.06 / +0.02 / +0.14 | with the 20-day trend +0.16, against -0.02 | partly (+0.03 / +0.38 vs +0.01 / -0.03); live already sizes counter-trend D2 at half |
| TDP | +0.10 / +0.15 / +0.13 | entries after 11:00 weak (-0.06) | mixed (VAL +0.06, OOS -0.33) |
| Pinball | +0.21 / +0.41 / +0.07 | no stable split | no |
| H2 | +0.01 / +0.02 / +0.45 | entries before 11:05 lose (-0.20 / -0.27 / -0.14) | yes, the only one |
| SGP (evening) | +0.06 / +0.11 / +0.18 | none | no |
| WCC (evening) | +0.19 / +0.34 / +0.25 | gap day > 0.64 ADR best (+0.41 / +0.93 / +0.83) | yes, but chosen after looking at all blocks: treat as a hypothesis |

Top single filters picked on IS, gain in total R (positive = filter helps):

| Strategy | Rule (skip...) | IS | VAL | OOS |
|---|---|---|---|---|
| NEWS | prior-day range >= 1.1 ADR | +4.1 | -1.6 | +0.4 |
| V4+ | first-hour range >= 0.6 ADR | +3.7 | -0.2 | -1.4 |
| TDP | entry at or after 11:00 | +2.5 | -0.7 | +3.0 |
| H2 | news day | +9.1 | -1.8 | -2.3 |
| H2 | prior-day range < 0.83 ADR | +6.8 | -3.4 | +1.0 |
| **H2** | **entry before 11:05** | **+5.9** | **+2.4** | **+0.8** |
| D2, Pinball, SGP, WCC | no IS rule worth >= 3R | | | |

## 2. Exits (MFE / MAE of the live exits)

- Losers rarely go far green first: share of losers that reached +1R before stopping: V4+ 9%, TDP 4%, Pinball 3%, D2 0%, H2 15%. Breakeven and trailing rules have little to protect.
- Winners barely heat: median MAE 0.17-0.35R. Stops are not too tight.

Best exit per strategy chosen on IS (avg R, IS / VAL / OOS):

| Strategy | Live | Best on IS | Verdict |
|---|---|---|---|
| V4+ | 1.25R, BE at 1R: +0.129 / +0.238 / +0.240 | 2R, BE at 1R: +0.130 / +0.296 / +0.325 | better per trade, but see eval below |
| TDP | 1.5R: +0.098 / +0.149 / +0.127 | no target: +0.123 / +0.018 / +0.210 | not robust |
| Pinball | 2R 180m: +0.207 / +0.408 / +0.066 | no target: +0.250 / +0.293 / +0.066 | not robust |
| H2 | 2R: +0.009 / +0.021 / +0.451 | live is best | keep |
| D2 | 13:15 exit: +0.063 / +0.018 / +0.138 | BE at 0.5R: +0.071 / -0.048 / +0.171 | not robust |
| Partial exits (50/50 blends) | | never best on IS | no |

## 3. Eval impact (Lucid Flex 50K, pass within 8 / 10 / 20 days, bust 0% in every row)

| Plan | 2026 | 2025 | 2022 |
|---|---|---|---|
| **BASE v31** | 3.4 / 4.4 / 21.8% | 2.7 / 5.1 / 18.3% | 9.7 / 13.8 / 30.0% |
| **+ evening module** | **4.4 / 7.3 / 24.3%** | **2.7 / 4.7 / 26.5%** | **9.7 / 13.8 / 32.7%** |
| V4+ 2R | 3.4 / 4.4 / 19.9% | 2.7 / 5.1 / 15.2% | 5.1 / 9.2 / 30.9% |
| V4+ 2R + H2 from 11:05 | 3.4 / 4.4 / 19.9% | 1.6 / 3.5 / 13.2% | 4.6 / 7.8 / 24.0% |
| V4+ 2R + H2 11:05 + evening | 4.4 / 7.3 / 24.3% | 1.6 / 3.1 / 19.8% | 4.6 / 7.8 / 25.8% |
| V4+ 1R | 2.9 / 4.9 / 18.4% | 3.5 / 8.9 / 29.2% | 6.5 / 12.0 / 26.7% |
| V4+ split 1.25R / 2R | 3.4 / 4.4 / 21.4% | 2.7 / 5.1 / 18.3% | 8.8 / 12.4 / 28.1% |
| TDP 1R / TDP no target | 2.4 / 3.4 / 14.1%, 1.9 / 2.9 / 17.5% | 1.6 / 3.1 / 12.8%, 1.6 / 3.1 / 13.2% | 9.7 / 13.8 / 30.0%, 8.8 / 13.8 / 30.0% |
| D2 1R target / D2 BE 0.5R | 3.4 / 4.4 / 21.4%, 1.9 / 2.9 / 20.4% | 2.7 / 5.1 / 18.3% (both) | 7.4 / 11.5 / 28.1%, 8.8 / 12.9 / 29.5% |
| A+ tilt (A full, B 0.6, C 0.3) + evening | 3.4 / 4.9 / 18.0% | 2.3 / 3.5 / 14.8% | 2.3 / 6.5 / 22.1% |
| A+ tilt (A full, B 0.5, C skip) + evening | 1.9 / 2.9 / 12.1% | 0.8 / 1.9 / 11.7% | 2.3 / 6.9 / 20.3% |
| A+ tilt, budget $1,500, f 0.8 + evening | 4.4 / 7.3 / 19.4% | 2.3 / 3.5 / 16.0% | 1.4 / 4.1 / 19.8% |
| A-only (Pinball, V4+, NEWS) + evening | 0.5 / 1.5 / 7.3% | 0 / 0 / 4.7% | 0.9 / 3.7 / 13.8% |

A = Pinball, V4+, NEWS; B = TDP, D2 with the trend; C = H2, D2 against the trend (grades from IS average R only).

Why better trades do not mean faster passes: a higher V4+ target turns some +1.25R wins into breakeven exits, so fewer green days. Skipping or shrinking C trades removes trading days. Frequency and the number of green days drive the pass, not the edge per trade.

## 4. The arithmetic behind "no one-week pass"

v31 sizing on a fresh $2,000 cushion, per calendar trading day:

| Year | Avg $/day | SD $/day | Green / red / flat days | Days >= +$1,000 |
|---|---|---|---|---|
| 2026 | +74 | 547 | 50 / 42 / 118 | 16 |
| 2025 | +53 | 477 | 60 / 44 / 153 | 15 |
| 2022 | +79 | 577 | 54 / 40 / 123 | 22 |

$3,000 at about $74 a day is about 40 trading days on average. Five days averages +$370 with an SD of about $1,220. Reaching +$3,000 needs a 2-sigma week (about 2%), before the 40% rule. A coin-flip one-week pass would need about $600 a day of expectancy, 8 times what the team makes. More size raises the SD, not the mean ratio, and the $2,000 trailing floor then busts accounts (FAST_PASS_2026.md).

## 5. Recommendation (exact rules)

1. Keep the v31 strategies, exits and sizing unchanged: NEWS 50/50 flat 10:30; V4+ 1.25R with BE at +1R, flat 15:00; D2 0.6 ADR, stop at the open, exit 13:15, half size against the trend; TDP 1.5R flat 15:00; Pinball 2R 180 min flat 15:00; H2 2R half size flat 15:00. $1,050 day budget, 65% of room, stop day at -$900 or 3 losers, recovery mode under $400.
2. Add the evening module (SGP + WCC, 18:00-20:00 ET) with its own $200 budget. This is the only change that never lowers the 8 / 10 / 20-day pass rate in any year.
3. Do not add filters, exit changes or A+ tilts. All 6 IS-picked filters except one failed out of sample. The one that held (H2 not before 11:05) lowers the eval pass rate in 2025 and 2022.
4. Paper-track, no money: V4+ at 1R (2025 20-day pass 29% vs 18%, but lower in 2026 and 2022). Also paper-track WCC at full $200 only on gap days of 0.64 ADR or more (hypothesis, not validated).
5. Plan for 3 to 5 weeks. The speed lever is more independent edge per day (new strategies or sessions), not reshaping the current trades.

Scripts: scripts/y2026/edge_feat.py (trade table, edge_trades.json), edge_slice.py, edge_top.py (filters), edge_exits.py (exits), edge_eval.py, edge_eval2.py (eval impact); results in the matching .json files.
