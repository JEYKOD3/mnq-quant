# Fast Pass Research: LucidFlex 50K (researched 2026-10-26)

Goal: pass in 3 to 5 trading days without breaching. Tags: [OFF] = Lucid help center, [3P] = third-party site, [ANEC] = practitioner anecdote (Reddit, forum, YouTube), [CALC] = our arithmetic. Full rule table lives in `LUCID_FLEX_RULES_2026.md`; this file is about how to use those rules.

## 1. What LucidFlex 50K allows (verified)

| Rule | Value | Source |
|---|---|---|
| Target | $3,000 | [OFF] Eval account |
| Max loss (MLL) | $2,000, EOD trailing on highest closing balance. Start $48,000. Locks at $50,100 once an EOD close exceeds $52,100. Breach if balance touches MLL (intraday touches count). | [OFF] Drawdown |
| Consistency (eval) | 40% default: largest day / total profit <= 40%. 50% is a paid add-on. Exceeding it is NOT a fail: you keep trading until the ratio is back under. | [OFF] Consistency |
| Min days | "Pass in as few as 3 days with 40% consistency, or 2 days with the 50% add-on" | [OFF] Eval account |
| Max size | 4 minis or 40 micros | [OFF] Eval account |
| Daily loss limit | Optional at checkout, cannot change later. Soft breach (locked out until next session). Amount not on help center; 3P says $1,200 on 50K. | [OFF] Customization, [3P] |
| News | Allowed on Flex. Trader owns slippage and "velocity logic" pauses. Red folder ban is LucidDaily only. | [OFF] Other trading activities (dated 2026-08-26) |
| Flat | 4:45 PM ET Mon to Fri, auto-closed; reopen 6:00 PM. Early-close holidays: flat before the close. | [OFF] Allowed trading times |
| Funded | No consistency rule. Scaling 2/3/4 minis by profit tier. | [OFF] Customization, [3P] scaling |

Note: third-party sites dated before mid Oct 2026 (proptradingvibes, Reddit) still say 50% flat. The help center says 40% default. Official wins; check your checkout receipt for which version you bought.

URLs:
- https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account
- https://support.lucidtrading.com/en/articles/12945805-lucidflex-consistency-percentage
- https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown
- https://support.lucidtrading.com/en/articles/16226050-lucidflex-customization
- https://support.lucidtrading.com/en/articles/11404729-allowed-trading-times
- https://intercom.help/lucid-trading/en/articles/11404728-other-trading-activities
- https://www.proptradingvibes.com/blog/lucidflex-funded-account-rules [3P]

## 2. Consistency math: why one-day passes are impossible [CALC]

Required total profit = max(3,000, best day / 0.40) = max(3,000, 2.5 x best day).

| Best day | Total needed (40%) | Total needed (50% add-on) |
|---|---|---|
| $1,000 | $3,000 | $3,000 |
| $1,200 | $3,000 | $3,000 |
| $1,500 | $3,750 | $3,000 |
| $2,000 | $5,000 | $4,000 |
| $3,000 | $7,500 | $6,000 |

- Fastest clean path at 40%: three green days with none above $1,200 (e.g. 1,100 / 1,100 / 800). At 50%: two days of $1,500.
- A losing day raises the ratio because it cuts total profit. A $1,200 best day plus one -$400 day means you need $3,400 gross from the other days.
- A huge day 1 is a trap: a $3,000 day forces $7,500 total, i.e. $4,500 more while the EOD trail has already moved up $2,000. You carry more exposure for longer. Reddit thread (Lucid, 50% era) shows exactly this: trader made ~$2,800 day 1 and was confused why the "target" moved to ~$5K [ANEC].
- Practical cap: stop trading for the day at about +$1,000 to +$1,100 net (40% version). Use a platform daily profit lock if available.

## 3. Trailing drawdown traps specific to EOD trail [CALC]

- Intraday unrealized peaks do not raise the floor. Only the 4:45 PM closing balance does. Good: you can hold a winner through a pullback without the floor chasing it.
- Every green close raises the floor by the same amount until the $52,100 lock. Room never grows above $2,000 before the lock; it only shrinks when you give back.
  - Day 1 close +$1,100: balance 51,100, MLL 49,100, room 2,000.
  - Day 2 close -$700: balance 50,400, MLL 49,100, room 1,300. The giveback is permanent.
- Lock: once a close exceeds $52,100 (+$2,100), MLL freezes at $50,100. From then on every extra dollar is real cushion. That is the first milestone; the target ($53,000) is 900 above it.
- Intraday breach is real: the floor is computed at EOD but touching it intraday fails the account. [3P] proptradingvibes: EOD trail "does not protect an account from a loss-limit breach during the session."

## 4. Position sizing approaches

| Approach | How | Pros | Cons |
|---|---|---|---|
| Fixed $ risk per trade | e.g. $200 to $250 (10 to 12.5% of $2,000) per trade | Simple, steady daily expectancy, fits the consistency cap | Each loss is a bigger share of shrinking room after a red day |
| % of remaining room | e.g. 12% of (balance - MLL) | Automatically de-risks after losses; mathematically never hits zero | Slower recovery; size creeps up after green days, which is when NexusFi says blowups happen |
| Hybrid (recommended) [CALC] | Fixed $ risk, but cap at 15% of remaining room and cut to half size when room < $1,200 | Keeps daily target reachable, protects the floor | Needs a running room calc each morning |

Sources and practitioner numbers:
- NinjaTrader Prop blog: risk a quarter or less of the daily limit per trade; set max trades and daily cap before the session; never move the stop. https://prop.ninjatrader.com/blogs/prop-firm-evaluation-mistakes/ [3P]
- NexusFi Academy: personal daily stop at 60 to 70% of the firm's daily limit; after losing 50% of your daily budget pause 30 min, at 75% stop. Do not sprint to target then size up. https://nexusfi.com/a/prop-firms/prop-firm-evaluation-strategy [3P]
- Tradezella: size so you survive 2 to 3 losers out of ~5 trades; daily budget 3 to 5R; never change size based on recent P&L. https://www.tradezella.com/blog/pass-prop-firm-challenge [3P]
- r/Daytrading 50K MNQ thread [ANEC]: risk 1/20 to 1/10 of drawdown per trade ($100 to $200), 1 to 3 MNQ typical, 1 to 2 trades a day and stop after a win, add one micro per $500 of cushion gained, "most blowups come from scaling up after a few good days." https://reddit.sentinel-team.org/posts/1rdnw9t/snapshots/2026-02-27T22%3A12%3A05.0165Z

MNQ sizing table [CALC] (MNQ = $2/pt, MES = $5/pt, ignore commissions ~ $1 per side per micro):

| Risk/trade | 15 pt stop | 25 pt stop | 40 pt stop |
|---|---|---|---|
| $150 | 5 MNQ | 3 MNQ | 1 to 2 MNQ |
| $250 | 8 MNQ | 5 MNQ | 3 MNQ |
| $400 | 13 MNQ | 8 MNQ | 5 MNQ |

## 5. A 3 to 5 day plan for this account [CALC, our interpretation]

- Daily profit goal: $1,000 to $1,100. Hard stop for the day when hit (consistency cap).
- Daily loss cap: $500 to $600 (25 to 30% of MLL). Three max-loss days in a row still leave the account alive.
- Risk per trade: $200 to $275, aim for 2R+ targets. Two winners at 2R = ~$1,000 day.
- Trades per day: max 3 to 4 attempts. Stop after 2 consecutive losers.
- After a red day: next day risk 50 to 75% of normal until the loss is recovered.
- After the $52,100 lock: may return to full size; still cap the day at the consistency limit.
- Expected timeline: 3 days best case, 4 to 6 realistic with one red day.
- Flatten all positions by 4:40 PM ET to avoid the 4:45 auto-liquidation fill.

## 6. Why evals fail

| Cause | Evidence |
|---|---|
| Oversizing per trade | traderpayout.com ranks it #1 impact. https://traderpayout.com/prop-firms/prop-firm-pass-rate [3P] |
| Overtrading / revenge after a loss | NinjaTrader calls it the most common behaviour behind failed evals. [3P] |
| Sprint to target then size up | NexusFi chart: sprint-to-target 31%, news blowups 24%, revenge 22%, flat-market overtrading 14%, final-day desperation 9%. No source given for these numbers; treat as illustrative. [3P] |
| News spikes | Allowed on Flex but slippage and velocity pauses are on you. FOMC, CPI, NFP, GDP/PCE bars can gap through stops. |
| Trailing drawdown misunderstanding | Giving back profit after a green close shrinks room permanently; intraday touch of MLL fails. [3P] proptradingvibes |
| Consistency blow-through | One big day forces 2.5x that day in total profit (section 2). [ANEC] Reddit Lucid thread. |
| Moving stops / no bracket orders | NinjaTrader. [3P] |
| Microscalping | Lucid limits profits from trades held <= ~5 seconds (see LUCID_FLEX_RULES_2026.md). News spike scalps can trip it. |

## 7. Published pass-rate stats

All self-reported, unaudited. Lucid publishes none that we found.

| Firm | Stat | Period |
|---|---|---|
| Topstep | 16.8% of Combines passed (per attempt); 51.8% of people passed at least one; 33.3% of funded traders paid | 2025 |
| Topstep | 12.4% per attempt; 28.3% of funded paid | 2024 |
| Tradeify | 17.2% of evals passed; 28.5% of funded paid | Aug 2025 to Jul 2026 |
| MyFundedFutures | 19.97% pass; 39.2% of funded paid | not stated |
| Earn2Trade | 8.89% pass | 2025 |
| Industry estimate | 5 to 15% per attempt (no audited data) | traderpayout.com |

Sources: https://il.ly/blog/prop-firm-pass-rates (compiles firm disclosures with links), https://tradecovex.com/guides/how-many-combines-passed-express-topstep-2025, https://traderpayout.com/prop-firms/prop-firm-pass-rate

Takeaway: roughly 1 in 6 attempts pass, but about half of persistent people eventually pass. Fees matter more than speed: thortradecopier's illustrative math shows a fast 25% pass attempt and a slower 50% attempt take similar total days once retries are counted. https://thortradecopier.com/blog/how-long-to-pass-prop-firm-evaluation [3P]

## 8. Top lessons

1. Three days is the floor at 40%. Cap each day near $1,100; a bigger day is not a faster pass.
2. Protect room, not P&L. EOD trail means every giveback after a green close is permanent until $52,100 locks.
3. Fixed $ risk with a room-based cap beats both pure fixed and pure percent for a 3 to 5 day sprint.
4. Max 3 to 4 trades, stop after 2 losers or the daily cap. Most failures are behavioural, not strategy.
5. News is allowed on Flex but is not free: flat before FOMC 2:00 PM and the 8:30 AM prints unless the setup is explicitly tested for them.
