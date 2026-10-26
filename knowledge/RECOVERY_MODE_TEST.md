# Recovery mode test: replacing the permanent $400 hard stop (Oct 25 2026)

Question: about half of all eval attempts end "stuck" because stop-day rule (b) blocks every entry, forever, once the room above the max-loss line is under $400. Does a 1-MNQ recovery mode turn some of those dead attempts into passes, without adding busts?

**Answer: yes, a little, and it is free if you run accounts in parallel. Adopt R9:** recovery at room < $400, 1 MNQ on any strategy whose 1-contract risk fits within room - $100, back to normal sizing at room >= $700, plus a room guard on normal sizing. Effects:
- **Pass rate:** 47% to 55% (2026), 47% to 52% (2025), 35% to 39% (2022).
- **Tradeify funded net EV:** +$520 (2026), +$230 (2025), +$210 (2022).
- **Busts:** none in any year or slippage stress. The baseline busts 0.7% of evals in 2022; R9 busts 0.0%.

The catch: only 10-16% of attempts that enter recovery go on to pass (6% in 2022), and they take months. About 43% of attempts still end stuck. Treat a recovering account as a free lottery ticket and buy the next eval straight away. Do not wait on it.

## 1. Setup

- Simulator: `scripts/y2026/prop_sim.py` (NEW rule set, 65% of room, $1,100 daily budget, stop-day rules a/c/d, +8 pt stop slip, $2.37/side, 1m intraday path). The BASE row reproduces PROP_FIRM_COMPARISON_2026.md exactly (Lucid Flex 2026: 47.0% pass, 52.7% stuck, $2,081 net EV).
- Firms: Lucid Flex and Tradeify Select Flex, using the plan definitions in `prop_plans.py`. Both have the same eval mechanics (EOD $2,000 trail locking at $50,100, 40% consistency), so their eval rows are identical. Only the fees and the funded rules differ.
- 2,000 Monte Carlo evals (120 trading days, random days drawn from the year) and 1,000 funded runs (120 days) per variant, firm and year. Every variant uses the same seed, so the comparisons are paired. 2026 is primary, 2025 is the check, 2022 is the extra stress year. A rolling calendar start on every trading day of the year is also run.
- **1-contract risk** = (stop pts + 1 tick + 8 pt slip allowance) x $2 + $4.74.
- **Live room** = start-of-day room + today's closed P&L - open risk of open trades that are not yet risk-free.
- **Recovery state** carries across days. The same rules apply in the funded phase.
- **Stuck:** BASE is stuck when it closes a day with room < $400 (the attempt is dead). Recovery variants never stop early, so "stuck" means still open at day 120 with room < $400. "Open" means still open at day 120 with room >= $400.
- Days per funded = mean eval days per attempt / pass rate, i.e. trading days per funded account if you run one attempt at a time.

| Var | Rule |
|---|---|
| BASE | Current engine: rule (b) blocks all entries when room < $400. |
| R1 | Room < $400: 1 MNQ on V4+, D2, H2 if risk <= room - $100. Normal sizing again at room >= $700. |
| R2 | R1 with V4+ and H2 only. |
| R3 | R1 with all strategies. |
| R4 | R1 with risk cap room - $200. |
| R5 | R1 with entry threshold $600. |
| R6 | No recovery mode. Rule (b) removed, 65% sizing, min 1 contract only if risk <= room - $100, and qty capped so qty x risk <= room - $100. |
| R7 | R3 without D2 and Pinball (lower-risk set: NEWS, V4+, TDP, H2). |
| R8 | R7, and only trades with 1-contract risk <= $150 (H2, NEWS). |
| R9 | R3 plus the R6 guard on normal sizing (qty x risk <= room - open risk - $100). |
| R10 | R9 with entry threshold $600. |

Why the strategy filter barely matters (2026 1-contract risk, median): NEWS $121, H2 $123, V4+ $345, TDP $307, Pinball $478, D2 $564. Below $400 of room, the most a trade can risk is $300. D2 fits 3% of the time, V4+ 39%, TDP 43%, and H2 and NEWS always fit. So "V4+, D2, H2" (R1) is in practice "V4+, H2" (R2), and R3 adds only NEWS and some TDP.

## 2. Results

### 2026 (primary)

| Var | Pass | Bust | Stuck | Open | Med days (p75) | Days per funded | Cost/funded Lucid | Cost/funded Tradeify | Funded bust | Funded net EV Lucid | Funded net EV Tradeify | Lowest intraday room |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BASE | 47.0% | 0.0% | 52.7% | 0.3% | 23 (37) | 54 | $277 | $246 | 0.0% | $2,081 | $2,591 | $6 |
| R1 | 54.5% | 0.0% | 40.1% | 5.3% | 26 (46) | 135 | $239 | $212 | 0.0% | $2,546 | $3,110 | $6 |
| R2 | 55.0% | 0.0% | 39.2% | 5.7% | 27 (46) | 133 | $236 | $210 | 0.0% | $2,560 | $3,112 | $6 |
| R3 | 55.4% | 0.0% | 42.2% | 2.4% | 27 (46) | 131 | $235 | $208 | 0.0% | $2,570 | $3,142 | $6 |
| R4 | 50.3% | 0.0% | 46.9% | 2.7% | 24 (40) | 149 | $259 | $229 | 0.0% | $2,265 | $2,815 | $6 |
| R5 | 55.6% | 0.0% | 39.2% | 5.2% | 27 (49) | 132 | $234 | $208 | 0.0% | $2,580 | $3,105 | $6 |
| R6 | 54.2% | 0.0% | 42.7% | 3.0% | 26 (45) | 135 | $240 | $213 | 0.0% | $2,513 | $3,053 | $100 |
| R7 | 55.6% | 0.0% | 41.8% | 2.5% | 27 (46) | 130 | $234 | $208 | 0.0% | $2,556 | $3,138 | $6 |
| R8 | 51.3% | 0.0% | 37.7% | 11.0% | 25 (41) | 146 | $254 | $225 | 0.0% | $2,324 | $2,876 | $6 |
| **R9** | **54.8%** | **0.0%** | **42.6%** | 2.5% | 27 (46) | 133 | **$237** | **$211** | **0.0%** | **$2,563** | **$3,109** | **$100** |
| R10 | 54.9% | 0.0% | 41.6% | 3.4% | 27 (46) | 133 | $237 | $210 | 0.0% | $2,517 | $3,072 | $100 |

### 2025 (check) and 2022 (stress)

| Var | 2025 pass | 2025 bust | 2025 stuck | 2025 net EV Lucid / Tradeify | 2022 pass | 2022 bust | 2022 stuck | 2022 funded bust | 2022 net EV Lucid / Tradeify |
|---|---|---|---|---|---|---|---|---|---|
| BASE | 47.1% | 0.0% | 52.4% | $1,633 / $1,861 | 35.2% | 0.7% | 63.9% | 1.0% | $1,018 / $1,184 |
| R1 | 52.5% | 0.0% | 42.1% | $1,853 / $2,095 | 38.0% | 0.9% | 60.4% | 1.1% | $1,212 / $1,403 |
| R2 | 51.3% | 0.0% | 42.7% | $1,846 / $2,096 | 37.9% | 0.9% | 60.4% | 1.2% | $1,213 / $1,398 |
| R3 | 52.4% | 0.0% | 45.1% | $1,906 / $2,138 | 38.8% | 0.9% | 59.7% | 1.1% | $1,242 / $1,424 |
| R4 | 48.9% | 0.0% | 48.7% | $1,722 / $1,965 | 36.2% | 0.9% | 62.3% | 1.0% | $1,104 / $1,257 |
| R5 | 51.4% | 0.0% | 41.5% | $1,794 / $2,006 | 37.6% | 0.3% | 61.2% | 0.5% | $1,170 / $1,358 |
| R6 | 51.6% | 0.0% | 45.6% | $1,847 / $2,107 | 39.0% | 0.0% | 59.7% | 0.0% | $1,213 / $1,386 |
| R7 | 52.5% | 0.0% | 44.7% | $1,906 / $2,143 | 38.4% | 1.0% | 60.0% | 1.2% | $1,193 / $1,370 |
| R8 | 48.0% | 0.0% | 43.1% | $1,681 / $1,917 | 36.6% | 0.9% | 58.5% | 1.0% | $1,107 / $1,281 |
| **R9** | **51.7%** | **0.0%** | **45.6%** | **$1,855 / $2,094** | **38.9%** | **0.0%** | **60.2%** | **0.0%** | **$1,216 / $1,397** |
| R10 | 51.2% | 0.0% | 45.1% | $1,823 / $2,072 | 39.1% | 0.0% | 60.0% | 0.0% | $1,218 / $1,395 |

Median days to pass: 25 to 27 in 2025 and 19 to 21 in 2022 for every variant. Cost per funded account (Tradeify): BASE $245 / $328, R9 $223 / $297 (2025 / 2022).

Monte Carlo noise is about +-2 points on pass rates and +-$100 on EV. **R1, R2, R3, R5, R7, R9 and R10 are a statistical tie.** R4 (a $200 cap is too tight, recovery trades rarely fit) and R8 (too few eligible trades) are clearly worse. Only the guard (R6, R9, R10) separates the variants: it is the only thing that removes the 2022 busts.

### Slippage stress (stop slip +8 = model default, +10, +12 pts), best 2 variants vs BASE

| Year | Var | Stop slip | Pass | Bust | Stuck | Funded bust | Net EV Lucid | Net EV Tradeify |
|---|---|---|---|---|---|---|---|---|
| 2026 | BASE | +8 | 47.0% | 0.0% | 52.7% | 0.0% | $2,081 | $2,591 |
| 2026 | BASE | +10 | 45.3% | 0.1% | 54.4% | 0.1% | $1,989 | $2,484 |
| 2026 | BASE | +12 | 44.5% | 0.0% | 55.3% | 0.0% | $1,862 | $2,329 |
| 2026 | R3 | +10 | 53.4% | 0.1% | 43.6% | 0.2% | $2,475 | $2,996 |
| 2026 | R3 | +12 | 51.7% | 0.1% | 46.0% | 0.3% | $2,330 | $2,848 |
| 2026 | R9 | +10 | 52.7% | 0.0% | 44.1% | 0.0% | $2,454 | $2,975 |
| 2026 | R9 | +12 | 51.2% | 0.0% | 46.4% | 0.0% | $2,315 | $2,814 |
| 2025 | BASE | +10 | 44.9% | 0.0% | 54.5% | 0.0% | $1,463 | $1,680 |
| 2025 | BASE | +12 | 42.6% | 0.0% | 57.1% | 0.0% | $1,293 | $1,508 |
| 2025 | R3 | +10 | 49.1% | 0.0% | 48.3% | 0.0% | $1,688 | $1,944 |
| 2025 | R3 | +12 | 46.2% | 0.0% | 51.5% | 0.0% | $1,519 | $1,754 |
| 2025 | R9 | +10 | 49.1% | 0.0% | 48.2% | 0.0% | $1,635 | $1,874 |
| 2025 | R9 | +12 | 45.8% | 0.0% | 51.9% | 0.0% | $1,492 | $1,728 |
| 2022 | BASE | +10 | 33.9% | 0.6% | 65.5% | 1.0% | $881 | $1,069 |
| 2022 | BASE | +12 | 32.5% | 1.2% | 66.3% | 2.0% | $837 | $1,004 |
| 2022 | R3 | +10 | 37.7% | 0.7% | 61.2% | 1.4% | $1,064 | $1,234 |
| 2022 | R3 | +12 | 35.8% | 1.5% | 62.4% | 2.3% | $1,028 | $1,210 |
| 2022 | R9 | +10 | 36.9% | 0.0% | 62.6% | 0.0% | $1,068 | $1,234 |
| 2022 | R9 | +12 | 35.1% | 0.0% | 64.4% | 0.0% | $1,007 | $1,201 |

The recovery gain survives the slippage stress (about +3 to +7 pass points over BASE at the same slippage). R3 without the guard busts 1.5% of 2022 evals and 2.3% of funded accounts at +12 pts. R9 busts 0% everywhere.

## 3. Where the stuck cases go

| Year | Var | Entered recovery | Passed after recovery | Recovery success | Stuck, room < $250 | Median room of stuck runs | Funded frozen at day 120 (Tradeify) | Rolling pass | Rolling stuck |
|---|---|---|---|---|---|---|---|---|---|
| 2026 | BASE | - | - | - | 19.5% | $284 | 81.8% | 46.2% | 41.9% |
| 2026 | R3 | 52.7% | 8.5% | 16.1% | 41.0% | $135 | 68.8% | 47.6% | 29.0% |
| 2026 | R8 | 52.7% | 4.3% | 8.2% | 33.7% | $142 | 59.1% | 46.2% | 35.7% |
| 2026 | R9 | 53.0% | 8.2% | 15.5% | 41.4% | $137 | 70.1% | 48.1% | 30.5% |
| 2026 | R10 | 59.8% | 14.7% | 24.6% | 40.1% | $136 | 68.4% | 48.1% | 35.2% |
| 2025 | BASE | - | - | - | 14.9% | $294 | 86.3% | 35.4% | 51.4% |
| 2025 | R9 | 52.7% | 5.1% | 9.7% | 44.6% | $131 | 75.8% | 35.4% | 49.8% |
| 2022 | BASE | - | - | - | 25.7% | $276 | 93.1% | 31.4% | 58.5% |
| 2022 | R9 | 65.1% | 4.1% | 6.3% | 59.9% | $133 | 89.6% | 32.9% | 57.0% |

("Recovery success" = passed after recovery / entered recovery. R10 counts a pass after entering at $600, so its higher success rate is not comparable.)

- **Remaining stuck rate with R9: 42.6% (2026), 45.6% (2025), 60.2% (2022).** At a 250-day horizon (2026, Tradeify) it falls only to 39.6%, with 60.0% passing (BASE at 250 days: 49% pass, 51% stuck).
- **A lower-risk strategy set does not fix it.** R7 (no D2, no Pinball) ties R3. R8 (only trades risking <= $150) lowers stuck to 37.7%, but those runs become "open" (still grinding at day 120), not passes, and the pass rate drops 3.5 points. The limit is edge, not eligibility. At 1 MNQ, the strategies earn only about $5 to $12 per calendar day each (2026: V4+ $80, H2 $50, NEWS $23 per trade). Climbing from about $300 back to $700 takes weeks, and one or two losers push room to the dead zone.
- **Dead zone:** stuck runs end at a median $135 of room. Below about $160 (room - $100 < the smallest H2 risk, about $57), nothing can trade. That is a permanent stall again, just $260 lower. About 41% of 2026 attempts end there.
- **Funded accounts freeze too, and that is where most of the EV gain comes from.** Under BASE, 82% of 2026 Tradeify funded runs end day 120 with room < $400, because payout policy B leaves only $1,100 of room after each request and one bad day takes it under $400. Recovery cuts that to 70% and adds about $480 of trader payouts per funded account. Leaving more room after a payout is worth a separate test.
- **Calendar-order check:** on rolling 2026 starts, R9 passes 48.1% vs 46.2% for BASE. On rolling 2025 starts it passes 35.4%, the same as BASE. The Monte Carlo gain is real but smaller on the actual 2025 sequence.

## 4. Worst-case path

| | BASE | R3 | R9 |
|---|---|---|---|
| Lowest intraday room, all MC evals (2026 / 2025 / 2022) | $6 / $45 / -$16 (bust) | $6 / $45 / -$24 (bust) | **$100 / $100 / $100** |
| Lowest intraday room, funded (2022) | -$33 (bust) | -$33 (bust) | $100 |
| Longest single recovery stretch | - | 117 days | 117 days |
| 95th percentile days in recovery per attempt | - | 109 | 109 to 112 |
| Worst calendar start (2025) | 2025-07-22: stuck day 13 | 2025-07-22: 102 days in recovery, never passed | same as R3 |

The guard makes $100 a hard floor of room in the model. Only a gap through the stop that is bigger than the +8 pt allowance plus $100 could breach it. The typical bad recovery is not a bust: the account sits on 1 MNQ for 100+ days and dies in the dead zone.

## 5. Recommendation: R9, exact Pine rules

Constants: `REC_IN = 400`, `REC_OUT = 700`, `REC_CAP = 100`, `SLIP_ALLOW_PTS = 8`.

1. `room` = realized account balance (including today's closed trades) - max-loss line. Eval line = min(highest EOD balance - 2000, 50,100). Funded line = per firm (Lucid 50,100 after the first payout).
2. `openRisk` = sum, over open positions not yet moved to breakeven, of qty x `risk1`.
3. `risk1` = (stopPts + 0.25 + SLIP_ALLOW_PTS) x 2 + 4.74 (MNQ $2/pt, $4.74 round trip).
4. `var bool recMode = false`. At session open and before every entry: if `recMode and room >= REC_OUT` then `recMode := false`. If `not recMode and room < REC_IN` then `recMode := true`. The state persists across days. Never reset it on a new session.
5. **Recovery mode** (all six strategies allowed: NEWS, V4+, D2, TDP, Pinball, H2): qty = 1 if `risk1 <= room - openRisk - REC_CAP` and `risk1 <= dailyBudget - usedToday`, else skip the signal. H2 gets 1 contract even though its normal weight is 0.5.
6. **Normal mode:** keep the current sizing (65% of room, $1,100 budget, min-1 rule). Then apply the guard: `qty := min(qty, floor((room - openRisk - REC_CAP) / risk1))`. If qty is 0, skip.
7. **Delete rule (b)** (room < $400 = no entries). Keep rules (a) realized loss >= budget - $150, (c) 3 losers, and (d) passed.
8. **Banner** (orange while in recovery): `RECOVERY 1 MNQ | room $312 | resume at $700 | max risk $212`. When `room - REC_CAP` is below the smallest stop the system can take (about $60), show it in red: `DEAD ZONE | room $140 | no setup fits | start a new eval`. Log every skip as `REC skip H2: risk $131 > $112`.

Operating rule: when an account enters recovery, buy the next eval at once and leave the bot running on the old one. In expectation a recovering account is worth about 15% x the funded EV (about $480), but waiting for it costs months.

## 6. Honest caveats

- The gain is modest: about +5 to +8 pass points, and EV gains within about 2x the noise band in 2025 and 2022. In the 2025 rolling calendar check it disappears for the eval (35.4% both). Adopt R9 mainly for the guard (zero busts in every year and stress) and because it costs nothing when accounts run in parallel.
- Run one account at a time and the picture changes: days per funded account rise from about 54 to about 133 (2026), and to 216 in 2022, because a recovering attempt holds the slot for up to 120 days. In that setup, closing the attempt and buying a new eval (BASE) is faster.
- The recovery trades are a small sample: in 2026, H2 had 22 trades, NEWS 15, and the V4+/TDP trades that fit at 1 contract were the tight-stop subset. The 1-MNQ edge in recovery rests on few trades.
- NEWS trades have no 1m path here (the dip is assumed), and the 1m path ignores the order of events inside a bar. The $100 floor holds only if real stop slippage stays under 8 pts + $100 / $2 = 58 pts.
- The funded-phase gain assumes payout policy B ($1,100 left after each request). With more room left after payouts, fewer funded accounts would freeze, and recovery would add less.
- The "stuck" definitions differ: BASE ends at the stall, recovery variants run to day 120. The pass, bust and EV comparisons are like for like. The stuck columns are not exactly comparable.
- The Lucid and Tradeify eval rows are identical by design. Firm differences show only in fees and the funded phase.

Files: `scripts/y2026/recovery_test.py` (run `python recovery_test.py main`, `add:R9,R10`, `stress:R3,R9`, `horizon:R9`). Raw results: `knowledge/src/recovery_test.json`.
