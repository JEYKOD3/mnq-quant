# Inside Bar research (Oct 27 2026)

Data: MNQ 1m RTH, 1,289 days (Oct 2021 - Oct 20 2026), trend from 15/60/240 EMA21 (5m full-session data). 1 MNQ, $1 fees, 1-tick slippage on stops. Out-of-sample = last 30% (from 2025-04-23).

## Exit versions (all signals)
| Version | WR | PF | $/day | OOS PF |
|---|---|---|---|---|
| A 1R fixed | 49% | 0.93 | -19.6 | 0.91 |
| B 1.5R fixed | 40% | 0.95 | -13.7 | 0.93 |
| C 1.5R, lock +1R once 1R reached | 49% | 0.99 | -2.3 | 0.97 |
| E 1R + exit when back in box | 34% | 0.91 | -21.0 | 0.89 |
| G C + key-level target | 49% | 0.99 | -2.5 | 0.97 |
| I C + time stop (10 bars, <0.5R) | 47% | 0.98 | -4.4 | 0.97 |

## Session filters (best: stop after first win)
C + stop after first win: PF 1.03, +$2.1/day, 59% green days, OOS PF 1.02. Stop after 1 loss, 2 consecutive losses, $400 cap: no edge.

## MFE ("how far did it go")
- 48% reach 1R, 38% reach 1.5R, 31% reach 2R.
- Of trades that never reach 1R (52%): 41% never get past 0.25R, 26% reach 0.25-0.5R, 19% 0.5-0.75R, 14% 0.75-1R.
- Key level (PDH/PDL/PDC/open/session high-low) before 1R: reach 1R 48.9% vs clear path 47.8%. Levels do NOT predict failure.

## Verdict
No version has a real edge (PF 0.93-1.05). C (1.5R with +1R lock) is the best exit structure and is now in the indicator. Keep IB as a paper tracker.
