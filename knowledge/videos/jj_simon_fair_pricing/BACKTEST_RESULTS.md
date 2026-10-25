# Fair Pricing Theory: backtest results (Oct 25, 2026)

MNQ, Jan 2022 to Oct 2026, one account, 1 contract, $2.37/side commission plus 1 tick of slippage. Versions were picked on 2022-24 and checked on 2025-26. Scripts are in scripts/fair/.

## 1. Raw claim: price returns to the fair price more often than chance
- **Result:** no. With a 9:30 open or a 9:29 close as fair, the return rate equals the random-walk odds S/(D+S). A placebo level (the 10:00 price) behaves the same.

## 2. Why his entries lose in New York 9:30-11:00
The baseline is his rules: displacement or break of structure toward fair, 38/25, 0.8 room, 4 trades, 3-loss stop. It wins 37% and needs 41% to break even.
- **The stop is noise:**
  - 51% of stops hit within 3 minutes.
  - 62% of stopped trades later reached the 38-pt target.
- **Trend days:**
  - On about 25% of days price never trades at the open after 9:35. Trades there win 26%, PF 0.45.
  - On days price trades at the open 6 or more minutes, PF is 1.15. This can't be known in advance.
  - Real-time filters didn't fix it: crossings so far, time since last touch, gap size, range-sized stops, structure stops.
- **Timing:** entries before 9:40 are the worst (PF 0.50).

## 3. Search
- **New York 9:30-11:00:**
  - 1,620 versions: fair price (open, 9:29 body, pre-open middle, news), timeframe 1/2/5 min, signal type, start time, 9 stop/target sets.
  - 282 more with his filters added: overnight bias, news only or skip, breakeven at fair, loss limits, continuation, gap, room, dmin/dmax.
  - 200 more with range-sized or structure stops.
  - None beats PF 1.0 in both periods except news days.
  - The best 2022-24 version reaches PF 1.17, then falls to 0.45 in 2025-26.
- **2 PM session back to the 9:30 price:** 75 versions, best PF 0.75.
- **6 PM, Asia (8 PM, fair = own open or 6 PM), London 3 AM, on 5m bars:** 90 versions, all lose.
- **News days after 9:30:** 480 versions, median PF 0.99. That's break-even, not an edge.

## 4. What does work: the 8:30 news reversion, 8:30-9:30, 5m bars
- **Setup:**
  - Days: CPI, PPI and NFP.
  - Fair price: the 8:29 price (close of the 8:25 5m bar).
  - Entry: a displacement or break-of-structure 5m close toward fair, with at least 0.8 × target of room.
  - Wide bracket: stop 38-50, target 50-76.
- **Results:**

| Version | Trades | Win | PF | 2022-24 PF | 2025-26 PF | Every year > 1 |
|---|---|---|---|---|---|---|
| either 38/57 | 59 | 59% | 1.96 | 1.60 | 2.69 | yes |
| either 50/50 | 64 | 62% | 1.51 | 1.55 | 1.45 | yes |
| either 50/76 | 45 | 58% | 1.86 | 1.53 | 2.40 | yes |
| displacement 50/76 | 36 | 61% | 2.22 | 1.68 | 3.50 | yes |
| either 25/38 | 88 | 39% | 0.81 | 0.73 | 0.94 | no (tight stop fails) |

- **Neighbourhood (36 versions):** median PF 1.56, and 28 of 36 pass both periods.
- **Placebo fair price:**
  - 8:00: median PF 1.20, 18/36 pass.
  - 7:30: median PF 1.27, 15/36 pass.
  - So part of the edge is simply fading the news spike with a wide stop. The 8:29 level adds to it.
- **Other 8:30 releases,** detected by a range spike: they lose (PF 0.5-0.9).
- **By event:** NFP PF 2.9, CPI 1.6, PPI 1.6.
- **Caveats:**
  - About 12 trades a year, so the sample is small.
  - 5m bars are coarser than his 1m chart.
  - The within-bar order of stop and target is assumed worst case.

## 5. Verdict
- **The general Fair Pricing Theory (reversion to the open) has no edge on MNQ 2022-2026.**
- **The one surviving piece is his news trade:** CPI, PPI and NFP, 8:30-9:30, back toward the 8:29 price, with a stop of 38 pts or more. It's too rare to pass an eval on its own (about 1 trade a month). It fits as an add-on to the Playbook on news mornings, before 9:30.
