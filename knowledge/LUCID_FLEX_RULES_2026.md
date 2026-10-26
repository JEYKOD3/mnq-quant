# Lucid Trading LucidFlex 50K Rules (checked 2026-10-25)

Scope: LucidFlex 50K evaluation and simulated funded account. Official help center (support.lucidtrading.com) wins over third parties. The lucidtrading.com pricing page could not be fetched from this environment (client error), so price figures come from third parties only and are marked as such. YouTube transcripts were blocked (RequestBlocked), so video notes come from titles, descriptions and chapter lists.

Legend: [OFF] = official help center article. [3P] = third party. [YT] = YouTube metadata.

## 1. Rules table

| Item | Rule (50K) | Source |
|---|---|---|
| Price | Not confirmed officially. Third-party list prices disagree: $136 (Phidias, Aug 2026), $146 (El Trader Financiado, Oct 13), $115 with $1,200 DLL / $165 without DLL (El Trader Financiado discounts page, Oct 25). Discount codes cut 27 to 50%. Price also depends on DLL on/off and 40% vs 50% consistency choice. | [3P] |
| Rebill | One-time fee, no monthly rebilling | [OFF] Eval account, Simulated Account Fees |
| Reset | Bought from dashboard, not automatic or free. Amount not on help center. Third parties: $80 (DLL on) / $115 (DLL off), or $95. | [OFF] fees + [3P] |
| Activation fee | None. Upgrade to funded takes 5 to 30 min after target | [OFF] Eval account |
| Profit target | $3,000 | [OFF] Eval account |
| Max loss type | EOD trailing (end of session closing balance), both eval and funded. Intraday dips do not move the floor; breach if balance reaches MLL. | [OFF] Drawdown |
| Max loss amount | $2,000. Start MLL = $48,000 | [OFF] Drawdown |
| Trail stop / lock | Trail stops when an EOD balance exceeds the Initial Trail Balance $52,100. MLL then locks at $50,100 (start + $100), NOT $50,000. | [OFF] Drawdown |
| Payout effect on MLL | Requesting a payout immediately moves MLL to the locked $50,100, whatever the balance. Requests are final. | [OFF] Drawdown, Payouts |
| Daily loss limit | Optional, chosen at checkout, cannot be changed later. DLL ON = soft breach (locked out until next session, account survives). Amount not stated on help center; third parties say $1,200 on 50K. | [OFF] Customization + [3P] amount |
| DLL vs payout type | Customization article: DLL ON configs get "On Demand Payouts", DLL OFF configs get "regular end-of-day payouts". Not explained elsewhere. | [OFF] Customization |
| Consistency (eval) | CHANGED: default is now 40%, 50% is a paid add-on (article "Updated this week"). Third-party pages dated Sep to Oct 11 still say 50% flat. Formula: largest single day profit / total account profit. | [OFF] Eval account, Consistency, Customization |
| Consistency (funded) | None | [OFF] Funded account |
| Minimum trading days (eval) | No explicit minimum. Consistency math implies at least 3 days at 40% or 2 days at 50% add-on. | [OFF] Eval account, Customization |
| Max contracts (eval) | 4 minis or 40 micros, full size from first trade | [OFF] Eval account, Scaling |
| Funded scaling | Profit $0 to $999: 2 minis / 20 micros. $1,000 to $1,999: 3 / 30. $2,000+: 4 / 40 (help center table shows "not available" for $3,000+ tiers on 50K, so 4/40 is the cap). Updates at end of session, not real time. Circumventing can wipe the day's profit. | [OFF] Scaling plan |
| Trading hours | Market reopens 6:00 PM ET Sunday to Thursday | [OFF] Allowed Trading Times |
| Must be flat | 4:45 PM ET Monday to Friday. Lucid auto-closes open positions at 4:45 PM; holding past it is not a failure. Holidays with early close: flat before that close. | [OFF] Allowed Trading Times |
| Overnight holding | Allowed within the session (6:00 PM to 4:45 PM next day) because the only flat requirement is 4:45 PM. No holding across the 4:45 PM to 6:00 PM break. | [OFF] inferred from Allowed Trading Times |
| Weekend holding | Not possible (flat 4:45 PM Friday, reopen 6:00 PM Sunday) | [OFF] Allowed Trading Times |
| News trading | Allowed on Flex (scheduled and unscheduled). Trader owns slippage and "velocity logic" risk. Red folder ban applies only to LucidDaily. No FOMC/CPI carve-out on Flex. | [OFF] Other Trading Activities |
| Automation / bots | Permitted, must follow all rules, trader responsible for software errors | [OFF] Other Trading Activities |
| Trade copiers | Permitted under the automated strategies section | [OFF] Other Trading Activities |
| Prohibited | HFT (no numeric threshold), microscalping (flag if more than 50% of profits come from trades held 5 seconds or less), hedging across own/other accounts or firms (third party: includes correlated ES vs NQ opposite positions), exploiting sim price errors | [OFF] Rules and Guidelines |
| Max accounts | 5 funded, 10 total (eval + funded) per household | [OFF] Maximum Number of Accounts |
| Platforms | CQG: NinjaTrader, Tradovate, TradingView. Rithmic: Quantower, Tradesea, MotiveWave, Sierra Chart, Jigsaw, Bookmap, ATAS, R Trader Pro, MultiCharts. All work with all account types. | [OFF] Supported Platforms |
| TradingView connection | Via Tradovate broker login in TradingView (Trade panel, choose Tradovate, Tradovate username/password, no Google/Apple SSO). No TradingView route on Rithmic. Tradovate side: Application Settings, Add-ons, TradingView. | [OFF] platforms list + [3P] proptradingvibes |
| TradingView auto-execution | Pine strategies cannot place orders on Tradovate natively; need a webhook bridge (CrossTrade, TradersPost, PickMyTrade or similar). | [3P] CrossTrade |
| Data fees | Not stated on help center. TradingView real-time CME data is billed by TradingView separately from the Tradovate entitlement; unconfirmed whether Lucid sim accounts unlock TV data. | [3P] |
| Commissions | MNQ $0.50 per side ($1.00 round turn). MES same. NQ/ES $1.75 per side. | [OFF] Approved Products and Commissions |
| Payout qualifying days | 5 days with at least $150 profit each per cycle, plus positive net profit for the cycle. Day count resets after each payout. | [OFF] Payouts |
| Payout min / max | Min $500. Max 50% of profit, capped at $2,000, cap does not grow | [OFF] Payouts |
| Split | 90% trader / 10% Lucid | [OFF] Payouts |
| Buffer | No buffer balance required (but MLL moves to $50,100 on request) | [OFF] Payouts, Drawdown |
| Number of payouts | Up to 5 per account, then moved live (risk team may move earlier). Legacy accounts (bought/reset on or before 2026-02-27) moved after the 6th payout. | [OFF] Payouts, LucidFlex Live (Legacy) |
| Processing | Funds deducted in minutes, paid within 2 business days, no fixed window | [OFF] Payouts |
| Inactivity | At least $1 net P/L every 30 calendar days or account deleted | [OFF] Inactivity |

## 2. Our assumptions vs findings

| Assumption | Status |
|---|---|
| $3,000 target | Correct |
| $2,000 EOD trailing | Correct |
| mll = min(peak EOD - 2000, 50000) | WRONG. Use mll = min(peakEOD - 2000, 50100); lock triggers when an EOD close exceeds 52,100. After any payout request, mll = 50100 immediately. |
| 50% consistency in eval | OUTDATED. Default is now 40%; 50% only with paid add-on. Pick the add-on or model 40%. |
| Funded: 5 days >= $150 | Correct, plus positive net cycle profit, min request $500 |
| 50% of profit capped at $2,000 | Correct |
| 90% split | Correct |
| About $69 fee | UNCONFIRMED. No source shows $69. Third-party list $115 to $165 depending on DLL; discounted roughly $80 to $115. Could only be $69 with a deep coupon. |
| TradingView via Tradovate (CQG) | Correct. Automation needs a webhook bridge. |

## 3. Impact on our system

1. Flat time: hard exit at 16:45 ET (use 16:40 ET as our internal flatten to avoid the auto-liquidation fill). On early-close holidays, flatten before the exchange close. EOD balance for the trailing MLL is the 16:45 close.
2. Trailing model: fix the backtest and live guard to `mll = min(max_eod_close - 2000, 50100)` starting at 48,000. In funded, set mll = 50,100 on the first payout request; do not request a payout until balance minus 50,100 leaves room for at least 2 full daily risk budgets.
3. Payout math example: funded balance 51,600 after 5 qualifying days. Max request 50% of 1,600 = 800. Balance falls to 50,800, MLL to 50,100: only $700 of room. Our $1,100 daily budget would exceed this, so post-payout risk must scale down until the cushion rebuilds.
4. Daily risk budget $1,100: fits under the reported $1,200 DLL if we buy DLL ON (soft breach, account survives). With DLL OFF there is no daily stop, only the MLL. Either way, $1,100 is 55% of the $2,000 MLL; two max-loss days in a row from start fails the eval. Consider $500 to $700 per day until EOD balance reaches 52,100.
5. Consistency: at 40%, the largest day must be <= $1,200 if we finish exactly at $3,000. Cap daily profit (stop trading for the day) around $1,000 to $1,100 in the eval, or buy the 50% add-on ($1,500 cap at target). Funded has no consistency rule.
6. News: CPI/PPI/NFP 8:30 and FOMC 14:00 are allowed on Flex. No change needed, but expect slippage and possible velocity-logic pauses; widen slippage assumptions in the backtest. Do NOT use LucidDaily (red folder is a hard breach there).
7. Microscalping: news spikes can close trades in seconds. Ensure that trades held 5 seconds or less never produce more than 50% of profits (add a minimum hold or log hold times).
8. Overnight modules: Sunday 18:00 to 20:00 is allowed (market opens 18:00 ET). Weeknight 18:05 to 03:30 long is allowed because it stays inside one session (flat by 16:45 is the only requirement). Note that P/L from 18:05 onward counts toward the next trading day for DLL, EOD close and qualifying days. Nothing may be held from 16:45 to 18:00 or over the weekend.
9. Contracts: 6 to 10 MNQ fits the eval cap of 40 micros. In funded, cap is 20 MNQ until $1,000 profit, 30 until $2,000, then 40. No change needed for 6 to 10 MNQ. If we ever mix NQ, 1 NQ = 10 MNQ against the cap.
10. Automation: allowed (bots and copiers). Pine strategy plus webhook bridge to Tradovate is fine. HFT is banned without a numeric threshold, so keep order rates low. Copying the same direction across up to 5 funded accounts is fine; never opposite direction (hedging ban).
11. Costs: use $1.00 round turn per MNQ in the backtest (plus slippage). TradingView CME real-time data may be an extra TradingView subscription.
12. Inactivity: at least one trade every 30 days per account.
13. Payout count: plan for at most 5 payouts (max $2,000 each, $9,000 to trader at 90%) before forced move to live.

## 4. Practical tips from videos and reviews

- The Prop Guy, "How to pass Lucid Trading Evaluation", 2026-04-15, https://www.youtube.com/watch?v=k2C3nk1zCSI : passed Flex 50K in 12 days with about $2,351 shown. Tips: start each day at half size ("Daily Bag"), add on pullbacks only as the trade works, tighten stop when adding, prefers 1:1 high win rate over 1:3.
- Prop Firm Review, "Lucid Trading Rules Explained (2026): What Closes Your Account", 2026-10-18, https://www.youtube.com/watch?v=TXr5dVowaj0 : confirms $48,000 start, lock $50,100 above $52,100, payout request moves floor to $50,100 and cannot be withdrawn, 4:45 PM flat, 2 to 4 minis funded scaling, microscalping 5 second rule, 50% consistency (pre-dates the 40% default change). Advice: compute remaining room before requesting a payout.
- ASFX, "How To Pass A LUCID FLEX Account FAST!! (3 Days or LESS)", 2026-04-30, https://www.youtube.com/watch?v=-9zoJMcq_UM : 3-day pass, VAL breakdown short, VWAP levels. Note: a 3-day pass will be harder at the new 40% default.
- Funded or Busted, "I Passed The Lucid Flex 50k Account...I'm Worried", 2026-03-27, https://www.youtube.com/watch?v=hK0uX5E9PpY : staying funded is harder than passing; plan first payout before trading funded.
- Hiro Fights Candles, "I Switched From $50K to a $25K Lucid Trading Account", 2026-08-23, https://www.youtube.com/watch?v=2cWBzcFYe30 : struggled on 50K for weeks, dropped to 25K (lower cost per attempt).
- Scrembo Trading and Tutorials, 2026-01-06 and 2026-02-15, https://www.youtube.com/watch?v=nbWeBEI3CKk and https://www.youtube.com/watch?v=bpjaXUbj9Cc : payout tutorials; title "No Consistency and Target" refers to the funded stage only.
- Cammy Capital, "Lucid Trading MADE SIMPLE", 2026-01-12, https://www.youtube.com/watch?v=vvI-o5vc6xE ; Flow Zone Trader review 2026-01-19, https://www.youtube.com/watch?v=Le69nl0RQfE ; TFX Traders 2026-03-12, https://www.youtube.com/watch?v=4ElJJdoc0O4 : general reviews, no rule details recoverable.
- Reviews: spread profit across days for consistency; intraday give-back does not move the EOD floor but a high close does; plan payouts around the $50,100 lock.

## 5. Common reasons people fail

1. Closing a big up day raises the EOD floor, then a normal losing day hits it (floor rises up to 52,100 close).
2. Requesting a payout with a thin cushion: MLL jumps to $50,100 and the next loss breaches.
3. One oversized winning day breaks consistency, forcing more days and more exposure.
4. Oversizing to "pass fast" with $2,000 of room.
5. DLL soft breach days (DLL ON) stalling progress; holding into 4:45 PM auto-liquidation.
6. Microscalping or HFT flags (profits forfeited after warning).
7. Inactivity deletion after 30 days.

## 6. Inconsistencies and recent changes

- Eval consistency: help center now says 40% default with 50% add-on and the 2/3 day framing; third-party pages through Oct 18 still say 50% only. Official wins: 40% default.
- Payout count: current Payouts article says live after 5 payouts; Legacy article says after the 6th payout for accounts bought or reset on or before 2026-02-27.
- DLL amount: help center gives no dollar figure; third parties say $1,200. Some third parties (PipBack, Tradetanto) still say Flex has no DLL at all (outdated: DLL became optional).
- DLL ON configs are tied to "On Demand Payouts" per Customization article; not described in the Payouts article. Ask support.
- Scaling: proptradingvibes listed $2,000 to $4,499 = 4 minis; help center shows $2,000 to $2,999 = 4 and blank higher tiers. Cap is 4/40 either way.
- Price: three third-party figures ($136, $146, $115/$165). Check the live checkout.
- Times are written "EST" by Lucid; treat as US Eastern local time (EDT in summer). Confirm with support.

## 7. Sources

Official (support.lucidtrading.com):
- LucidFlex collection: https://support.lucidtrading.com/en/collections/16914631-lucidflex
- Evaluation Account: https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account
- Funded Account: https://support.lucidtrading.com/en/articles/12945795-lucidflex-funded-account
- Payouts (2026-07-28): https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts
- Consistency Percentage: https://support.lucidtrading.com/en/articles/12945805-lucidflex-consistency-percentage
- Scaling Plan (2026-05-06): https://support.lucidtrading.com/en/articles/12945808-lucidflex-scaling-plan
- Drawdown (2026-08-26): https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown
- Customization: https://support.lucidtrading.com/en/articles/16226050-lucidflex-customization
- LucidFlex Live (Legacy): https://support.lucidtrading.com/en/articles/13424914-lucidflex-live-legacy
- Allowed Trading Times (2026-08-26): https://support.lucidtrading.com/en/articles/11404729-allowed-trading-times
- Other Trading Activities (news, automation): https://support.lucidtrading.com/en/articles/11404728-other-trading-activities
- Prohibited Microscalping: https://support.lucidtrading.com/en/articles/11404742-prohibited-microscalping
- Prohibited HFT: https://support.lucidtrading.com/en/articles/11404736-prohibited-high-frequency-trading
- Prohibited Hedging: https://support.lucidtrading.com/en/articles/11404734-prohibited-hedging
- Trade with Integrity: https://support.lucidtrading.com/en/articles/11404732-trade-with-integrity
- Inactivity Policy: https://support.lucidtrading.com/en/articles/11404632-inactivity-policy
- Approved Products and Commissions: https://support.lucidtrading.com/en/articles/11508978-approved-products-and-commissions
- Supported Platforms: https://support.lucidtrading.com/en/articles/11404614-lucid-trading-supported-platforms
- Maximum Number of Accounts: https://support.lucidtrading.com/en/articles/11404617-maximum-number-of-accounts
- Simulated Account Fees: https://support.lucidtrading.com/en/articles/11404620-simulated-account-fees
- Pricing page (not fetchable here): https://lucidtrading.com/#plans

Third party:
- https://www.proptradingvibes.com/blog/lucidflex-funded-account-rules (2026-10-11)
- https://www.proptradingvibes.com/blog/lucidflex-consistency (2026-10-11)
- https://proptradingvibes.com/blog/lucid-trading-news-trading-policy (2026-10-09)
- https://proptradingvibes.com/blog/lucid-trading-tradingview (2026-10-10)
- https://proptradingvibes.com/blog/lucid-trading-live-account-transition (2026-10-19)
- https://tradetanto.com/learn/lucid-trading-rules-explained-every-plan-rule-and-limit (2026-09-10)
- https://www.eltraderfinanciado.com/en/news/lucid-trading/lucid-trading-optional-daily-loss-limit (2026-10-13)
- https://www.eltraderfinanciado.com/nl/discounts/lucid-trading (2026-10-25)
- https://phidiaspropfirm.com/education/lucidflex-review (2026-08-06)
- https://pipback.com/blog/lucid-trading-review (2026-09-13)
- https://crosstrade.io/prop-firms/lucid-trading (reviewed 2026-09-23, rechecked 2026-10-25)

YouTube: see section 4 URLs.
