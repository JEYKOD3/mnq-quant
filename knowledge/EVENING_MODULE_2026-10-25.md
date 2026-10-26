# MNQ Evening Module, 18:00-20:00 ET (Oct 25, 2026)

**The constraint:** the trader can only trade 18:00-20:00 ET on Sunday to Thursday evenings, and not every evening. The evening module has its own budget, separate from the day engine, and is flat by 20:00. Trades are manual at the session open.

**Bottom line:**
- Two rules hold up: the **Sunday Gap Pullback (SGP)** and a new one, the **Wednesday Close Continuation (WCC)**.
- Everything else fails in-sample, out-of-sample, or against its shifted-window baseline. That includes the truncated S2 sell-off long, weeknight gap pullbacks, opening-range sweeps, fades of the 18:00 open, the Tokyo-open range and post-earnings fades.
- WCC is the strongest result in this study: PF 2.61 IS, 2.24 OOS, 2.00 in 2026, every year positive. It is still a day-of-week cell found inside a broader effect, with no proven mechanism, so it is sized small.

## Setup

- **Data:** `data/raw/mnq_eth_5m.txt`, 5m ETH bars from 2022-01 to 2026-10-20. Each session is keyed by the date it ends, so the evening of calendar day X (Sun-Thu) is the key of the next trading day. The prior RTH is the previous key (Friday for Sunday evenings).
- **Evening filter:** an evening counts only when the full 18:00-20:00 bars and a full prior RTH exist. The evening after a holiday or half day is skipped. That leaves 1,186 evenings: Sun 235, Mon 223, Tue 247, Wed 244, Thu 237.
- **ADR:** the mean of the prior 10 RTH (9:30-16:00) ranges, known before the session opens (`scripts/sessions/common.py`).
- **Costs per trade (1 MNQ):** 2 x $2.37 commission plus 1 tick of slippage per side (0.5 pt round turn). $2 per point.
- **Fills:**
  - Market entries fill at the bar open.
  - Limits fill only if price trades 1 tick through the level, and a stop touched inside the fill bar counts as hit.
  - If stop and target are in the same bar, the stop is assumed.
  - "Exit 20:00" means the close of the 19:55 bar.
- **Periods:** IS 2022-2024, OOS 2025-2026, plus a separate 2026 YTD column. The years column shows the sign of net P&L for 2022 to 2026.
- **Pass rule:** n >= 40 in both IS and OOS, PF >= 1.15 in both, the neighbouring cells must not collapse, and the rule must beat its shifted-window baseline. For the baseline, the same rule is run with its clock moved to the 20-22, 22-24, 00-02, 02-04, 04-06 and 06-08 windows and the results are pooled.
- **Earnings dates:** AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AVGO and NFLX all report after the close. 174 reports fell on 134 evenings, pulled from the Nasdaq earnings calendar into `data/earnings_megacap.csv`.

Scripts (all in `scripts/evening/`, outputs `out_e*.txt`):

| File | Question |
|---|---|
| `ev_common.py` | evening table, market/limit simulators, 3-period stats, baselines |
| `fetch_earnings.py` | mega-cap earnings dates |
| `e1_s2_trunc.py` | Q1 S2 truncated to 18:05-20:00 |
| `e2_gap.py` | Q2 gaps vs the 17:00 and 16:00 closes (pullback, fade, follow), SGP replication |
| `e3_cont_rev.py` | Q3 continuation/fade of the last hour, RTH day, post-close hour, 16:00->18:00 change; reversion to 16:00 close; DST split |
| `e4_open_patterns.py` | Q4 OR15/OR30 sweep-and-reclaim, ORB, pre-Tokyo hour, 18-19 range at the Tokyo open, 18:00 open as fair price |
| `e5_earnings_dow.py` | Q5 earnings evenings, Q6 day of week |
| `e6_wed_check.py` | Wednesday robustness (FOMC, earnings, season, grid, entry/exit, baseline) |
| `e7_module.py` | final rules, budget sizing, Lucid Flex 50K eval with the day engine |

## Q1. S2 sell-off long truncated to 18:05-20:00

Condition: the prior RTH closed below its 9:30 open, and 15:00-16:00 was <= -0.15 ADR. Long at 18:05, exit 20:00.

| Test | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF | years |
|---|---|---|---|---|---|---|---|
| S2 original, exit 03:30 (reference) | 115 | 1.50 | 58 | 1.30 | 26 | 1.61 | +++++ |
| truncated, stop 0.30 | 115 | 0.93 | 58 | 1.52 | 26 | 2.17 | -+-++ |
| truncated, no stop | 115 | 0.91 | 58 | 2.04 | 26 | 2.53 | -+-++ |
| truncated, stop 0.15 / 0.20 / 0.25 | 115 | 0.78 / 0.86 / 0.92 | 58 | 1.39 / 1.35 / 1.32 | 26 | 1.95 / 2.23 / 2.15 | -+--+ |
| targets 0.2-0.5 ADR (any stop) | 115 | 0.67-0.98 | 58 | 1.02-1.94 | 26 | 1.57-2.61 | mixed |
| unconditional long, same window | 741 | 0.86 | 445 | 1.07 | 200 | 1.11 | ---++ |
| same rule, later windows pooled | 690 | 0.88 | 348 | 1.09 | 156 | 1.35 | +---+ |

**Answer: NO.** The overnight edge of S2 does not live in the first two hours in 2022-2024: IS PF is below 1 in every stop and target cell. The strong 2025-2026 numbers are mostly the bull-market long drift, since the unconditional long and the shifted windows are also positive in 2026. Keep S2 as an overnight rule. It is not an evening-module rule.

## Q2. Weeknight gap and pullback (the SGP analog)

**Base rates (Mon-Thu evenings):**
- The gap vs the 17:00 close is tiny: median 1.3% ADR, 90th percentile 6.4%.
- The change from the 16:00 RTH close to the 18:00 open is larger: median 5.9% ADR, 90th percentile 21.6%.
- For comparison, the Sunday gap median is 6.4% ADR.

| Test | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF | years |
|---|---|---|---|---|---|---|---|
| SGP (Sunday) on this engine | 36 | 1.39 | 37 | 1.39 | 17 | 1.53 | +++++ |
| SGP rule run on Mon-Thu evenings | 40 | 1.08 | 47 | 0.99 | 20 | 0.67 | -+++- |
| Weeknight pullback vs 17:00 close, 96-cell grid | | 0 cells pass | | | | | |
| Fade gap vs 17:00 to the 17:00 close, >= 0.05 ADR | 63 | 0.52 | 60 | 0.56 | 25 | 0.48 | ----- |
| Follow gap vs 17:00, >= 0.05 ADR, stop 0.15 | 66 | 1.29 | 65 | 1.21 | 28 | 1.25 | ++-++ |
| same at >= 0.02 / >= 0.10 ADR | 189 / 26 | 0.94 / 0.66 | 163 / 27 | 0.94 / 2.18 | | | unstable |
| Pullback vs 16:00 close, gap >= 0.05, k 0.75, stop 0.15 | 105 | 1.34 | 96 | 1.64 | 51 | 1.95 | +++++ |
| same with gap >= 0.10 | 32 | 0.39 | 33 | 1.89 | 18 | 1.97 | ---++ |
| Fade 16:00->18:00 change back to the 16:00 close (15 cells) | | 0.45-0.72 | | 0.57-0.84 | | 0.41-0.84 | ----- |
| Follow 16:00->18:00 change, >= 0.05, stop 0.15 | 324 | 1.24 | 207 | 1.28 | 96 | 1.36 | +++++ |
| its baseline (2h move into later times) | 2132 | 0.81 | 1478 | 0.85 | 711 | 0.85 | ----- |

**SGP replication:** PF 1.39 on 73 trades (IS 36, OOS 37), every year positive, 2026 PF 1.53.
- That is lower than the 1.95 in `SUNDAY_OPEN_2026-10-25.md`. This engine charges 1 tick on every side, needs a trade-through fill, and uses the RTH-based ADR.
- Neighbours are mostly positive. The k 0.375-0.5 x gap 0.03-0.05 cells score PF 1.0-2.4 in every column.
- The t-stat is only 0.8 per period. The edge is plausible but statistically thin.

**Answer:**
- No weeknight version of SGP: the halt gap is too small to pull back into.
- Fading toward the 17:00 or 16:00 close is one of the worst things you can do in the evening (PF about 0.5).
- The direction of the 16:00 close -> 18:00 open change continues (Q3 below). The pullback version of that idea is fragile: it works for 0.05-0.10 ADR changes and fails above 0.10, so it is not used.

## Q3. Continuation of the 15:00-16:00 move, the RTH day, the post-close hour; reversion to 16:00

Entry is market at 18:05 in the direction (or against the direction) of the signal, exit 20:00, Mon-Thu evenings.

| Signal (stop 0.2 ADR) | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF | years | baseline IS/OOS |
|---|---|---|---|---|---|---|---|---|
| CONT 15:00-16:00 move, any size | 592 | 0.82 | 357 | 0.77 | 161 | 0.65 | ----- | 0.75 / 0.89 |
| FADE 15:00-16:00 move, any size | 592 | 0.72 | 357 | 0.92 | 161 | 1.12 | ----+ | 0.79 / 0.86 |
| FADE 15:00-16:00 >= 0.3 ADR | 95 | 1.05 | 54 | 1.46 | 19 | 3.64 | -++-+ | |
| CONT RTH day >= 0.5 ADR | 280 | 1.20 | 147 | 1.25 | 71 | 1.04 | +-+++ | 0.77 / 0.62 |
| FADE RTH day (any threshold) | | 0.47-0.66 | | 0.41-0.66 | | 0.45-0.78 | ----- | |
| CONT post-close 16:00-17:00 >= 0.05 ADR | 333 | 1.25 | 196 | 1.17 | 94 | 1.17 | +-+++ | 0.77 / 0.83 |
| CONT 16:00 close -> 18:00 open >= 0.05 ADR ("G16") | 324 | 1.22 | 207 | 1.28 | 96 | 1.32 | +++++ | 0.81 / 0.85 |
| G16, US daylight time only (EDT) | 216 | 1.50 | 148 | 1.51 | 77 | 1.52 | +++++ | |
| G16, standard time only (EST) | 108 | 0.87 | 59 | 0.84 | 19 | 0.66 | ----- | |
| Revert to the 16:00 close (15 cells) | | 0.45-0.72 | | 0.57-0.84 | | 0.41-0.84 | ----- | |

**G16 timing checks:**
- Entry time barely matters (18:00 to 19:00 entries: PF 1.08-1.30 IS, 1.23-1.34 OOS).
- The exit must be 20:00. Exits at 18:30, 19:00 and 19:30 all have IS PF below 1.
- Most of the profit comes in the 19:00-20:00 hour, and only in EDT. In EDT that hour is the one before the Tokyo open (20:00 EDT).
- In EST the Tokyo open falls at 19:00, but holding into it does not work either (18:05->19:00 EST: PF 0.59 / 0.56), so the "pre-Tokyo positioning" story is not confirmed.
- Changes under 0.05 ADR lose (PF 0.92 / 0.71).

**Answer:**
- The evening continues the RTH and post-close direction (PF 1.2-1.3 above a 0.05-0.5 ADR threshold), and fading it loses badly.
- The "16:00 close as fair price" reversion idea is clearly negative.
- Q6 shows the continuation is mostly a Wednesday effect.

## Q4. Manual open patterns

| Test | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF | years |
|---|---|---|---|---|---|---|---|
| OR15 sweep (>= 0.02 ADR) and reclaim, fade, stop beyond sweep, target OR mid | 190 | 0.76 | 167 | 0.61 | 73 | 0.59 | +---- |
| OR15/OR30 sweep-and-reclaim, all 54 cells | | 0.64-1.59 (n < 50 above 1.2) | | 0.61-1.03 | | 0.49-1.04 | mostly +---- |
| OR15 break-and-go, stop other side | 589 | 0.61 | 370 | 0.99 | 167 | 1.17 | ----+ |
| OR30 break-and-go, stop other side | 473 | 0.59 | 308 | 0.92 | 139 | 1.04 | ----+ |
| Pre-Tokyo hour: at 19:00 go with (price - 16:00 close) >= 0.10 ADR, stop 0.15, exit 20:00, EDT | 206 | 1.25 | 191 | 1.55 | 91 | 1.74 | +-+++ |
| same, EST | 103 | 0.89 | 68 | 0.99 | 25 | 1.11 | --+-+ |
| same, fade (any threshold, either season) | | 0.34-0.83 | | 0.35-0.88 | | 0.14-1.00 | ----- |
| 18:00-19:00 range break at 19:00 (EST Tokyo open) | 136 | 0.78 | 81 | 0.67 | 31 | 0.57 | ----- |
| 18:00-19:00 range fade at 19:00, EST | 74 | 0.69 | 45 | 0.74 | 20 | 1.04 | --+-+ |
| 18:00 open as fair price: fade first extension >= X ADR (X 0.08-0.30, 18 cells) | | 0.58-0.83 | | 0.25-0.68 | | 0.16-0.73 | ----- |
| same, follow the extension | | 0.66-0.95 | | 0.96-1.60 | | 0.92-1.54 | ---++ |

- **Sweep-and-reclaim:** the shifted-window baselines are even worse (PF 0.46-0.67). This failure is not specific to 18:00.
- **What happens after 20:00:** the 20:00-21:00 hour continues the 18:00-20:00 move 48-52% of the time, with a mean of about 0% ADR in both seasons. Being flat by 20:00 costs nothing.

**Answer:**
- No open pattern works on its own: sweep-and-reclaim, ORB, the Tokyo-open range and fading the 18:00 open all lose.
- The only positive 19:00 behaviour is the G16 continuation measured at 19:00 in EDT. It is the same effect as Q3, not a separate rule.

## Q5. Post-earnings evenings

| Set | n | median abs 16:00-17:00 move | median abs 16:00->18:00 change | median 18-20 range | median abs 18->20 move |
|---|---|---|---|---|---|
| mega-cap earnings evenings | 130 | 17.8% ADR | 21.4% | 23.9% | 10.6% |
| normal Mon-Thu evenings | 821 | 5.1% | 5.1% | 15.8% | 6.4% |

| Test (stop 0.2, 18:05-20:00) | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF | years |
|---|---|---|---|---|---|---|---|
| EARN: G16 continuation | 80 | 1.15 | 37 | 1.37 | 15 | 1.07 | -++++ |
| NORMAL: G16 continuation | 244 | 1.26 | 170 | 1.25 | 81 | 1.37 | +-+++ |
| EARN: fade the 16:00->18:00 change | 80 | 0.79 | 37 | 0.96 | 15 | 1.24 | +---+ |
| EARN: continue the post-close move >= 0.2 ADR | 38 | 0.84 | 20 | 1.92 | 8 | 1.93 | --+++ |
| EARN: fade the post-close move >= 0.2 ADR | 38 | 1.02 | 20 | 1.02 | 8 | 1.05 | -+--+ |
| EARN: long 18:00-20:00 | 86 | 0.73 | 44 | 2.29 | 19 | 1.99 | --+++ |
| WCC on earnings Wednesdays | 29 | 2.14 | 20 | 1.50 | 10 | 0.66 | -+++- |
| WCC on non-earnings Wednesdays | 65 | 2.91 | 34 | 3.04 | 18 | 4.14 | +-+++ |

**Answer:** on earnings evenings, the post-close move is 3.5x larger and the evening range is 1.5x larger, but there is no extra edge in either direction. Fading the earnings move does not work. The rules still work on earnings nights but weaker. Do not build an earnings rule. Trade WCC at most 1 MNQ on a mega-cap earnings evening.

## Q6. Day of week, 18:00-20:00

| Evening | n | mean 18->20 %ADR | up % | t | median range %ADR | IS mean | OOS mean | 2026 mean |
|---|---|---|---|---|---|---|---|---|
| Sun | 235 | +3.1 | 52% | +1.8 | 28.1 | +1.0 | +6.6 | +8.0 |
| Mon | 223 | -1.1 | 48% | -1.3 | 15.3 | -0.1 | -2.8 | -2.6 |
| Tue | 247 | +1.8 | 58% | +1.7 | 15.9 | +0.6 | +3.8 | +7.2 |
| Wed | 244 | +1.3 | 54% | +1.0 | 18.1 | -0.4 | +4.1 | +5.3 |
| Thu | 237 | -0.8 | 48% | -0.9 | 17.5 | -0.9 | -0.6 | -2.0 |

**Plain direction:** no fixed long or short by weekday passes IS. Every "long on X evening" is positive only in 2025-2026, the bull years. Sunday evenings move almost twice as much as weeknights.

**G16 continuation split by weekday:**

| Evening | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF | years | baseline IS/OOS/2026 |
|---|---|---|---|---|---|---|---|---|
| Mon | 61 | 1.05 | 43 | 0.96 | 19 | 1.82 | ++--+ | 0.73 / 1.05 / 1.06 |
| Tue | 74 | 0.67 | 57 | 0.86 | 25 | 0.62 | ---+- | 0.83 / 0.65 / 0.65 |
| **Wed** | **94** | **2.61** | **54** | **2.24** | **28** | **2.00** | **+++++** | **0.83 / 0.81 / 0.73** |
| Thu | 95 | 0.92 | 53 | 1.09 | 24 | 1.30 | -++-+ | 0.86 / 0.95 / 1.06 |
| Mon+Tue+Thu | 230 | 0.86 | 153 | 0.97 | 68 | 1.05 | ----+ | |

**Wednesday robustness** (`out_e6.txt`):
- **Grid:** every threshold (0 to 0.15 ADR) x stop (0.15/0.2/0.3) cell is PF >= 1.4 IS and OOS. Without a stop, OOS drops to 1.17-1.64, and the stopless and widest cells drop toward 1.0-1.2 in 2026.
- **Entry time:** 18:00 to 18:30 entries all score PF >= 1.88 IS/OOS.
- **Exit time:** the exit should be late. 19:50 gives 2.21 / 2.27 / 2.05, but 18:30 loses.
- **Splits:** PF above 1 in every split. Longs: 2.19 / 4.44 / 4.30. Shorts: 3.08 / 1.22 / 1.21. FOMC: 3.19 / 1.90. Non-FOMC: 2.43 / 2.42. EDT: 3.11 / 2.35. EST: 1.85 / 1.85 (EST 2026 only n 5).
- **Statistics:** t-stat +3.2 IS and +2.0 OOS.
- **Mechanism:** none found. Wednesdays carry FOMC (37 of 244), CPI (23) and many mega-cap reports, but the effect survives with all of those removed (non-FOMC non-earnings: 2.17 / 1.90 / 2.48).

**Answer:** treat WCC as real but mined. It was found by splitting a passing family (G16) by weekday, after roughly 800 variants in this study. Expect live PF nearer 1.4-1.6 than 2.2, and size it accordingly.

## The evening module

**Variants considered:**

| Variant | Rules | Why you would pick it | Trade-off |
|---|---|---|---|
| A | SGP only | the safest pick; was already the plan | about 15 trades/yr, thin t-stat, does little for the eval |
| **B (recommended)** | **SGP + WCC** | the two rules with the best evidence, about 46 trades/yr, on fixed evenings (Sun, Wed) | WCC is a weekday-mined cell |
| C | SGP + G16 Mon-Thu | no weekday selection | about 125 trades/yr at PF 1.2-1.3; Mon/Tue/Thu only break even |
| D | SGP + G16 Mon-Thu, EDT only | best broad version | season-mined, and off from Nov 1, 2026 to Mar 8, 2027 |

Module B at 1 MNQ per trade: IS n 130, PF 2.11, +$17.9/trade; OOS n 91, PF 1.83, +$32.2; 2026 n 45, PF 1.80, +$35.0; maxDD $581; every year positive.

### Rule E1: Sunday Gap Pullback (SGP)

- **Day:** Sunday evening only, and the prior Friday must be a full RTH day.
- **Reference:** `fri = close of Friday's 16:55 bar` (the 17:00 close). `gap = open of Sunday's 18:00 bar - fri`.
- **Filter:** `abs(gap) >= 0.05 * ADR`, else no trade.
- **Entry:** at 18:00, place a limit order in the gap direction at `lvl = open18 - sign(gap) * 0.5 * abs(gap)` (the midpoint between the 18:00 open and Friday's close). It is a buy limit for an up gap, a sell limit for a down gap. The limit is valid from the 18:00 bar through the 19:25 bar. Cancel it at 19:30 if it has not filled.
- **Stop:** `fill - sign(gap) * 0.15 * ADR` (about 50 pts at 2026 ADR).
- **Target:** none.
- **Time exit:** flat at the close of the 19:55 bar (20:00). Flattening at 19:55 is equivalent (PF 1.40 / 1.43 / 1.57).
- **Frequency:** about 15 fills a year. 135 of 235 Sundays had a qualifying gap and 73 filled.

### Rule E2: Wednesday Close Continuation (WCC)

- **Day:** Wednesday evening only. Skip if Wednesday's RTH was not a full day, or if Thursday is a market holiday (for example Thanksgiving week).
- **Signal (known at 18:00:00):** `x = open of the Wednesday 18:00 bar - close of the Wednesday 15:55 bar (the 16:00 RTH close)`.
- **Filter:** `abs(x) >= 0.05 * ADR` (about 20 pts). Otherwise no trade.
- **Entry:** market at the open of the 18:05 bar, long if `x > 0`, short if `x < 0`. A manual entry anywhere from 18:00 to 18:15 is equivalent.
- **Stop:** `entry - sign(x) * 0.20 * ADR` (about 80 pts at 2026 ADR, $166 risk per MNQ with costs).
- **Target:** none. A 0.3 ADR target is slightly worse (PF 2.57 / 1.85 / 1.60).
- **Time exit:** flat at the close of the 19:55 bar (20:00). Flattening at 19:50 keeps most of it (2.21 / 2.27 / 2.05).
- **Earnings:** if a mega-cap (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AVGO, NFLX) reported after Wednesday's close, trade at most 1 MNQ.
- **Frequency:** about 31 trades a year (148 of 244 Wednesdays). Average win $78, average loss $55 at 1 MNQ; 12 of 148 trades stopped out.

### Budget, sizing and stop rules

- **Separate budget:** a fixed dollar risk per evening, B. It never borrows from, or counts toward, the day engine's $1,100 daily budget. Evening P&L does land in the next trading day's account P&L, because the futures day starts at 18:00. That matters for the consistency rule and for the EOD trailing line.
- **Contracts:** `q = floor(min(B, 0.5 * roomAboveMLL) / riskPerMNQ)`, where `riskPerMNQ = stopPts * 2 + 2 * 2.37 + 1`. If q = 0, skip the trade; do not widen B to force 1 contract.
- **During an eval:** B = $200. That is 1 MNQ on both rules at current ADR; WCC is skipped when 0.2 ADR is above about 95 pts.
- **On a funded account:** B = $300-$400 (2-3 MNQ) once the room above the max-loss line is at least $1,500.
- **Stop the session:** one trade per evening, then done, win or lose. The rules never fire on the same evening. No re-entry and no second rule.
- **Module kill switch:** if module P&L falls $1,200 below its high (6 budgets at $200, above the worst historical drawdown of $946), pause the module and review.
- **Expected losing streaks:** 7 trades longest (B). The worst single evening is the full budget.

**Module P&L with the evening budget (contracts = floor(B / risk)):**

| Module | B | trades | avg MNQ | 2022 | 2023 | 2024 | 2025 | 2026 YTD | maxDD | longest losing streak |
|---|---|---|---|---|---|---|---|---|---|---|
| A SGP | $200 | 72 | 1.8 | +245 | -24 | +136 | +552 | +428 | 661 | 5 |
| **B SGP+WCC** | **$200** | **209** | **1.5** | **+802** | **-59** | **+2,133** | **+1,812** | **+1,465** | **946** | **7** |
| B SGP+WCC | $300 | 220 | 2.4 | +1,760 | +18 | +3,683 | +2,601 | +2,361 | 1,435 | 7 |
| B SGP+WCC | $400 | 221 | 3.4 | +2,350 | +275 | +4,658 | +3,904 | +3,780 | 1,896 | 7 |
| C SGP+G16 | $300 | 601 | 2.3 | +1,486 | -269 | +3,277 | +1,534 | +3,006 | 1,863 | 11 |
| D SGP+G16-EDT | $300 | 434 | 2.3 | +1,376 | -166 | +3,167 | +1,924 | +3,592 | 1,666 | 11 |

### Lucid Flex 50K eval alongside the day engine

**Sim setup:**
- Eval rules: EOD trailing max loss `mll = min(peakEOD - 2000, 50000)`, $3,000 target, best day <= 50% of profit.
- Day engine: final defaults (`rules2.build('current', be=True, v4t=1.25)`, size_day 'updated', 65% of room, $1,100/day, 8-pt stop-slip stress).
- Evening stop exits get an extra 2-pt slip stress.
- Each window starts an attempt on every trading day and runs it to 2026-10-20.

**Outcomes:**
- The day engine never breaches the MLL here, because its sizing shrinks with the room.
- The failure mode is **stalling**: the room above the line falls below about $300, no trade fits, and the account is dead in practice.
- "Gained / lost a pass" compares each start with the day-engine-only run from the same day.

| Window | Setup | pass % | stalled % | pass <= 40d | median days to pass | passes earlier | gained a pass | lost a pass |
|---|---|---|---|---|---|---|---|---|
| 2025 | day engine only | 55 | 35 | 38% | 29.5 | | | |
| 2025 | + A SGP $200 | 67 | 32 | 34% | 40 | 11% | 16% | 4% |
| 2025 | **+ B $200** | **74** | **26** | **37%** | **41** | **19%** | **22%** | **4%** |
| 2025 | + B $400 | 61 | 37 | 40% | 33 | 29% | 10% | 4% |
| 2025 | + D $200 | 80 | 20 | 42% | 39 | 16% | 25% | 0% |
| 2026 YTD | day engine only | 30 | 28 | 26% | 25.5 | | | |
| 2026 YTD | + A SGP $200 | 36 | 41 | 26% | 26 | 7% | 7% | 0% |
| 2026 YTD | **+ B $200** | **46** | **12** | **28%** | **32.5** | **19%** | **16%** | **0%** |
| 2026 YTD | + B $300 | 39 | 39 | 27% | 29 | 19% | 13% | 3% |
| 2026 YTD | + B $400 | 54 | 31 | 35% | 31 | 22% | 26% | 2% |
| 2026 YTD | + D $300 | 57 | 22 | 29% | 40.5 | 9% | 29% | 1% |

(2026 attempts start up to Sep 15, so many are still open at the data end. The full table is in `out_e7.txt`.)

**Reading:**
- **Pass rate:** module B at $200 raises the 2026 pass rate from 30% to 46% and cuts stalled attempts from 28% to 12%. It never turns a passing 2026 start into a non-pass. In 2025: 55% to 74%.
- **Speed:** it does not make passing faster on average. The median days to pass rises slightly because the extra passes are slow rescues.
- **How it helps:** it adds about $35 per week of small, steady P&L. That lifts stalled accounts back above the room needed for a day-engine trade, and it pads total profit against the 50% consistency rule without creating a new best day.
- **Budget:** above $200 the effect becomes path-dependent: $300 is worse than $200 in 2026, $400 is better. $200 is the size that helps in both windows with almost no lost passes.
- **Variant D** scores higher in this sim, but it is season-selected and inactive from Nov 1 to Mar 8. Use it only as a paper-tracked alternative.

## Honest notes

- **SGP:** keeps a positive edge on the stricter engine (PF 1.39), but it is about 15 trades a year with a t-stat under 1. Its value is mostly that it is cheap and does not overlap anything.
- **WCC:** the one new rule that clears every test, including the shifted baseline (0.83 / 0.81 / 0.73). It was selected from a weekday split, so paper-trade it, or run it at $200 risk, for at least 20 trades before sizing up.
- **Dead ideas for this window:** the S2 sell-off long truncated to 20:00 fails IS. Also dead: weeknight gap pullbacks, every fade (of the gap, the 16:00 close, the 18:00 open, the RTH day, the last hour), OR sweep-and-reclaim, ORB, and the Tokyo-open range.
- **The general pattern:** the evening continues what happened since 16:00, and it pays only if held to 20:00. The broad Mon-Thu version (G16) is real but thin (PF 1.2-1.3, t 1.3) and concentrated in daylight-time months.
- **Not tested:** real tick-level fills in the first 5 minutes after the 18:00 reopen. Spreads there are wider than 1 tick on some nights. Use the 18:05 entry, never a market order at 18:00:00.
