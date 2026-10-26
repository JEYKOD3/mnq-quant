# Fast pass study: can we pass Lucid Flex 50K in about a week? (Oct 26 2026)

**Short answer: not with these strategies, and adding risk makes it worse.** With the v31 team, a pass inside 5 trading days happened in 0.5% of 2026 starts (3% in 2022). Inside 8 days it was 3% in 2026, 3% in 2025 and 10% in 2022. The median pass takes 14 trading days when it comes within 20 days, about 23 when given 60. No sizing, budget, front-loading or strategy-subset variant raised the 5-day or 8-day pass rate in all three years. Every bigger-risk version lowered the 20-day pass rate, and the no-guard versions also blew 11-20% of accounts.

## Method
- Scripts: `scripts/y2026/fast_pass.py` (simulator), `fast_plans.py` (plans), `fast_variants.py` (strategy changes), `fail_an.py` (failure analysis), `fast_tree.py` (day-5 / day-8 position). The raw results are in `fast_*.json`.
- Lucid Flex 50K rules modeled:
  - $3,000 target.
  - EOD trailing $2,000 floor, capped at 50,100. The floor is checked against intraday equity on the 1m path.
  - Pass requires best day <= 40% of total profit.
  - $1,200 daily loss limit as a soft lock: flattened at the first touch, day over.
  - No trade's worst case may push today's losses past $1,200. Max 40 MNQ.
- Trades come from the NEW rule set the Playbook runs: NEWS, V4+, D2 0.6/13:15, TDP, Pinball 2R/180m, H2. Costs are $2.37/side plus 1 tick, and an extra 8 pts on stop exits. Same-minute signals are sized in Pine order.
- v31 sizing:
  - 65% of room per trade.
  - $1,050 day budget (realized losses + open risk).
  - Stop day at budget - $150 or 3 losers, and once the eval is passed.
  - Recovery 1-lot mode when room < $400.
  - Guard: qty x 1-lot risk <= room - $100.
- Rolling sequential evals: every trading day is a start, then the real following days run. 2026 = Jan 2 to Oct 23 (206 starts), 2025 = check year, 2022 (Mar-Dec) = stress year.

## Why a one-week pass is unlikely (the arithmetic)
- In 2026 the team fired 0.73 trades per day, and **114 of 210 days had no signal at all**.
- Average 1-lot risk was $342 and expectancy 0.16 R per trade. That is about $41 per day per contract set.
- $3,000 in 5 days means about $600 per day. That needs 15x the 1-lot edge, while the $2,000 trailing floor allows roughly 3-4x the 1-lot risk on one trade.
- The 40% rule means at least 3 winning days are needed: no day can count more than $1,200 of a $3,000 pass. A good week needs most of its 5 days to produce a winner, and the team only trades on about half of the days.
- Per-strategy edge in 2026 (R per trade on 1 MNQ): H2 0.54, NEWS 0.27, V4+ 0.24, TDP 0.13, D2 0.13, Pinball 0.03.

## Plan grid (pass in 5 / 8 / 20 trading days)

| Plan | 2026 | 2025 | 2022 | Worst bust rate (20d) | 2026 median days | Worst equity seen |
|---|---|---|---|---|---|---|
| BASE v31: $1,050/day, 65% of room | 0% / 3% / 22% | 0% / 3% / 18% | 3% / 10% / 30% | 0% | 14 | -1898 |
| $1,500/day, 65% | 0% / 2% / 16% | 0% / 1% / 17% | 1% / 6% / 26% | 0% | 14.5 | -1894 |
| $2,000/day, 80% | 0% / 0% / 6% | 1% / 2% / 16% | 1% / 5% / 22% | 0% | 19 | -1898 |
| $2,500/day, 100% | 0% / 0% / 2% | 1% / 1% / 15% | 1% / 5% / 22% | 0% | 19 | -1898 |
| $1,050/day, 100% of room | 0% / 1% / 13% | 0% / 3% / 21% | 3% / 9% / 30% | 0% | 14 | -1897 |
| Fixed 4 MNQ per trade | 0% / 0% / 1% | 0% / 3% / 19% | 0% / 2% / 22% | 0% | 14.5 | -1898 |
| Fixed 8 MNQ per trade | 0% / 0% / 7% | 1% / 3% / 18% | 0% / 5% / 27% | 0% | 18 | -1899 |
| Front-load $2,000, $2,000, then $1,050 | 0% / 2% / 14% | 1% / 3% / 20% | 2% / 9% / 29% | 0% | 13 | -1898 |
| Front-load $2,500, $1,500, then $1,050 (100%) | 0% / 2% / 15% | 0% / 3% / 21% | 2% / 7% / 29% | 0% | 14.0 | -1898 |
| BASE + day profit cap $1,200 | 0% / 2% / 20% | 0% / 3% / 16% | 3% / 9% / 30% | 0% | 15.0 | -1898 |
| V4+ and D2 only | 0% / 0% / 5% | 1% / 2% / 4% | 0% / 4% / 17% | 0% | 17 | -1804 |
| No Pinball/H2 | 0% / 1% / 20% | 0% / 2% / 11% | 2% / 7% / 29% | 0% | 15.5 | -1868 |
| No NEWS | 0% / 2% / 11% | 1% / 4% / 22% | 2% / 9% / 28% | 0% | 13.0 | -1898 |
| Fixed $600 risk per trade | 0% / 2% / 7% | 0% / 1% / 7% | 0% / 1% / 14% | 0% | 13 | -1884 |
| Fixed $900 risk per trade | 1% / 3% / 16% | 0% / 2% / 19% | 0% / 5% / 24% | 0% | 15.0 | -1896 |
| $500 risk + 35% of profit | 0% / 2% / 8% | 0% / 1% / 9% | 0% / 3% / 25% | 0% | 13 | -1781 |
| All-in: 100% of room, $1,200, no guard, no recovery | 0% / 1% / 17% | 0% / 2% / 20% | 1% / 9% / 33% | 11% | 15 | -2061 |
| All-in: 100% of room, $2,000, no guard | 0% / 0% / 3% | 1% / 1% / 16% | 1% / 4% / 19% | 20% | 12 | -2118 |
Reading the table:
- Raising the budget or the room fraction lets two trades stack. One bad day then drops the eval into the slow 1-lot mode, so it stalls for weeks.
- Fixed contract counts are too big on wide-stop trades (D2, Pinball) and too small on tight ones.
- Front-loading gives no lasting gain.
- A daily profit cap at $1,200 (to stay inside the 40% rule) costs a little, because the rule rarely blocks: open-but-consistency-blocked evals were 3% or less.
- Removing strategies cuts the number of trading days, which is the bottleneck.

## Strategy changes tested (BASE sizing; 1-lot net 2026 / 2025 / 2022, then pass in 8 / 20 days)

| Variant | 1-lot net $ | 2026 | 2025 | 2022 |
|---|---|---|---|---|
| BASE team | 8,515 / 6,976 / 9,030 | 3% / 22% | 3% / 18% | 10% / 30% |
| D2 th .5 | 7,798 / 7,548 / 8,748 | 3% / 22% | 3% / 14% | 10% / 29% |
| D2 half stop | 6,606 / 6,591 / 9,239 | 2% / 12% | 2% / 12% | 10% / 32% |
| D2 th .5 half stop | 5,588 / 7,455 / 9,323 | 2% / 10% | 3% / 10% | 10% / 29% |
| D2 2R target | 8,033 / 6,976 / 9,030 | 3% / 20% | 3% / 18% | 10% / 30% |
| V4+ 2R | 9,361 / 7,829 / 9,495 | 3% / 20% | 3% / 15% | 5% / 31% |
| V4+ 1R | 8,113 / 8,521 / 8,285 | 3% / 18% | 4% / 29% | 6% / 27% |
| V4+ no BE | 8,515 / 7,463 / 9,002 | 3% / 22% | 3% / 20% | 8% / 30% |
| TDP 1R | 8,270 / 6,321 / 8,356 | 2% / 14% | 2% / 13% | 10% / 30% |
| TDP 2R | 8,461 / 6,568 / 9,301 | 2% / 20% | 2% / 17% | 9% / 30% |
| H2 full size | 8,515 / 6,976 / 9,030 | 1% / 18% | 3% / 16% | 6% / 28% |
| H2 1.5R | 8,389 / 6,781 / 9,115 | 2% / 20% | 2% / 16% | 9% / 30% |
| H2 th .3 | 8,393 / 7,396 / 8,350 | 4% / 20% | 2% / 12% | 8% / 26% |
| drop Pinball | 8,327 / 4,810 / 7,180 | 3% / 22% | 3% / 17% | 10% / 30% |
| drop TDP | 7,005 / 5,010 / 6,878 | 2% / 13% | 0% / 9% | 9% / 28% |
| H2 full + drop Pin | 8,327 / 4,810 / 7,180 | 1% / 19% | 3% / 15% | 6% / 29% |
| H2 full + D2 th.5 | 7,798 / 7,548 / 8,748 | 1% / 19% | 3% / 15% | 6% / 27% |
- No change improved all three years.
- V4+ 1R target helped 2025 (20-day pass 29% vs 18%) but cost 2026 and 2022.
- H2 trend threshold 0.3 gave the best 2026 8-day rate (4%) but is worse in 2025 and 2022.
- The D2 half stop raises contract count but loses edge and adds busts.
- Kept: none. The current rules stay.

## MES instead of MNQ
The same engine was run on MES (5m bars expanded to 1m, $5/pt, 2 pt stop slip, NEWS off). V4+ produced no MES signals in this port (its retest engine has MNQ-specific settings), so the MES team is D2, TDP, Pinball and H2.

| Plan | 2026 | 2025 | 2022 | Worst bust (20d) | 2026 median | Worst equity |
|---|---|---|---|---|---|---|
| MES BASE v31 sizing | 0% / 0% / 7% | 0% / 0% / 8% | 0% / 0% / 3% | 0% | 14 | -1887 |
| MES bud1500 f.8 | 0% / 0% / 2% | 0% / 0% / 11% | 0% / 0% / 3% | 0% | 19 | -1895 |
| MES bud1200 f1.0 guard | 0% / 0% / 7% | 0% / 0% / 9% | 0% / 0% / 3% | 0% | 14 | -1895 |
| MES risk $900 | 0% / 0% / 7% | 0% / 0% / 5% | 0% / 0% / 3% | 0% | 14 | -1894 |
| MES no Pin | 0% / 0% / 6% | 0% / 0% / 0% | 0% / 0% / 5% | 0% | 13 | -1895 |
| MES V4+D2 | 0% / 0% / 0% | 0% / 0% / 0% | 0% / 0% / 0% | 0% | None | -1613 |
On MES, D2 was flat in 2026 and 2025 and Pinball lost in 2026. MES is clearly worse for these rules: stay on MNQ.

## Failure analysis (BASE, non-passing evals within 20 days)
- **Too slow, not a loss:** 2026 93 of 161, 2025 112 of 210, 2022 62 of 152 evals never fell below -$800. They just did not earn enough.
- **First hole (equity <= -$800) came from:**
  - 2026: TDP 29, V4+ 23, NEWS 8, D2 5.
  - 2025: V4+ 58, TDP 23, NEWS 11.
  - 2022: TDP 32, NEWS 22, V4+ 21, Pinball 15.
- **Day type of that hole:**
  - 2026: mostly "mid" (38) and chop (25).
  - 2025: mostly chop (69).
  - 2022: spread across trend, mid and chop.
- Event days caused 12% (2026) to 39% (2022) of the holes. Skipping all event days was not better, because NEWS and D2 earn on them.
- Typical losing trade size: 3-6 MNQ. One full-size loser plus a second loser puts the eval under $1,000 of room, and the guard then cuts it to 1 lot. Recovery from there takes 2-4 weeks.
- Fixes tried against these causes: smaller fixed-$ risk, profit-scaled risk, skipping weak strategies, tighter/looser targets. None beat BASE on 8- and 20-day passes across years. The slow-mode stall is the price of having almost no busts: 0% at 20 and 60 days in all three years.

## Probability tree for a week (BASE v31, rolling starts)

| Where you are | After 5 days: 2026 / 2025 / 2022 | After 8 days: 2026 / 2025 / 2022 |
|---|---|---|
| passed | 0% / 0% / 3% | 3% / 3% / 10% |
| ahead +1500 or more | 18% / 8% / 12% | 24% / 14% / 11% |
| up 0 to 1500 | 42% / 52% / 45% | 34% / 40% / 37% |
| down 0 to -1000 | 27% / 30% / 30% | 25% / 30% / 28% |
| down more than -1000 (slow mode) | 13% / 10% / 11% | 15% / 13% / 14% |

Given 40 trading days: 43% (2026), 45% (2025), 50% (2022). Given 60: 53% / 48% / 51%, with a median of 23 / 24 / 19 days. Busts: 0% in every year. Late-2026 starts run out of data, so these 2026 numbers are understated.

- Good week (about 1 in 5 in 2026): +$1,500 or more after 5 days. The pass then usually comes in week 2.
- Average week (about 4 in 10): up a little. Expect 3-5 weeks.
- Bad week (about 4 in 10): down. 13% are below -$1,000 and in slow mode.

## Recommended plan
1. **Keep v31 exactly: $1,050 day budget, 65% of room, stop day, recovery mode.** It had the best or tied-best 8-day and 20-day pass rate in every year, with 0% busts. Every higher-risk version was worse.
2. Plan for 3-5 weeks, not one. A pass in week 1 is a 1-in-30 bonus, not the base case.
3. Keep the stop-at-pass rule. Do not add a daily profit cap: the 40% rule rarely blocks.
4. Stay on MNQ, not MES.
5. Only a strategy with more signals can make it faster. Half the days have no trade, so the next lever is a validated extra setup on no-signal days, such as the evening module (SGP + WCC) with its own small budget. More risk on the same signals is not that lever.
