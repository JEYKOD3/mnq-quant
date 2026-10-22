# MNQSCALP Master Plan (decided 2026-10-20)

## End goal
Fully automated price-action strategy trading $50K prop accounts (Lucid / FundedNext), MNQ first then MES, any timeframe, nearly 24h (18:00 to 16:40 ET, flat before 4:45 PM prop close). Stop + TP1 scalp + breakeven + runner, or 1:1 in low volatility.

## Decisions
- Development platform: **TradingView Pine Script strategy** (Claude edits, backtests and reads results directly in the browser). Moomoo retired after the V5 port (V4.0/V4.1 kept as reference).
- Jey's NinjaTrader: **NT8 desktop on Windows**.
- Live mode: **fully automated**.
- Session: **nearly 24h**.
- Live route (decide at V10): (a) TradingView alerts -> webhook bridge (TradersPost / CrossTrade) -> Tradovate or NT8 prop account, or (b) port final logic to NT8 NinjaScript C# (native ATM brackets). Both supported by Lucid (Tradovate cloud routing, NT8 via CrossTrade add-on) and FundedNext (automation allowed, no exploit strategies).
- Prop rules to encode (Lucid 50K, verify before buying): max loss $2,000 (EOD trailing on Flex/Pro/Direct, intraday on Daily), daily loss limit $1,200 optional, 4:45 PM ET close-out, no HFT/microscalping, no red-folder news on LucidDaily.

## Strategy definition (from Jey + the 3 price-action transcripts)
Bias and context
- EMA 20 = dynamic support/resistance and bias filter.
- Market structure: swing highs/lows, legs, push phase vs correction phase.
- "Trend played out": once a trend breaks its channel and pushes to a new extreme, PAUSE entries in that direction until new structure forms.
- Chop filter: EMA inside the bars / no HH-HL or LH-LL sequence = no trades.
- Key levels: session high/low (Asia, London, NY), prior day high/low, range extremes, measured move.
Setups (with-trend first)
- Second entry (H2 long / L2 short) at the EMA after a two-legged pullback.
- Higher low above EMA / lower high below EMA after a break.
- Breakout pullback (old resistance becomes support, and vice versa).
- Double trap; failed second entry (reversal) only in weak/medium trends.
- Failed breakout at key level / measured move (reversal), only after the trend played out.
Entry filters
- Strong signal bar (close near extreme, decent body); NO inside-bar signal bars.
- Entry = stop order 1 tick beyond signal bar (trigger) or limit inside it.
- Room to target: skip if nearest key level is closer than 1R.
Trade management
- Stop: 1 tick beyond signal bar or swing, capped by max $ risk.
- TP1 = 1R scalp on contract 1; then stop -> breakeven.
- Runner (contract 2): to next key level / measured move, or trailing swing.
- Volatility mode: high volatility = TP1 + runner; low volatility = both contracts at 1R.

## Milestones
| Version | Goal | Exit criteria |
|---|---|---|
| V4.x (done) | Moomoo plumbing: re-entry, per-trade state, structural stop | V4.1: 5 trades, re-entry works, 0 orphan stops |
| **V5.0** | Port to Pine strategy: current V4 signals + VWAP + risk clamp + native stop/TP1/BE/runner brackets. Symbol-agnostic inputs (point value, ticks, contracts, timeframe). | Compiles, trades MNQ 5m, every trade has stop at entry (no 5-min gap) |
| V5.1-5.2 | Baseline report MNQ + MES, 3 to 6 months | Metrics table produced, bugs fixed |
| **V6.0** | Price-action brain: EMA bias, swing/leg structure, H2/L2, LH/HL, breakout pullback, signal-bar + inside-bar filter, trend-played-out pause, chop filter, key levels + room-to-target. Long and short. | More quality trades, PF > 1.2 on in-sample |
| V6.1-6.3 | Tune setups one at a time (keep/revert by metrics) | |
| **V7.0** | Trade management: 1R TP1 + BE + runner to key level / trail; volatility mode switch | Avg win > avg loss, runner adds net $ |
| **V8.0** | Prop risk layer: daily loss stop, trailing max-loss guard, max trades/day, cooldown, flat 16:40 ET, news-off toggle, size by $ risk | Never breaches $2,000 / $1,200 in backtest |
| **V9.0** | Robustness: 12+ months, MNQ + MES, 3m/5m/10m, parameter stability, out-of-sample, Monte Carlo DD | Go/no-go: PF >= 1.3 OOS, max DD < $1,500 on 50K sizing, >= 100 trades |
| **V10.0** | Forward test automated on SIM (webhook bridge or NT8 port), 2 to 4 weeks | Sim matches backtest behavior, no execution errors |
| V11.0 | Live prop evaluation (one 50K account), then scale accounts | |

Rule: up to ~3 minor versions between milestones. Each version = one hypothesis, one change set, same backtest window, metrics table, keep or revert. Results logged in MNQSCALP_ITERATION_LOG.md.

## Standard backtest report (every version)
Trades, net $, profit factor, win rate, avg win/loss, max DD $, worst day $, trades/day, long vs short, by session (Asia/London/NY), rule breaches vs prop limits.
