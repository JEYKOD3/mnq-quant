# MNQ price action, Oct 19-30 2026 (MNQZ6 1m, through Oct 30 05:09 ET)

## Sessions (18:00 to 17:00)
| Day | Range | Net | Notes |
|---|---|---|---|
| Mon 10-19 | 781 | +514 | overnight +549, RTH -58 |
| Tue 10-20 | 512 | +149 | RTH low 9:45, closed at the high |
| Wed 10-21 | 387 | +99 | high 30,114 at 13:21 |
| Thu 10-22 | 963 | -892 | high at the open, fell all day to 29,033, closed at the low |
| Fri 10-23 | 340 | +64 | low 28,986 held |
| Mon 10-26 | 548 | +198 | RTH +209 |
| Tue 10-27 | 593 | +323 | closed near high |
| Wed 10-28 | 506 | -61 | high 30,180 at 16:01, then the earnings drop 16:00-16:50 |
| Thu 10-29 | 683 | -573 | high at the 18:00 open, low 29,111 at 16:06, closed near the low |
| Fri 10-30 | | | overnight broke 29,111 (prior day low) at 18:19 |
Two-sided range 28,986-30,180 with violent legs. Support zone 29,000-29,100 (Oct 22, 23, 29 lows). Resistance 30,000-30,180.
Choppiness: price travels 10-150x its net move in a session (efficiency 0.006-0.09).

## When it moved (ET, sum over sessions)
10:00-11:59 rallied (hour up 70-80% of days). 12:00-14:59 faded (down ~70%). 16:00 hour: big drops (earnings Oct 28).
Evening 19:00-22:00 and 01:00/03:00 leaned down.

## Key levels (first touch)
Broke 17 of 26 times. Breaks above highs (PDH/ONH, 1m close 5 pts beyond, stop 25 pts, 2R): 11 trades, -390 pts.
Breaks below lows (PDL/ONL): 7 trades, +386 pts. Downside breaks followed through; upside breaks were sold.

## Fair Value Gaps (1,824 retests, same result both weeks)
- Fresh (retested within 2 min): continued 60-62%. 3-5 min: 44-49%. 6-15 min: 26-29%. 16+ min: 14-20% (old gaps fill).
- Bearish gaps held 51%, bullish 43-46%.
- Bullish gaps during DOWN BOUNCE / DOWN BREAKING filled 60-67%: do not buy gaps on a bounce in a downtrend.
- Bearish gaps during DOWN BOUNCE / UP BREAKING held 60%.
- 15m/1h/4h bias alone made no difference.

## Rules that made money in these 2 weeks (in-sample, tiny samples)
| Rule | Trades | Pts | 5-year check |
|---|---|---|---|
| Short a break of PDL/ONL (1m close 5 pts below, stop 25 pts above the level, 2R) | 7 | +386 | similar breakout rules ~ PF 1.0 |
| Midday fade: at 12:00 if above VWAP and above the 9:30 open, short, stop morning high +5, target VWAP | 7 (5 wins) | +401 | PF 0.81 (loses) |
| 10:00 long if above VWAP, stop below 9:30-10:00 low, exit 12:00 | 5 (4 wins) | +370 | PF 0.99 |
| Buy a break of PDH/ONH | 11 | -390 | avoid in this regime |
These describe the current regime only. Stop using a rule after 3 losses in a row.

## Can an indicator call the trend? (trend_engine.py, Oct 19 -> Oct 30 07:00)
- 69 swings of 150+ pts in ~10 sessions (about 6 per day, both directions).
- Engine (5m EMA21 slope + close beyond last 5m swing) confirmed a new direction 30-120 min and 100-200 pts after the turn.
- Its states did not predict the next hour: DOWN -> price lower 60 min later 52% of the time; UP -> higher 44%. Coin flip.
- Conclusion: direction indicators confirm, they do not forecast. Use them only as a filter for pullback entries;
  invalidation = close beyond the last lower high / higher low (pullback > 100% of the leg continued only 21%).
