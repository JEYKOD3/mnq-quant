# MNQ Playbook: V4+ and D2 (research of Oct 24, 2026)

Data: MNQ RTH 1-minute and 24h 5-minute bars, Oct 2021 to Oct 2026 (Databento, checked against TradingView).
Method: tune on 2022-2024, confirm on 2025-2026 (unseen). Costs included: $4.74 commission, 1 tick slippage, plus 8 points of extra slippage on every stop in the eval simulations.
An independent backtest, written from scratch by a separate agent, confirmed the main result.

## 1. The daily routine (no screen-watching)

| Time (ET) | What to do |
|---|---|
| Before 9:30 | Read the daily trend: is yesterday's close above or below its 20-day average? Only trade V4+ in that direction. Check the news calendar (CPI, FOMC). |
| 9:45 | Mark the opening range (9:30-9:45). Decide whether V4+ is active today. |
| 9:45-13:00 | V4+: set an alert at the opening-range edge. When it fires, enter on the 1-minute rejection candle. Place the bracket (stop and 2R target) and walk away. |
| 10:30 | D2 check: if price is 0.5 ADR or more from the open, enter with the move. Stop at the open. Exit at 15:00. |
| 15:00 / 15:55 | Time exits (D2 at 15:00, V4+ at 15:55 if neither stop nor target is hit). Be flat by 16:45 (Lucid rule). |

## 2. V4+ rules

- **Direction:** the daily trend only. Long when the prior close is above its 20-day average, short when below.
- **Committed open:** gap of at least 0.4 ADR, or a first-15-minute move (close at 9:45 minus the open) of at least 40% of the 15-minute range. Direction = gap if it qualifies, else the first 15 minutes. It must match the trend, otherwise no trade.
- **Entry:** on the 1-minute chart, price breaks out of the 9:30-9:45 range (a 5-minute close outside it), retests the edge, then a rejection candle prints:
  - It closes outside the range.
  - It closes in the trade-direction half of its own range.
  - Its body is at least 30% of its range.
  - Then enter on a stop order 1 tick beyond that candle, between 9:45 and 13:00.
- **Stop and target:** stop at the other side of the opening range. Target 2R, otherwise exit at 15:55.
- **Stats 2022-2026:**
  - 219 trades (about 46 a year), PF 1.65, win rate 54%.
  - PF by year: 1.70 / 1.74 / 1.14 / 2.51 / 1.80.
  - Longest losing streak: 5.
- **Same rule against the trend:** PF 0.6-0.8 in 2025-26, so never take it.

## 3. D2 rules

- **Trigger:** at 10:30, if |price - open| is at least 0.5 ADR, enter in the direction of the move.
- **Stop and exit:** stop 1 tick beyond the open. Exit at 15:00.
- **Sizing:** full size when the trade matches the daily trend, half size when it doesn't.
- **Skip:** FOMC days and CPI days.
- **Stats:** 225 trades (about 47 a year), PF 1.39, every year between 1.20 and 1.60. 79% of D2 days are days without a V4 trade.
- **Optional filter:** trade only in London's direction (3:00-9:30 move). That gives PF 1.66 / 2.26 with London, versus 1.28 / 0.69 against.

## 4. Sizing for the eval

- **Risk per trade:** 65% of (balance - trailing max-loss line), capped so total daily risk stays under $1,100.
- **Example:** at the start, the room is $2,000, so risk is $1,300 capped to $1,100. On a 110-point stop, that is about 5 MNQ.
- **Why this rule:** sizing from the room makes a blowup almost impossible; the eval stalls instead of dying.

## 5. Eval odds (Lucid Flex 50K, simulated attempts started every 2 days)

| | Passed within 10 trading days | 20 | 40 | 60 | Failed |
|---|---|---|---|---|---|
| 2022-24 | ~5% | ~14% | ~29% | ~37% | ~5% |
| 2025-26 (unseen) | ~5% | ~19% | ~37% | ~46% | ~0% |

- **The ceiling:** every combination and filter tried lands on this same frontier.
- **Why it can't go higher:** speed = edge per trade x number of trades, and the $2,000 max loss caps the size.
- **What a bigger size does:** risking the full room raises failures to 15-37% without passing any faster.

## 6. What was tested and rejected

- **High-R opening breakouts** (tight 5-15% ADR stops, 5-10R winners):
  - They win only 8-24% of the time, so drawdowns run 25-200R.
  - The portfolio optimizer gave them zero weight.
- **Other rejects:**
  - Tighter stops on V4 (they fail on the unseen 2025-26 data).
  - Late-day momentum and fades.
  - London and pre-market breakouts.
  - The FOMC 2 PM breakout.
  - Inside-bar breakouts (all variants).
  - 10-point scalps.
- **Big fast moves:** 62% start between 9:30 and 10:30, but their direction follows the trend only 44% of the time. They are not predictable enough to trade on their own.
- **Overnight sessions:** they do not predict New York's direction (about 50/50).
- **Overnight holding:** not allowed on Lucid (flat by 4:45 PM).

## 7. Week of Oct 26, 2026 context

- **Trend:**
  - MNQ closed Friday at 29,122, below its 20-day average (30,454), which is falling.
  - It is 7.9% off the high, with the semiconductor index (SOX) down about 15% this month.
  - So: V4+ shorts only; D2 shorts at full size, longs at half.
- **Events:**
  - Wed Oct 28: FOMC at 2:00 PM (skip D2). Microsoft and Alphabet report after the close.
  - Thu Oct 29: Q3 GDP and September PCE at 8:30, so a gap is likely and could trigger V4+. Amazon reports after the close.
- **Levels:** prior-day high 29,325.75, low 28,986.25, close 29,122.25. ADR is about 444 points.

Scripts: `scripts/lab/` (core.py, opt_v4.py, cont.py, regime2.py, v4max.py, hir.py, anatomy.py, eth.py, sessions.py, news.py, portfolio.py, evalsess.py). The rule registry is in `knowledge/RULES.md`, entries X6-X14.
