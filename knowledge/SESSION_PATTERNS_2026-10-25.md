# MNQ Session Patterns outside our trading hours (2026-10-25)

Goal: find repeatable patterns in the windows our current strategies do not trade (weeknight Asia, 00:00-03:00, London, pre-market, midday, afternoon, post-close, Sunday evening beyond the gap fill) and turn the survivors into mechanical rules.

## Setup

- Data: `data/raw/mnq_eth_5m.txt` (5m ETH bars, session key = date the session ends; 18:00 prior evening to 16:55). 1,195 full sessions with an ADR, 2022-01 to 2026-10-20.
- ADR = mean of the prior 10 RTH (9:30-16:00) ranges, computed from the 5m bars (the `day_features.json` file has no `adr` field, so `common.py` builds it). Known before the session opens. Median ADR: IS 237 pts, OOS 325 pts.
- Costs on every trade, 1 MNQ: 2 x $2.37 commission + 1 tick slippage per side (0.5 pt round turn). Total about $5.74 per trade, or 2.9 pts.
- Fills: market entries at the next 5m bar open after the signal bar closes. Limit fills at the level. If stop and target are both inside one bar, the stop is assumed (conservative). Stops that gap fill at the bar open. Time exits at the close of the last bar before the exit time.
- IS = 2022-2024, OOS = 2025-01 to 2026-10. "years" column = sign of net P&L for 2022, 2023, 2024, 2025, 2026.
- Pass rule set before looking: IS n >= 60, OOS n >= 30, PF > 1.15 in both, and the neighbouring parameter cells must not collapse.

Scripts (all in `scripts/sessions/`):

| File | What it does | Output |
|---|---|---|
| `common.py` | loader, slot clock (slot 0 = 18:00), ADR, trade simulator, stats, IS/OOS split | |
| `q1_drift.py` | mean move per window, IS/OOS, weekday | console |
| `q2_tests.py` | 250 rule variants across 11 question families (all printed, losers included) | `out_q2.txt`, `out_q2.md` |
| `q3_refine.py` | neighbourhood grids around the families that were not dead | `out_q3.txt` |
| `q4_desc_and_final.py` | base rates (sweep frequency, sign agreement), lunch-range break, final candidate stats per year | `out_q4.txt` |
| `q5_checks.py` | robustness of the afternoon candidate (side split, overnight filter, exit time, threshold/stop grid) | `out_q5.txt` |
| `q6_research.py` | the six setups proposed in `knowledge/RESEARCH_OFF_HOURS_MNQ.md` (M1, M2, L3, L2, A1/L1, M3), with shifted-window baselines for L2/L3 | `out_q6.txt` |
| `q7_selloff_grid.py` | neighbourhood grid and mirror test for the sell-off overnight long (A1) | `out_q7.txt` |

## Headline

The overnight is close to efficient for simple rules after costs. Of 250 first-pass variants only one cleared the pass rule (a weekday effect, which I do not trust). Two families hold up in both periods, in every year, and across their parameter neighbourhood:

1. **Sell-off overnight long (Q13, R5):** after an RTH day that closed down with a weak last hour (15:00-16:00 <= -0.15 ADR), go long at 18:05 (or 01:30) and exit 03:30. PF 1.39 IS / 1.32 OOS, every year positive, about 36 trades/year, maxDD $1,792. This is the NY Fed closing-imbalance reversal (Boyarchenko, Larsen, Whelan). The mirror (short after a strong rally hour) does not work, which matches the paper's sell-side asymmetry.
2. **Afternoon trend continuation (Q7):** 13:00 to 15:55 in the direction of the 9:30-13:00 move. PF 1.27 IS / 1.23 OOS, about 195 trades/year, but thin in quiet years.

Everything else failed in-sample, out-of-sample, or both: Asia range sweeps (ours and the research version), session ORBs, prior-day high/low tests, London-to-pre-market persistence, London Partial continuation, Sunday follow-through, last-half-hour momentum, the Zarattini noise area, and the post-lunch long.

## Q1. Is there unconditional drift in any window?

Mean move from window open to window close, all sessions (pts, % of ADR, % up days, t-stat).

| Window | IS mean pt | IS %ADR | IS up% | IS t | OOS mean pt | OOS %ADR | OOS up% | OOS t |
|---|---|---|---|---|---|---|---|---|
| 18:00-20:00 | -0.7 | -0.2 | 51% | -0.3 | +5.6 | +1.8 | 54% | +1.5 |
| 20:00-24:00 | +1.4 | +0.4 | 53% | +0.8 | +1.0 | +0.5 | 54% | +0.5 |
| 00:00-03:00 | +0.1 | 0.0 | 50% | 0.0 | +2.4 | +0.4 | 55% | +0.5 |
| 03:00-06:00 | +1.0 | +0.5 | 51% | +0.7 | +1.8 | +0.4 | 53% | +0.4 |
| 06:00-08:30 | +0.9 | +0.4 | 52% | +0.6 | +0.7 | +0.6 | 52% | +0.5 |
| 08:30-09:30 | -2.1 | -0.9 | 47% | -1.0 | -1.1 | -0.4 | 50% | -0.4 |
| 12:00-14:00 | 0.0 | +0.1 | 53% | +0.1 | +5.8 | +0.6 | 54% | +0.4 |
| 14:00-15:00 | +0.7 | +0.3 | 54% | +0.4 | -3.0 | -0.8 | 48% | -0.8 |
| 15:00-16:00 | -1.1 | -0.6 | 51% | -0.6 | +0.2 | +0.2 | 51% | +0.2 |
| 16:00-16:55 | +1.4 | +0.8 | 51% | +1.4 | +1.9 | +0.4 | 49% | +0.5 |
| 18:00-09:30 overnight | +0.5 | +0.2 | 51% | +0.2 | +10.8 | +3.5 | 56% | +1.4 |

Result: no window has a drift larger than the 2.9 pt round-turn cost with any statistical weight. The "overnight drift" is +0.5 pt in 2022-2024 (bear year included) and +10.8 pt in 2025-2026; not a stable edge. Weekday breakdown (all years, %ADR, 18:00-09:30): Mon key +5.7, Tue -5.8, Wed +4.3, Thu +3.5, Fri +0.2. See Q11.

## Q2. Is the Asia range (20:00-02:00) swept at London and does it revert?

Base rates (days where 02:00-03:00 stays inside the Asia range):

| | IS | OOS |
|---|---|---|
| days | 307 | 211 |
| London (03:00-06:00) trades beyond one side | 84% | 72% |
| trades beyond both sides | 13% | 4% |
| one-side sweeps that revisit Asia mid by 9:25 | 60% | 51% |
| one-side sweeps still beyond the swept side at 9:25 | 52% | 59% |

Trades (selected; full table in `out_q2.md`, section A/A2):

| Test | IS n | IS PF | IS avg pt | OOS n | OOS PF | OOS avg pt | years |
|---|---|---|---|---|---|---|---|
| fade back inside, stop beyond sweep, tgt Asia mid, win 3-6, exit 8:00 | 111 | 0.58 | -1.8 | 63 | 0.87 | +0.7 | ----+ |
| same, stop 0.15 ADR | 111 | 0.75 | -1.7 | 63 | 0.71 | -5.8 | +---- |
| fade, range 18:00-02:00, win 3-6, stop beyond sweep | 123 | 0.67 | -0.8 | 75 | 0.97 | +1.9 | ----+ |
| break (close outside), 1:1 at half-range, exit 9:25 | 244 | 0.84 | -0.6 | 139 | 1.04 | +3.7 | ----+ |
| break, range 18:00-02:00, exit 9:25 | 273 | 0.94 | +1.2 | 147 | 0.92 | -0.2 | ----+ |

Result: FAILED. London does take a side most days, but the side it takes is a coin flip for the rest of the night. The sweep-and-reclaim fade has a 22-28% win rate with stops beyond the sweep wick; widening the stop to 0.15 ADR lifts win rate to 58% but the losers are bigger. The break-and-go version is also below PF 1.

## Q3. Session opening-range breakout vs fade (18:00, 20:00, 21:00, 03:00, 06:00, 08:00, 12:00, 14:00)

48 variants: OR 15 or 30 min, hold 2h or 4h, break with 1R target, break with time exit only, fade the failed break back to the other side of the OR.

| Open | Best IS PF (variant) | its OOS PF | Best OOS PF (variant) | its IS PF |
|---|---|---|---|---|
| 18:00 | 0.85 (break OR30 4h 1R) | 0.83 | 1.05 (break OR15 2h no tgt) | 0.64 |
| 20:00 | 0.70 (break OR30 4h 1R) | 0.85 | 1.03 (break OR15 4h 1R) | 0.68 |
| 21:00 | 0.84 (break OR15 2h no tgt) | 0.83 | 1.11 (break OR30 4h no tgt) | 0.83 |
| 03:00 | 0.87 (fade OR30 4h) | 0.79 | 1.04 (break OR30 2h 1R) | 0.85 |
| 06:00 | 0.89 (break OR30 4h 1R) | 0.86 | 1.02 (break OR15 4h no tgt) | 0.77 |
| 08:00 (all days, news not filtered) | 1.03 (break OR15 4h no tgt) | 0.80 | 0.90 (break OR30 4h 1R) | 0.89 |
| 12:00 | 1.12 (fade OR15 230m) | 0.99 | 0.99 (same) | 1.12 |
| 14:00 | 0.95 (break OR15 2h no tgt) | 0.75 | 0.98 (fade OR30 2h) | 0.76 |

Result: FAILED everywhere. No session open has an ORB or ORB-fade edge that survives costs in either period. Night ORBs lose mostly to costs: the median 30-min night range is small, so a stop at the other side of the range plus 2.9 pts of costs is a large fraction of risk.

## Q4. Mean reversion to the 18:00 open / running TWAP at night

No volume in the ETH file, so a running TWAP of (H+L+C)/3 from 18:00 stands in for VWAP. Trigger: first 5m close at least k x ADR from the reference inside the window; fade to the reference, stop 0.15 ADR, time exit.

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| fade 18:00 open, 20:00-02:00, k0.2 | 382 | 0.73 | 336 | 0.72 | ----- |
| fade 18:00 open, 20:00-02:00, k0.3 | 199 | 0.89 | 227 | 0.86 | -+--- |
| fade TWAP, 20:00-02:00, k0.3 | 59 | 1.11 | 124 | 0.93 | --++- |
| fade 18:00 open, 18:30-24:00, k0.2 | 334 | 0.61 | 319 | 0.68 | ----- |
| go with stretch, TWAP, 18:30-24:00, k0.2 | 157 | 0.97 | 206 | 1.19 | --+++ |
| fade TWAP, 00:00-03:00, k0.3, exit 4:00 | 62 | 1.16 | 109 | 1.07 | +--++ |
| fade TWAP, 00:00-03:00, k0.35, stop 0.25, exit 4:00 | 34 | 1.65 | 84 | 1.45 | ++-++ |
| fade 18:00 open, 03:00-06:00, k0.3, exit 7:00 | 362 | 0.97 | 273 | 1.07 | +--+- |

Result: FAILED as a general rule. Evening stretches do not revert (fading them is the worst thing tested). There is a thin pocket after midnight: when price is 0.3-0.4 ADR away from the session TWAP between 00:00 and 03:00, a fade to TWAP is mildly positive in both periods, but only at large k where IS n drops to 20-34 (below our n >= 60 rule). Watchlist only (W3 below).

## Q5. Does the overnight direction persist into RTH?

Sign agreement of 18:00->9:30 with later windows:

| Pair | IS | OOS |
|---|---|---|
| overnight vs 9:30-16:00 | 50% | 47% |
| overnight vs 9:30-10:00 | 50% | 50% |
| overnight vs 12:00-15:55 | 55% | 53% |
| overnight vs 14:00-15:55 | 53% | 53% |

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| go with overnight 12:00-15:55 | 743 | 1.04 | 448 | 0.92 | --+-+ |
| go with overnight (>= 0.3 ADR) 12:00-15:55 | 319 | 0.86 | 228 | 1.21 | --+-+ |
| go with overnight 14:00-15:55 | 743 | 0.98 | 448 | 0.91 | --+-+ |

Result: FAILED as a standalone signal; overnight direction says nothing about the RTH session as a whole. It is useful as a filter on the afternoon continuation (S1A).

## Q6. Intraday momentum: does the last 30 min follow the day? (Gao et al.)

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| prior close -> 10:00 sign, trade 15:30-15:55 | 724 | 0.72 | 432 | 0.95 | ----+ |
| same, only if move >= 0.3 ADR | 387 | 0.86 | 261 | 1.07 | ----+ |
| 9:30 -> 15:30 sign, trade 15:30-15:55 | 747 | 0.86 | 448 | 0.80 | +---- |
| 15:00 -> 15:30 sign, trade 15:30-15:55 | 745 | 0.78 | 446 | 0.81 | +---- |
| 9:30 -> 15:00 sign, trade 15:00-15:55 | 746 | 1.05 | 448 | 0.94 | ++-+- |
| same, only if >= 0.3 ADR | 454 | 1.17 | 291 | 0.88 | ++-+- |

Result: FAILED. The published "first half hour predicts last half hour" effect does not survive costs on MNQ 2022-2026; a 25-minute hold is too short to beat 2.9 pts. The momentum that does exist needs an earlier entry and a longer hold (Q7).

## Q7. Midday: does the morning direction continue or revert after 12:00?

Base rate: 9:30->13:00 has the same sign as 13:00->15:55 on 55% (IS) / 56% (OOS) of days. Reversal tests are uniformly negative (PF 0.66-0.96 in every cell). Continuation grid, signal = 9:30 open to entry time, exit 15:55 (`out_q3.txt`):

| Entry | thr (ADR) | stop | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|---|---|
| 12:00 | 0 | none | 747 | 1.11 | 448 | 1.21 | +--++ |
| 12:30 | 0.2 | none | 510 | 1.16 | 320 | 1.29 | ++-++ |
| 12:30 | 0.2 | 0.25 | 510 | 1.14 | 320 | 1.22 | ++-++ |
| 13:00 | 0 | 0.25 | 747 | 1.12 | 448 | 1.15 | ++-++ |
| 13:00 | 0.1 | 0.35 | 634 | 1.21 | 382 | 1.21 | ++-++ |
| **13:00** | **0.15** | **0.35** | **573** | **1.27** | **350** | **1.23** | **+++++** |
| 13:00 | 0.2 | none | 516 | 1.21 | 315 | 1.23 | ++-+- |
| 13:00 | 0.2 | 0.35 | 516 | 1.28 | 315 | 1.15 | ++++- |
| 13:00 | 0.3 | 0.35 | 415 | 1.29 | 258 | 1.10 | ++-+- |
| 13:30 | 0.2 | none | 522 | 1.32 | 328 | 1.11 | ++-+- |
| 14:00 | 0 | none | 746 | 1.03 | 448 | 1.23 | +--++ |
| 14:00 | 0.2 | none | 538 | 1.26 | 335 | 1.02 | ++-+- |
| 14:30 | 0.4 | none | 366 | 1.18 | 217 | 1.18 | +--++ |

Checks (`out_q5.txt`, 13:00 entry):

| Check | IS PF | OOS PF |
|---|---|---|
| longs only (thr 0.2, no stop) | 1.11 | 1.35 |
| shorts only (thr 0.2, no stop) | 1.31 | 1.12 |
| overnight agrees with morning | 1.34 | 1.27 |
| overnight disagrees | 1.10 | 1.20 |
| exit 15:00 instead of 15:55 | 0.99 | 0.95 |
| exit 15:30 | 1.18 | 1.13 |

Result: PASSED. The surface is positive in almost every cell in both periods, works for longs and shorts, and the profit is earned mostly in the last hour (exit at 15:00 kills it). Weakness: it is regime-dependent. 2022 and 2025 (high-volatility trending years) carry most of the money; 2023, 2024 and 2026 are near breakeven (PF 1.02-1.11).

Variant tried and FAILED: lunch-range (12:00-14:00) breakout after 14:00 with the day's direction, stop at range mid: IS PF 1.04, OOS 0.78. Range 12:00-13:00 break: IS 1.08, OOS 0.72. The continuation is a hold, not a breakout.

## Q8. Prior-day RTH high/low tested overnight

Base rate (18:00 opens inside the prior RTH range): the prior high or low is touched before 9:25 on 65% (IS) / 76% (OOS) of days, and 63% / 71% of touches extend at least 0.15 ADR beyond the level.

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| fade first touch 18:00-03:00, stop 0.1 / tgt 0.15 ADR | 253 | 0.72 | 188 | 0.65 | ----- |
| fade first touch 18:00-03:00, stop 0.2 / tgt 0.2 | 253 | 1.00 | 188 | 0.83 | +-+-- |
| fade first touch 03:00-09:25, stop 0.2 / tgt 0.2 | 274 | 0.79 | 165 | 1.17 | ---++ |
| break first touch 18:00-09:25, stop 0.15 / tgt 0.3 | 410 | 0.72 | 272 | 0.69 | ----- |
| break first touch 03:00-09:25, stop 0.15 / tgt 0.3 | 274 | 0.82 | 165 | 0.51 | ----- |

Result: FAILED. Prior-day levels are usually exceeded overnight (so fading the touch loses) but the extension is not large or fast enough to pay a break-and-go either.

## Q9. Pre-market (06:00-09:30): does London or the overnight trend continue?

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| go with 03:00->06:00, hold 06:00-09:25 | 745 | 0.88 | 447 | 1.14 | ----+ |
| fade 03:00->06:00 | 745 | 0.92 | 447 | 0.75 | ----- |
| go with 18:00->06:00 (>= 0.3 ADR), hold 06:00-09:25 | 220 | 0.89 | 187 | 1.24 | -++-+ |
| go with 18:00->08:30, 08:30-09:25, no-news days | 638 | 0.86 | 387 | 0.80 | -+--- |
| fade 18:00->08:30, 08:30-09:25, no-news days | 638 | 0.78 | 387 | 0.91 | +---- |

Result: FAILED. Pre-market continuation looks good only in 2025-2026 (an uptrend), not in 2022-2024.

## Q10. Sunday evening beyond the gap fill (Monday-keyed sessions only)

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| go with Sun 18:00->20:00, hold 20:00-03:00 | 136 | 0.78 | 86 | 0.70 | --++- |
| fade Sun 18:00->20:00, hold 20:00-03:00 | 136 | 0.98 | 86 | 1.25 | ++--+ |
| fade Sun 18:00->24:00, hold 00:00-09:25 | 137 | 1.19 | 86 | 0.75 | ++--+ |
| fade Sun 18:00->20:00 (>= 0.1 ADR), 20:00-03:00 | 73 | 0.77 | 59 | 1.22 | +---+ |
| long Sun 18:00 -> Mon 09:25 | 137 | 0.83 | 86 | 2.00 | --+++ |
| long Sun 20:00 -> Mon 03:00 | 137 | 0.78 | 86 | 1.08 | +--++ |

Result: FAILED. Nothing after the gap fill holds in both halves; the long-Sunday-night result is a 2025-2026 bull-market artifact.

## Q11. Prior RTH day direction into the evening, and the post-close hour

| Test | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| go with prior RTH open->close, 18:00-20:00 | 722 | 0.80 | 430 | 0.97 | --+-+ |
| fade prior RTH day, 18:00-09:25 | 722 | 0.96 | 430 | 1.14 | ++-++ |
| fade prior RTH day >= 0.75 ADR, 18:00-09:25, stop 0.3 ADR | 191 | 0.96 | 100 | 1.17 | -++++ |
| go with 15:00->16:00, hold 16:00-16:55 | 745 | 0.78 | 447 | 0.89 | --+-- |
| fade 15:00->16:00, hold 16:00-16:55 | 745 | 0.77 | 447 | 0.80 | ----- |

Result: FAILED (IS PF below 1). The fade-big-days idea is positive four years out of five but lost 2022 badly; not enough to trade.

## Q12. Day-of-week overnight holds (long 18:00 -> 09:25)

| Session key | IS n | IS PF | OOS n | OOS PF | years |
|---|---|---|---|---|---|
| Mon (Sunday night) | 137 | 0.83 | 86 | 2.00 | --+++ |
| Tue (Monday night) | 155 | 0.89 | 94 | 0.63 | +---- |
| Wed (Tuesday night) | 153 | 1.17 | 92 | 1.55 | +++++ |
| Thu (Wednesday night) | 152 | 1.14 | 88 | 0.97 | -+++- |
| Fri (Thursday night) | 150 | 0.79 | 88 | 0.94 | -+--- |

Result: the Tuesday-night long is the only cell in the whole 250-variant first pass that met the pass rule. With 250 variants one pass is what chance alone would produce, and there is no mechanism for it. Watchlist only (W2).

## Q13. Setups proposed by the web research (`knowledge/RESEARCH_OFF_HOURS_MNQ.md`)

Same engine, same costs, rules as written in the research file. 5m bars, so "exit 15:59" = close of the 15:55 bar. Late 2021 is shown in the per-year lines where it is available (all of our data is 2021+, so the "report 2021+ separately" request is the whole sample; 2021 has only 7-15 trades per test).

### R1. Last-half-hour momentum (W4-M1, Baltussen form)

At 15:30, R = price at 15:30 minus the prior RTH close. If |R| >= 0.15 ADR, enter in the sign of R at 15:30, stop 0.12 ADR, exit 15:59.

| Test | IS n | IS win | IS PF | OOS n | OOS win | OOS PF | years |
|---|---|---|---|---|---|---|---|
| M1 thr 0.15, stop 0.12 | 589 | 41% | 0.91 | 367 | 36% | 0.68 | +---- |
| M1 thr 0.15, no stop | 589 | 48% | 0.89 | 367 | 41% | 0.65 | +---- |
| M1 thr 0.3, stop 0.12 | 495 | 41% | 0.89 | 299 | 36% | 0.67 | +---- |
| M1b Gao filter (sign 9:30-10:00 = sign 15:00-15:30) | 317 | 40% | 0.86 | 190 | 37% | 0.79 | +---- |
| M1c day range >= 1 ADR (gamma proxy) | 258 | 34% | 0.83 | 158 | 28% | 0.62 | +---- |

Result: FAILED. Positive only in 2022. Since 2023 the last half hour has, if anything, reversed the day on MNQ. A 30-minute hold cannot pay 2.9 pts of costs on a gross edge this small.

### R2. Afternoon noise-area breakout with VWAP trail (W4-M2, Zarattini)

Per-slot sigma = mean |close(slot)/open(9:30) - 1| over the prior 14 days; bands = max/min(open, prior close) x (1 +/- sigma); checks at 14:00, 14:30, 15:00, 15:30; trail = max(upper band, RTH VWAP) on 5m closes (VWAP is a TWAP proxy, no volume in the file); re-entry allowed at a later check; exit 15:59.

| Test | IS n | IS win | IS PF | OOS n | OOS win | OOS PF | years |
|---|---|---|---|---|---|---|---|
| M2 trail band + TWAP | 380 | 46% | 1.43 | 219 | 37% | 0.93 | ++--- |
| M2 trail band only | 331 | 48% | 1.46 | 178 | 38% | 0.98 | ++-+- |
| M2 14:00 check only | 217 | 43% | 1.01 | 125 | 42% | 1.10 | +--++ |

Per year (band + TWAP): 2022 PF 2.13, 2023 1.46, 2024 0.83, 2025 0.92, 2026 0.94. Result: FAILED OOS. It worked in 2022-2023 and has been flat to negative since 2024. Our simpler S1 hold (enter 13:00, no trail) holds up better OOS than the trailed breakout.

### R3. London Partial continuation (W3-L3) vs a shifted-window baseline

Asia 20:00-02:00, London 02:00-08:00. Partial Up = London broke the Asia high but not the low, and the 08:00 price is above the London mid. Long at 08:05, target London high + 1 tick, 1:1 stop, exit 11:00, skip if the target is < 0.04 or > 0.25 ADR away. Mirror for Partial Down. Baseline = the identical rule with both 6h windows shifted through the session.

| Test | IS n | IS win | IS PF | OOS n | OOS win | OOS PF | years |
|---|---|---|---|---|---|---|---|
| L3 as specified | 244 | 45% | 0.66 | 148 | 42% | 0.73 | --+-+ |
| L3 without room filter | 325 | 44% | 0.65 | 201 | 43% | 0.78 | --+-- |
| baseline, shift -2h (range from 18:00) | 281 | 52% | 0.77 | 176 | 56% | 1.22 | ----+ |
| baseline, shift +4h (range from 00:00) | 193 | 54% | 0.90 | 99 | 57% | 1.01 | -+--+ |
| pooled baseline (8 shifts) | 1652 | 50% | 0.82 | 974 | 50% | 0.94 | ----+ |

Result: FAILED, and worse than the baseline. The real London clock wins 42-45% at 1:1 against about 50% for the shifted windows. The "NY breaks the London high 80% of the time" statistic is geometry plus a long time window; once the target has to be hit before a 1:1 stop by 11:00, there is nothing left.

### R4. Asia range sweep-and-reclaim 02:00-05:00 (W3-L2) vs a shifted-window baseline

Sweep >= 0.02 ADR beyond the Asia high/low, a close back inside within 3 bars, enter on the next open, stop = sweep extreme + 0.02 ADR, half at the Asia mid, half at the far side, exit 08:00, first sweep only.

| Test | IS n | IS win | IS PF | OOS n | OOS win | OOS PF | years |
|---|---|---|---|---|---|---|---|
| L2 as specified | 296 | 35% | 0.68 | 146 | 31% | 0.79 | ----- |
| L2, any trade beyond the level | 450 | 28% | 0.59 | 247 | 27% | 0.70 | ----- |
| pooled baseline (10 shifted windows) | 3072 | 32% | 0.79 | 1859 | 31% | 0.87 | ----- |

Result: FAILED. The real Asia/London clock is no better than random 6h windows, and both lose. This matches Q2.

### R5. Sell-off evening / overnight long (W2-A1, W3-L1; closing-imbalance reversal)

Condition on the prior RTH session: 15:00-16:00 move <= -0.15 ADR (A1 also requires the RTH day to close down). Long, exit 03:30.

| Test | IS n | IS win | IS PF | OOS n | OOS win | OOS PF | years |
|---|---|---|---|---|---|---|---|
| **A1: day down too, long 18:05, stop 0.30 ADR** | **115** | **57%** | **1.39** | **58** | **50%** | **1.32** | **+++++** |
| A1, last hour only (no day filter) | 149 | 56% | 1.48 | 84 | 45% | 1.11 | +++++ |
| **A1b: day down too, long 01:30, stop 0.20 ADR** | **115** | **60%** | **1.45** | **58** | **47%** | **1.29** | **+++++** |
| L1: last hour only, long 01:30, stop 0.20 | 149 | 57% | 1.08 | 84 | 49% | 1.33 | +--++ |
| A1c: top-tercile ADR, long 18:05 | 39 | 54% | 1.43 | 33 | 55% | 1.59 | +++++ |
| L1, top-tercile ADR, long 01:30 | 51 | 59% | 0.98 | 46 | 52% | 1.47 | ++-++ |
| Mirror: short after 15:00-16:00 >= +0.15 ADR with day up, 18:05 | 109 | | 0.87 | 63 | | 0.43 | -+--- |
| Mirror, 01:30 entry | 109 | | 0.87 | 63 | | 1.24 | -+-++ |
| Unconditional long 18:00-03:00 (baseline, q3_refine.py) | 747 | 50% | 0.92 | 448 | 52% | 1.14 | --+++ |

A1 per year: late 2021 n 7 PF 0.86, 2022 PF 1.41, 2023 1.64, 2024 1.20, 2025 1.03, 2026 1.64. A1b: 2021 n 7 PF 2.69, 2022 1.77, 2023 1.16, 2024 1.13, 2025 1.05, 2026 1.61.

Neighbourhood (`out_q7.txt`, A1 with the day-down filter; threshold 0.10/0.15/0.20/0.25 ADR x entry 18:05/20:00/00:00/01:30 x stop x exit 03:30/06:00/09:25, 64 cells): every 18:05 and 01:30 cell is PF >= 1.19 in both periods except the 09:25 exits in IS (PF 0.99-1.12). The 20:00 entry is the weak spot (OOS PF 0.68-1.11 at 03:30/06:00 exits). The edge is in the first two hours after the reopen and again at 01:30-03:30, which matches the paper (Tokyo-open and 1:30-3:30 correction). Stopless versions score higher (PF 1.45-2.7) but carry gap risk overnight; keep the stop.

Result: PASSED. It is conditional (the unconditional overnight long is PF 0.92 IS), long-only (the mirror fails), has a published mechanism, and its neighbourhood is smooth. Caveats: n is small (OOS 58 trades), and 2025 was close to flat (PF 1.03).

### R6. Post-lunch long 12:00-14:00 (W4-M3)

| Test | IS n | IS win | IS PF | OOS n | OOS win | OOS PF | years |
|---|---|---|---|---|---|---|---|
| M3 long 12:00-14:00, stop 0.20 | 747 | 44% | 0.92 | 448 | 46% | 1.05 | -+++- |
| M3b only if 11:00-12:00 down | 329 | 44% | 0.91 | 207 | 43% | 0.88 | -+++- |
| M3c plus 11:00-12:00 short leg | 1494 | 41% | 0.82 | 896 | 43% | 0.98 | ---+- |

Result: FAILED. 2022 lost $4,702 (PF 0.70); 2023-2025 slightly positive; 2026 negative. The SPY lunch effect does not survive costs on MNQ. The midday window only works directionally (S1), not as a fixed long.

## What failed (summary)

- Asia range sweep fade and break at London: PF 0.58-0.97.
- All session ORBs and ORB fades (18:00, 20:00, 21:00, 03:00, 06:00, 08:00, 12:00, 14:00): best IS PF 1.12, never confirmed OOS.
- Evening stretch fades from the 18:00 open: PF 0.61-0.89, the worst family.
- Prior-day high/low fades and breaks overnight: PF 0.51-1.00.
- London-to-pre-market and overnight-to-8:30 persistence: positive only in 2025-2026.
- Last-30-min intraday momentum (Gao): PF 0.72-0.95 after costs.
- Midday reversal of the morning: negative everywhere. Lunch-range breakouts: OOS PF 0.72-0.78.
- Sunday follow-through or fade after 20:00: unstable between halves.
- Post-close 16:00-16:55: negative both ways.
- Research setups: last-half-hour momentum (OOS PF 0.62-0.79), Zarattini noise area (IS 1.43, OOS 0.93), London Partial continuation (PF 0.66/0.73, below its own random-window baseline), Asia sweep-and-reclaim 02:00-05:00 (PF 0.68/0.79, same as baseline), post-lunch long (0.92/1.05), and the short mirror of the sell-off reversal.

## Ranked shortlist

Ranked by robustness, not by dollars. S2, S2b, S1 and S1A are recommended for build. W1-W3 are not tradable as they stand; keep them on paper.

### S2. Sell-off evening long (recommended, rank 1)

- Condition (known at 16:00): prior RTH session closed below its 9:30 open, and the 15:00-16:00 move was <= -0.15 x ADR.
- Entry: long at the 18:05 bar open (the first 5m bar after the reopen closes).
- Stop: 0.30 x ADR below entry. Target: none. Time exit: 03:30 ET.
- Expected trades/year: about 36.
- Net results (1 MNQ, after costs): IS n 115, win 57%, +11.3 pt, PF 1.39, maxDD $758. OOS n 58, win 50%, +17.4 pt, PF 1.32, maxDD $1,573. 2022-2026 all positive (PF 1.41, 1.64, 1.20, 1.03, 1.64). Whole period n 173, PF 1.35, +$22.0/trade, maxDD $1,792.
- Source and mechanism: NY Fed SR917 closing-imbalance reversal. Long-only by design (the short mirror fails).

### S2b. Sell-off overnight long, 01:30 entry (recommended, alternative to S2)

- Same condition. Long at 01:30, stop 0.20 x ADR, exit 03:30.
- About 36 trades/year. IS n 115, win 60%, +8.3 pt, PF 1.45, maxDD $383. OOS n 58, win 47%, +10.3 pt, PF 1.29, maxDD $806. Every year positive. Whole period PF 1.37, +$13.2/trade, maxDD $1,040.
- Less money per trade than S2 but half the drawdown and a 2-hour hold. Choose S2 or S2b, not both (same signal, same night).


### S1. Afternoon trend continuation (recommended, rank 2)

- Window: 13:00-15:55 ET, every RTH day (half days skipped automatically by the data check).
- Signal: at the close of the 12:55 5m bar, move M = price - 9:30 open. Trade only if |M| >= 0.15 x ADR (ADR = mean of the prior 10 RTH ranges).
- Entry: market at the 13:00 bar open, long if M > 0, short if M < 0.
- Stop: 0.35 x ADR from entry (about 80-115 pts at current ADR).
- Target: none.
- Time exit: 15:55 (fits inside the existing flat-by-15:55 rule).
- Expected trades/year: about 195 (77% of days).
- Net results (1 MNQ, after costs): IS n 573, win 55%, +10.5 pt/trade, PF 1.27, maxDD $1,624. OOS n 350, win 53%, +11.1 pt/trade, PF 1.23, maxDD $3,178. Every year positive: 2022 PF 1.59, 2023 1.11, 2024 1.02, 2025 1.46, 2026 1.02. Whole period +$15,483, maxDD $3,178, average +$16.8/trade.
- Caveats: thin in quiet years (2023, 2024, 2026 near breakeven). 26% of trades stop out. The threshold/stop pair was picked from a 15-cell grid whose neighbours are all OOS PF 1.08-1.23, so expect live PF closer to 1.15 than 1.25.

### S1A. Afternoon continuation, overnight in agreement (recommended, rank 3, lower frequency)

- Same as S1, plus a filter: the overnight move (18:00 open -> 9:30) has the same sign as M.
- Expected trades/year: about 94.
- IS n 284, win 61%, +15.1 pt, PF 1.48, maxDD $1,271. OOS n 163, win 58%, +10.7 pt, PF 1.24, maxDD $2,364. Years: 2022 1.73, 2023 1.12, 2024 1.56, 2025 0.82, 2026 1.75. Whole period +$9,947, maxDD $2,717, +$22.3/trade.
- Use instead of S1 when one afternoon trade per day has to clear a higher bar, for example on a prop eval with a tight daily loss limit. The "disagree" half is still positive (IS 1.10, OOS 1.20), so the filter improves quality more than it reveals a separate edge.

### W1. Midnight TWAP stretch fade (watchlist)

- Window 00:00-03:00. Running TWAP of (H+L+C)/3 from 18:00. First 5m close at least 0.3 ADR from TWAP: fade at the next open, target TWAP, stop 0.15 ADR, exit 04:00.
- About 36 trades/year. IS n 62, PF 1.16; OOS n 109, PF 1.07; whole period PF 1.09, maxDD $1,441, +$4.9/trade. Too thin for the cost; better cells exist only at n < 60.

### W2. Tuesday-night long (watchlist, likely data-mined)

- Long at Tuesday 18:00 (Wednesday session), exit Wednesday 09:25, no stop.
- About 52 trades/year. IS n 153, PF 1.17; OOS n 92, PF 1.55; every year positive; maxDD $2,985 at 1 contract. No mechanism, 1 pass in 250 variants. Paper-track only.

### W3. Fade a big prior RTH day overnight (watchlist)

- If the prior RTH open->close move is at least 0.75 ADR, enter against it at 18:00, stop 0.3 ADR, exit 09:25.
- About 61 trades/year. IS n 191, PF 0.96; OOS n 100, PF 1.17; years -++++ (2022 lost $2,775). Fails IS.

## Notes for building S2

- Signal is fixed at 16:00: `lastHour = close(15:55 bar) - open(15:00 bar)`, `day = close(15:55 bar) - open(9:30 bar)`, both in points, ADR = mean of the prior 10 RTH ranges. If `lastHour <= -0.15*ADR and day < 0`, arm a long for the 18:05 bar open (S2) or 01:30 (S2b).
- It does not overlap any current strategy (all of them are flat by 15:55 and none trade the night). It does hold through the Tokyo open and, for S2, through the low-liquidity 18:00-20:00 period: check prop-firm rules on overnight holding before an eval.
- Next tests worth running: add the closing 15:50-16:00 bar to the imbalance proxy, and check real MOC imbalance data if it becomes available.

## Notes for building S1

- It needs only 5m bars and the 9:30 open, so it ports to Pine directly: `adr = ta.sma(rthRange, 10)[1]`, signal on the 12:55 bar close, one trade, `strategy.close` at 15:55.
- It overlaps nothing current: the trend-day pullback setups stop at 12:00, and S1 enters at 13:00. On days when a morning trade is still open at 13:00, decide on the portfolio rule (skip S1, or allow a second contract) before live use.
- A next step worth testing: the same continuation hold with an entry on the first afternoon pullback (instead of fixed 13:00) to cut the 0.35 ADR stop size. This was not tested here.

## Appendix A. All 250 first-pass variants (generated by q2_tests.py)

#### A Asia range swept at London: fade back to Asia mid

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fade rng2000-200 win300-600 x800 stop=sweep | 111 | 28% | -1.8 | 0.58 | 1039 | 63 | 25% | +0.7 | 0.87 | 596 | ----+ |
| fade rng2000-200 win300-600 x800 stop=0.15 | 111 | 58% | -1.7 | 0.75 | 1462 | 63 | 46% | -5.8 | 0.71 | 1601 | +---- |
| fade rng2000-200 win200-600 x800 stop=sweep | 320 | 22% | -1.3 | 0.58 | 2565 | 187 | 18% | -2.9 | 0.59 | 1987 | ----- |
| fade rng2000-200 win200-600 x800 stop=0.15 | 320 | 56% | -3.6 | 0.67 | 4215 | 187 | 44% | -8.6 | 0.63 | 4445 | ----- |
| fade rng2000-200 win300-600 x925 stop=sweep | 111 | 28% | -1.8 | 0.58 | 1039 | 63 | 25% | +0.7 | 0.87 | 596 | ----+ |
| fade rng2000-200 win300-600 x925 stop=0.15 | 111 | 58% | -2.2 | 0.73 | 1590 | 63 | 46% | -7.5 | 0.68 | 1754 | +---- |
| fade rng1800-200 win300-600 x800 stop=sweep | 123 | 28% | -0.8 | 0.67 | 1046 | 75 | 19% | +1.9 | 0.97 | 764 | ----+ |
| fade rng1800-200 win300-600 x800 stop=0.15 | 123 | 50% | -3.5 | 0.67 | 1762 | 75 | 40% | +0.3 | 0.93 | 1411 | ---+- |
| fade rng1800-200 win200-600 x800 stop=sweep | 291 | 22% | -0.7 | 0.67 | 2107 | 173 | 15% | -1.2 | 0.74 | 1633 | ----- |
| fade rng1800-200 win200-600 x800 stop=0.15 | 291 | 51% | -3.2 | 0.71 | 3477 | 173 | 39% | -6.0 | 0.74 | 4036 | ----- |
| fade rng1800-200 win300-600 x925 stop=sweep | 123 | 28% | -0.5 | 0.70 | 1046 | 75 | 19% | +1.9 | 0.97 | 764 | ----+ |
| fade rng1800-200 win300-600 x925 stop=0.15 | 123 | 50% | -4.5 | 0.64 | 2122 | 75 | 39% | -1.2 | 0.89 | 1465 | ----- |

#### A2 Asia range broken at London: go with break

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break rng2000-200 win300-600 x800 1:1 half-range | 244 | 47% | -2.3 | 0.74 | 3098 | 139 | 55% | +3.0 | 1.02 | 2428 | ----+ |
| break rng2000-200 win200-600 x800 1:1 half-range | 672 | 49% | -2.1 | 0.74 | 6492 | 366 | 52% | +0.0 | 0.92 | 4764 | ----+ |
| break rng2000-200 win300-600 x925 1:1 half-range | 244 | 48% | -0.6 | 0.84 | 2936 | 139 | 55% | +3.7 | 1.04 | 2188 | ----+ |
| break rng1800-200 win300-600 x800 1:1 half-range | 273 | 48% | -0.3 | 0.86 | 3414 | 147 | 46% | -3.1 | 0.83 | 3284 | +---+ |
| break rng1800-200 win200-600 x800 1:1 half-range | 620 | 48% | -1.9 | 0.78 | 6202 | 333 | 50% | +0.3 | 0.93 | 4049 | ----+ |
| break rng1800-200 win300-600 x925 1:1 half-range | 273 | 51% | +1.2 | 0.94 | 2328 | 147 | 50% | -0.2 | 0.92 | 2952 | ----+ |

#### B ORB 1800

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 657 | 41% | -1.2 | 0.61 | 4786 | 395 | 46% | +2.2 | 0.99 | 1636 | ----+ |
| break OR15 hold120 no tgt | 657 | 39% | -1.1 | 0.64 | 4734 | 395 | 45% | +3.2 | 1.05 | 1300 | ----+ |
| fade failed break OR15 hold120 | 451 | 34% | -0.2 | 0.63 | 2509 | 270 | 33% | -2.5 | 0.61 | 2647 | ----- |
| break OR15 hold240 1R | 723 | 51% | +0.1 | 0.82 | 3379 | 440 | 48% | -0.3 | 0.89 | 3961 | ----+ |
| break OR15 hold240 no tgt | 723 | 43% | +0.0 | 0.83 | 4104 | 440 | 41% | -1.3 | 0.87 | 4188 | ----- |
| fade failed break OR15 hold240 | 584 | 37% | -1.0 | 0.64 | 4054 | 354 | 38% | +0.5 | 0.88 | 2500 | ----- |
| break OR30 hold120 1R | 570 | 40% | -0.9 | 0.63 | 3725 | 354 | 47% | +1.1 | 0.91 | 2097 | ----+ |
| break OR30 hold120 no tgt | 570 | 39% | -0.7 | 0.65 | 3629 | 354 | 47% | +2.1 | 0.98 | 1475 | ----+ |
| fade failed break OR30 hold120 | 347 | 37% | +1.2 | 0.80 | 1389 | 228 | 34% | -2.0 | 0.62 | 2234 | +---- |
| break OR30 hold240 1R | 701 | 49% | +0.6 | 0.85 | 2928 | 433 | 49% | -2.2 | 0.83 | 5380 | ----- |
| break OR30 hold240 no tgt | 701 | 43% | -0.2 | 0.81 | 3999 | 433 | 43% | -3.5 | 0.80 | 6166 | ----- |
| fade failed break OR30 hold240 | 549 | 36% | -0.4 | 0.68 | 3158 | 341 | 37% | +1.8 | 0.96 | 1366 | ----- |

#### B ORB 2000

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 711 | 45% | -0.8 | 0.68 | 4759 | 428 | 51% | +2.5 | 1.01 | 1367 | ----+ |
| break OR15 hold120 no tgt | 711 | 40% | -0.9 | 0.69 | 5246 | 428 | 46% | +0.7 | 0.90 | 1970 | ----- |
| fade failed break OR15 hold120 | 490 | 42% | -1.1 | 0.53 | 3435 | 299 | 40% | -2.3 | 0.67 | 3174 | ----- |
| break OR15 hold240 1R | 741 | 45% | -1.5 | 0.68 | 5966 | 440 | 54% | +3.0 | 1.03 | 1921 | ---+- |
| break OR15 hold240 no tgt | 741 | 35% | -1.5 | 0.70 | 6620 | 440 | 45% | +0.6 | 0.93 | 2644 | ----- |
| fade failed break OR15 hold240 | 591 | 43% | -0.4 | 0.64 | 3651 | 342 | 40% | -2.1 | 0.72 | 3043 | ----- |
| break OR30 hold120 1R | 647 | 41% | -0.4 | 0.68 | 3878 | 397 | 48% | +0.2 | 0.87 | 1886 | ----- |
| break OR30 hold120 no tgt | 647 | 39% | -1.0 | 0.64 | 4701 | 397 | 47% | +0.1 | 0.86 | 1870 | ----- |
| fade failed break OR30 hold120 | 421 | 38% | -1.1 | 0.52 | 3342 | 267 | 36% | -0.6 | 0.77 | 1900 | ----- |
| break OR30 hold240 1R | 716 | 43% | -1.3 | 0.70 | 5781 | 429 | 50% | -1.0 | 0.85 | 3090 | ----- |
| break OR30 hold240 no tgt | 716 | 37% | -1.8 | 0.67 | 6735 | 429 | 48% | -0.5 | 0.88 | 3009 | ----- |
| fade failed break OR30 hold240 | 571 | 38% | -0.4 | 0.65 | 3970 | 339 | 36% | -0.5 | 0.82 | 2421 | ----- |

#### B ORB 2100

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 725 | 45% | +0.4 | 0.74 | 3073 | 437 | 47% | -1.5 | 0.76 | 4056 | ----- |
| break OR15 hold120 no tgt | 725 | 36% | +1.0 | 0.84 | 2996 | 437 | 43% | -0.5 | 0.83 | 3240 | +---- |
| fade failed break OR15 hold120 | 500 | 40% | -1.3 | 0.42 | 3677 | 320 | 46% | -0.1 | 0.78 | 2079 | ----- |
| break OR15 hold240 1R | 743 | 48% | -0.2 | 0.74 | 3883 | 446 | 49% | +0.7 | 0.91 | 2720 | ----+ |
| break OR15 hold240 no tgt | 743 | 34% | +0.0 | 0.79 | 4667 | 446 | 39% | +3.2 | 1.04 | 2802 | ----+ |
| fade failed break OR15 hold240 | 581 | 45% | -0.9 | 0.52 | 3895 | 363 | 49% | -0.3 | 0.79 | 2151 | ----- |
| break OR30 hold120 1R | 654 | 40% | +0.9 | 0.80 | 2456 | 398 | 48% | +1.1 | 0.91 | 2560 | +---+ |
| break OR30 hold120 no tgt | 654 | 38% | +1.1 | 0.84 | 2505 | 398 | 46% | +1.3 | 0.92 | 2652 | +---+ |
| fade failed break OR30 hold120 | 433 | 34% | -1.0 | 0.43 | 2949 | 272 | 40% | -1.0 | 0.70 | 1823 | ----- |
| break OR30 hold240 1R | 717 | 46% | +0.5 | 0.81 | 3590 | 440 | 53% | +3.2 | 1.04 | 2751 | ----+ |
| break OR30 hold240 no tgt | 717 | 40% | +0.5 | 0.83 | 3506 | 440 | 46% | +4.6 | 1.11 | 3207 | ----+ |
| fade failed break OR30 hold240 | 562 | 36% | -0.8 | 0.57 | 3795 | 350 | 38% | -1.6 | 0.72 | 3131 | ----- |

#### B ORB 0300

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 727 | 45% | -1.7 | 0.72 | 6656 | 441 | 51% | +2.2 | 0.99 | 1726 | ---+- |
| break OR15 hold120 no tgt | 727 | 40% | -1.6 | 0.74 | 7104 | 441 | 45% | +1.9 | 0.98 | 2177 | ---+- |
| fade failed break OR15 hold120 | 528 | 48% | +1.1 | 0.86 | 1807 | 306 | 45% | -1.3 | 0.73 | 2378 | ----- |
| break OR15 hold240 1R | 745 | 46% | -3.3 | 0.69 | 9308 | 448 | 51% | +1.0 | 0.94 | 2134 | ----- |
| break OR15 hold240 no tgt | 745 | 37% | -3.7 | 0.69 | 11007 | 448 | 39% | -1.7 | 0.85 | 4383 | ----- |
| fade failed break OR15 hold240 | 601 | 51% | +0.8 | 0.85 | 2281 | 355 | 47% | -1.8 | 0.74 | 3141 | ----- |
| break OR30 hold120 1R | 656 | 45% | +0.5 | 0.85 | 3556 | 413 | 49% | +3.2 | 1.04 | 1668 | ---++ |
| break OR30 hold120 no tgt | 656 | 43% | -0.3 | 0.79 | 4591 | 413 | 46% | +2.1 | 0.98 | 1857 | +---- |
| fade failed break OR30 hold120 | 439 | 38% | -0.0 | 0.74 | 2423 | 269 | 37% | -2.1 | 0.69 | 2689 | ----- |
| break OR30 hold240 1R | 723 | 44% | -1.8 | 0.76 | 6592 | 435 | 47% | -1.1 | 0.86 | 3207 | ----- |
| break OR30 hold240 no tgt | 723 | 39% | -2.7 | 0.72 | 9028 | 435 | 41% | -4.5 | 0.75 | 6292 | ----- |
| fade failed break OR30 hold240 | 568 | 42% | +1.0 | 0.87 | 2199 | 340 | 38% | -1.2 | 0.79 | 3102 | ----- |

#### B ORB 0600

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 741 | 46% | -0.3 | 0.77 | 4463 | 444 | 50% | +0.4 | 0.88 | 3036 | ----- |
| break OR15 hold120 no tgt | 741 | 36% | -0.9 | 0.74 | 5942 | 444 | 37% | -1.9 | 0.78 | 5180 | ---+- |
| fade failed break OR15 hold120 | 559 | 46% | -0.9 | 0.58 | 3693 | 335 | 49% | -1.4 | 0.67 | 2638 | ----- |
| break OR15 hold240 1R | 746 | 48% | -0.8 | 0.78 | 5408 | 447 | 51% | -0.4 | 0.87 | 3919 | ----- |
| break OR15 hold240 no tgt | 746 | 20% | -2.6 | 0.77 | 8678 | 447 | 23% | +3.1 | 1.02 | 4393 | ---+- |
| fade failed break OR15 hold240 | 642 | 52% | -0.9 | 0.64 | 4331 | 376 | 53% | -2.2 | 0.69 | 3719 | ----- |
| break OR30 hold120 1R | 710 | 45% | -0.0 | 0.79 | 4458 | 429 | 43% | -2.7 | 0.73 | 4752 | ----- |
| break OR30 hold120 no tgt | 710 | 41% | -0.4 | 0.77 | 5172 | 429 | 38% | -4.3 | 0.68 | 5854 | ----- |
| fade failed break OR30 hold120 | 493 | 45% | -0.2 | 0.68 | 2583 | 313 | 48% | -0.2 | 0.79 | 2034 | ----- |
| break OR30 hold240 1R | 746 | 50% | +0.4 | 0.89 | 3496 | 446 | 49% | -1.3 | 0.86 | 3889 | +---- |
| break OR30 hold240 no tgt | 746 | 26% | -1.2 | 0.85 | 7185 | 446 | 27% | +2.2 | 1.00 | 3523 | ---+- |
| fade failed break OR30 hold240 | 630 | 50% | +0.4 | 0.81 | 3042 | 391 | 50% | -0.0 | 0.85 | 3221 | ----- |

#### B ORB 0800

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 746 | 49% | +0.0 | 0.86 | 4907 | 446 | 47% | -3.5 | 0.79 | 5967 | +---- |
| break OR15 hold120 no tgt | 746 | 30% | +1.9 | 0.98 | 4031 | 446 | 28% | -5.5 | 0.78 | 8108 | ++--- |
| fade failed break OR15 hold120 | 516 | 53% | -1.3 | 0.67 | 3955 | 331 | 50% | -3.2 | 0.67 | 4241 | ----- |
| break OR15 hold240 1R | 746 | 49% | -0.4 | 0.84 | 5388 | 447 | 47% | -3.5 | 0.80 | 6007 | +---- |
| break OR15 hold240 no tgt | 746 | 21% | +3.1 | 1.03 | 4745 | 447 | 20% | -5.9 | 0.80 | 9112 | ++--- |
| fade failed break OR15 hold240 | 553 | 56% | -0.7 | 0.73 | 3731 | 358 | 52% | -4.7 | 0.62 | 5543 | ----- |
| break OR30 hold120 1R | 745 | 50% | +0.3 | 0.91 | 5163 | 436 | 49% | -1.3 | 0.89 | 4159 | ----- |
| break OR30 hold120 no tgt | 745 | 38% | +0.2 | 0.92 | 6065 | 436 | 35% | -5.2 | 0.81 | 8897 | ----- |
| fade failed break OR30 hold120 | 512 | 50% | -0.4 | 0.80 | 3892 | 303 | 49% | -1.3 | 0.81 | 2860 | --+-- |
| break OR30 hold240 1R | 747 | 51% | -0.6 | 0.89 | 6518 | 447 | 48% | -1.3 | 0.90 | 4574 | ----- |
| break OR30 hold240 no tgt | 747 | 29% | +3.0 | 1.02 | 5515 | 447 | 26% | -9.1 | 0.78 | 11763 | +-+-- |
| fade failed break OR30 hold240 | 569 | 54% | +0.9 | 0.90 | 3752 | 351 | 51% | -1.4 | 0.82 | 3673 | --+-- |

#### B ORB 1200

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 739 | 49% | -2.6 | 0.77 | 7723 | 441 | 49% | -2.4 | 0.83 | 5426 | ----- |
| break OR15 hold120 no tgt | 739 | 42% | -2.0 | 0.81 | 6894 | 441 | 44% | +0.6 | 0.94 | 5724 | ---+- |
| fade failed break OR15 hold120 | 541 | 50% | +1.6 | 0.94 | 3306 | 317 | 48% | +1.0 | 0.92 | 2262 | +--+- |
| break OR15 hold230 1R | 745 | 48% | -3.2 | 0.79 | 8940 | 447 | 47% | -1.5 | 0.88 | 5171 | ----- |
| break OR15 hold230 no tgt | 745 | 33% | -4.5 | 0.78 | 10811 | 447 | 37% | +1.4 | 0.97 | 5393 | ---+- |
| fade failed break OR15 hold230 | 603 | 54% | +3.9 | 1.12 | 2281 | 355 | 49% | +2.2 | 0.99 | 2347 | +--+- |
| break OR30 hold120 1R | 699 | 50% | +0.3 | 0.90 | 3833 | 411 | 48% | -0.8 | 0.88 | 4989 | -+--- |
| break OR30 hold120 no tgt | 699 | 48% | +0.7 | 0.92 | 3787 | 411 | 45% | +1.2 | 0.96 | 5836 | --++- |
| fade failed break OR30 hold120 | 453 | 44% | +1.7 | 0.95 | 1846 | 283 | 44% | -0.2 | 0.86 | 2170 | +---+ |
| break OR30 hold230 1R | 743 | 50% | -0.3 | 0.91 | 5534 | 439 | 46% | -2.9 | 0.86 | 7079 | ----- |
| break OR30 hold230 no tgt | 743 | 42% | +0.8 | 0.95 | 6187 | 439 | 39% | -0.6 | 0.93 | 8656 | --++- |
| fade failed break OR30 hold230 | 582 | 45% | +2.5 | 1.01 | 2727 | 356 | 44% | +1.8 | 0.97 | 1734 | +---+ |

#### B ORB 1400

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| break OR15 hold120 1R | 735 | 50% | -1.1 | 0.84 | 8194 | 442 | 51% | -4.4 | 0.77 | 6440 | -+--+ |
| break OR15 hold120 no tgt | 735 | 43% | +1.2 | 0.95 | 5359 | 442 | 41% | -6.0 | 0.75 | 8586 | -+--- |
| fade failed break OR15 hold120 | 539 | 49% | -0.3 | 0.82 | 3751 | 342 | 44% | -1.6 | 0.79 | 3418 | ----- |
| break OR15 hold115 1R | 733 | 48% | -2.2 | 0.79 | 9286 | 437 | 49% | -4.4 | 0.77 | 6387 | -+--+ |
| break OR15 hold115 no tgt | 733 | 41% | -1.0 | 0.86 | 7795 | 437 | 41% | -7.2 | 0.70 | 9045 | -+--- |
| fade failed break OR15 hold115 | 523 | 47% | -0.1 | 0.83 | 3526 | 335 | 45% | -0.9 | 0.82 | 3067 | ----- |
| break OR30 hold120 1R | 697 | 51% | +0.3 | 0.91 | 5789 | 414 | 48% | -2.5 | 0.83 | 4788 | -+--- |
| break OR30 hold120 no tgt | 697 | 47% | +1.0 | 0.94 | 4944 | 414 | 43% | -4.9 | 0.76 | 6952 | -+--- |
| fade failed break OR30 hold120 | 494 | 40% | -1.6 | 0.76 | 5168 | 303 | 42% | +2.0 | 0.98 | 1515 | ---+- |
| break OR30 hold115 1R | 685 | 48% | -0.6 | 0.86 | 6573 | 404 | 48% | -2.1 | 0.84 | 4239 | ----- |
| break OR30 hold115 no tgt | 685 | 45% | -1.0 | 0.85 | 7114 | 404 | 44% | -5.1 | 0.74 | 6536 | ----- |
| fade failed break OR30 hold115 | 475 | 40% | -1.7 | 0.75 | 4883 | 289 | 41% | +1.7 | 0.96 | 1299 | ----- |

#### C Night stretch from 18:00 open/TWAP

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fade open win2000-200 k0.2 stop.15 x300 | 382 | 42% | -2.9 | 0.73 | 4755 | 336 | 37% | -6.3 | 0.72 | 6694 | ----- |
| fade twap win2000-200 k0.2 stop.15 x300 | 188 | 41% | -0.9 | 0.84 | 1942 | 230 | 39% | -0.8 | 0.90 | 3637 | +---- |
| fade open win2000-200 k0.3 stop.15 x300 | 199 | 46% | +0.3 | 0.89 | 1243 | 227 | 37% | -1.9 | 0.86 | 4528 | -+--- |
| fade twap win2000-200 k0.3 stop.15 x300 | 59 | 47% | +4.6 | 1.11 | 565 | 124 | 33% | +0.2 | 0.93 | 3142 | --++- |
| fade open win1830-2400 k0.2 stop.15 x200 | 334 | 37% | -5.4 | 0.61 | 5625 | 319 | 35% | -7.5 | 0.68 | 6676 | ----- |
| fade twap win1830-2400 k0.2 stop.15 x200 | 157 | 41% | -2.0 | 0.79 | 1984 | 206 | 34% | -5.4 | 0.76 | 4473 | +---- |
| fade open win1830-2400 k0.3 stop.15 x200 | 161 | 39% | -4.1 | 0.70 | 2142 | 196 | 35% | -2.1 | 0.86 | 3669 | ----- |
| fade twap win1830-2400 k0.3 stop.15 x200 | 50 | 48% | +3.0 | 1.03 | 576 | 101 | 36% | -0.0 | 0.93 | 2442 | -+++- |
| fade open win0-300 k0.2 stop.15 x400 | 387 | 45% | +1.1 | 0.93 | 4173 | 330 | 37% | -4.7 | 0.76 | 4944 | --+-- |
| fade twap win0-300 k0.2 stop.15 x400 | 187 | 48% | +4.3 | 1.10 | 1212 | 221 | 36% | -5.4 | 0.74 | 4245 | +-+-- |
| fade open win0-300 k0.3 stop.15 x400 | 215 | 45% | +2.3 | 1.00 | 2231 | 224 | 37% | -1.7 | 0.86 | 2699 | --+-- |
| fade twap win0-300 k0.3 stop.15 x400 | 62 | 40% | +5.7 | 1.16 | 654 | 109 | 39% | +4.3 | 1.07 | 1441 | +--++ |
| fade open win300-600 k0.2 stop.15 x700 | 536 | 43% | -0.2 | 0.87 | 3344 | 368 | 45% | +4.2 | 1.07 | 3459 | ---+- |
| fade twap win300-600 k0.2 stop.15 x700 | 434 | 43% | -2.4 | 0.76 | 4209 | 285 | 39% | -3.2 | 0.80 | 3629 | ----- |
| fade open win300-600 k0.3 stop.15 x700 | 362 | 44% | +1.9 | 0.97 | 1367 | 273 | 41% | +4.2 | 1.07 | 2614 | +--+- |
| fade twap win300-600 k0.3 stop.15 x700 | 217 | 39% | -2.6 | 0.75 | 2420 | 178 | 37% | -0.7 | 0.90 | 2042 | ----- |

#### C2 Night stretch: go with

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont open win2000-200 k0.2 stop.15 x300 | 382 | 44% | -0.2 | 0.86 | 2579 | 336 | 43% | -0.6 | 0.90 | 2782 | --+-- |
| cont twap win2000-200 k0.2 stop.15 x300 | 188 | 47% | +0.8 | 0.92 | 1377 | 230 | 43% | +0.4 | 0.93 | 2377 | -++-- |
| cont open win2000-200 k0.3 stop.15 x300 | 199 | 42% | -0.9 | 0.84 | 2107 | 227 | 37% | -2.1 | 0.86 | 3587 | --+-- |
| cont twap win2000-200 k0.3 stop.15 x300 | 59 | 32% | -6.7 | 0.66 | 1192 | 124 | 35% | -4.4 | 0.80 | 2430 | ----- |
| cont open win1830-2400 k0.2 stop.15 x200 | 334 | 47% | +0.8 | 0.91 | 2243 | 319 | 45% | +1.8 | 0.98 | 2918 | -+++- |
| cont twap win1830-2400 k0.2 stop.15 x200 | 157 | 48% | +1.7 | 0.97 | 1733 | 206 | 48% | +7.7 | 1.19 | 2144 | --+++ |
| cont open win1830-2400 k0.3 stop.15 x200 | 161 | 47% | +1.7 | 0.97 | 1113 | 196 | 39% | +5.0 | 1.08 | 2314 | --+-+ |
| cont twap win1830-2400 k0.3 stop.15 x200 | 50 | 34% | -7.6 | 0.63 | 1213 | 101 | 30% | -7.9 | 0.73 | 2430 | ----- |
| cont open win0-300 k0.2 stop.15 x400 | 387 | 40% | -1.6 | 0.80 | 3066 | 330 | 46% | +2.7 | 1.01 | 2627 | ----+ |
| cont twap win0-300 k0.2 stop.15 x400 | 187 | 40% | -4.2 | 0.70 | 2863 | 221 | 47% | +1.7 | 0.97 | 1537 | --+-+ |
| cont open win0-300 k0.3 stop.15 x400 | 215 | 39% | -2.0 | 0.79 | 2472 | 224 | 43% | +1.1 | 0.95 | 2379 | --+-+ |
| cont twap win0-300 k0.3 stop.15 x400 | 62 | 39% | -2.1 | 0.81 | 1206 | 109 | 42% | +0.8 | 0.95 | 1265 | --+-+ |
| cont open win300-600 k0.2 stop.15 x700 | 536 | 40% | -0.9 | 0.83 | 4595 | 368 | 38% | -2.9 | 0.82 | 5442 | --+-- |
| cont twap win300-600 k0.2 stop.15 x700 | 434 | 42% | -1.2 | 0.81 | 4182 | 285 | 40% | -1.9 | 0.85 | 3019 | ----- |
| cont open win300-600 k0.3 stop.15 x700 | 362 | 36% | -3.4 | 0.73 | 4940 | 273 | 40% | -1.5 | 0.87 | 3438 | ----- |
| cont twap win300-600 k0.3 stop.15 x700 | 217 | 38% | -2.2 | 0.78 | 3085 | 178 | 34% | -8.2 | 0.67 | 4386 | +---- |

#### D Overnight (18:00-9:30) direction -> afternoon

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont thr0 12:00-15:55 | 743 | 53% | +3.8 | 1.04 | 9075 | 448 | 52% | -1.7 | 0.92 | 15029 | --+-+ |
| cont thr0 14:00-15:55 | 743 | 51% | +1.8 | 0.98 | 7161 | 448 | 52% | -0.8 | 0.91 | 6483 | --+-+ |
| rev thr0 12:00-15:55 | 743 | 43% | -4.8 | 0.84 | 17987 | 448 | 46% | +0.7 | 0.97 | 13741 | ---+- |
| rev thr0 14:00-15:55 | 743 | 45% | -2.8 | 0.83 | 12936 | 448 | 45% | -0.2 | 0.93 | 6613 | +--+- |
| cont thr0.3 12:00-15:55 | 319 | 51% | -4.1 | 0.86 | 6654 | 228 | 55% | +13.4 | 1.21 | 5627 | --+-+ |
| cont thr0.3 14:00-15:55 | 319 | 52% | +0.4 | 0.93 | 2662 | 228 | 53% | +5.5 | 1.10 | 1917 | ----+ |
| rev thr0.3 12:00-15:55 | 319 | 45% | +3.1 | 1.02 | 3867 | 228 | 43% | -14.4 | 0.74 | 13309 | +--+- |
| rev thr0.3 14:00-15:55 | 319 | 45% | -1.4 | 0.88 | 4631 | 228 | 43% | -6.5 | 0.77 | 5760 | ----- |

#### E Intraday momentum (last 30 min)

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont Gao prevclose->10:00 thr0 15:30-15:55 | 724 | 45% | -2.3 | 0.72 | 6824 | 432 | 48% | +1.3 | 0.95 | 3640 | ----+ |
| cont 9:30->15:30 thr0 15:30-15:55 | 747 | 47% | +0.1 | 0.86 | 7716 | 448 | 44% | -1.8 | 0.80 | 5194 | +---- |
| cont 9:30->15:00 thr0 15:00-15:55 | 746 | 50% | +3.3 | 1.05 | 4952 | 448 | 48% | +0.8 | 0.94 | 4834 | ++-+- |
| cont 15:00->15:30 thr0 15:30-15:55 | 745 | 44% | -1.3 | 0.78 | 8824 | 446 | 45% | -1.6 | 0.81 | 3578 | +---- |
| rev Gao prevclose->10:00 thr0 15:30-15:55 | 724 | 47% | +1.3 | 0.93 | 3508 | 432 | 44% | -2.3 | 0.78 | 4881 | ----- |
| rev 9:30->15:30 thr0 15:30-15:55 | 747 | 46% | -1.1 | 0.78 | 6096 | 448 | 49% | +0.8 | 0.92 | 1862 | -++-- |
| rev 9:30->15:00 thr0 15:00-15:55 | 746 | 44% | -4.3 | 0.71 | 11098 | 448 | 47% | -1.8 | 0.85 | 5076 | --+-- |
| rev 15:00->15:30 thr0 15:30-15:55 | 745 | 48% | +0.3 | 0.87 | 4492 | 446 | 48% | +0.6 | 0.91 | 3619 | --+-- |
| cont Gao prevclose->10:00 thr0.3 15:30-15:55 | 387 | 48% | +0.2 | 0.86 | 2190 | 261 | 51% | +3.8 | 1.07 | 1958 | ----+ |
| cont 9:30->15:30 thr0.3 15:30-15:55 | 480 | 46% | -0.5 | 0.83 | 5873 | 291 | 42% | -4.1 | 0.73 | 4551 | +---- |
| cont 9:30->15:00 thr0.3 15:00-15:55 | 454 | 52% | +5.4 | 1.17 | 2917 | 291 | 45% | -1.2 | 0.88 | 4455 | ++-+- |
| cont 15:00->15:30 thr0.3 15:30-15:55 | 297 | 45% | +0.8 | 0.91 | 3753 | 166 | 46% | -1.4 | 0.86 | 2030 | +---- |
| rev Gao prevclose->10:00 thr0.3 15:30-15:55 | 387 | 45% | -1.2 | 0.79 | 3936 | 261 | 43% | -4.8 | 0.70 | 4526 | ----- |
| rev 9:30->15:30 thr0.3 15:30-15:55 | 480 | 48% | -0.5 | 0.82 | 4203 | 291 | 51% | +3.1 | 1.04 | 1548 | --+-+ |
| rev 9:30->15:00 thr0.3 15:00-15:55 | 454 | 42% | -6.4 | 0.64 | 8678 | 291 | 49% | +0.2 | 0.92 | 3161 | --+-+ |
| rev 15:00->15:30 thr0.3 15:30-15:55 | 297 | 50% | -1.8 | 0.79 | 3730 | 166 | 48% | +0.4 | 0.92 | 2005 | -++-- |

#### F Midday: morning direction -> 12:00-14:00

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont 9:30->12:00 thr0 12:00-14:00 | 747 | 50% | +1.4 | 0.97 | 5368 | 448 | 50% | +3.8 | 1.04 | 3695 | --++- |
| cont 9:30->12:00 thr0 12:00-15:55 | 747 | 52% | +6.5 | 1.11 | 3593 | 448 | 54% | +12.1 | 1.21 | 3735 | +--++ |
| cont 9:30->14:00 thr0 14:00-15:55 | 746 | 51% | +3.2 | 1.03 | 6942 | 448 | 51% | +9.3 | 1.23 | 2530 | +--++ |
| rev 9:30->12:00 thr0 12:00-14:00 | 747 | 45% | -2.4 | 0.84 | 8284 | 448 | 47% | -4.8 | 0.83 | 9206 | ----- |
| rev 9:30->12:00 thr0 12:00-15:55 | 747 | 44% | -7.5 | 0.78 | 17240 | 448 | 45% | -13.1 | 0.74 | 14959 | ----- |
| rev 9:30->14:00 thr0 14:00-15:55 | 746 | 45% | -4.2 | 0.79 | 13414 | 448 | 46% | -10.3 | 0.68 | 12082 | --+-- |
| cont 9:30->12:00 thr0.3 12:00-14:00 | 400 | 50% | +0.2 | 0.92 | 3518 | 247 | 49% | -2.0 | 0.89 | 2789 | --+-- |
| cont 9:30->12:00 thr0.3 12:00-15:55 | 400 | 54% | +5.8 | 1.09 | 2644 | 247 | 51% | -1.0 | 0.93 | 5242 | +--+- |
| cont 9:30->14:00 thr0.3 14:00-15:55 | 430 | 55% | +7.9 | 1.23 | 3920 | 274 | 48% | +2.0 | 0.99 | 4571 | ++-+- |
| rev 9:30->12:00 thr0.3 12:00-14:00 | 400 | 45% | -1.2 | 0.88 | 6058 | 247 | 49% | +1.0 | 0.96 | 3441 | +---- |
| rev 9:30->12:00 thr0.3 12:00-15:55 | 400 | 43% | -6.8 | 0.79 | 11209 | 247 | 47% | +0.0 | 0.95 | 3976 | ----+ |
| rev 9:30->14:00 thr0.3 14:00-15:55 | 430 | 42% | -8.9 | 0.66 | 12319 | 274 | 49% | -3.0 | 0.86 | 4545 | --+-+ |

#### H Pre-market: London direction -> 6:00-9:30

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont 3:00->6:00 thr0.0 6:00-9:25 | 745 | 46% | -1.1 | 0.88 | 8479 | 447 | 49% | +7.0 | 1.14 | 4072 | ----+ |
| rev 3:00->6:00 thr0.0 6:00-9:25 | 745 | 51% | +0.1 | 0.92 | 5583 | 447 | 48% | -8.0 | 0.75 | 11348 | ----- |
| cont 3:00->6:00 thr0.15 6:00-9:25 | 299 | 41% | -3.6 | 0.79 | 4949 | 188 | 46% | +6.3 | 1.11 | 1932 | ----+ |
| rev 3:00->6:00 thr0.15 6:00-9:25 | 299 | 56% | +2.6 | 1.01 | 2476 | 188 | 50% | -7.3 | 0.77 | 3946 | --+-- |

#### H Pre-market: overnight -> 8:30-9:30 (no-news days)

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont 18:00->8:30 thr0 8:30-9:25 | 638 | 47% | +0.2 | 0.86 | 4243 | 387 | 45% | -1.6 | 0.80 | 3310 | -+--- |
| cont 18:00->6:00 thr0 6:00-9:25 | 746 | 45% | -0.7 | 0.89 | 7802 | 447 | 49% | +5.5 | 1.09 | 4379 | -+-++ |
| rev 18:00->8:30 thr0 8:30-9:25 | 638 | 44% | -1.2 | 0.78 | 6492 | 387 | 47% | +0.6 | 0.91 | 3188 | +---- |
| rev 18:00->6:00 thr0 6:00-9:25 | 746 | 52% | -0.3 | 0.90 | 9025 | 447 | 48% | -6.5 | 0.78 | 9454 | +---- |
| cont 18:00->8:30 thr0.3 8:30-9:25 | 236 | 50% | +1.6 | 0.95 | 1721 | 181 | 43% | -0.3 | 0.87 | 1472 | -++-- |
| cont 18:00->6:00 thr0.3 6:00-9:25 | 220 | 47% | -0.6 | 0.89 | 3100 | 187 | 50% | +9.4 | 1.24 | 1650 | -++-+ |
| rev 18:00->8:30 thr0.3 8:30-9:25 | 236 | 43% | -2.6 | 0.73 | 3570 | 181 | 49% | -0.7 | 0.85 | 2447 | +---- |
| rev 18:00->6:00 thr0.3 6:00-9:25 | 220 | 48% | -0.4 | 0.89 | 4147 | 187 | 47% | -10.4 | 0.67 | 5366 | +---- |

#### I Sunday evening beyond the gap

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont Sun 18:00->20:00 thr0.0 20:00-03:00 | 136 | 43% | -2.9 | 0.78 | 2389 | 86 | 49% | -13.4 | 0.70 | 4304 | --++- |
| cont Sun 18:00->20:00 thr0.0 20:00-09:25 | 136 | 44% | -6.2 | 0.79 | 3794 | 86 | 49% | -1.8 | 0.94 | 3024 | --++- |
| cont Sun 18:00->24:00 thr0.0 00:00-09:25 | 137 | 44% | -9.0 | 0.70 | 3730 | 86 | 56% | +13.5 | 1.21 | 1790 | ---+- |
| rev Sun 18:00->20:00 thr0.0 20:00-03:00 | 136 | 51% | +1.9 | 0.98 | 2082 | 86 | 50% | +12.4 | 1.25 | 1638 | ++--+ |
| rev Sun 18:00->20:00 thr0.0 20:00-09:25 | 136 | 54% | +5.2 | 1.08 | 2405 | 86 | 50% | +0.8 | 0.98 | 2857 | ++--+ |
| rev Sun 18:00->24:00 thr0.0 00:00-09:25 | 137 | 56% | +8.0 | 1.19 | 1592 | 86 | 42% | -14.5 | 0.75 | 4722 | ++--+ |
| cont Sun 18:00->20:00 thr0.15 20:00-03:00 | 45 | 42% | +6.4 | 1.17 | 1059 | 52 | 48% | -21.2 | 0.62 | 3619 | --++- |
| cont Sun 18:00->20:00 thr0.15 20:00-09:25 | 45 | 33% | -20.6 | 0.61 | 3491 | 52 | 54% | +7.4 | 1.06 | 1706 | --++- |
| cont Sun 18:00->24:00 thr0.15 00:00-09:25 | 67 | 40% | -19.5 | 0.54 | 3452 | 60 | 57% | +8.8 | 1.11 | 1997 | --++- |
| rev Sun 18:00->20:00 thr0.15 20:00-03:00 | 45 | 49% | -7.4 | 0.67 | 1566 | 52 | 50% | +20.2 | 1.44 | 1206 | +---+ |
| rev Sun 18:00->20:00 thr0.15 20:00-09:25 | 45 | 62% | +19.6 | 1.45 | 1693 | 52 | 46% | -8.4 | 0.88 | 2921 | ++--+ |
| rev Sun 18:00->24:00 thr0.15 00:00-09:25 | 67 | 60% | +18.5 | 1.58 | 1366 | 60 | 40% | -9.8 | 0.82 | 2502 | ++--+ |

#### J Prior RTH day direction -> evening

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont prevRTH thr0 18:00-20:00 | 722 | 43% | -0.4 | 0.80 | 5761 | 430 | 48% | +1.6 | 0.97 | 3842 | --+-+ |
| cont prevRTH thr0 18:00-03:00 | 722 | 46% | -0.2 | 0.90 | 7383 | 430 | 45% | -4.6 | 0.87 | 8277 | --+-- |
| cont prevRTH thr0 18:00-09:25 | 722 | 48% | -1.6 | 0.91 | 8440 | 430 | 48% | -12.9 | 0.81 | 15474 | --+-- |
| rev prevRTH thr0 18:00-20:00 | 722 | 48% | -0.6 | 0.78 | 5106 | 430 | 47% | -2.6 | 0.83 | 5887 | -+--- |
| rev prevRTH thr0 18:00-03:00 | 722 | 49% | -0.8 | 0.87 | 5472 | 430 | 52% | +3.6 | 1.03 | 4060 | -+--+ |
| rev prevRTH thr0 18:00-09:25 | 722 | 49% | +0.6 | 0.96 | 6259 | 430 | 50% | +11.9 | 1.14 | 4783 | ++-++ |
| cont prevRTH thr0.6 18:00-20:00 | 275 | 44% | -0.2 | 0.82 | 2258 | 143 | 49% | -7.8 | 0.73 | 4512 | ----- |
| cont prevRTH thr0.6 18:00-03:00 | 275 | 45% | +1.7 | 0.97 | 2995 | 143 | 49% | -6.6 | 0.84 | 5360 | +-++- |
| cont prevRTH thr0.6 18:00-09:25 | 275 | 45% | -5.9 | 0.82 | 8436 | 143 | 50% | -17.0 | 0.77 | 8367 | +---- |
| rev prevRTH thr0.6 18:00-20:00 | 275 | 50% | -0.8 | 0.79 | 2116 | 143 | 48% | +6.8 | 1.15 | 2327 | -+--+ |
| rev prevRTH thr0.6 18:00-03:00 | 275 | 49% | -2.7 | 0.80 | 3468 | 143 | 50% | +5.6 | 1.07 | 2685 | -+--+ |
| rev prevRTH thr0.6 18:00-09:25 | 275 | 52% | +4.9 | 1.07 | 4041 | 143 | 49% | +16.0 | 1.20 | 3164 | -++++ |

#### J2 Last hour -> post-close 16:00-16:55

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cont 15:00->16:00 thr0.0 16:00-16:55 | 745 | 42% | -0.4 | 0.78 | 5655 | 447 | 47% | +0.4 | 0.89 | 3378 | --+-- |
| rev 15:00->16:00 thr0.0 16:00-16:55 | 745 | 46% | -0.6 | 0.77 | 5098 | 447 | 44% | -1.4 | 0.80 | 5774 | ----- |
| cont 15:00->16:00 thr0.15 16:00-16:55 | 317 | 43% | -0.5 | 0.80 | 2805 | 187 | 45% | +0.4 | 0.92 | 2247 | ----- |
| rev 15:00->16:00 thr0.15 16:00-16:55 | 317 | 45% | -0.5 | 0.79 | 1949 | 187 | 46% | -1.4 | 0.84 | 3478 | ----- |

#### K Weekday overnight hold (long)

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| long 18:00-09:25 key wd0 | 137 | 53% | -4.1 | 0.83 | 2807 | 86 | 58% | +59.8 | 2.00 | 2237 | --+++ |
| long 20:00-03:00 key wd0 | 137 | 50% | -2.9 | 0.78 | 2301 | 86 | 57% | +5.8 | 1.08 | 1549 | +--++ |
| long 18:00-09:25 key wd1 | 155 | 46% | -2.2 | 0.89 | 4028 | 94 | 47% | -28.1 | 0.63 | 6669 | +---- |
| long 20:00-03:00 key wd1 | 155 | 47% | -2.6 | 0.77 | 2128 | 94 | 46% | -15.3 | 0.67 | 4080 | --+-- |
| long 18:00-09:25 key wd2 | 153 | 54% | +9.3 | 1.17 | 2985 | 92 | 61% | +27.1 | 1.55 | 1463 | +++++ |
| long 20:00-03:00 key wd2 | 153 | 45% | +2.3 | 0.99 | 1984 | 92 | 53% | +14.0 | 1.43 | 1419 | +-+++ |
| long 18:00-09:25 key wd3 | 152 | 56% | +8.4 | 1.14 | 5505 | 88 | 51% | -0.1 | 0.97 | 3359 | -+++- |
| long 20:00-03:00 key wd3 | 152 | 52% | +4.3 | 1.10 | 1758 | 88 | 57% | +5.7 | 1.09 | 1682 | --++- |
| long 18:00-09:25 key wd4 | 150 | 49% | -7.0 | 0.79 | 3872 | 88 | 59% | -2.1 | 0.94 | 5247 | -+--- |
| long 20:00-03:00 key wd4 | 150 | 52% | +3.3 | 1.05 | 1046 | 88 | 58% | +5.6 | 1.09 | 3248 | +--++ |

#### G Prior-day RTH high/low touched overnight

| Test | IS n | IS win | IS avg pt | IS PF | IS maxDD$ | OOS n | OOS win | OOS avg pt | OOS PF | OOS maxDD$ | years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fade win1800-300 stop0.1 tgt0.15 | 253 | 35% | -2.8 | 0.72 | 2889 | 188 | 34% | -6.3 | 0.65 | 3304 | ----- |
| fade win1800-300 stop0.15 tgt0.3 | 253 | 32% | -4.2 | 0.76 | 3480 | 188 | 27% | -15.9 | 0.55 | 6940 | ----- |
| fade win1800-300 stop0.2 tgt0.2 | 253 | 51% | +2.3 | 1.00 | 1980 | 188 | 48% | -3.9 | 0.83 | 3247 | +-+-- |
| break win1800-300 stop0.1 tgt0.15 | 253 | 36% | -4.4 | 0.64 | 3548 | 188 | 39% | -2.0 | 0.81 | 2174 | ----- |
| break win1800-300 stop0.15 tgt0.3 | 253 | 31% | -5.3 | 0.73 | 4163 | 188 | 33% | -6.9 | 0.75 | 4883 | ---+- |
| break win1800-300 stop0.2 tgt0.2 | 253 | 47% | -5.0 | 0.74 | 4224 | 188 | 52% | +2.9 | 1.01 | 1551 | ---+- |
| fade win300-925 stop0.1 tgt0.15 | 274 | 39% | -1.1 | 0.79 | 2137 | 165 | 45% | +3.0 | 1.03 | 892 | ---++ |
| fade win300-925 stop0.15 tgt0.3 | 274 | 33% | -6.5 | 0.64 | 4964 | 165 | 43% | +3.9 | 1.06 | 1470 | ---+- |
| fade win300-925 stop0.2 tgt0.2 | 274 | 45% | -2.5 | 0.79 | 2728 | 165 | 55% | +6.7 | 1.17 | 911 | ---++ |
| break win300-925 stop0.1 tgt0.15 | 274 | 34% | -3.8 | 0.65 | 3932 | 165 | 27% | -12.7 | 0.44 | 5108 | ----- |
| break win300-925 stop0.15 tgt0.3 | 274 | 36% | -1.9 | 0.82 | 3710 | 165 | 28% | -15.0 | 0.51 | 5994 | ----- |
| break win300-925 stop0.2 tgt0.2 | 274 | 47% | -2.4 | 0.79 | 4004 | 165 | 40% | -10.0 | 0.64 | 4216 | ----- |
| fade win1800-925 stop0.1 tgt0.15 | 410 | 37% | -1.9 | 0.75 | 3978 | 272 | 36% | -4.9 | 0.69 | 4005 | ----- |
| fade win1800-925 stop0.15 tgt0.3 | 410 | 32% | -5.3 | 0.70 | 6278 | 272 | 31% | -11.9 | 0.61 | 7816 | ----- |
| fade win1800-925 stop0.2 tgt0.2 | 410 | 49% | -0.1 | 0.90 | 3467 | 272 | 48% | -3.1 | 0.84 | 3301 | --+-- |
| break win1800-925 stop0.1 tgt0.15 | 410 | 33% | -5.3 | 0.59 | 6333 | 272 | 36% | -4.7 | 0.71 | 4415 | ----- |
| break win1800-925 stop0.15 tgt0.3 | 410 | 32% | -5.1 | 0.72 | 6505 | 272 | 32% | -8.6 | 0.69 | 6499 | ----- |
| break win1800-925 stop0.2 tgt0.2 | 410 | 47% | -3.4 | 0.77 | 5906 | 272 | 49% | +0.8 | 0.95 | 2060 | ----- |
