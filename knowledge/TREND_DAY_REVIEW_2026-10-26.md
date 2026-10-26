# Trend-day review, Mon Oct 26 2026, and IB v2 / trend-pullback tests

**Bottom line**
- The day was not a clean trend day. It had one trend leg, 10:00 to 11:00 (+400 pts), with chop before and a range after.
- Every good trade was a reaction at a key level. None was a pattern signal.
- Making the inside-bar breakout level-aware does not create an edge: 168 variants were tested, none was profitable in all three periods, and the best 2022-24 profit factor was 1.02.
- A dedicated trend-day pullback rule (9 variants) also fails, and it would have lost today.
- Nothing new goes into the Playbook. The inside bar stays as a $200 tracker. One display-only change is proposed below.

Data: today's TradingView 1m bars (08:15-16:59 ET) in `data/live/mnq_1m_2026-10-26.csv`. Backtests use `common.DB` (RTH 1m to 2026-10-23), with the higher-timeframe trend taken from ETH 5m (data ends Oct 20). Script: `scripts/y2026/ib_v2.py` and `ib_v2_grid.py`, results in `ib_v2_grid.json` and `tpb_grid.json`.

## 1. Today's structure (ET)

| Window | Range | Character |
|---|---|---|
| 08:15-09:29 | 29,222-29,354 | Pre-open ran above PDH (29,325.75), then faded |
| 09:30-10:00 | 29,169-29,335 | Two-sided. Opening range 29,169.25-29,334.75. PDH rejected at 9:40 |
| 10:00-11:00 | 29,172 → 29,571.75 | **The trend leg.** Double bottom at the OR low, PDH/ORH breakout, then a 1-minute staircase |
| 11:00-12:48 | 29,571 → 29,397 | Pullback back into the 10:35-10:45 breakout zone (29,394-29,424) |
| 12:48-16:00 | 29,397-29,555 | Range with lower highs. Close 29,440 |

**Why our strategies stayed off:**
- **V4+:** bias conflict between the daily trend (DOWN) and the opening bias (none).
- **D2:** at 10:29 price was +120 pts from the open, 0.28 ADR, below the 0.6 needed.
- **TDP:** first-hour efficiency was 0.56 (needs 0.60), and at 10:29 price was back inside yesterday's range by a few points.
- **Pinball and H2:** no setup.
- **NEWS:** not a news day.

## 2. Best opportunities (hindsight, each with an objective trigger)

| # | Time | Setup | Entry / stop | Logic target | Result |
|---|---|---|---|---|---|
| 1 | 10:09 | Double bottom at the OR low (29,169 / 29,172), reclaim of 29,216 | long ~29,232, stop 29,171 (61 pts) | PDH/ORH 29,325-29,335 (1.5R) | Target hit 10:16. Price ran to 6R |
| 2 | 10:28 | PDH + ORH break, retest held (lows 29,322.5-29,331) | long ~29,350, stop 29,321 (29 pts) | No level above: trail | +1R within minutes, +7.5R at the 11:00 high |
| 3 | 12:51 | Pullback into the 10:35-10:45 breakout zone (29,394-29,424), higher low at 29,397 | long ~29,428, stop 29,396 (32 pts) | Day high 29,571 (4.5R) | 1R at 12:58. 29,555 by ~13:20 (4R) |
| 4 | 13:52 | Higher low 29,437 (13:47) plus IB signal | long 29,464, stop 29,437 (27 pts) | 29,500 round / 29,509 13:00 high | 29,534 at 13:55 (2.6R) |
| 5 | 11:4x | Double top under the 29,571 high (counter-trend) | short ~29,540, stop 29,573 | 29,456 | About 2.5R, lower quality |

The common thread: the trigger was a key level (OR low, PDH/ORH, a prior breakout zone, a higher low), and the target was the next level.

## 3. Today's inside-bar signals, live rules (1m, full body, HTF 2-of-3, 1R)

| Tag time | Side | Entry | Stop (R pts) | Tag size at $200 | Result |
|---|---|---|---|---|---|
| ~9:50 | short | | | 3 | not replicated (HTF trend needs ETH data after Oct 20; seen on chart only) |
| 10:13 | long | 29,305 | 29,248.5 (56.5) | 1 | +1R (+$108) |
| 10:46 | long | 29,506 | 29,439 (67) | 1 | **-1R.** The target 29,573 missed the day high by 1.25 pts, then the stop hit at 12:43 (-$140). You exited +36 manually, the better call |
| 13:05 | long | 29,534 | 29,495 (39.5) | 2 | -1R (-$168) |
| 13:51 | long | 29,464 | 29,437 (27) | 3 | +1R (+$148). You took 1 contract |
| 15:03 | long | 29,498 | 29,459 (39) | 2 | -1R (-$166) |

The tags as printed lost about **-$220** today. Your two picks made +$125.50. Your discretion beat the raw signals.

## 4. IB v2: key-level targets and room filter

**Rules tested:**
- **Target:** the next key level in the trade's direction (PDH, PDL, PDC, overnight high/low, OR high/low after 9:45, day high/low so far, and optionally 100-pt round numbers), capped at `cap` × R.
- **Skip:** if the room to that level is under `k` × R.
- **Optional day filter:** price outside yesterday's range, or first-hour efficiency of at least 0.5 in the trade's direction (after 10:30).

**Grid:** k {0, 0.75, 1, 1.5} × cap {1, 1.5, 2, 3} × day filter {none, outside, eff} × round {no, yes} × timeframe {1m, 5m} = **168 variants**.

**Costs:** $2.37 per side, 1 tick on entries and stops, plus a stop-slip stress of 2 pts on 1m and 4 pts on 5m. The 2026 column covers data through Oct 20.

| Variant | 2022-24 n / WR / PF / avg R | 2025 | 2026 |
|---|---|---|---|
| v1 1m (live rules) | 8074 / 48% / 0.70 / -0.22 | 2435 / 48% / 0.76 / -0.20 | 1991 / 49% / 0.76 / -0.16 |
| v2 1m, k1, cap 3 | 3804 / 33% / 0.76 / -0.24 | 1158 / 33% / 0.74 / -0.23 | 983 / 32% / 0.74 / -0.22 |
| v2 1m, k1.5, cap 3, outside (best 1m) | 1835 / 30% / 0.84 / -0.19 | 546 / 27% / 0.68 / -0.31 | 473 / 28% / 0.82 / -0.20 |
| v1 5m | 1602 / 51% / 0.86 / -0.09 | 458 / 45% / 0.76 / -0.16 | 353 / 47% / 0.84 / -0.09 |
| v2 5m, k1, cap 1, round | 258 / 54% / 0.89 / -0.09 | 60 / 45% / 0.73 / -0.21 | 48 / 42% / 0.61 / -0.26 |
| 5m, eff day filter only (best 2022-24) | 576 / 55% / 1.02 / -0.01 | 171 / 46% / 0.79 / -0.17 | 142 / 51% / 1.00 / -0.01 |

**Findings:**
- **The room filter helps a little.** On 5m, the median 2022-24 PF goes from 0.82 at k=0 to 0.85-0.87 at k = 0.75-1. That is not enough.
- **Longer level targets don't help.** They lower the win rate about as much as they raise the payoff.
- **0 of 168 variants are profitable in all three periods.**
- **The eval simulation was not run,** because nothing survived to test. The reference stays v31 plus the evening module.
- **On today alone, v2 would not have saved the day.** k1 cap1 made -$158, k1 cap3 made -$484, and k1 with round numbers made -$130, against -$219 for v1.

## 5. Trend-day pullback (TPB)

**Rules:**
- **Trend check:** at 10:30, first-hour efficiency of at least `th` sets the direction.
- **Entry:** from 10:30 to 14:30 on 5m, a bar touches the 20 EMA, closes back beyond it, and has a candle body in the trend's direction.
- **Stop:** beyond the extreme of the last 3 bars.
- **Target:** 1.5R, 2R, or a retest of the day's extreme.
- **Limits:** at most 2 trades a day, flat 15:59.

**Grid:** th {0.4, 0.5, 0.6} × target {1.5R, 2R, day extreme} = 9 variants.

| Variant | 2022-24 n / WR / PF | 2025 | 2026 |
|---|---|---|---|
| th 0.6, 2R (best) | 445 / 39% / 1.01 | 144 / 31% / 0.70 | 103 / 38% / 1.01 |
| th 0.5, 2R | 581 / 38% / 0.95 | 193 / 31% / 0.72 | 149 / 35% / 0.91 |

**Result:** fails in 2025 in every variant. Today it would have lost: a long at 12:10 was stopped, and a long at 13:00 ended -38.5 at the time exit.

## 6. Recommendation

1. **Don't change the inside-bar trading rules.** Keep the module as a tracker at $200, or turn it off.
2. **Don't add the TPB rule.**
3. **The real lesson from today is key-level trading:** OR-low double bottom, PDH/ORH breakout-retest, a pullback into a prior breakout zone, higher lows. Two of these were already tested as rules and failed: prior-day breakout (MORE_TRADES_2026: 11% pass in 20 days) and IB retest (E3). They work as discretionary context, not as rules.
4. **Display-only Pine change (not deployed):** show the room to the next key level in the IB tag. Gray out the tag when room < 1R, so you can see when a target sits behind a level.

```pine
// in the IB signal block, after ib_t is computed (display only, no rule change)
ib_lv = array.from(pdh, pdl, pdc, ibH, ibL)          // ibH/ibL: day high/low so far, already tracked
float ib_next = na
for x in ib_lv
    if not na(x) and (x - ib_e) * ib_side > 2 * ib_tick
        ib_next := na(ib_next) ? x : ((x - ib_e) * ib_side < (ib_next - ib_e) * ib_side ? x : ib_next)
ib_room = na(ib_next) ? na : math.abs(ib_next - ib_e) / ib_r
ib_tip := ib_tip + "\nNext level " + (na(ib_next) ? "none" : ib_fmt(ib_next) + " (" + str.tostring(ib_room, "#.0") + "R away)")
// tag color: gray when ib_room < 1 (target sits behind a level)
```
