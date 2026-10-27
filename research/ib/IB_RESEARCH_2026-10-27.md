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

## Night run: what do the losing trades have in common? (Oct 27, 02:40)
12,842 trades (1m RTH, 5y), 20 features measured AT ENTRY: time of day, stop size (pts and x ATR), mother-candle size, bars inside, breakout candle body/size/extension, distance to EMA20, nearest key level ahead/behind (PDH/PDL/PDC/open/HOD/LOD), day range vs ADR, position in day's range, move from open, gap, 5m volume vs 20-bar avg, previous IB result, trades so far today, weekday, side.
- Every bucket of every feature reaches 1R 43-51% of the time. Nothing separates losers from winners.
- Gradient-boosting model on all 20 features: train AUC 0.68, unseen-data AUC 0.525 (coin flip). Keeping only its top 10-50% picks does not improve results.
- Small, consistent drops: last 75 min of RTH (hit 1R 43%/40%), 8+ IB trades already that day (45%/43%), stop > 2.5 ATR (45%/43%). Too small to make money from.
- Trading the opposite way when the breakout fails (stop-and-reverse, or reverse when it closes back in the box): PF 0.91-1.01. No edge.

## Candle size matters more than any filter (RTH, 1.5R + lock, 1 MNQ, $1 fee)
| Chart | Trades | avgR | Train PF | Test PF | $/day | PF by year 22/23/24/25/26 |
|---|---|---|---|---|---|---|
| 1m | 13,054 | +0.013 | 1.00 | 0.97 | -2.3 | 1.04/0.96/0.96/0.98/0.98 |
| 2m | 6,171 | +0.047 | 1.07 | 1.03 | +9.6 | 1.14/1.13/0.98/1.09/0.95 |
| 3m | 3,933 | +0.046 | 1.08 | 0.99 | +5.8 | 1.13/1.09/1.05/0.94/1.02 |
| 5m | 2,193 | +0.048 | 1.09 | 1.10 | +6.4 | 1.22/1.00/1.10/0.92/1.26 |
| 10m | 899 | +0.043 | 1.08 | 1.14 | +2.9 | |
5m full 24h session: PF 1.05 train / 1.16 test, +$19/day; evening 18-20h 1.15/1.14; RTH 1.11/1.11.
Conclusion: the 1m inside bar is noise; 5m is a weak positive (PF ~1.1), still not strong enough to trade real money on.
