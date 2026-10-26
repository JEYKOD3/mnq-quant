# MNQ day engine: 2026 YTD backtest, old vs new rules (Oct 25 2026)

Data: MNQ RTH 1m (Databento to 2026-10-20, plus TradingView bars to 10/23), 2026-01-02 to 2026-10-23, 210 trading days. Per-year tables cover 2022-2026. Selection windows: 2026 + 2025 are primary (the closest regime twins), 2022 is the second check (big gaps and volatility), and 2023-24 are the calm-regime stress test.

Costs: 1 MNQ figures pay $2.37 per side commission plus 1 tick slippage on entries and stop exits. Engine figures use the live sizing (65% of room above the max-loss line, $1,100 shared daily budget, H2 half size, D2 half size against the daily trend) and the existing +8 pt stop slippage convention. Same-minute signals are sized in Pine script order (NEWS, V4+, D2, TDP, Pinball, H2).

## 1. Rule sets

**OLD** (live Pine v6): NEWS 50/50 flat 10:30 | V4+ 1.25R, breakeven at +1R, flat 15:55 | D2 0.5 ADR, exit 15:00 | TDP 1.5R, flat 15:55 | Pinball no target, flat 15:55 | H2 2R, 3/day, flat 15:55.

**NEW** (recommended, nothing open after 15:00):

| Strategy | Change | Exact rule |
|---|---|---|
| NEWS | none | 8:30 reversion, stop 50 / target 50 pts, flat 10:30 |
| V4+ | hard flat 15:00 | 1.25R target, stop to entry +1.25 pt at +1R, entries 9:45-13:00, flat 15:00 |
| D2 | threshold 0.6, exit 13:15 | at 10:29 close, \|close - open\| >= 0.6 ADR, market at 10:30, stop = open -/+ 1 tick, no target, flat 13:15 (see D2_EXITS_2026.md) |
| TDP | hard flat 15:00 | unchanged entry (limit at 1/3 first-hour range pullback until 12:00), stop 0.4 ADR, 1.5R target, flat 15:00 |
| Pinball | 2R target, 180 min cap, flat 15:00 | unchanged entry (break of first-hour extreme after 3-day RSI extreme, with trend), stop other side of the first hour, 2R target, exit 180 min after entry or 15:00, whichever is first |
| H2 | hard flat 15:00 | 2R target, max 3/day, half size, last entry 14:55, flat 15:00 |
| Day engine | stop-day rule | no new entries once (a) realized loss >= $950, (b) room above the max-loss line < $400, (c) 3 losing trades today, or (d) the eval is passed (target reached AND best day <= 40% of profit) |

### Priority 2: why these caps

Grid: targets x time caps (60-240 min) x hard flat 13:00 / 14:00 / 15:00 / 15:55, each variant swapped into the team (new D2, other strategies live) and scored on the 40-day pass rate (`scripts/y2026/caps.py`, `caps.json`).

| Variant | 2022 $ | 2023 $ | 2024 $ | 2025 $ | 2026 $ | 2026 hold (min) | eval 2026 | eval 2025 | eval 2022 | eval 2023-24 |
|---|---|---|---|---|---|---|---|---|---|---|
| V4+ live, flat 15:55 | 1,762 | 1,536 | 1,735 | 2,879 | 1,821 | 207 | 33% / 2% | 42% / 0% | 48% / 1% | 32% / 1% |
| **V4+ flat 15:00** | 2,067 | 1,436 | 1,696 | 2,654 | 2,578 | 179 | 34% / 0% | 39% / 0% | 49% / 0% | 31% / 1% |
| V4+ flat 14:00 | 1,507 | 1,251 | 1,239 | 2,623 | 1,321 | 148 | 26% / 0% | 32% / 0% | 42% / 0% | 30% / 2% |
| V4+ 120 min cap | 1,942 | 732 | 998 | 2,443 | 655 | 97 | 19% / 0% | 37% / 0% | 50% / 0% | 29% / 2% |
| Pinball live, flat 15:55 | 4,115 | 1,545 | -127 | 1,142 | 330 | 245 | 33% / 2% | 42% / 0% | 48% / 1% | 32% / 1% |
| **Pinball 2R, 180 min, flat 15:00** | 2,110 | 1,064 | 139 | 2,166 | 188 | 152 | 38% / 0% | 43% / 0% | 48% / 0% | 31% / 1% |
| Pinball no target, 180 min, 15:00 | 2,566 | 1,064 | 103 | 1,355 | 188 | 152 | 38% / 0% | 43% / 0% | 46% / 0% | 32% / 1% |
| Pinball 2R, flat 14:00 | 2,098 | 1,337 | 499 | 2,085 | 342 | 131 | 36% / 0% | 44% / 0% | 46% / 0% | 31% / 1% |
| TDP live, flat 15:55 | 2,080 | 962 | 1,473 | 1,920 | 1,553 | 242 | 33% / 2% | 42% / 0% | 48% / 1% | 32% / 1% |
| **TDP 1.5R, flat 15:00** | 1,751 | 690 | 1,366 | 1,966 | 1,510 | 205 | 35% / 2% | 44% / 0% | 49% / 6% | 28% / 0% |
| TDP 1.5R, flat 14:00 | 1,181 | 511 | 918 | 1,090 | 1,220 | 161 | 32% / 2% | 44% / 0% | 50% / 0% | 30% / 1% |
| TDP 180 min cap | 1,283 | 177 | 1,054 | 1,141 | 1,138 | 152 | 29% / 2% | 44% / 0% | 47% / 0% | 30% / 0% |
| H2 live, flat 15:55 | 505 | 232 | 389 | -11 | 1,247 | 68 | 33% / 2% | 42% / 0% | 48% / 1% | 32% / 1% |
| **H2 2R, flat 15:00** | 105 | 245 | 350 | 101 | 1,205 | 63 | 34% / 2% | 44% / 0% | 48% / 1% | 33% / 1% |
| H2 2R, flat 14:00 | -689 | 84 | 182 | 51 | 857 | 67 | 34% / 2% | 38% / 0% | 50% / 1% | 32% / 2% |
| H2 1.5R, 90 min, 14:00 | -323 | -124 | -19 | -150 | 520 | 39 | 40% / 2% | 44% / 0% | 50% / 1% | 31% / 2% |

Eval cells are pass within 40 days / fail, 40% consistency.

- **V4+:** 15:00 is the only earlier exit that does not hurt. 14:00 and the 2-3 hour caps cut the 2026 pass rate by 7 to 17 points, because V4+ winners often need the afternoon to reach 1.25R.
- **Pinball:** the 180 min cap plus a 15:00 flat raises the 2026 pass rate from 33% to 38% and removes the 15:55 holds. The 2R target only adds 2025 money. 2022 at 1 MNQ halves ($4,115 to $2,110), the price of leaving early.
- **TDP:** 15:00 is best on 2026 + 2025. 14:00 is the safer fallback (0% vs 6% fails in 2022, but $180 to $880 less a year at 1 MNQ).
- **H2:** the faster exits (1.5R, 90 min, 14:00) look better in the eval but lose money in 4 of 5 years at 1 MNQ, so they are rejected. Keep 2R and just flatten at 15:00.
- **The high first-hour share supports earlier exits only for D2, and only down to about 13:15.** Below that, every strategy loses edge in 2025 and 2026.

## 2. 2026 YTD brief per strategy

### OLD rules, 2026 YTD

| Strategy | Trades | Wins | Win % | PF | Net 1 MNQ | Net engine* | Avg win | Avg loss | Max DD 1 MNQ | Best day | Worst day | Longest losing streak | Avg hold | Latest exit (1m bar) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NEWS | 15 | 10 | 67% | 1.81 | 426 | 2,511 | 95 | -105 | 210 | 95 (01/09) | -105 (01/13) | 2 | 16 min | 9:40 |
| V4+ | 31 | 19 | 61% | 1.67 | 1,821 | 3,600 | 238 | -226 | 1,324 | 521 (10/16) | -609 (07/28) | 2 | 206 min | 15:55 |
| D2 | 50 | 25 | 50% | 1.21 | 1,507 | 2,513 | 342 | -281 | 1,571 | 1,347 (06/05) | -522 (04/30) | 4 | 241 min | 15:00 |
| TDP | 37 | 22 | 60% | 1.48 | 1,553 | 1,929 | 217 | -215 | 1,488 | 523 (06/30) | -463 (07/07) | 4 | 241 min | 15:55 |
| Pinball | 13 | 7 | 54% | 1.2 | 330 | 1,990 | 283 | -275 | 1,178 | 538 (03/26) | -625 (04/07) | 3 | 244 min | 15:55 |
| H2 | 23 | 13 | 56% | 2.3 | 1,247 | 1,929 | 170 | -96 | 508 | 318 (09/21) | -260 (05/07) | 4 | 67 min | 15:55 |
| TEAM | 169 | 96 | 57% | 1.43 | 6,885 | 14,472 | 240 | -221 | 2,555 | 1,725 (10/16) | -1,444 (07/28) | 10 | 191 min | 15:55 |

### NEW rules, 2026 YTD

| Strategy | Trades | Wins | Win % | PF | Net 1 MNQ | Net engine* | Avg win | Avg loss | Max DD 1 MNQ | Best day | Worst day | Longest losing streak | Avg hold | Latest exit (1m bar) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NEWS | 15 | 10 | 67% | 1.81 | 426 | 2,511 | 95 | -105 | 210 | 95 (01/09) | -105 (01/13) | 2 | 16 min | 9:40 |
| V4+ | 31 | 20 | 64% | 2.12 | 2,578 | 4,952 | 244 | -210 | 1,153 | 521 (10/16) | -609 (07/28) | 2 | 179 min | 15:00 |
| D2 | 36 | 18 | 50% | 1.73 | 2,608 | 2,567 | 342 | -197 | 985 | 1,652 (06/09) | -429 (06/25) | 4 | 162 min | 13:15 |
| TDP | 37 | 21 | 57% | 1.5 | 1,510 | 986 | 217 | -191 | 1,225 | 498 (06/30) | -463 (07/07) | 4 | 205 min | 15:00 |
| Pinball | 13 | 7 | 54% | 1.16 | 188 | 682 | 191 | -191 | 873 | 376 (03/26) | -469 (04/07) | 3 | 152 min | 15:00 |
| H2 | 22 | 13 | 59% | 2.31 | 1,205 | 5,429 | 164 | -102 | 396 | 312 (07/29) | -260 (05/07) | 2 | 63 min | 15:00 |
| TEAM | 154 | 89 | 58% | 1.74 | 8,515 | 17,129 | 225 | -177 | 2,099 | 1,652 (06/09) | -951 (07/28) | 10 | 146 min | 15:00 |

*Net engine: each day sized as on a fresh eval with $2,000 of room, all strategies sharing the $1,100 budget, +8 pt stop slippage. It shows how the sizing tilts the results (NEWS and H2 get many contracts, D2 gets about 1), not an account curve.

### Monthly net, 1 MNQ

**OLD**

| Strategy | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct |
|---|---|---|---|---|---|---|---|---|---|---|
| NEWS | -115 | 0 | 95 | 0 | -10 | 0 | 191 | 95 | 286 | -115 |
| V4+ | 0 | 146 | 303 | 213 | 440 | 458 | 186 | -310 | -335 | 720 |
| D2 | -86 | -867 | 731 | -522 | -50 | 2,093 | -1,026 | 392 | 395 | 448 |
| TDP | 66 | 61 | 912 | 413 | 458 | 1,078 | -795 | -155 | -251 | -235 |
| Pinball | 0 | 62 | 976 | -822 | -112 | 0 | 151 | -159 | 0 | 235 |
| H2 | 165 | 13 | 56 | 0 | -25 | 0 | 312 | -170 | 404 | 492 |
| TEAM | 30 | -586 | 3,074 | -719 | 702 | 3,629 | -981 | -307 | 499 | 1,544 |

**NEW**

| Strategy | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct |
|---|---|---|---|---|---|---|---|---|---|---|
| NEWS | -115 | 0 | 95 | 0 | -10 | 0 | 191 | 95 | 286 | -115 |
| V4+ | 0 | 55 | 303 | 628 | 468 | 588 | 201 | -310 | -234 | 879 |
| D2 | -136 | 312 | 387 | -427 | 298 | 2,303 | -375 | -421 | 277 | 390 |
| TDP | 4 | -30 | 829 | 296 | 372 | 1,103 | -718 | -10 | -183 | -155 |
| Pinball | 0 | -11 | 802 | -688 | -41 | 0 | 84 | -171 | 0 | 214 |
| H2 | 206 | 13 | 56 | 0 | 87 | 0 | 312 | -170 | 235 | 466 |
| TEAM | -41 | 339 | 2,472 | -191 | 1,175 | 3,994 | -305 | -986 | 380 | 1,679 |

### Per year, 1 MNQ (net $ / PF)

| Strategy | Rules | 2022 | 2023 | 2024 | 2025 | 2026 YTD |
|---|---|---|---|---|---|---|
| NEWS | OLD | 45 / 1.09 | 351 / 2.11 | 416 / 1.66 | 45 / 1.09 | 426 / 1.81 |
| NEWS | NEW | 45 / 1.09 | 351 / 2.11 | 416 / 1.66 | 45 / 1.09 | 426 / 1.81 |
| V4+ | OLD | 1,762 / 1.38 | 1,536 / 1.64 | 1,735 / 1.53 | 2,879 / 2.71 | 1,821 / 1.67 |
| V4+ | NEW | 2,067 / 1.47 | 1,436 / 1.62 | 1,696 / 1.52 | 2,654 / 2.48 | 2,578 / 2.12 |
| D2 | OLD | 2,310 / 1.82 | 1,599 / 1.9 | 924 / 1.22 | 1,508 / 1.28 | 1,507 / 1.21 |
| D2 | NEW | 1,485 / 2.0 | 549 / 1.64 | -76 / 0.97 | 44 / 1.01 | 2,608 / 1.73 |
| TDP | OLD | 2,080 / 1.62 | 962 / 1.42 | 1,473 / 1.52 | 1,920 / 1.62 | 1,553 / 1.48 |
| TDP | NEW | 1,751 / 1.58 | 690 / 1.33 | 1,366 / 1.5 | 1,966 / 1.72 | 1,510 / 1.5 |
| Pinball | OLD | 4,115 / 3.42 | 1,545 / 4.47 | -127 / 0.88 | 1,142 / 6.6 | 330 / 1.2 |
| Pinball | NEW | 2,110 / 2.57 | 1,064 / 5.11 | 139 / 1.23 | 2,166 / 15.62 | 188 / 1.16 |
| H2 | OLD | 505 / 1.22 | 232 / 1.22 | 389 / 1.4 | -11 / 0.99 | 1,247 / 2.3 |
| H2 | NEW | 105 / 1.05 | 245 / 1.26 | 350 / 1.39 | 101 / 1.12 | 1,205 / 2.31 |
| TEAM | OLD | 10,818 / 1.7 | 6,226 / 1.75 | 4,811 / 1.37 | 7,484 / 1.63 | 6,885 / 1.43 |
| TEAM | NEW | 7,564 / 1.58 | 4,335 / 1.64 | 3,891 / 1.37 | 6,976 / 1.73 | 8,515 / 1.74 |

### How each strategy did in 2026 (new rules)

- **NEWS:** Unchanged and flat by 10:30. Small, steady: 15 trades, two-thirds winners, at most 2 losses in a row this year. At engine size it is the most efficient module because its 50 pt stop allows 9 to 10 MNQ.
- **V4+:** The 2026 workhorse. The 15:00 hard exit (was 15:55) lifts 2026 from $1,821 to $2,578 at 1 MNQ. 2022 improves (+$305) and 2023-25 are within $230 of the old rule. It struggled in August and September (choppy, -$544 combined), then came back in October (+$879).
- **D2:** New rule: 0.6 ADR threshold, exit 13:15. Fewer trades (36 vs 50) and a much smaller drawdown ($985 vs $1,571). It depends on a few big trend days: June alone (+$2,303) is most of the year. It loses in choppy months (Apr, Jul, Aug). In 2024-25 it is only breakeven at 1 MNQ.
- **TDP:** Needs real trend days: strong March to June, then four losing months in a row (Jul to Oct) when trend days with clean pullbacks dried up. The 15:00 exit costs almost nothing ($1,510 vs $1,553) and keeps PF 1.5.
- **Pinball:** The weakest module in 2026 (PF 1.16, 13 trades). One great March, a bad April, nothing in June or September. Its big edge in 2022-25 came from long holds, so the 3-hour cap and 2R target cut 2022 roughly in half. Treat it as a low-weight diversifier.
- **H2:** Quietly the best 2026 risk-adjusted module (PF 2.31, drawdown $396), at half size. 2022-25 is only slightly positive, so most of the 2026 result is regime. With the 15:00 exit nothing changes except one trade.
- **TEAM:** Best months March, June and October (trend months). Worst stretch July-August, when trend-following setups lost together. NEW is better than OLD on 2026 at 1 MNQ (+$1,630, PF 1.74 vs 1.43, drawdown -$456), but gives back $500 to $3,250 a year in 2022-25.

### Optional evening modules (separate budget, 1 MNQ, 2026 YTD)

The trader trades evenings only from 18:00 to 20:00 ET, on a separate budget handled by another agent. These numbers are for reference only.

| Module | Trades | Wins | Win % | PF | Net | Avg win | Avg loss | Max DD | Best | Worst | Losing streak | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S2 sell-off evening long (18:05, stop 0.30 ADR, exit 03:30) | 26 | 12 | 46% | 1.64 | 1,656 | 353 | -184 | 1,573 | 741 | -298 | 8 | 1,163 / 1.41 | 592 / 1.64 | 306 / 1.2 | 92 / 1.03 |
| S2 cut at 20:00 (fits 18:00-20:00 window) | 26 | 16 | 62% | 2.07 | 1,105 | 133 | -103 | 574 | 394 | -251 | 2 | -684 / 0.66 | 234 / 1.6 | -44 / 0.95 | 214 / 1.13 |
| Sunday Gap Pullback (half-gap limit, stop 0.15 ADR, exit 20:00) | 18 | 9 | 50% | 2.68 | 1,252 | 222 | -83 | 275 | 372 | -127 | 3 | 283 / 2.63 | -36 / 0.79 | 318 / 2.73 | -54 / 0.91 |

| Module | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct |
|---|---|---|---|---|---|---|---|---|---|---|
| S2 sell-off evening long | 446 | -864 | -676 | 201 | -234 | 2,353 | 846 | -257 | -377 | 218 |
| S2 cut at 20:00 | 92 | -399 | 11 | 49 | -234 | 966 | 424 | -57 | 4 | 249 |
| Sunday Gap Pullback | 30 | 274 | 224 | 0 | 271 | 514 | -3 | 131 | -81 | -108 |

- **S2 as specified (exit 03:30):** good 2026 (PF 1.64), but all of it comes from June and July, and it had 8 losers in a row. It holds outside the 18:00-20:00 window the trader accepts.
- **S2 cut at 20:00:** fits the window and looks clean in 2026 (PF 2.07, drawdown $574). It loses in 2022 and 2024, so most of the 2026 result is regime. Paper only.
- **Sunday Gap Pullback:** 18 trades, PF 2.68, drawdown $275. It is the best evening candidate for 2026, but slightly negative in 2023 and 2025. Small size, paper first.

## 3. Stop-day rule test (team eval, 40% consistency)

| Rules | Stop-day | 2026 | 2025 | 2022 | 2023-24 | net 2026 engine | net 2025 engine |
|---|---|---|---|---|---|---|---|
| OLD | off | 37% / 0.5% / 29d | 36% / 0.0% / 23d | 42% / 0.9% / 18d | 30% / 3.9% / 19d | 14,472 | 17,111 |
| OLD | a,b,d only | 41% / 0.0% / 23d | 34% / 0.0% / 22d | 42% / 0.0% / 18d | 27% / 0.8% / 15d | 14,472 | 17,111 |
| OLD | N=1 | 41% / 0.0% / 23d | 34% / 0.0% / 22d | 42% / 0.0% / 18d | 28% / 0.8% / 15d | 14,602 | 17,111 |
| OLD | N=2 | 41% / 0.0% / 23d | 34% / 0.0% / 22d | 42% / 0.0% / 18d | 27% / 0.8% / 15d | 14,472 | 17,111 |
| OLD | N=3 | 41% / 0.0% / 23d | 34% / 0.0% / 22d | 42% / 0.0% / 18d | 27% / 0.8% / 15d | 14,472 | 17,111 |
| OLD | N=4 | 41% / 0.0% / 23d | 34% / 0.0% / 22d | 42% / 0.0% / 18d | 27% / 0.8% / 15d | 14,472 | 17,111 |
| OLD | N=3 naive (d) | 24% / 0.0% / 19d | 28% / 0.0% / 22d | 21% / 0.0% / 12d | 17% / 0.8% / 12d | 14,472 | 17,111 |
| NEW | off | 38% / 0.0% / 28d | 43% / 0.0% / 22d | 48% / 0.0% / 20d | 31% / 1.2% / 19d | 17,129 | 15,504 |
| NEW | a,b,d only | 43% / 0.0% / 20d | 48% / 0.0% / 22d | 48% / 0.0% / 18d | 29% / 0.4% / 15d | 17,129 | 15,504 |
| NEW | N=1 | 45% / 0.0% / 20d | 48% / 0.0% / 22d | 48% / 0.0% / 18d | 28% / 0.4% / 15d | 16,764 | 15,167 |
| NEW | N=2 | 43% / 0.0% / 20d | 48% / 0.0% / 22d | 48% / 0.0% / 18d | 29% / 0.4% / 15d | 17,129 | 15,504 |
| NEW | N=3 | 43% / 0.0% / 20d | 48% / 0.0% / 22d | 48% / 0.0% / 18d | 29% / 0.4% / 15d | 17,129 | 15,504 |
| NEW | N=4 | 43% / 0.0% / 20d | 48% / 0.0% / 22d | 48% / 0.0% / 18d | 29% / 0.4% / 15d | 17,129 | 15,504 |
| NEW | N=3 naive (d) | 34% / 0.0% / 20d | 37% / 0.0% / 21d | 34% / 0.0% / 16d | 18% / 0.4% / 14d | 17,129 | 15,504 |

Cells: pass within 40 days / fail / median days to pass.

- **Rule (c) (N losing trades) never binds for N = 2, 3 or 4.** In 2022-2026 only 2 entries came after 2 closed losses, and the $1,100 budget had already sized both at 0. Rules (a) and (b) are also covered by the budget. N = 1 changes little (+2 points in 2026, -1 in 2023-24).
- **Rule (d) does the work.** Stopping new entries once the eval is passed protects the passing day: +4 to +6 points of pass rate in 2026 and 2025.
- **(d) must mean "passed", not "target reached".** With the 40% consistency rule, "stop at $3,000" freezes accounts that are over target but not yet consistent ("naive (d)" rows: -9 to -17 points).
- **Recommendation:** keep N = 3 as a harmless safety net, and code (d) as "target reached and best day <= 40% of total profit".

## 4. Prop-firm validation, 2026 only

Lucid Flex 50K: $3,000 target, $2,000 end-of-day trailing max loss, mll = min(peakEOD - 2000, 50,100), 40% consistency (50% shown for reference), flat by 16:45 (the engine is flat by 15:00).

### (i) Rolling start every 2026 trading day (210 starts, run until data end)

| Rules | Consistency | Stop-day | Pass <= 40d | Pass by data end | Fail | Still open | Median days to pass | Worst DD from start | Median worst DD | Runs blocked by consistency | Extra days needed (median / max) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OLD | 40% | off | 37% | 51% | 0.5% | 49% | 31 | -2,001 | -560 | 108 (72% of runs that hit $3,000) | 10.0 / 65 |
| OLD | 40% | N=3 | 41% | 44% | 0.0% | 56% | 23 | -1,880 | -527 | 73 (58% of runs that hit $3,000) | 1 / 65 |
| OLD | 50% | off | 43% | 60% | 0.5% | 39% | 26 | -2,001 | -560 | 72 (48% of runs that hit $3,000) | 6.0 / 50 |
| OLD | 50% | N=3 | 45% | 51% | 0.0% | 49% | 22.0 | -1,880 | -527 | 50 (40% of runs that hit $3,000) | 16.0 / 50 |
| NEW | 40% | off | 38% | 53% | 1.9% | 45% | 30 | -1,999 | -183 | 100 (68% of runs that hit $3,000) | 5 / 86 |
| NEW | 40% | N=3 | 43% | 46% | 0.0% | 54% | 20 | -1,827 | -183 | 45 (38% of runs that hit $3,000) | 4.0 / 48 |
| NEW | 50% | off | 43% | 55% | 1.9% | 43% | 26 | -1,999 | -183 | 61 (42% of runs that hit $3,000) | 2.0 / 13 |
| NEW | 50% | N=3 | 47% | 49% | 0.0% | 51% | 20 | -1,827 | -183 | 31 (26% of runs that hit $3,000) | 2.0 / 40 |

- **Still open** is high because starts after August have little data left, and some runs sit over target waiting for consistency. Of the runs that ended, NEW passed 100% with the stop-day rule on.
- **Consistency is the main brake.** Without the stop-day rule, 69-72% of runs that reach $3,000 are blocked by one big day, and need a median 5 (NEW) to 10 (OLD) extra trading days. The stop-day rule's pass check cuts that to 38% of runs for NEW.

### (ii) Monte Carlo: 10,000 bootstrapped 40-day evals from 2026 trading days

| Rules | Consistency | Stop-day | Pass | Fail | Open after 40 days | Median days to pass |
|---|---|---|---|---|---|---|
| OLD | 40% | off | 30% | 0.4% | 69% | 21.0 |
| OLD | 40% | N=3 | 31% | 0.1% | 69% | 20 |
| OLD | 50% | off | 38% | 0.4% | 62% | 19 |
| OLD | 50% | N=3 | 37% | 0.1% | 63% | 18 |
| NEW | 40% | off | 37% | 0.3% | 63% | 21 |
| NEW | 40% | N=3 | 38% | 0.0% | 62% | 20.0 |
| NEW | 50% | off | 44% | 0.3% | 56% | 19 |
| NEW | 50% | N=3 | 43% | 0.0% | 57% | 18.0 |

### (iii) Stress (rolling 2026, 40% consistency, stop-day N=3)

| Scenario | OLD pass <= 40d | OLD fail | NEW pass <= 40d | NEW fail | NEW median days |
|---|---|---|---|---|---|
| Base (+8 pt stop slip, $4.74 RT) | 41% | 0.0% | 43% | 0.0% | 20 |
| +1 pt per side (entries and stop exits) | 39% | 0.0% | 43% | 0.0% | 20 |
| +2 pt per side | 37% | 0.0% | 44% | 0.0% | 20.5 |
| +4 pt per side | 34% | 0.0% | 37% | 0.0% | 24.0 |
| Only 1 tick slippage (no +8 pt) | 45% | 0.0% | 44% | 0.0% | 24 |
| Commission $1.00 RT | 43% | 0.0% | 45% | 0.0% | 21 |
| Skip 20% of signals at random (100 runs: mean, 5th pct) | 32% (19%) | 0.0% | 35% (20%) | 0.0% | 25.0 |

- **Extra slippage up to +2 pts barely moves the pass rate.** Cells move by a point or two either way, because smaller winning days also help the consistency rule. +4 pts costs 6 to 7 points for both rule sets.
- **Missing 20% of trades costs about 8-9 points of pass rate.** A bad draw drops it to 20%, but fails stay at 0%.
- **No stress scenario produced a failed eval with the stop-day rule on.** The budget and the 65% sizing keep the worst drawdown from start above -$1,970.

### (iv) Funded phase after the pass (stop-day N=3)

Lucid Flex funded: 5 days of >= $150 profit per cycle plus positive profit, then request min(50% of profit, $2,000), minimum $500, 90% to the trader. A request moves the floor to $50,100 at once. Policy A requests as soon as allowed. Policy B waits until $1,100 of room would remain above $50,100 after the request.

| Rules | Policy | Sample | Got >= 1 payout | Median days to 1st payout | Payouts per account | Avg paid to trader | Median payout | Bust |
|---|---|---|---|---|---|---|---|---|
| OLD | A | Monte Carlo, 120 days (n 3000) | 55% | 18.0 | 1.27 | $1,758 | $1,737 | 0.1% |
| OLD | A | chained from 2026 passes (truncated at data end) (n 93) | 19% | 19.0 | 0.34 | $382 | $1,387 | 0.0% |
| OLD | B | Monte Carlo, 120 days (n 3000) | 47% | 19.0 | 1.24 | $1,962 | $1,974 | 0.1% |
| OLD | B | chained from 2026 passes (truncated at data end) (n 93) | 19% | 19.0 | 0.34 | $536 | $1,995 | 0.0% |
| NEW | A | Monte Carlo, 120 days (n 3000) | 59% | 18 | 1.56 | $2,253 | $1,977 | 0.0% |
| NEW | A | chained from 2026 passes (truncated at data end) (n 97) | 38% | 25 | 0.52 | $640 | $1,480 | 0.0% |
| NEW | B | Monte Carlo, 120 days (n 3000) | 53% | 19 | 1.55 | $2,516 | $2,000 | 0.0% |
| NEW | B | chained from 2026 passes (truncated at data end) (n 97) | 22% | 20 | 0.35 | $530 | $1,618 | 0.0% |

- **The real constraint in funded is the 50% / $2,000 cap.** The first request usually comes 18-19 trading days after funding. Payouts run $1,500-2,000, about 1.5 payouts per 120 days with the new rules.
- **Policy B** pays less often but in bigger amounts, about the same money (+$260 over 120 days with NEW). Its value is the cushion after the floor jumps to $50,100. Both policies had essentially 0% busts in the 2026 bootstrap.

## 5. Verdict

- **On 2026 the new rules are better at 1 MNQ** (+$1,630, PF 1.74 vs 1.43, max drawdown $2,099 vs $2,555). With the stop-day rule they are also better in the 2026 eval: 43% vs 41% pass within 40 days, median 20 vs 23 days, 0% fails.
- **On 2025 and 2022 the new rules pass more often** (48% vs 34% and 48% vs 42% with the stop-day rule). 2023-24 is level (29% vs 27%).
- **The cost of leaving early is lower 1 MNQ profit in older years:** 2022 -$3,250, 2023 -$1,900, 2024 -$900, 2025 -$500. Most of it is D2 and Pinball giving up the afternoon drift. That is the price of no afternoon holds.
- **The stop-day rule matters only through (d).** Code it as "passed" (target and 40% consistency both met), not "target reached".
- **Biggest risks:** small 2026 samples (Pinball 13 trades, D2 36), and July-August-style chop, when V4+, TDP and D2 lose together. A 20% miss rate on signals costs about 8 points of pass rate.

Scripts: `scripts/y2026/common.py` (engine), `rulesets.py`, `d2_grid.py`, `d2_team.py`, `d2_exit_time.py`, `d2_scan2.py`, `d2_final.py`, `caps.py`, `report.py`, `gen_md.py`. Data for charts: `knowledge/src/y2026_summary.json`.
