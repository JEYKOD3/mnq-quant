# The 5-strategy Playbook: how they work together (Oct 25, 2026)

## Sizing decision
- **Tested:** risk fraction 0.65-1.0, daily cap $1,100-2,000, and daily profit stops of $750-1,450.
- **Fastest safe setup:** 65% of the room, a $1,100 shared daily budget, TDP at full size.
  - 2025-26: 46% pass within 40 trading days, 0% fail, about $117 in eval fees per funded account ($69 fee ÷ pass rate, JJ Simon's maths).
  - Larger size passes slower, because the 50% consistency rule blocks the pass after one big day, and failures jump to 15-30%.
  - Profit stops change almost nothing.

## Team roles (1 MNQ, costs in; 2022-24 | 2025-26)

| Strategy | Role | Window | Trades/yr | PF |
|---|---|---|---|---|
| V4+ | Opening-range retest with the daily trend | 9:45-13:00 | 49 / 41 | 1.49 / 2.07 |
| D2 | 10:30 continuation after a big first hour | 10:30, exit 15:00 | 38 / 56 | 1.55 / 1.24 |
| TDP | Pullback entry on confirmed trend days | 10:30-12:00 | 41 / 41 | 1.53 / 1.55 |
| Pinball | Counter-swing after a 3-day RSI extreme, with the trend | 10:30-15:00 | 20 / 13 | 2.75 / 1.79 |
| H2 | Second-entry pullbacks on trend days, half size | 10:30-15:00 | 33 / 24 | 1.26 / 1.68 |

## Shared budget in action
- **The cap:** all five draw from one $1,100 daily budget, made of open risk plus realized losses. A trade at breakeven or closed in profit frees its risk.
- **Cuts damage:** on a bad day the budget stops the second loss. Example: Sep 29 2025, D2 was stopped, and TDP got 0 contracts at the same stop.
- **Recycles risk:** on a good day, a win frees risk for the next setup. Example: Sep 22 2025, V4+ hit its target at 12:09, then TDP took 6 MNQ.

## Real days (fresh 50K eval, $2,000 room)

**Sep 22 2025 (+$2,517), trend day up:**
- V4+ long 9:59, 9 MNQ, target 12:09: +$1,229.
- TDP long 11:12, 6 MNQ, target 15:15: +$1,389.
- H2 got 0 contracts while the budget was busy, then lost $100 later.

**Jun 5 2026 (+$2,075), trend day down:**
- D2 short 10:30, 1 MNQ, +676 pts: +$1,347.
- TDP short 10:32, 2 MNQ, target 11:35: +$728.

**Oct 22 2026 (+$1,847):**
- V4+ short 10:15, 4 MNQ, target 10:30: +$1,079.
- Pinball short 10:30, 2 MNQ, held to 15:55: +$769.

**Oct 16 2026 (+$1,315):**
- V4+ short 10:10, target: +$1,042.
- H2 short 11:55, target: +$273.
- D2 got 0 contracts (budget full).

**Sep 25 2026 (-$1,099):**
- V4+ long, stopped in 5 minutes.
- The budget was used up, so nothing else traded. That's the worst day size.

**Sep 29 2025 (-$1,091):**
- D2 long stopped.
- TDP's signal got 0 contracts, which saved a second loss.

## Caveats
- **Busy days are rare:** on 2025-26 data, only 20 of 200 trading days had 3 or more strategies firing.
- **TDP overlaps:** it shares 134 of its 196 days with the Playbook, and their results correlate 0.7. It mostly adds a second entry on trend days.
