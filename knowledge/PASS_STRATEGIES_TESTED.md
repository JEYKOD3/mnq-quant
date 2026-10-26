# Online "eval pass" strategies + friend's mother candle, tested (Oct 26 2026)

Source rules: knowledge/PASS_STRATEGIES_CATALOG.md shortlist SL1-SL6, catalog S4 (trend-filtered ORB), and the friend's mother-candle breakout (RULES E27) as clarified by the user: fixed 1R target, exit at target, stop trading the setup for the day after a win (also tested: whole day stops after its first win). Scripts: scripts/y2026/pass_tested.py (scan), pass_eval.py (Lucid sim). Results: pass_scan.json, pass_eval.json, pass_trades.json.

## Method
- Data: MNQ RTH 1m 2022-01 to 2026-10-23; ETH 5m (overnight, pre-open); 5m continuous with volume (VWAP, EMA200, 15m/1h/4h EMA21 bias, no lookahead). There is NO 1m data before 9:30, so the pre-open mother candle (what the user saw on Oct 22 at 9:16-9:25) is tested on 5m bars.
- Costs: $2.37/side, 1 tick entry slip, 1 tick stop slip, $2/pt. Extra column with +8 pt on stop exits (engine convention).
- Protocol: rules as written first, then at most 2 tuned params per setup on 2022-24 (IS), checked on 2025 (VAL) and 2026 YTD. Survivor = net > 0 in all three blocks and n_IS >= 60. 68 variants tried in total, so 2-3 false survivors are expected by chance.

## Result in one line
Nothing tested has a real edge after costs. One cell (friend's 5m box, 9:30-10:30, 2R, HTF majority bias) is positive in all 3 blocks, but it is ~45 trades/yr, PF 0.69 in 2022 and 0.92 in 2023 (the IS block is carried by 2024 at PF 2.26), avg R about 0, and below PF 1 with +8 pt stop slip in 2026. Treat it as luck.

## Headline: friend's mother candle, user's version (1R target, stop the setup after a win)
| Variant | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| 1m box, 9:30-10:30, 1R, stop after win (n / WR / PF) | 415 / 49% / 0.83 | 413 / 47% / 0.71 | 380 / 53% / 1.07 | 402 / 48% / 0.79 | 316 / 50% / 0.95 |

It wins about 50% at 1R, which is break-even before costs. Average stop is 38-68 pts, so commission + slippage take about 0.05-0.1R per trade and it loses money in 4 of 5 years. Bias filters (HTF 2-of-3 majority, or 9:30 open: longs only above the open) do not fix it; see table. 2R is worse on 1m.

## All variants
| Variant | IS 2022-24 n / WR / PF / avgR | 2025 n / WR / PF / avgR | 2026 n / WR / PF / avgR | PF with +8 pt stop slip (IS/25/26) | All 3 > 0 |
|---|---|---|---|---|---|
| SL1 as written (.5W, .8%, cap50) | 689 / 59% / 0.97 / -0.02 | 227 / 56% / 1.02 / +0.01 | 186 / 44% / 0.88 / -0.07 | 0.84 / 0.89 / 0.76 | no |
| SL1 tgt .33W | 689 / 68% / 0.9 / -0.04 | 227 / 68% / 1.12 / +0.04 | 186 / 53% / 0.82 / -0.08 | 0.78 / 0.97 / 0.71 | no |
| SL1 tgt .75W | 689 / 49% / 0.99 / -0.01 | 227 / 47% / 1.07 / +0.04 | 186 / 33% / 0.83 / -0.11 | 0.86 / 0.93 / 0.72 | no |
| SL1 tgt 1.0W | 689 / 43% / 1.01 / +0.00 | 227 / 41% / 1.11 / +0.06 | 186 / 25% / 0.72 / -0.21 | 0.88 / 0.96 / 0.62 | no |
| SL1 W<.5% | 504 / 61% / 0.88 / -0.05 | 171 / 60% / 1.01 / +0.00 | 110 / 48% / 0.82 / -0.09 | 0.76 / 0.88 / 0.71 | no |
| SL1 W<1.0% | 728 / 56% / 0.92 / -0.04 | 240 / 55% / 1.03 / +0.01 | 196 / 43% / 0.91 / -0.05 | 0.79 / 0.9 / 0.79 | no |
| SL1 cap30 | 689 / 49% / 0.96 / -0.02 | 227 / 43% / 0.99 / -0.01 | 186 / 28% / 0.75 / -0.18 | 0.77 / 0.79 / 0.6 | no |
| SL1 cap75 | 689 / 65% / 0.99 / -0.01 | 227 / 64% / 1.07 / +0.02 | 186 / 54% / 0.92 / -0.04 | 0.89 / 0.96 / 0.83 | no |
| SL2 as written (PDH else 2R) | 222 / 35% / 1.03 / +0.01 | 69 / 39% / 1.05 / +0.05 | 56 / 28% / 0.69 / -0.28 | 0.83 / 0.89 / 0.61 | no |
| SL2 tgt 1R | 222 / 52% / 0.9 / -0.06 | 69 / 59% / 1.17 / +0.10 | 56 / 45% / 0.75 / -0.14 | 0.72 / 1.0 / 0.67 | no |
| SL2 tgt 2R | 222 / 36% / 0.91 / -0.05 | 69 / 39% / 1.02 / -0.00 | 56 / 28% / 0.69 / -0.28 | 0.73 / 0.86 / 0.61 | no |
| SL2 retrace .33 | 189 / 22% / 0.6 / -0.30 | 58 / 31% / 0.91 / -0.02 | 50 / 28% / 0.72 / -0.20 | 0.44 / 0.72 / 0.61 | no |
| SL2 retrace .15 | 270 / 39% / 1.14 / +0.01 | 85 / 40% / 1.28 / +0.11 | 64 / 30% / 0.57 / -0.26 | 0.97 / 1.13 / 0.52 | no |
| SL3 as written (opp side) | 533 / 16% / 0.79 / -0.22 | 157 / 15% / 0.89 / -0.15 | 120 / 9% / 0.63 / -0.47 | 0.55 / 0.63 / 0.46 | no |
| SL3 tgt mid | 493 / 25% / 0.85 / -0.16 | 152 / 24% / 0.95 / -0.03 | 118 / 16% / 0.59 / -0.42 | 0.58 / 0.67 / 0.43 | no |
| SL3 tgt 2R | 534 / 30% / 0.71 / -0.26 | 157 / 35% / 0.85 / -0.12 | 120 / 31% / 0.79 / -0.19 | 0.49 / 0.61 / 0.59 | no |
| SL3 rmax 25 | 434 / 14% / 0.68 / -0.28 | 121 / 12% / 0.8 / -0.23 | 76 / 5% / 0.39 / -0.67 | 0.45 / 0.53 / 0.26 | no |
| SL4 as written (opp side) | 408 / 25% / 0.8 / -0.21 | 139 / 20% / 0.86 / -0.02 | 76 / 13% / 0.64 / -0.43 | 0.54 / 0.62 / 0.47 | no |
| SL4 tgt mid | 290 / 31% / 0.75 / -0.24 | 109 / 26% / 0.76 / -0.14 | 71 / 24% / 0.72 / -0.19 | 0.48 / 0.53 / 0.53 | no |
| SL4 tgt 2R | 441 / 32% / 0.79 / -0.21 | 142 / 27% / 0.67 / -0.30 | 77 / 35% / 0.77 / -0.11 | 0.55 / 0.48 / 0.58 | no |
| SL4 rmax 25 | 339 / 22% / 0.81 / -0.24 | 102 / 19% / 0.89 / +0.04 | 52 / 8% / 0.33 / -0.65 | 0.51 / 0.59 / 0.23 | no |
| SL5 as written (10 pt leg, cap25) | 1197 / 31% / 0.57 / -0.30 | 388 / 38% / 0.73 / -0.22 | 299 / 28% / 0.66 / -0.28 | 0.35 / 0.45 / 0.42 | no |
| SL5 leg 20 | 751 / 26% / 0.64 / -0.28 | 253 / 28% / 0.7 / -0.28 | 218 / 27% / 0.73 / -0.24 | 0.39 / 0.44 / 0.47 | no |
| SL5 cap 15 | 926 / 26% / 0.53 / -0.35 | 286 / 33% / 0.63 / -0.28 | 222 / 25% / 0.55 / -0.37 | 0.3 / 0.36 / 0.32 | no |
| SL5 all RTH hours | 1680 / 32% / 0.6 / -0.29 | 546 / 38% / 0.69 / -0.25 | 449 / 31% / 0.64 / -0.29 | 0.36 / 0.42 / 0.4 | no |
| SL6 as written (15/15, BE+8) | 660 / 36% / 0.66 / -0.14 | 227 / 39% / 0.69 / -0.13 | 193 / 44% / 0.73 / -0.12 | 0.38 / 0.41 / 0.46 | no |
| SL6 BE+5 | 653 / 30% / 0.63 / -0.13 | 223 / 38% / 0.79 / -0.07 | 191 / 42% / 0.74 / -0.11 | 0.33 / 0.44 / 0.45 | no |
| SL6 BE+10 | 667 / 41% / 0.68 / -0.14 | 229 / 42% / 0.7 / -0.13 | 195 / 46% / 0.72 / -0.13 | 0.42 / 0.44 / 0.47 | no |
| SL6 no BE | 688 / 50% / 0.73 / -0.14 | 237 / 49% / 0.7 / -0.15 | 197 / 51% / 0.75 / -0.12 | 0.5 / 0.48 / 0.52 | no |
| SL6 gap>=4 | 546 / 36% / 0.63 / -0.15 | 188 / 39% / 0.65 / -0.15 | 173 / 44% / 0.71 / -0.13 | 0.37 / 0.4 / 0.45 | no |
| SL6 20/20 | 646 / 33% / 0.74 / -0.09 | 219 / 33% / 0.72 / -0.10 | 190 / 41% / 0.82 / -0.07 | 0.44 / 0.43 / 0.53 | no |
| MC 1m 9:30-10:30 1R | 773 / 49% / 0.86 / -0.09 | 257 / 47% / 0.76 / -0.11 | 210 / 50% / 0.91 / -0.04 | 0.72 / 0.66 / 0.82 | no |
| MC 1m 9:30-10:30 2R | 773 / 35% / 0.96 / -0.05 | 257 / 35% / 0.88 / -0.04 | 210 / 31% / 0.81 / -0.14 | 0.81 / 0.77 / 0.73 | no |
| MC 1m 9:30-10:30 1R HTF bias | 401 / 48% / 0.78 / -0.12 | 130 / 46% / 0.76 / -0.13 | 118 / 53% / 1.07 / +0.02 | 0.65 / 0.66 / 0.96 | no |
| MC 1m 9:30-10:30 2R HTF bias | 401 / 33% / 0.9 / -0.07 | 130 / 32% / 0.89 / -0.11 | 118 / 31% / 0.9 / -0.14 | 0.75 / 0.77 / 0.8 | no |
| MC 1m 9:30-9:45 1R HTF bias | 143 / 55% / 0.99 / +0.03 | 54 / 44% / 0.67 / -0.16 | 46 / 61% / 1.38 / +0.17 | 0.84 / 0.6 / 1.25 | no |
| MC 5m pre-open 9:00-9:30 1R | 371 / 47% / 0.77 / -0.14 | 123 / 46% / 0.72 / -0.15 | 96 / 53% / 0.89 / +0.00 | 0.64 / 0.61 / 0.78 | no |
| MC 5m pre-open 2R | 371 / 34% / 0.92 / -0.08 | 123 / 28% / 0.66 / -0.21 | 96 / 27% / 0.62 / -0.23 | 0.77 / 0.56 / 0.54 | no |
| MC 5m pre-open 1R HTF bias | 114 / 49% / 0.64 / -0.10 | 44 / 45% / 1.02 / -0.16 | 32 / 38% / 0.5 / -0.28 | 0.54 / 0.86 / 0.44 | no |
| MC 5m pre-open 2R HTF bias | 114 / 36% / 0.73 / -0.02 | 44 / 25% / 0.65 / -0.36 | 32 / 12% / 0.31 / -0.64 | 0.62 / 0.56 / 0.27 | no |
| MC 5m 9:30-10:30 1R HTF bias | 133 / 49% / 0.87 / -0.07 | 47 / 49% / 1.03 / -0.05 | 36 / 44% / 0.83 / -0.14 | 0.79 / 0.96 / 0.78 | no |
| MC 5m 9:30-10:30 2R HTF bias | 133 / 43% / 1.1 / +0.04 | 47 / 43% / 1.13 / +0.00 | 36 / 44% / 1.05 / -0.03 | 1.0 / 1.06 / 0.98 | yes |
| MC 1m 9:30-10:30 1R close-trigger | 774 / 46% / 0.71 / -0.15 | 257 / 50% / 0.79 / -0.07 | 210 / 44% / 0.68 / -0.16 | 0.59 / 0.68 / 0.61 | no |
| MC 1m 9:30-10:30 1R close-trigger HTF bias | 434 / 50% / 0.85 / -0.09 | 142 / 49% / 0.85 / -0.10 | 125 / 50% / 0.85 / -0.06 | 0.69 / 0.71 / 0.75 | no |
| MC 5m pre-open 1R close-trigger | 478 / 45% / 0.73 / -0.18 | 160 / 51% / 0.85 / -0.06 | 125 / 50% / 0.82 / -0.05 | 0.58 / 0.72 / 0.71 | no |
| MC 5m 9:30-10:30 1R close-trigger HTF bias | 152 / 50% / 0.97 / -0.04 | 52 / 46% / 0.77 / -0.08 | 40 / 53% / 1.0 / +0.01 | 0.87 / 0.71 / 0.93 | no |
| MC 5m 9:30-10:30 1R | 438 / 49% / 0.89 / -0.06 | 139 / 47% / 0.74 / -0.05 | 96 / 43% / 0.69 / -0.16 | 0.81 / 0.69 / 0.65 | no |
| MCW 1m 9:30-10:30 1R stop-after-win | 1208 / 50% / 0.86 / -0.09 | 402 / 48% / 0.79 / -0.10 | 316 / 50% / 0.95 / -0.04 | 0.72 / 0.69 / 0.85 | no |
| MCW 1m 9:30-10:30 1R stop-after-win HTF bias | 468 / 49% / 0.84 / -0.09 | 160 / 44% / 0.74 / -0.18 | 141 / 50% / 0.95 / -0.04 | 0.7 / 0.63 / 0.84 | no |
| MCW 1m 9:30-11:30 1R stop-after-win | 1421 / 50% / 0.87 / -0.08 | 479 / 48% / 0.79 / -0.11 | 383 / 51% / 0.96 / -0.03 | 0.72 / 0.68 / 0.85 | no |
| MCW 1m 9:30-11:30 1R stop-after-win HTF bias | 748 / 48% / 0.77 / -0.13 | 249 / 46% / 0.76 / -0.15 | 212 / 50% / 0.94 / -0.04 | 0.62 / 0.65 / 0.82 | no |
| MCW 1m 9:30-10:30 2R stop-after-win (cmp) | 1272 / 34% / 0.94 / -0.06 | 418 / 33% / 0.83 / -0.09 | 330 / 32% / 0.88 / -0.11 | 0.78 / 0.71 / 0.78 | no |
| MCW 5m pre-open 1R stop-after-win | 371 / 47% / 0.77 / -0.14 | 123 / 46% / 0.72 / -0.15 | 96 / 53% / 0.89 / +0.00 | 0.64 / 0.61 / 0.78 | no |
| MCW 5m pre-open 1R stop-after-win HTF bias | 114 / 49% / 0.64 / -0.10 | 44 / 45% / 1.02 / -0.16 | 32 / 38% / 0.5 / -0.28 | 0.54 / 0.86 / 0.44 | no |
| MCW 5m 9:30-10:30 1R stop-after-win | 441 / 49% / 0.88 / -0.06 | 139 / 47% / 0.74 / -0.05 | 96 / 43% / 0.69 / -0.16 | 0.8 / 0.69 / 0.65 | no |
| MCW 5m 9:30-10:30 1R stop-after-win HTF bias | 133 / 49% / 0.87 / -0.07 | 47 / 49% / 1.03 / -0.05 | 36 / 44% / 0.83 / -0.14 | 0.79 / 0.96 / 0.78 | no |
| MCW 5m 9:30-10:30 2R stop-after-win HTF bias (cmp) | 133 / 43% / 1.1 / +0.04 | 47 / 43% / 1.13 / +0.00 | 36 / 44% / 1.05 / -0.03 | 1.0 / 1.06 / 0.98 | yes |
| MCW 1m 9:30-10:30 1R stop-after-win OPEN bias | 1091 / 49% / 0.84 / -0.09 | 367 / 49% / 0.85 / -0.08 | 292 / 49% / 0.87 / -0.07 | 0.71 / 0.74 / 0.78 | no |
| MCW 1m 9:30-11:30 1R stop-after-win OPEN bias | 1375 / 50% / 0.85 / -0.09 | 454 / 50% / 0.91 / -0.06 | 381 / 48% / 0.82 / -0.09 | 0.71 / 0.79 / 0.74 | no |
| MCW 1m 9:30-10:30 2R stop-after-win OPEN bias (cmp) | 1127 / 35% / 0.95 / -0.05 | 374 / 34% / 0.88 / -0.07 | 301 / 34% / 0.89 / -0.07 | 0.8 / 0.76 / 0.8 | no |
| MCW 5m 9:30-10:30 1R stop-after-win OPEN bias | 385 / 50% / 0.94 / -0.04 | 124 / 52% / 0.84 / +0.04 | 80 / 44% / 0.74 / -0.14 | 0.86 / 0.8 / 0.7 | no |
| MCW 5m 9:30-10:30 2R stop-after-win OPEN bias (cmp) | 385 / 44% / 1.18 / +0.08 | 124 / 44% / 0.88 / +0.05 | 80 / 38% / 0.77 / -0.14 | 1.08 / 0.82 / 0.72 | no |
| S4 trend ORB15 2R SMA200 | 469 / 37% / 1.02 / +0.01 | 186 / 33% / 0.88 / -0.08 | 164 / 27% / 0.68 / -0.23 | 0.85 / 0.73 / 0.57 | no |
| S4 ORB15 1.5R | 469 / 44% / 1.06 / +0.03 | 186 / 40% / 0.89 / -0.07 | 164 / 33% / 0.66 / -0.23 | 0.88 / 0.74 / 0.55 | no |
| S4 ORB15 3R | 469 / 32% / 1.06 / +0.04 | 186 / 25% / 0.74 / -0.19 | 164 / 20% / 0.65 / -0.28 | 0.88 / 0.62 / 0.54 | no |
| S4 ORB30 2R | 416 / 36% / 0.95 / -0.03 | 172 / 32% / 0.8 / -0.13 | 145 / 28% / 0.72 / -0.20 | 0.8 / 0.67 / 0.6 | no |
| S4 ORB15 2R SMA150 | 508 / 36% / 0.95 / -0.04 | 185 / 34% / 0.89 / -0.07 | 158 / 28% / 0.7 / -0.22 | 0.79 / 0.74 / 0.58 | no |
| S4 ORB15 2R cap50 | 469 / 40% / 1.12 / +0.06 | 186 / 36% / 0.95 / -0.03 | 164 / 30% / 0.79 / -0.15 | 0.97 / 0.82 / 0.69 | no |

## Lucid Flex 50K eval sim (same rules/sizing as FAST_PASS_2026.md; rolling starts; pass within N trading days)
| Plan | 2026 p5 / p8 / p10 / p20 | 2025 p5 / p8 / p10 / p20 | 2022 p5 / p8 / p10 / p20 | Bust |
|---|---|---|---|---|
| v31 + evening (reference) | 0.5 / 4.4 / 7.3 / 24.3% | 0 / 2.7 / 4.7 / 26.5% | 3.2 / 9.7 / 13.8 / 32.7% | 0% |
| MC 5m 2R HTF (survivor) alone | 0 / 0.5 / 1.5 / 2.4% | 0 / 0 / 0 / 0% | 0 / 0 / 0 / 0% | 0% |
| v31 + evening + MC 5m 2R HTF | 1.9 / 3.9 / 6.3 / 12.6% | 0.8 / 3.5 / 5.1 / 15.6% | 1.8 / 4.6 / 8.8 / 16.1% | 0% |
| same, whole day stops after its first win | identical | identical | identical | 0% |
| MC 1m 1R stop-after-win alone | 5.3 / 9.2 / 11.2 / 14.1% | 1.9 / 3.1 / 3.9 / 3.9% | 3.2 / 5.1 / 6.0 / 6.0% | 0% |
| v31 + evening + MC 1m 1R | 4.9 / 7.8 / 11.2 / 13.6% | 2.3 / 5.1 / 6.6 / 7.4% | 2.8 / 4.6 / 4.6 / 5.1% | 0% |
| v31 + evening + MC 1m 1R, whole day stops after its first win | 4.9 / 9.7 / 12.6 / 17.5% | 1.9 / 4.3 / 5.8 / 5.8% | 3.2 / 5.1 / 6.0 / 6.5% | 0% |

Reading: the 1m 1R version adds lots of coin-flip trades. In 2026 that variance produces a few more quick passes (5-day pass ~5% vs 0.5%), but the negative edge then drags most evals into the 1-contract recovery floor, so the 20-day pass rate falls to 14-18% (2026) and 4-7% (2025, 2022) vs 24-33% for the reference. No bust because of the room guard, but most evals stall. The 5m 2R survivor also lowers the 20-day pass rate (it takes budget and room from the team).

## Takeaways
1. None of the shortlisted online "pass" strategies (ORB 50% target, IB retrace, 9:00-hour sweep, Asia sweep London reversal, hourly sweep to hour open, VWAP/EMA200 FVG 15/15) is positive after costs; most are PF 0.6-0.95 in every block. The high win-rate claims (60-70%) come with targets smaller than the stop, and costs flip them negative.
2. The trend-filtered ORB (S4, claimed OOS PF 1.32) is PF 1.02-1.12 on 2022-24 here but 0.79-0.95 on 2025 and 0.65-0.79 on 2026.
3. The friend's mother candle at 1R is a ~50% coin flip; costs make it lose. Seeing one clean winner live (Oct 22 pre-open) is consistent with a 50% setup.
4. Recommendation unchanged: keep v31 + evening module; do not add any of these. Fast passes in the sim come only from variance, at the cost of a much lower overall pass rate.
