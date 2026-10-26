# PDC magnet test (2026-10-26)

Question: does MNQ treat the previous day RTH close (PDC, 16:00) as a magnet or fair price that it keeps trading back to? This was inspired by JJ Simon's "fair price" idea and by Sunday night chop seen around the PDC line.

**Verdict: NO. The PDC behaves like any nearby level.**
- It is touched as often as a fake level at the same distance, no more.
- Price does not stay near it longer and does not bounce off it.
- Trading it as a magnet loses money in every period.
- The one real effect: when the RTH open is far from the PDC (>= 0.5 ADR), price comes back to the PDC more often than to the mirror level (31% vs 22% by the close). The prior day's 15:00 price (29%) and lines 0.25 ADR off the PDC (28%) come back just as often. That is "big gaps partly retrace into yesterday's late range", not something special about the close.
- Overnight, the PDC is slightly *less* sticky than the mirror level, because the evening continues the 16:00 -> 18:00 move.

## Method

- **Data:** MNQ ETH 5m bars, sessions keyed by end date (18:00 -> 16:55), from 2022-01-01 to 2026-10-20. 1,153 sessions with a full 18:00-16:00 session and a full prior RTH.
- **Windows:** overnight (ON) = 18:00-09:30, starting from the 18:00 open; RTH = 09:30-16:00, starting from the 09:30 open.
- **ADR:** the mean of the prior 10 RTH ranges (`scripts/sessions/common.py`).
- **Placebo levels** (each is scored against its own distance from the start price):
  - **MIR (mirror):** same distance from the start price as the PDC, on the other side (2 x start - PDC). This is the exact "any nearby level" null.
  - **P15:** the prior day's 15:00 price, a real recent price that is not a close.
  - **O2:** the RTH open from 2 sessions ago.
  - **SHIFT:** PDC +0.25 ADR and PDC -0.25 ADR, two fake lines that move with the PDC.
- **Costs:** 2 x $2.37 commission plus 1 tick of slippage per side, $2/pt.
- **Fills:**
  - Market entries fill at the bar open.
  - Limits need a 1-tick trade-through, and a stop touched in the fill bar counts as hit.
  - If stop and target are in the same bar, the stop is assumed.
- **Periods:** IS 2022-2024, OOS 2025-2026, 2026 YTD (a subset of OOS).
- **Code:** `scripts/pdc/pdc_common.py` and `scripts/pdc/pdc_test.py`. The full tables are in `scripts/pdc/out_pdc.md`, which comes out the same on every run.

## 1. Touch frequency

Share of sessions that touch the level inside the window, by starting distance. PDC-MIR is in percentage points, with +/- 2 standard errors.

**Overnight (18:00-09:30)**

| Period | Dist ADR | n | PDC | MIR | PDC-MIR | P15 | SHIFT |
|---|---|---|---|---|---|---|---|
| 2022-24 | 0-0.10 | 510 | 90% | 92% | -2 (+/-4) | 90% | 89% |
| 2022-24 | 0.10-0.25 | 157 | 59% | 76% | -17 (+/-10) | 69% | 63% |
| 2022-24 | 0.25-0.50 | 40 | 38% | 50% | -12 (+/-22) | 53% | 42% |
| 2025-26 | 0-0.10 | 267 | 94% | 93% | +1 (+/-4) | 89% | 85% |
| 2025-26 | 0.10-0.25 | 98 | 70% | 71% | -1 (+/-13) | 64% | 66% |
| 2025-26 | 0.25-0.50 | 41 | 49% | 46% | +2 (+/-22) | 47% | 46% |
| 2026 YTD | 0-0.10 | 120 | 95% | 94% | +1 (+/-6) | 88% | 78% |
| 2026 YTD | 0.10-0.25 | 44 | 77% | 75% | +2 (+/-18) | 74% | 70% |
| 2026 YTD | 0.25-0.50 | 18 | 72% | 50% | +22 (+/-32) | 57% | 52% |

**RTH (09:30-16:00)**

| Period | Dist ADR | n | PDC | MIR | PDC-MIR | P15 | SHIFT |
|---|---|---|---|---|---|---|---|
| 2022-24 | 0-0.10 | 157 | 95% | 96% | -1 (+/-5) | 94% | 96% |
| 2022-24 | 0.10-0.25 | 182 | 79% | 74% | +4 (+/-9) | 75% | 77% |
| 2022-24 | 0.25-0.50 | 199 | 52% | 56% | -4 (+/-10) | 55% | 57% |
| 2022-24 | 0.50-1.00 | 155 | 34% | 26% | +7 (+/-10) | 33% | 33% |
| 2025-26 | 0.10-0.25 | 110 | 73% | 72% | +1 (+/-12) | 70% | 75% |
| 2025-26 | 0.25-0.50 | 98 | 53% | 52% | +1 (+/-14) | 60% | 55% |
| 2025-26 | 0.50-1.00 | 107 | 32% | 24% | +7 (+/-12) | 33% | 33% |
| 2026 YTD | 0.10-0.25 | 43 | 72% | 77% | -5 (+/-19) | 77% | 77% |
| 2026 YTD | 0.25-0.50 | 39 | 51% | 49% | +3 (+/-23) | 60% | 54% |
| 2026 YTD | 0.50-1.00 | 59 | 29% | 27% | +2 (+/-17) | 24% | 28% |

- **Time to touch:** within each bucket, the median time to touch is about the same for the PDC and the mirror. In the RTH, both are touched in about 10 minutes from 0.10-0.25 ADR and about 30-40 minutes from 0.25-0.50 ADR.
- **Far opens, pooled 2022-2026:** with the RTH open at least 0.5 ADR away, the level is touched by the close for PDC 31%, MIR 22%, P15 29%, SHIFT 28% and O2 15% (each about +/-5). The PDC beats the fake mirror, but not the other prior-day levels.

## 2. Gap fill at the RTH open (09:30 open vs PDC)

Fill rate by 11:00 / by the close, with gap direction pooled. Each level is bucketed by its own gap.

| Period | Gap ADR | PDC | MIR | P15 | SHIFT |
|---|---|---|---|---|---|
| 2022-24 | 0.10-0.25 | 64% / 79% | 55% / 74% | 60% / 75% | 55% / 77% |
| 2022-24 | 0.25-0.50 | 31% / 52% | 34% / 56% | 28% / 55% | 31% / 57% |
| 2022-24 | 0.50-1.00 | 8% / 34% | 7% / 26% | 7% / 33% | 9% / 33% |
| 2025-26 | 0.10-0.25 | 61% / 73% | 60% / 72% | 55% / 70% | 67% / 75% |
| 2025-26 | 0.25-0.50 | 37% / 53% | 29% / 52% | 39% / 60% | 26% / 55% |
| 2025-26 | 0.50-1.00 | 11% / 32% | 8% / 24% | 14% / 33% | 16% / 33% |
| 2026 YTD | 0.10-0.25 | 58% / 72% | 63% / 77% | 65% / 77% | 73% / 77% |
| 2026 YTD | 0.25-0.50 | 44% / 51% | 31% / 49% | 47% / 60% | 27% / 54% |
| 2026 YTD | 0.50-1.00 | 15% / 29% | 7% / 27% | 14% / 24% | 17% / 28% |

- **By direction:** splitting by gap direction, and by fill time (10:00 / 11:00 / close), shows no consistent pattern. See `out_pdc.md` section 2. For example, in 2022-24 down gaps of 0.10-0.25 ADR fill by 11:00 in 67% of sessions vs 56% for the mirror. Up gaps of the same size show 61% vs 55%, and in 2025-26 the direction of the difference flips.
- **Answer:** the PDC gap fills at about the rate of any level at the same distance, within the sampling noise.

## 3. Dwell (is the PDC sticky?)

Share of 5m closes within 0.05 ADR of the level:
- **A** = all sessions.
- **B** = sessions that start within 0.25 ADR of the level.
- **C** = the 60 minutes after the first touch.

| Window | Period | PDC A / B / C | MIR A / B / C | P15 A / B / C | SHIFT A / B / C |
|---|---|---|---|---|---|
| ON | 2022-24 | 18.3 / 19.5 / 54.3 | 21.1 / 22.4 / 60.2 | 14.2 / 17.7 / 56.6 | 7.4 / 10.7 / 52.7 |
| ON | 2025-26 | 14.1 / 16.2 / 45.2 | 13.9 / 15.5 / 49.7 | 9.8 / 12.8 / 44.0 | 7.6 / 10.7 / 47.6 |
| ON | 2026 YTD | 12.6 / 14.3 / 39.6 | 11.6 / 12.9 / 45.3 | 8.8 / 11.0 / 41.7 | 7.1 / 9.7 / 44.0 |
| RTH | 2022-24 | 7.4 / 11.0 / 18.5 | 6.5 / 9.1 / 21.1 | 6.8 / 9.3 / 21.2 | 5.5 / 7.8 / 19.1 |
| RTH | 2025-26 | 5.9 / 8.1 / 20.4 | 5.1 / 7.9 / 20.2 | 6.0 / 7.9 / 19.9 | 5.2 / 7.8 / 19.3 |
| RTH | 2026 YTD | 4.6 / 6.2 / 18.9 | 3.8 / 6.2 / 18.8 | 5.2 / 7.0 / 17.0 | 4.5 / 6.5 / 16.2 |

- **Overall:** dwell near the PDC equals or trails the mirror. After the first touch, price spends *less* time at the PDC overnight than at the mirror, and the close crosses the PDC no more often (about 1.4 vs 1.5 side switches per hour).
- **Sunday nights (pooled 2022-2026, n 213):** the 18:00-21:00 dwell is PDC 15.5% vs MIR 21.8%, and the touch rate is 73% vs 78%. Mon-Thu nights look the same (28.7% vs 30.7%).
- **What the trader saw:** the Sunday chop around the PDC is real, but price chops just as much around any line drawn at that distance. The Sunday 18:00 open usually sits close to the Friday close (median 0.07 ADR, vs 0.06 on weeknights), so the PDC is simply the nearest line on the chart.

## 4. Reaction on the first touch

Price must start at least 0.05 ADR from the level.
- **Rej60:** the close 60 minutes after the touch is back on the side price came from.
- **Race:** price moves +0.1 ADR back the way it came before it moves 0.1 ADR through the level.

| Window | Period | PDC n | PDC Rej60 / Race | MIR Rej60 / Race | P15 Rej60 / Race | SHIFT Rej60 / Race |
|---|---|---|---|---|---|---|
| ON | 2022-24 | 270 | 53% / 49% | 50% / 44% | 55% / 48% | 54% / 49% |
| ON | 2025-26 | 186 | 48% / 49% | 52% / 52% | 51% / 48% | 55% / 47% |
| ON | 2026 YTD | 94 | 49% / 51% | 52% / 50% | 51% / 48% | 52% / 46% |
| RTH | 2022-24 | 365 | 49% / 42% | 47% / 48% | 48% / 47% | 52% / 49% |
| RTH | 2025-26 | 200 | 52% / 44% | 41% / 48% | 53% / 55% | 50% / 47% |
| RTH | 2026 YTD | 82 | 57% / 48% | 41% / 49% | 55% / 58% | 49% / 44% |

- **Result:** a first touch of the PDC is a coin flip, bounce or pass-through, at both horizons (30 min is in `out_pdc.md`). In the RTH, the race actually favours *passing through* the PDC (42-48% bounce).
- **The 2025-26 Rej60 gap vs the mirror:** this is the long drift, not the PDC. The mirror on gap-down days sits below the open and gets broken in a rising market. P15 shows the same 53-55%.

## 5. Mechanical tests (1 MNQ, net of costs)

| Test | IS n | IS PF | OOS n | OOS PF | 2026 n | 2026 PF |
|---|---|---|---|---|---|---|
| 5a 9:30 fade to PDC, gap 0.1-0.6, stop 0.25, exit 11:00 | 436 | 0.98 | 244 | 0.92 | 98 | 1.06 |
| 5a same toward the mirror (follow the gap) | 436 | 0.95 | 244 | 0.95 | 98 | 0.89 |
| 5a same toward P15 | 437 | 0.88 | 231 | 0.96 | 93 | 1.00 |
| 5a PDC, stops 0.15 / 0.40 | 436 | 0.88 / 0.97 | 244 | 0.86 / 0.89 | 98 | 1.05 / 1.07 |
| 5a PDC, gap 0.1-0.3 / 0.3-0.6 | 234 / 202 | 0.91 / 1.05 | 133 / 111 | 0.88 / 0.95 | 49 / 49 | 0.89 / 1.19 |
| 5b RTH first-touch limit at PDC, stop 0.1 tgt 0.1 | 361 | 0.51 | 197 | 0.67 | 80 | 0.72 |
| 5b same at the mirror | 344 | 0.65 | 181 | 0.84 | 81 | 0.79 |
| 5b RTH PDC stop 0.1 tgt 0.2 / stop 0.15 tgt 0.3 | 361 | 0.69 / 0.70 | 197 | 0.75 / 0.65 | 80 | 1.07 / 0.83 |
| 5b ON first-touch at PDC, stop 0.1 tgt 0.2 | 257 | 0.72 | 179 | 0.83 | 90 | 0.80 |
| 5c evening 18:00 fade to PDC, 0.05-0.3 ADR, stop 0.2, exit 20:00 | 363 | 0.44 | 215 | 0.77 | 100 | 0.75 |
| 5c same, stops 0.15 / 0.3 | 363 | 0.46 / 0.44 | 215 | 0.75 / 0.71 | 100 | 0.73 / 0.66 |
| 5c mirror (follow the 16:00 -> 18:00 change), stop 0.2 | 363 | 1.24 | 215 | 1.09 | 100 | 1.15 |
| 5c same fade toward P15 / O2, stop 0.2 | 432 / 129 | 0.65 / 0.62 | 237 / 73 | 0.65 / 0.63 | 113 / 33 | 0.66 / 0.59 |

- **5a:** the 9:30 fade to the PDC is break-even before luck: PF 0.92-1.06, no better than the mirror or P15. The 2026 PF of 1.06 (+$5.6/trade on 98 trades) is noise.
- **5b:** buying or selling the first PDC touch loses in every cell. The PDC is no better than any placebo and is often worse.
- **5c:** this confirms the earlier evening study. Fading back toward the 16:00 close at night is clearly negative: PF 0.44 IS, 0.71-0.77 OOS, 0.66-0.75 in 2026. The opposite side, following the 16:00 -> 18:00 change, is the positive one: PF 1.09-1.27. That matches G16 in `EVENING_MODULE_2026-10-25.md`.

## Takeaways for the playbook

- **The PDC line:** keep it on the chart as a reference, but do not use it as a target, an entry trigger or a "fair price".
- **Nothing new to trade:**
  - No rule passes, and nothing is added to the playbook.
  - The only robust related edge stays the existing one: evening continuation (G16), which goes *away* from the PDC.
- **Far opens:** for opens 0.5+ ADR away, about 30% retrace to the PDC by the close. That is the same for any late prior-day level, so it is not a reason to target the close specifically.
