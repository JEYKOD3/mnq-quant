# Rulebook (read every morning; change only through the monthly gate)

Gate for any rule: positive in 2026 AND in 2022-2025, more green days than red in both, judged on net P&L, max drawdown, % profitable, profit factor.

## Playbook A: ORB Retest V4 Adaptive (committed-open days)
- 9:45 read: committed open = |gap vs prior RTH close| >= 0.6 x 10-day avg daily range, OR first 15 min |close-open| >= 60% of its range. Skip if prior day range > 1.2 x ADR.
- Direction = gap direction if a gap qualifies, else first-15-min direction. Trade that side only.
- Setup: 5m close outside the 9:30-9:45 range on that side; a close back inside disarms; retest of the edge + signal candle (closes in the trade-side half, real body); stop order 1 tick beyond it, next candle only.
- Stop: other side of the opening range. Target: 2R. Last entry 13:00. Flat 15:55. Risk $400, max 20 micros.
- Optional (small gain): skip trades against the 20-day regime (+5% / -5% trailing return).
- Stats: 2026 +$2,684, 40 tr, PF 1.70, 58% profitable, 23 G / 17 R days; 2022-25 PF 1.24; last 6 months PF 1.77.

## Playbook B: Failed Break at the prior day high/low (quiet-open days)
- 10:00-13:00. Price pokes 2-45 pts beyond yesterday's RTH high (low) within the last 5 bars; a bearish (bullish) signal candle closes back inside; stop order 1 tick beyond it.
- Stop: beyond the poke extreme + 5 pts (max 60 pts). Target: 1R. Risk $300.
- Regime-bound: wins in whipsaw years (2023, 2026), loses in trend years. Review monthly.

## Not allowed (tested, loses)
- Trades on quiet opens with Playbook A (PF 0.56 last 6 months). Trades against the open's direction (PF 0.66).
- Time-capped exits, TP1 + breakeven, trailing stops, structure stops on Playbook A.
- Mechanical Wade 2nd entries / LH-HL / breakout pullbacks on 1m-5m (no edge in 2026). 1-minute scalps of any kind.
- 20-day momentum as a standalone strategy (2022-25 PF 0.88).
