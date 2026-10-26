# Red-folder news study for MNQ (Oct 25 2026)

The question: how can the high-impact US releases (ForexFactory red folders) help with direction and behavior around the release? We are not trying to predict the number.

**Data:**
- MNQ ETH 5m bars, 18:00 to 17:00, for every measurement.
- RTH 1m bars for the trade tests and the next-day tests.
- Period: Jan 2022 to Oct 20 2026.
- ADR is the mean of the prior 10 RTH ranges. The median was about 290 pts in 2022, 200 in 2023, 225 in 2024, 280 in 2025 and 360 in 2026.

**Costs:** 1 MNQ, $2/pt, 2.37 commission per side, plus 1 tick of slippage on entry and 1 tick on stops (same as `fp.walk`). In-sample (IS) is 2022-2024 and out-of-sample (OOS) is 2025-2026.

**Baseline:** every number is compared with "clean" days at the same clock time. A clean day has no major red folder at all and nothing at that minute.

---

## 0. Cheat sheet: how to use each red folder

| Release (ET) | Size of reaction (first 15 min, vs a normal day) | What it tends to do | Use it as | Evidence |
|---|---|---|---|---|
| **CPI** 8:30 | Biggest: 0.36 ADR, 6.8x | The spike holds. 89% are still on the spike side at +60 min, and only 21% trade back to the 8:29 price within an hour (normal: 60%). | **Fade it, only through the NEWS module** (reversion to 8:29 on a trigger). **Never chase it.** After 9:30, trade normally: our strategies make money on CPI days. | fade-to-F PF 1.58 IS / 1.44 OOS. Following the 30m or 60m move: PF 0.62 and 0.42 (p=0.001). |
| **NFP** 8:30 | 0.21 ADR, 4.0x | The first hour's direction often reverses by the close: in 61% of days the 30m-to-close move goes against the first 30 min. | **Fade it / bias.** At 9:30, if 8:30-9:30 moved at least 0.10 ADR, lean the other way for the day. | 9:30 fade, hold to close: PF 3.25 IS / 1.49 OOS, n 43, +$98/trade, p<0.001. Holds across neighbouring settings (fade at +20 to +60 min). |
| **PPI** 8:30 | 0.12 ADR, 2.3x | Ordinary | **Trade normally.** Do not chase the first 5 min. | No rule passes. Our strategies on PPI days: PF 2.9 / 9.9. |
| **PCE** 8:30 | 0.12 ADR, 2.2x (about 1/3 of CPI) | Muted. 77% back to F by +2h. | **Stand aside from news setups.** Treat it as a normal day. | follow60 PF 1.68 / 1.83, but p=0.065: not proven. |
| **GDP advance** 8:30 | 0.10 ADR, 1.8x | The first 30 min reverse by the close in 74% of days, but n=19. | **Weak bias only** (fade the first hour). | fade60 PF 3.3 / 1.2 on 12 trades: too few. |
| **Retail Sales** 8:30 | 0.09 ADR, 1.8x (nearly a non-event) | The next day goes against the Retail-day move 60% of the time. | **Next-day bias**: lean against the Retail-day move (8:29 to close). | Next-day fade PF 1.65 / 2.04, n 47, +$89, p=0.047. Holds across stop sizes. |
| **Jobless Claims** Thu 8:30 (control) | 1.3x | Behaves like a normal day | **Ignore.** | All rules are close to clean days. |
| **ISM Mfg / Services** 10:00 | 1.3-1.5x (Services: 2.5x on the first 5m bar) | Not faded: price does not come back to the 9:59 price. | **Stand aside from fading it.** Hold trades already open. | Fade to F: PF 0.71 and 0.75 in both periods. |
| **JOLTS** 10:00 | 1.0-1.2x | Nothing special | **Ignore.** | follow30 2R PF 1.56 / 1.46, p=0.19: not significant. |
| **FOMC statement** 14:00 | 0.17 ADR, 3.2x; day range 1.30 ADR | The first move is a coin flip after 60 min (51% still on the spike side). It comes back to the 13:59 price by the close 87% of the time (normal: 79%). | **Fade it back to the 13:59 price. Never chase the statement candle.** | At 14:15, against a move of at least 0.10 ADR, target the 13:59 price, stop = same distance: PF 1.36 / 3.61, n 25, +$54, win 60%, p<0.001. Positive for every k and stop tested. Following the 14:00-14:30 move to the close: PF 0.20 (p<0.001). |
| **FOMC press conference** 14:30 | 0.20 ADR, 3.7x | It often reverses the statement (also found in academic work). | **Fade the 14:30-14:45 move back to the 14:29 price.** | PF 1.19 / 5.94, n 30, p<0.001. |
| **Day after FOMC** | Normal range (1.04 ADR) | The "FOMC reversal next day" is not real here: only 42% reverse. | **Trade normally.** | Next-day fade PF 1.21, p=0.30. Skipping the day: IS better, OOS worse. |
| **FOMC minutes** 14:00 | Small reaction (1.5x), but the **quietest day type** (range 0.87 ADR, 23% trend days vs 34%) | Chop. Trend entries fail. | **STAND ASIDE from trend entries** (D2, TDP). Add minutes days to D2's skip list next to FOMC/CPI. | Our strategies on minutes days: 26 trades, PF 0.16 IS / 0.36 OOS, -$2,782 in total. p=0.003 vs random days, p<0.001 vs random Wednesdays. D2: 9 trades, 1 winner. |
| **Fed Chair testimony** 10:00 | 1.4x, dates approximate | Too few days (n=17) | **Ignore.** | n.a. |
| **Any red folder** | n.a. | Chasing the first 5-min candle loses. | **Rule: never enter in the direction of the first 5-min news candle.** | Pooled over 13 event types: PF 0.69 (n 461) vs 1.03 on clean days, in both periods. |

**Plain rules to carry on the chart:**
1. On any red folder, the first 5-min candle is not a signal to chase.
2. After CPI, FOMC and the press conference, the pre-release price is the magnet. Trade back toward it, with a target at it.
3. After NFP, lean against the 8:30-9:30 move for the rest of the day.
4. On FOMC-minutes days, expect chop: skip D2 and TDP, or cut size.
5. The day after Retail Sales, lean against the Retail-day move.
6. PCE, PPI, JOLTS, ISM and Claims: no special trade. Do not fade ISM.

---

## 1. Date list: `data/macro_dates_ext.csv`
The columns are `date,event,time_et,approx,source`. There are 891 rows for 2022-2026. Built by `scripts/news2/build_dates.py`.

| Event | n | Source | Approx? |
|---|---|---|---|
| FOMC 14:00, FOMC_PC 14:30, FOMC_SEP | 40 / 40 / 20 | Existing macro_dates.csv plus federalreserve.gov FOMC calendar | official |
| FOMC_MIN 14:00 | 39 | federalreserve.gov ("Minutes released ...") | official |
| GDP advance 8:30 | 19 | bea.gov news archive. Q3 2025 was published as the "initial" estimate on Dec 23 2025 after the shutdown. | official |
| PCE (Personal Income and Outlays) | 55 | bea.gov archive. 2025-04-30 was at 10:00. 2025-12-05 is set to 10:00 and the 2026 combined GDP+PCE days to 8:30. | 2025-12-05 and 2026 times approx |
| RETAIL 8:30 | 58 | census.gov MARTSreleasedates.xlsx | official |
| ISM_MFG / ISM_SRV 10:00 | 58 / 58 | Rule: 1st and 3rd business day, with January exceptions | approx |
| JOLTS 10:00 | 56 | 2025 from the BLS schedule copy on equalsmoney.com, other years from memory. bls.gov blocked automated access. | approx except Jan-Sep 2025 |
| CLAIMS 8:30 | 250 | Thursdays, or Wednesday when Thursday is a holiday | Oct-Nov 2025 shutdown weeks flagged |
| TESTIMONY 10:00, JACKSON 10:00 | 17 / 4 | from memory | approx |
| CPI / PPI / NFP | copied | macro_dates.csv | official |

**Validation** (`validate_dates.py`): the range of the release 5m bar divided by the median range of the 12 bars before it.
- Clean days: about 1.1 to 1.45.
- Median on event days: CPI 12.2, NFP 8.9, FOMC 5.9, PPI 5.1, PCE 4.6, GDP 4.4, RETAIL 3.6, CLAIMS 3.0, FOMC_PC 2.5, FOMC_MIN 2.4, ISM 2.1-2.2, JOLTS 2.0, TESTIMONY 1.9.

So the 10:00 dates are mostly right. About 10-20% of ISM and JOLTS days show no reaction at all, which is either a quiet print or a wrong date. Treat ISM, JOLTS and TESTIMONY results as noisier.

---

## 2. Behavior around the release (`measure.py`, full table in `knowledge/src/red_folder_measure.txt`)
F is the last price before the release (close of the 5m bar ending at T). Moves are in ADR units.

| Event | n | First 5m | First 15m | 60-min drift before | Still on the 15m spike side at +60 / close | Back to F by +60 / close | Close direction = overnight direction |
|---|---|---|---|---|---|---|---|
| clean 8:30 | 563 | 0.03 | 0.05 | 0.06 | 75% / 54% | 60% / 90% | 52% |
| CPI | 57 | 0.34 (10x) | 0.36 (7x) | 0.06 | 89% / 67% | 21% / 70% | 60% |
| NFP | 54 | 0.23 (7x) | 0.21 (4x) | 0.07 | 74% / 59% | 37% / 80% | 58% |
| PPI | 57 | 0.12 (4x) | 0.12 (2x) | 0.06 | 91% / 56% | 32% / 70% | 53% |
| PCE | 52 | 0.10 (3x) | 0.12 (2x) | 0.08 | 81% / 62% | 42% / 85% | 41% |
| GDP | 19 | 0.08 (2.5x) | 0.10 (2x) | 0.13 | 79% / 37% | 42% / 89% | 58% |
| RETAIL | 58 | 0.05 (1.5x) | 0.09 (2x) | 0.05 | 67% / 54% | 52% / 84% | 41% |
| CLAIMS-only | 168 | 0.05 (1.5x) | 0.07 (1.3x) | 0.08 | 68% / 59% | 57% / 88% | 46% |
| clean 10:00 | 707 | 0.06 | 0.10 | 0.19 | 73% / 62% | 61% / 78% | 52% |
| ISM_MFG | 57 | 0.10 (1.6x) | 0.15 (1.5x) | 0.20 | 72% / 56% | 56% / 75% | 40% |
| ISM_SRV | 55 | 0.16 (2.5x) | 0.13 (1.3x) | 0.24 | 75% / 55% | 45% / 75% | 64% |
| JOLTS | 56 | 0.10 (1.6x) | 0.12 (1.2x) | 0.19 | 73% / 59% | 59% / 82% | 52% |
| clean 14:00 | 707 | 0.03 | 0.05 | 0.11 | 64% / 59% | 68% / 79% | 55% |
| FOMC | 38 | 0.18 (5x) | 0.17 (3x) | 0.07 | 70% / 51% | 76% / 87% | 53% |
| FOMC_PC 14:30 | 38 | 0.14 (4x) | 0.20 (4x) | 0.22 | 71% / 66% | 55% / 63% | 55% |
| FOMC_MIN | 38 | 0.06 (2x) | 0.08 (1.5x) | 0.09 | 68% / 68% | 68% / 82% | 45% |

**Takeaways:**
- **The drift before the release does not predict the reaction.** Its sign matches the 30-min reaction 38-59% of the time; the 68% on minutes days is n=38.
- **CPI and PPI spikes stick.** Price rarely gets back to F within the hour, so a fade needs a trigger and a target at F, not a blind fade. This is what the NEWS module already does.
- **The FOMC statement move is noise.** By +60 min it is 51/50, price revisits F 87% of the time, and the two halves of the afternoon are unrelated. The 14:00-14:30 move matches the 14:30-close move only 50% of the time (normal 52%).
- **"Wait for the second move" has no direction edge.** The 14:30-15:00 move matches the 15:00-close move only 53% of the time. The edge is in going back to F, not in following move 2.
- **NFP and GDP reverse.** The 30m-to-close move goes against the 0-30m move 61% of the time for NFP (n 54) and 74% for GDP (n 19). The normal rate is about 50%.
- **The overnight trend does not set the event-day trend.** Alignment is 41-60% on every event.
- **Next day:**
  - The day after FOMC goes the same way as the FOMC afternoon 58% of the time (normal 50%; n=38, not significant). So there is no "next-day reversal".
  - Retail Sales is the only event with a reversal: 60% (63% on Retail-only days).
- **Day range (RTH, ADR units)** (`dayrange.py`):
  - FOMC 1.30, GDP 1.21, PCE 1.12, ISM 1.06, NFP 1.04, CPI 1.02 vs clean days 0.90.
  - FOMC minutes 0.87, the only event below a clean day, with 23% trend days vs 34%.

---

## 3. Mechanical tests (`trades.py`, `robust.py`; outputs in `knowledge/src/red_folder_trades.txt` and `red_folder_robust.txt`)
13 simple rules per event, run on 15 event types and on clean days as a control.

**Multiple-testing warning:**
- A rule "passes" when IS PF >= 1.2, OOS PF >= 1.2 and OOS n >= 8.
- On random 55-day samples of clean days, rules pass this screen **6-10% of the time** (`null.py`).
- On real events, about 14% pass.
- So most single passes are noise. I only keep rules that also pass a permutation test (`p` = share of random clean-day samples of the same size doing at least as well) **and** stay positive across neighbouring parameters.

**Kept (passes the screen, the permutation test and the neighbour check):**

| Rule | IS (n, PF, $/trade) | OOS (n, PF, $/trade) | p |
|---|---|---|---|
| FOMC: at 14:15, fade a 14:00-14:15 move of at least 0.10 ADR. Target the 13:59 price, stop = same distance, flat 16:00. | 17, 1.36, +27 | 8, 3.61, +112 | <0.001 |
| FOMC press conference: the same, on 14:30-14:45 | 21, 1.19, +15 | 9, 5.94, +159 | <0.001 |
| NFP: at 9:30, fade an 8:30-9:30 move of at least 0.10 ADR. Stop 0.25 ADR, exit 15:55. | 26, 3.25, +124 | 17, 1.49, +59 | <0.001 |
| NFP: the same, entered at 9:00 (fade the 8:30-9:00 move) | 28, 2.55, +109 | 17, 2.63, +155 | <0.001 |
| CPI: at 8:45, fade an 8:30-8:45 move of at least 0.10 ADR, target the 8:29 price (overlaps the NEWS module) | 32, 1.58, +42 | 15, 1.44, +33 | <0.001 |
| Retail Sales, next day: at 9:30, trade against the Retail-day move (8:29 to close, at least 0.2 ADR). Stop 0.5 ADR, exit 15:55. | 26, 1.65, +58 | 21, 2.04, +128 | 0.047 |

**Kept as "do not do this":**

| Rule | IS PF | OOS PF | p |
|---|---|---|---|
| Follow the FOMC 14:00-14:30 move to the close | 0.11 | 0.35 | <0.001 |
| Follow the CPI first hour to the close | 0.65 | 0.15 | 0.001 |
| Follow the FOMC-minutes 30-min move | 0.57 | 0.08 | 0.003 |
| Chase the first 5-min candle, pooled over 13 events (n 461) | 0.71 | 0.66 | n.a. (clean days 1.03) |
| Fade ISM to the 9:59 price | 0.70 | 0.74 (Mfg); 0.68 / 0.87 for Services | 0.2, so "no edge" rather than "anti-edge" |

**Pooled families** (all 13 events vs clean days at 8:30, 10:00 and 14:00, all periods):

| Family | Events PF | Clean-day PF |
|---|---|---|
| Fade to F at +15 | 1.29 | 0.89 |
| Fade at +60 to the close | 1.29 | 0.82 |
| Follow at +30 | 0.92 | 1.08 |
| Next-day fade | 1.25 | 1.01 |

News days reward fading. Normal days reward following a little.

---

## 4. Avoid-trading rules for our existing strategies (`avoid.py`, `avoid_min.py`)
The strategies are V4+, D2, Pinball, H2 and TDP, built as in `scripts/lab/news_test.py`: 857 trades, PF 1.60 IS / 1.52 OOS.

- **FOMC-minutes days are the one clear avoid.**
  - All strategies: 26 trades, PF 0.16 / 0.36, -$2,782 in total.
  - The losses are mostly **before** 14:00: trades closed before 13:55 lost -$2,090. So this is not a release-spike problem. These are chop days.
  - D2 on minutes days: 9 trades, 1 winner, -$2,114. TDP: 7 trades, PF 0.30 / 0.63.
  - **Recommendation:** add FOMC_MIN days to D2's existing FOMC/CPI skip, and consider half size for TDP. This is a small sample (9 D2 trades), but cheap to apply and consistent with the day-range finding.
- **10:00 releases (ISM, JOLTS):**
  - Entries 9:45-10:15 on those days: PF 1.54 (n 16) vs 2.02 on other days.
  - V4+ trades open across 10:00: PF 1.29 (n 9) vs 3.55 on other days.
  - Skipping entries 9:50-10:05 removes winners (+$562). **No rule.**
- **FOMC days:** trades still open at 14:00 do well (PF 2.58). Skipping FOMC days removes winners. **No rule.**
- **Day after FOMC:** skipping it helps OOS (+$1,069 saved) but would have cost $1,968 IS. **No rule.**
- **CPI, PPI, Retail and JOLTS days are good for our strategies.** Keep trading them.

---

## 5. What others say, graded against our data

| Claim | Source | Grade | Our data |
|---|---|---|---|
| Since 2020, Powell press conferences tend to **reverse** the statement reaction; volatility is about 3x higher during them | Narain & Sangani, VoxEU/CEPR 2023 ([link](https://cepr.org/voxeu/columns/market-impact-fed-press-conference)) | A- (academic, recent) | **Agrees.** Following the statement loses (PF 0.20), fading to F wins, and the press-conference fade wins. |
| Stocks drift up in the 24h before FOMC | Lucca & Moench 2015, NY Fed / Journal of Finance ([link](https://econpapers.repec.org/RePEc:fip:fednsr:512)) | A | **Partly.** +0.34 ADR, up 75% in 2022-24 (long 9:30 to 13:55: PF 2.82). In 2025-26 it was flat (PF 0.23). |
| The pre-FOMC drift disappeared after 2015 | Kurov, Wolfe & Gilbert, Finance Research Letters 2021 ([link](https://ideas.repec.org/a/eee/finlet/v40y2021ics1544612320315956.html)) | A | Consistent with our 2025-26 result: **do not trade it.** |
| NFP is the most significant mover; ISM has the biggest range; GDP and Retail Sales matter little | CME Group "Impact of Economic Indicators" (E-mini S&P, 2007-2013) ([link](https://www.cmegroup.com/education/files/impact-of-economic-indicators.pdf)) | B (old, S&P only, vendor) | **Mostly agrees.** CPI is now bigger than NFP (post-2022 inflation regime). Retail is nearly a non-event at 8:30. GDP has n=19. |
| Core PCE is muted because economists nowcast it from CPI and PPI components | Sell-side practice (Newsquawk and MNI previews) | B | **Agrees.** The first 5m is 0.10 ADR vs 0.34 for CPI. |
| "Wait for the second move" after FOMC | Practitioner forums, YouTube, prop-firm blogs | C | **Half true.** Waiting is right: the first candle is a coin flip and chasing it loses. But the second move has no direction edge (53%). The edge is the return to the pre-release price. |
| The pre-release price is "fair"; trade the reversion (JJ Simon) | Practitioner | C | **Supported** on CPI and FOMC (fade to F wins). Not on ISM, where fading loses. |

---

## 6. What failed (honest list)
- **Pre-release drift** (follow the 60-min drift into the release): PF 0.81 pooled. It only "works" on JOLTS (1.78 / 1.40, p not tested), which is likely noise.
- **Following the 30-min or 60-min reaction:** loses on CPI, FOMC and minutes. Mixed or insignificant on PPI, PCE, ISM and JOLTS.
- **PCE follow60** (1.68 / 1.83): p=0.065, not good enough. **JOLTS follow30 2R** (1.56 / 1.46): p=0.19.
- **Next-day FOMC reversal:** PF 1.21, p=0.30. Depends on settings: some stop sizes lose.
- **Long into FOMC (pre-FOMC drift):** IS PF 2.82, OOS 0.23. Dead.
- **"Morning trend continues after the release"** (enter at T in the 9:30-to-T direction): 0.97 pooled, worse than clean days (1.10).
- **NFP and CPI next-day fades:** strongly positive OOS, flat or negative IS. Not stable.
- **ISM, JOLTS and testimony:** nothing tradable. The dates are partly approximate, so their numbers are the noisiest.
- **Avoid windows at 10:00, around FOMC 14:00, and on the day after FOMC:** none improve the existing strategies.
- **Sample sizes are small:** FOMC 38 days, so a rule has 25-30 trades. Even the kept rules carry wide error bars. A PF of 1.4-1.8 with n 25-45 should be traded small, at most 1 MNQ, until live results confirm it.

## 7. Files
- `scripts/news2/build_dates.py`: builds `data/macro_dates_ext.csv`
- `scripts/news2/validate_dates.py`: spike-ratio check of the dates
- `scripts/news2/common.py`: loaders and stats helpers
- `scripts/news2/measure.py`: section 2 (to `knowledge/src/red_folder_measure.txt`)
- `scripts/news2/trades.py`: section 3 (`red_folder_trades.txt`)
- `scripts/news2/null.py`: false-positive rate of the screen
- `scripts/news2/robust.py`: permutation p-values, neighbours, pooled families (`red_folder_robust.txt`)
- `scripts/news2/avoid.py`, `avoid_min.py`: section 4 (`red_folder_avoid*.txt`)
- `scripts/news2/prefomc.py`: pre-FOMC drift (`red_folder_prefomc.txt`)
- `scripts/news2/dayrange.py`: day range by event (`red_folder_dayrange.txt`)

**Possible next steps:**
- Add FOMC_MIN to D2's skip list in the engine and the Pine script.
- Add the FOMC 14:15 and press-conference fade-to-F as a NEWS-module extension (same trigger logic as the 8:30 version, on 1m bars).
- Show "NFP: fade the 8:30-9:30 move" and "post-Retail: fade" as bias labels on the chart.
