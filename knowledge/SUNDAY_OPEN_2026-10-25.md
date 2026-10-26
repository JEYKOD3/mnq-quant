# Sunday 6 PM open: patterns and the Sunday Gap Pullback (Oct 25, 2026)

**Data:** MNQ 5m ETH bars, 247 Sundays from Jan 2022 to Oct 2026. The gap is the Sunday 18:00 open minus Friday's last close.

**User constraints:** Sunday only, out by about 20:00, a small separate risk slice, let the data choose the style.

## Patterns
- **Gap size:** median 18 pts (7% ADR); 75th percentile 42 pts. 142 gaps up, 102 down.
- **Gaps do not fill more than chance.** Fill by 20:00 for gaps of 10-20% ADR is 26%, while a fake level the same distance on the other side gets hit 63% of the time. The open tends to continue away from Friday's close.
- **Continuation:** price moves further in the gap direction over the first 2 hours (+2 to +19% ADR, bigger gaps more). 18:00-20:00 goes with the gap 59% of the time.
- **Range:** Sunday 18:00-20:00 moves 29% ADR (median), against 17% on weekday evenings.
- **No link to Monday:** Sunday evening direction matches Monday RTH 52% (coin flip).

## Styles tested (exit by 20:00, 1 MNQ, costs in)
| Family | Versions | PF > 1 both periods | Median PF |
|---|---|---|---|
| Follow the gap at 18:05-18:30 | 240 | 17 | 0.85 |
| First-range breakout (15/30/60 min) | 136 | 3 | 1.01 |
| Gap fade back to Friday close | 3 | 0 | 0.5-0.8 |
| Pullback into the gap, then join it | 72 | 30 | 1.26 |

## Candidate: Sunday Gap Pullback (SGP)
- **Gap filter:** gap of at least 5% ADR.
- **Entry:** limit order in the gap direction at half the gap back toward Friday's close. It must fill by 19:30.
- **Stop:** 0.15 x ADR, about 55-60 pts lately.
- **Exit:** 20:00 (no target). A 2R target is almost the same.
- **Results:**
  - 64 trades, about 13 a year (about 1 a month), 53% win.
  - PF 1.95 (2.08 in 2022-24, 1.90 in 2025-26), +0.31R per trade.
  - Years: 2022 2.63, 2023 0.79, 2024 2.73, 2025 0.91, 2026 2.68.
- **Neighbourhood:**
  - Half-gap pullbacks are profitable with every stop and target tested (PF 1.3-2.5), and quarter-gap pullbacks mostly too.
  - Pullbacks of 3/4 or the full gap fail. When price retraces the whole gap, the gap is failing.
- **Caveat:** a small sample (64 trades) and two slightly negative years. Paper first.
