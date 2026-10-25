# New strategy discovery: market questions (Oct 25, 2026)

MNQ, RTH 1m bars and ETH 5m bars, Jan 2022 to Oct 2026. Each result is checked in 2022-24 and again in 2025-26. Scripts are in scripts/discover/.

**User's constraints:**
- All hours available.
- 1-3 trades a day, held 15-60 minutes.
- Playbook (add to it or replace it) and execution style are decided after the research.

| # | Question | Answer | Holds in both periods? |
|---|---|---|---|
| 1 | When does MNQ move? | 9:30-10:15 has the biggest range (27-37% of ADR per 15 min), falling to about 15% from 12:00 to 15:30; 15:45 rises again (21%). Efficiency is about 0.45 in every slot, the same as a random walk, so no slot trends more than another inside itself. | yes |
| 2 | Does the morning predict the day? | Only weakly: the first 15-60 min continues 51-60% of the time. Not enough alone. | weak |
| 3 | Do levels bounce or break? | Compared with fake levels, real levels break more often. Overnight high: 7 points less bounce in both periods; OR30 high: 4-5; prior close: 3-8. Prior-day and overnight lows: about neutral. | yes (breakout bias on highs and prior close) |
| 4 | Do gaps fill? | Fill rates equal a fake level the same distance away. Small gaps fill because they're close. | no edge |
| 5 | After a big 60-min move? | No reliable continuation or reversal at any hour. | no |
| 6 | Trend day known by 10:30? | Yes. With first-hour efficiency >= 0.6 and price outside the prior-day range, 71% / 68% of days trend (base rate 52% / 48%), and the rest of the day goes the same way +9.5% / +7.4% ADR. | yes |
| 7 | Segments | Weekday, news, FOMC and volatility regime: nothing stable across periods. | no |
| 8 | Stop size vs noise | For 80% of random entries to reach +60 pts before the stop, the stop needs about 120 pts at 10:00 and about 95 pts after 13:00 (2025-26). 25-40 pt stops are inside the noise. | n/a |

## First candidate: 10:30 trend-day continuation
- **Rule:** first-hour efficiency >= E, price outside the prior-day range at 10:30, trade in that direction.
- **2022-24:** PF 1.4-1.8 across almost all stop and exit versions.
- **2025-26:** PF 0.5-1.1. Only E 0.7, stop 0.4 ADR, 1.5R target stays positive (PF 1.78 / 1.14). The trend-day odds hold, but entering at 10:30 gets stopped out by noise in 2025-26.
- **Next step:** enter on the first pullback after 10:30 instead of at 10:30, with a wider stop and a partial exit.

## Earlier result kept
- **8:30 news reversion to the 8:29 price** on CPI, PPI and NFP days, 5m bars, stop 38-50. PF 1.5-2.2 and positive every year, but only about 12 trades a year. See FAIR_PRICING_BACKTEST_RESULTS.md.
