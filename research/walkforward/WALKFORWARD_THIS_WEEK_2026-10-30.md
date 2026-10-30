# Walk-forward contest, Oct 26 -> Oct 30 07:00 ET (wf.py)
Decisions every 5 min using only closed bars; ML retrained before each session on prior sessions only.
Trade sim: one position at a time, stop 1.5 x ATR(14, 5m) (~43 pts this week), target 1:1, time stop 60 min, cost 1 pt.

| Model | Call accuracy (60 min) | Trades | Pts | PF | Max DD pts |
|---|---|---|---|---|---|
| Fade the last hour (60-min move > 2 ATR, bet the other way) | 61.4% | 115 | +723 | 1.32 | 297 |
| Always short (benchmark) | 51.1% | 189 | +167 | 1.04 | 802 |
| Swing structure HH/HL vs LH/LL | 47.8% | 149 | +37 | 1.01 | 588 |
| Pullback 61.8 + trend (5m) | 46.9% | 39 | -27 | 0.97 | 351 |
| ML logistic (walk-forward) | 44.9% | 140 | -30 | 0.99 | 581 |
| Trend (5m EMA slope) | 42.0% | 122 | -182 | 0.94 | 614 |
| Breakout of last-hour high/low | 42.1% | 90 | -270 | 0.87 | 622 |
| VWAP side | 43.4% | 186 | -492 | 0.89 | 942 |
ML probabilities were inverted this week (P(up) <= 0.35 -> up 63%): it learned trend, the market mean-reverted.

Fade robustness: threshold 2 ATR worked both weeks (last week PF 1.12, this week 1.32); 1.5 / 2.5 / 3 ATR mixed.
RTH PF 2.17 vs overnight 1.11 this week. Last week sell-the-rips 1.56 / buy-the-dumps 0.84; this week 1.26 / 1.37.
5-year check: fade-2ATR loses every year (RTH PF 0.83-0.94). A daily switch fade/trend based on the prior 3 days also loses (5y).
=> Regime behavior of the current choppy high-volatility market, not a durable edge. Retire it after a losing day or 3 straight losses.
