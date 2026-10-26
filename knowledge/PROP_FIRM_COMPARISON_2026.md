# Prop firm comparison for the MNQ day engine, 50K accounts (Oct 25 2026)

Question: which futures prop firm gives the cheapest path to a funded 50K account and the biggest expected payouts, when its real rules are applied to our actual 2026 trade stream?

**Answer: Tradeify Select Flex, then My Funded Futures Rapid EOD, then Lucid Flex (the account we use now).** All three use end-of-day (EOD) trailing drawdown, allow automation and have 0% modeled fails. They pay out $2,100 to $2,600 per funded account over 120 funded days, for $250 to $280 of expected fees. Firms that ban automation (Blue Guardian, Top One, Apex funded accounts, E8, Take Profit Trader) score as well or better on paper, but our system cannot legally run there unattended.

## 1. How it was tested

- **Trades:** NEW rule set (`rulesets.NEW`: NEWS, V4+, D2 0.6 ADR out 13:15, TDP, Pinball, H2, flat 15:00), 2026-01-02 to 2026-10-23 (210 days). 2025 is the check year.
- **Sizing:** live engine (copy of `common.size2`): 65% of the room above the max-loss line, $1,100 shared daily budget, stop-day rule N=3 plus (d) "passed" (target and consistency both met). With a daily loss limit (DLL), the budget becomes min($1,100, DLL - $150), e.g. $850 under a $1,000 DLL. The micro cap is set per plan (and per funded scaling tier). Costs: $2.37 per side, 1 tick slippage, +8 pt on stop exits.
- **Intraday path:** each day's sized trades are replayed on 1m bars, so the sim knows how far equity dipped and peaked during the day. This drives four checks: EOD and static floors are checked against intraday equity (a real-time breach), intraday-trailing floors follow intraday equity highs including open profit, hard DLLs fail the account, and soft DLLs flatten the day at -DLL. Pre-RTH NEWS trades have no 1m bars here: a loser's dip is its loss, and a winner's dip is assumed to be -0.5R (-25 pts).
- **Eval:** 2,000 Monte Carlo runs per plan, each 120 trading days built from randomly drawn 2026 days (or the firm's time limit: Apex and Top One Elite Access 30 calendar days, about 21 trading days; Traders Launch 60 days). Check runs: 2025 Monte Carlo, plus a rolling 2026 start on every trading day (in the JSON).
- **"Not passed"** counts fails, stalled runs and runs still open at the horizon. A run stalls when, at a close, less than $400 of room is left above the max-loss line. The engine then takes no new entries (stop-day rule b), so the attempt is dead and is priced as a new purchase. Real fails are 0% to 2% for EOD plans, so almost every "not passed" is a stall.
- **Cost per funded account** = average fees per attempt / pass probability + activation fee. Fees per attempt are the price plus, on monthly plans, a rebill every 21 trading days while the attempt is open.
- **Funded phase:** 1,000 runs of 120 bootstrapped funded days per plan, using that firm's funded drawdown, DLL, scaling, qualifying days, buffer, caps, consistency and split. Payout policy B: request as soon as allowed, but leave at least $1,100 of room above the floor that applies after the request. Policy A (empty the account at every request) busted 60% of E8 Zero accounts and 6% of TradeDay QuickPay accounts, so it was dropped.
- **Net EV** = trader dollars in the first 120 funded days minus the cost per funded account. "$ per $1 fee" = trader dollars / cost per funded account.
- **Calibration:** with Lucid Flex rules and a 40-day horizon, this sim gives a 38.4% pass rate and 0% fails. BACKTEST_2026_YTD.md shows 38% and 0.0% for the same setup, so the new sim reproduces the old one.

## 2. Ranked table (EOD and static plans, firms that allow our automation)

Pass, median days and cost cover the eval. "Funded: got payout / 1st" is the share of funded accounts paid at least once in 120 days, and the median trading day of the first payout. Prices are the propfirmmatch prices with code MATCH.

| # | Plan | Fee (MATCH price) | DD (eval/funded) | Auto OK | Pass 2026 | Med days | Not passed | Cost per funded | Funded: got payout / 1st | Trader $ 120d | Net EV 2026 | $ per $1 fee | Net EV 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FundedNext Futures Legacy | $180 | EOD $2000 | yes | 48% | 23 | 52% | $376 | 58% / 20d | $2,990 | **$2,614** | 8.0 | $1,617 |
| 2 | Tradeify Select Flex | $116 | EOD $2000 | yes | 47% | 23 | 53% | $246 | 59% / 19d | $2,837 | **$2,591** | 11.6 | $1,861 |
| 3 | Tradeify Select Daily | $116 | EOD $2000 | yes | 47% | 23 | 53% | $246 | 58% / 19d | $2,755 | **$2,509** | 11.2 | $1,670 |
| 4 | My Funded Futures Pro | $132 | EOD $2000 | yes | 49% | 19 | 51% | $269 | 49% / 19d | $2,749 | **$2,480** | 10.2 | $1,830 |
| 5 | My Funded Futures Rapid EOD | $112 | EOD $2000 | yes | 42% | 37 | 58% | $266 | 53% / 15d | $2,593 | **$2,327** | 9.7 | $1,945 |
| 6 | Lucid Trading LucidFlex | $130 | EOD $2000 | yes | 47% | 23 | 53% | $277 | 55% / 19d | $2,358 | **$2,081** | 8.5 | $1,633 |
| 7 | FundedNext Futures Flex | $75 | EOD $1500 | yes | 41% | 20 | 59% | $185 | 45% / 20d | $1,808 | **$1,623** | 9.8 | $1,275 |
| 8 | Lucid Trading LucidPro | $150 | EOD $2000 | yes | 51% | 17 | 49% | $296 | 48% / 27d | $1,901 | **$1,605** | 6.4 | $1,346 |
| 9 | My Funded Futures Builder | $76 | EOD $2000 | yes | 53% | 22 | 47% | $144 | 59% / 20d | $1,651 | **$1,508** | 11.5 | $1,113 |
| 10 | Tradeify Growth | $102 | EOD $2000 | yes | 51% | 17 | 49% | $199 | 46% / 33d | $1,299 | **$1,100** | 6.5 | $1,013 |
| 11 | FundedNext Futures Rapid Pro | $160 | EOD $2000 | yes | 52% | 17 | 48% | $310 | 49% / 26d | $1,358 | **$1,048** | 4.4 | $953 |
| 12 | Traders Launch Static 80% | $239 | static $1000 | yes (3P) | 37% | 18 | 63% | $640 | 71% / 4d | $1,291 | **$651** | 2.0 | $430 |

### Firms where our automation is banned or unclear (same model, shown for reference)

| # | Plan | Fee (MATCH price) | DD (eval/funded) | Auto OK | Pass 2026 | Med days | Not passed | Cost per funded | Funded: got payout / 1st | Trader $ 120d | Net EV 2026 | $ per $1 fee | Net EV 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Blue Guardian Futures Express | $98 | EOD $2000 | no (full auto) | 50% | 29 | 50% | $193 | 56% / 21d | $2,773 | **$2,580** | 14.4 | $1,690 |
| B | Top One Futures Elite Daily | $109 | EOD $2000 | no | 50% | 29 | 50% | $216 | 58% / 19d | $2,671 | **$2,455** | 12.4 | $1,681 |
| C | Topstep No Activation Fee (monthly) | $95/mo | EOD $2000 | unclear | 51% | 18 | 49% | $282 | 58% / 19d | $2,658 | **$2,376** | 9.4 | $1,689 |
| D | Topstep Standard (monthly) | $49/mo + $149 act | EOD $2000 | unclear | 51% | 18 | 49% | $294 | 58% / 19d | $2,658 | **$2,364** | 9.0 | $1,702 |
| E | Blue Guardian Futures Reserve | $84 | EOD $2000 | no (full auto) | 47% | 23 | 53% | $179 | 57% / 19d | $2,524 | **$2,345** | 14.1 | $1,786 |
| F | Blue Guardian Futures Standard | $157 | EOD $2000 | no (full auto) | 53% | 22 | 47% | $294 | 52% / 31d | $2,148 | **$1,854** | 7.3 | $1,224 |
| G | Earn2Trade Gauntlet Mini (monthly) | $85/mo + $139 act | EOD/INTRA $2000 | unclear | 44% | 40 | 57% | $566 | 52% / 21d | $2,324 | **$1,758** | 4.1 | $659 |
| H | Apex Trader Funding Standard EOD | $59 + $129 act | EOD $2000 | no (PA) | 26% | 14 | 74% | $352 | 53% / 27d | $1,874 | **$1,522** | 5.3 | $966 |
| I | Take Profit Trader Test 50K (PRO intraday) | $102/mo + $130 act | EOD/INTRA $2000 | no | 50% | 20 | 50% | $445 | 51% / 12d | $1,916 | **$1,471** | 4.3 | $1,021 |
| J | Apex Trader Funding No Activation EOD | $119 | EOD $2000 | no (PA) | 26% | 14 | 74% | $451 | 53% / 27d | $1,874 | **$1,423** | 4.2 | $722 |
| K | Top One Futures Elite Access | $39 + $189 act | EOD $2000 | no | 33% | 13 | 67% | $308 | 48% / 27d | $1,670 | **$1,362** | 5.4 | $1,203 |
| L | TradeDay FastPass EOD (monthly) | $94/mo | EOD $2000 | own only | 49% | 21 | 51% | $308 | 50% / 23d | $1,648 | **$1,340** | 5.3 | $1,129 |
| M | TradeDay QuickPay EOD (monthly) | $79/mo | EOD $2000 | own only | 43% | 37 | 57% | $388 | 83% / 4d | $1,227 | **$839** | 3.2 | $839 |
| N | E8 Futures Signature | $128 | EOD $2000 | no | 52% | 17 | 48% | $247 | 50% / 37d | $909 | **$662** | 3.7 | $575 |
| O | E8 Futures Zero Starter | $142 | EOD $1500 | no | 31% | 20 | 69% | $461 | 59% / 8d | $809 | **$348** | 1.8 | $289 |

Monte Carlo noise is about +-$100 on trader dollars and +-2 points on pass rates. Plans less than about $150 of net EV apart are a tie.

## 3. Recommendation: top 3

1. **Tradeify Select Flex 50K ($115.50 one-time, no activation fee).** It has the same eval mechanics as Lucid Flex (EOD $2,000 trailing that locks at $50,100, 40% consistency, 3-day minimum), so it passes just as often (47%, median 23 days, 0% fails). It is about $30 cheaper, and its funded cap is $2,500 per request instead of $2,000. Ranked 1st or 2nd in both 2026 ($2,591) and 2025 ($1,861). It has no funded DLL and no funded consistency rule, and bots are allowed if we are the sole owner. Watch-outs: do not run the same bot at another firm (Tradeify policy forbids it), and the platform is chosen at purchase. Funded scaling starts at 2 minis (20 micros), which D2 rarely needs anyway. Select Daily scored the same ($2,509): its many small daily payouts ($1,250 cap) suit fast cash, while Flex suits bigger requests.
2. **My Funded Futures Rapid EOD 50K ($112.50 one-time).** Best plan in the 2025 check ($1,945 net EV). Funded is still EOD (locks at +$100), payouts are daily once the $2,100 buffer is built, there is no payout cap, and the split is 90%. The eval is slower (median 37 days, 42% pass) because of the 30% consistency rule, a 4-day minimum and a 3-mini (30 micro) cap. Our NEWS entries start at 8:45 at the earliest, so the funded ban on Tier 1 news (no trades from 2 min before to 2 min after) does not touch the module. Check that no V4+/TDP position is open at a 14:00 FOMC release. **Do not buy plain MFF "Rapid": its funded drawdown is intraday trailing.** MFF Pro ($132.50) is the alternative: faster eval (19 days), $2,480 net EV, but an 80% split and payouts only every 14 days.
3. **Lucid Flex 50K ($130.20, the incumbent).** Every rule is verified on the official help center (LUCID_FLEX_RULES_2026.md). Net EV is $2,081 (2026) and $1,633 (2025). It costs a little more than Tradeify and its funded cap is $2,000. Keeping it lets us run up to 3 firms at once without breaking any firm's account limits.

**Why FundedNext Legacy is not in the top 3** (it has the highest 2026 net EV, $2,614): its lead comes from a $6,000 payout cap and a $200 benchmark-day minimum, both taken from a June 2026 third-party page, and it drops to 6th in 2025. It also pays an 80% split, costs $180 and allows 30 micros in the eval. Verify those rules on the official site before adding it as a 4th firm.

**Biggest fit factor: drawdown type.** D2's stop is the day's open (about 270 pts), so under an intraday trailing drawdown, open profit that is given back raises the floor for the rest of the day. The appendix shows that intraday plans did not blow up in the model, because the 65% sizing keeps the cushion wide. They do pay out less and fail more (2-3% fails, 2-3% funded busts, vs 0% for EOD), and the modeling is less precise. Prefer EOD.

## 4. Per-firm notes (fit with our system)

| Firm | Fit notes |
|---|---|
| Lucid | Flex: EOD, 40% eval consistency (50% paid add-on), no funded consistency, scaling 20/30/40 micros by profit, 5 days of $150, 50% of profit up to $2,000, 5 payouts then live. Pro: no eval consistency (passes faster, median 17 days), but the funded 40% consistency and $52,100 buffer make the first payout late (day 27). Automation allowed; TradingView through Tradovate plus a webhook bridge. Flat 16:45. |
| Tradeify | Select Flex and Select Daily, see top 3. Growth: no eval consistency (median 17 days), but a $1,250 soft DLL, 35% funded consistency and a $53,000 minimum balance delay payouts (first at day 33, $1,100 net EV). Prices verified on the official pricing page. |
| My Funded Futures | Rapid EOD and Pro, see top 3. Builder ($76.50) is the cheapest way to get funded ($144), but its $1,000 soft DLL cuts our budget to $850 and it pays 80% with a $2,000 cap. Plain Rapid: intraday funded drawdown (appendix). One-time billing since 2026-08-25, no activation fees. |
| FundedNext | Legacy: see above. Flex ($75): only $1,500 max loss and 30 micros, so it passes less (41%), but it is cheap ($185 per funded) with a 95% split (propfirmmatch; Tanto says 80/90). Rapid Pro: no eval consistency, but a $1,500 cap per cycle and 40% funded consistency limit payouts. Bots allowed. |
| Top One | Elite Daily scores well ($2,455) but has a HARD $1,000 DLL (budget $850) and bans bots and scripts. propfirmmatch shows $109 one-time, proptradingvibes $218 monthly: billing is unresolved. Elite Access: $39 + $189 activation, 30-day window, so only 33% pass. |
| Apex | One-time fee since March 2026, but only 30 days to pass, so 26% pass (16% in 2025). The EOD eval has a $1,000 soft DLL. Funded accounts (PA): manual order entry only, so not usable for automation. 100% split, 6 payouts. |
| Topstep | $49/mo + $149, or $95/mo with no activation fee. Best day must be <= 55% (a big day raises the target; the eval does not fail). The funded floor resets to the start balance after the 1st payout. Model fit is good ($2,376), but TopstepX cannot route TradingView orders and webhook relays look prohibited, so the engine cannot run there as built. |
| Traders Launch | No trailing 50K. The Static 50K has only a $1,000 static max loss and 2 minis, which the engine's room rule hates (37% pass, $640 per funded account). Its 100K/200K EOD plans lock at the start balance but have $1,000 drawdowns. Poor fit. |
| E8 | Manual only. Signature's 35% funded consistency plus the $2,000 permanent buffer push the first payout to day 37. Zero: the $1,500 trail never locks in the challenge, so 31% pass. Poor fit. |
| TradeDay | Monthly. QuickPay pays a 50/50 split until a threshold (modeled as a 65% blend) and has 30% consistency with 5 days. FastPass 45%. Third-party automation tools (TradersPost) prohibited. Middling. |
| Take Profit Trader | The test is EOD, but PRO funded is INTRADAY trailing, bots are banned, and news is banned +-1 min around FOMC/NFP/CPI. $445 per funded account. Poor fit. |
| Blue Guardian | Express and Reserve are among the best by the numbers ($2,580 and $2,345, top "$ per $1 fee"), but fully automated trading is prohibited (semi-automated with active management only), with a 2-3% payout fee. Usable only if the trader clicks the orders. |
| Earn2Trade | Monthly + $139 activation, $1,200 DLL (modeled hard), 30% consistency, 10-day minimum: median 40 days and $566 per funded account. LiveSim trails in real time. Poor fit. |

## 5. Free practice

- **No firm in the list has a confirmed no-cost futures trial today.** One source says Topstep and TradeDay have run genuine free trials in the past (same rules and platform), but neither is confirmed current. Topstep's 150K practice account requires an active paid Combine.
- **Tradovate free demo:** 14 days, no card, $50K sim with real-time data. TradingView alerts can be routed to it through a webhook bridge (PickMyTrade says this works on demo; it is the vendor's own claim). This is the closest free match to the prop route (TradingView, bridge, Tradovate), since Lucid, Tradeify, MFF and FundedNext all run on Tradovate. Use it to test the end-to-end automation, not the firm rules. A new trial needs a new email.
- **TradingView Paper Trading:** free and runs the Pine strategy directly, but it does not test the bridge or Tradovate fills.
- **Cheapest "real rules" practice:** MFF Builder at $76.50 or FundedNext Flex at $75.25 runs a real firm rulebook on the real platform.

## 6. Where rules could not be modeled exactly

- **Intraday trailing:** approximated from 1m bar highs and lows, with the order inside a bar unknown (the peak is updated after checking the bar's low). Pre-RTH NEWS dips are assumed. Treat appendix numbers as optimistic by a few points.
- **Soft DLL:** the day is flattened at exactly -DLL at the first 1m touch, with no extra slippage.
- **Funded scaling tiers:** Lucid's are official. Tradeify, Blue Guardian and Apex tiers are assumed at 20/30/40 micros. Topstep is assumed at 20/30/50.
- **Unpublished funded payout rules** (assumed, listed in the JSON `model_note`): Top One buffer and cap, Earn2Trade payouts (monthly, 50% of profit), TradeDay FastPass caps and QuickPay blended split, FundedNext Legacy benchmark-day minimum, Traders Launch funded drawdown (sources conflict).
- **Monthly rebills** are priced at the discounted price. Many codes apply only to the first month, which makes Topstep, TradeDay and Earn2Trade costs too low, if anything.
- **Not included:** reset discounts (often cheaper than a new account), data and bridge fees (TradingView CME data plus a webhook bridge, roughly $30-60/mo), Lucid's 5-payout move to live, inactivity rules, payout processing fees (except Blue Guardian, modeled at 88%).
- **2026 dependence:** funded and eval runs use 2026 days only (and 2025 for the check), so a July-August-style chop regime would lower every row about equally. The ranking is more reliable than the dollar levels.

## 7. Sources and verification (checked 2026-10-25)

- Prices: `data/propfirmmatch_50k_1step_2026-10-25.csv` (propfirmmatch.com challenges, 50K, 1-step, code MATCH, captured 2026-10-25). propfirmmatch pages could not be fetched from here (403 / client error).
- Official: Tradeify pricing reference (help.tradeify.co/en/articles/14369021) confirms $145 / $165 / $205 / $492 one-time, no activation fee. Lucid help center (from LUCID_FLEX_RULES_2026.md). Other official sites were blocked by the fetch tool, so rules come from third parties and are flagged:
  - proptradingvibes.com: Lucid 50K (2026-10-11), Lucid payouts (2026-10-19), MFF account types and Rapid EOD (2026-09-10), MFF pricing, Topstep Combine (2026-10-09), Top One (2026-10-14), Take Profit Trader (2026-10-14), TradeDay (2026-09-08)
  - tradetanto.com: Tradeify (2026-09-30), FundedNext (2026-06-16), Apex (2026-04-22), E8 (2026-08-22), Blue Guardian (2026-10-11)
  - fundedtrading.com: FundedNext (2026-08-28)
  - fundedsim.com: 50K compare (2026-10-25)
  - quantvps.com: futures firm list (2026-10-23)
  - propfirmmap.com: Apex (2026-04-18), Earn2Trade (2026-08-29)
  - tradecopia.com: Traders Launch
  - propfirmapp.com: E8 Signature
  - thegodfunded.com: Blue Guardian
  - thedesk.onrender.com: Earn2Trade (2026-05-01)
  - blog.pickmytrade.trade: automation policies (2026-09-28)
- Main open questions: Top One billing, Lucid Pro caps, FundedNext split and Legacy cap, Apex funded consistency (30% vs 50% across sources), Traders Launch funded drawdown type.

## Appendix A: intraday-trailing plans (modeled, not ranked)

| # | Plan | Fee (MATCH price) | DD (eval/funded) | Auto OK | Pass 2026 | Med days | Not passed | Cost per funded | Funded: got payout / 1st | Trader $ 120d | Net EV 2026 | $ per $1 fee | Net EV 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | Apex Trader Funding Standard Intraday | $25 + $99 act | INTRA $2000 | no (PA) | 30% | 13 | 70% | $183 | 42% / 22d | $1,874 | **$1,691** | 10.2 | $1,204 |
| b | My Funded Futures Rapid (funded intraday) | $104 | EOD/INTRA $2000 | yes | 49% | 19 | 51% | $212 | 44% / 14d | $2,148 | **$1,936** | 10.1 | $1,482 |
| c | TradeDay QuickPay Intraday (monthly) | $59/mo | INTRA $2000 | own only | 37% | 36 | 63% | $734 | 77% / 3d | $1,133 | **$398** | 1.5 | $189 |
| d | Lucid Trading LucidDaily Intraday DLL | $100 | INTRA $2000 | yes | 42% | 19 | 58% | $241 | 43% / 16d | $2,130 | **$1,889** | 8.8 | $1,300 |

## Appendix B: propfirmmatch 50K one-step screen (all 77 rows, eval only)

Generic rules from the CSV columns only: no DLL, EOD lock at +$100, no minimum days, no time limits. Use this to spot candidates, not to rank them. Ylos Standard is cheapest ($89 per funded account), but propfirmmatch lists no news trading, no EAs and the BlackArrow Pro platform only, so it does not fit. The Topstep Static Combine and FTMO Futures Pro pass more often (64-66%) thanks to a static or wider max loss. They are worth a closer look if their automation rules allow us.

| Firm | Plan | DD | Billing | Price + act | Max micros | Eval cons | Pass 2026 | Med days | Cost per funded |
|---|---|---|---|---|---|---|---|---|---|
| Ylos Trading | Standard | eod | one time | $18.00 + $59 | 100 | none | 60% | 17 | $89 |
| Apex Trader Funding | No Activation Intraday | intraday | one time | $49.00 + $0 | 60 | none | 42% | 16 | $115 |
| DayTraders | Static | static | one time | $50.00 + $5 | 60 | 50% | 43% | 25 | $121 |
| Ylos Trading | No Activation | eod | one time | $74.25 + $0 | 100 | none | 60% | 17 | $124 |
| Goat Funded Futures | EOD | eod | one time | $69.00 + $0 | 50 | 50% | 49% | 19 | $141 |
| DayTraders | Trail | intraday | one time | $70.00 + $5 | 100 | 50% | 51% | 19.0 | $142 |
| My Funded Futures | Builder | eod | one time | $76.50 + $0 | 40 | none | 50% | 17.0 | $153 |
| AquaFunded Futures | Daily | eod | one time | $73.45 + $0 | 40 | 40% | 47% | 22 | $155 |
| Apex Trader Funding | Standard Intraday | intraday | one time | $24.90 + $99 | 60 | none | 42% | 16 | $158 |
| The Trading Pit Futures | Prime | eod | one time | $79.20 + $0 | 50 | 40% | 47% | 22 | $167 |
| AquaFunded Futures | Flex DLL | eod | one time | $85.15 + $0 | 40 | 50% | 49% | 19 | $174 |
| Blue Guardian Futures | Reserve | eod | one time | $84.00 + $0 | 40 | 40% | 47% | 22 | $178 |
| FundedNext Futures | Flex | eod | one time | $75.25 + $0 | 30 | 40% | 40% | 20.0 | $190 |
| The5ers Futures | Day Trade | eod | one time | $90.00 + $0 | 40 | 40% | 47% | 22 | $190 |
| FuturesElite | Nitro | eod | one time | $98.80 + $0 | 50 | 50% | 49% | 19 | $202 |
| Tradeify | Growth | eod | one time | $101.50 + $0 | 40 | none | 50% | 17.0 | $203 |
| FuturesElite | Elite with DLL | eod | one time | $97.30 + $0 | 40 | 40% | 47% | 22 | $206 |
| Blue Guardian Futures | Express | eod | one time | $97.50 + $0 | 40 | 40% | 47% | 22 | $206 |
| AquaFunded Futures | Flex No DLL | eod | one time | $101.40 + $0 | 40 | 50% | 49% | 19 | $207 |
| AquaFunded Futures | Standard | eod | one time | $104.00 + $0 | 40 | none | 50% | 17.0 | $208 |
| My Funded Futures | Rapid | eod | one time | $104.50 + $0 | 50 | 50% | 49% | 19 | $214 |
| Finotive Futures | One step | eod | one time | $107.40 + $0 | 40 | none | 50% | 17.0 | $215 |
| Goat Funded Futures | 1-Day Pass | eod | one time | $109.00 + $0 | 30 | none | 50% | 17.0 | $218 |
| Top One Futures | Elite Daily | eod | one time | $109.00 + $0 | 30 | 40% | 47% | 22 | $230 |
| Topstep | Static Drawdown Combine | static | one time | $149.00 + $0 | 40 | 55% | 64% | 26.0 | $232 |
| FuturesElite | Prime | eod | one time | $116.35 + $0 | 40 | none | 50% | 17.0 | $233 |
| FuturesElite | Elite without DLL | eod | one time | $112.00 + $0 | 40 | 40% | 47% | 22 | $237 |
| Apex Trader Funding | No Activation EOD | eod | one time | $119.00 + $0 | 60 | none | 50% | 17.0 | $238 |
| Lucid Trading | LucidDaily Intraday DLL | intraday | one time | $100.10 + $0 | 40 | 50% | 42% | 18 | $241 |
| Tradeify | Select Daily | eod | one time | $115.50 + $0 | 40 | 40% | 47% | 22 | $244 |
| Tradeify | Select Flex | eod | one time | $115.50 + $0 | 40 | 40% | 47% | 22 | $244 |
| Apex Trader Funding | Standard EOD | eod | one time | $59.00 + $129 | 60 | none | 50% | 17.0 | $247 |
| Funded Futures Family | Velocity | intraday | monthly | $26.50 + $0 | 50 | 40% | 45% | 28.0 | $248 |
| Trade The Pool | Edge | eod | one time | $124.80 + $0 | 40 | none | 50% | 17.0 | $250 |
| Goat Funded Futures | Goat Daily | eod | one time | $119.00 + $0 | 40 | 40% | 47% | 22 | $252 |
| E8 Futures | Signature | eod | one time | $127.50 + $0 | 40 | none | 50% | 17.0 | $255 |
| DayTraders | EOD (listed intraday) | intraday | one time | $105.00 + $5 | 100 | 50% | 42% | 18 | $258 |
| Apex Trader Funding | Legacy (Tradovate/Rithmic/WealthCharts) | intraday | monthly | $19.70 + $125 | 100 | none | 52% | 17.0 | $262 |
| My Funded Futures | Rapid EOD | eod | one time | $112.50 + $0 | 30 | 30% | 43% | 36 | $264 |
| Lucid Trading | LucidDaily EOD DLL | eod | one time | $130.20 + $0 | 40 | 50% | 49% | 19 | $266 |
| Lucid Trading | LucidFlex | eod | one time | $130.20 + $0 | 40 | 50% | 49% | 19 | $266 |
| Top One Futures | Elite Access | eod | one time | $39.00 + $189 | 30 | none | 50% | 17.0 | $267 |
| FTMO Futures | Pro | eod | monthly | $97.30 + $0 | 40 | 50% | 66% | 21.0 | $271 |
| My Funded Futures | Pro | eod | one time | $132.50 + $0 | 30 | 50% | 49% | 19 | $271 |
| Ylos Trading | Freedom | eod | one time | $129.00 + $0 | 50 | 40% | 47% | 22 | $273 |
| Blueberry Futures | Ascent | eod | monthly | $98.00 + $0 | 20 | none | 50% | 17.0 | $280 |
| Topstep | No Activation Fee | eod | monthly | $95.00 + $0 | 50 | 55% | 50% | 18 | $282 |
| FTMO Futures | Growth | eod | monthly | $83.30 + $0 | 40 | 40% | 47% | 22 | $284 |
| Funded Futures Family | Premier Plus FastPass EOD | eod | monthly | $87.30 + $0 | 40 | none | 40% | 17.0 | $293 |
| Topstep | Standard | eod | monthly | $49.00 + $149 | 50 | 55% | 50% | 18 | $294 |
| TradeDay | FastPass EOD | eod | monthly | $94.50 + $0 | 50 | 45% | 48% | 21.0 | $301 |
| Lucid Trading | LucidPro | eod | one time | $150.50 + $0 | 40 | none | 50% | 17.0 | $301 |
| Blue Guardian Futures | Standard | eod | one time | $156.75 + $0 | 40 | none | 50% | 17.0 | $314 |
| FundedNext Futures | Rapid Pro | eod | one time | $159.99 + $0 | 40 | none | 50% | 17.0 | $320 |
| Goat Funded Futures | Flex | eod | monthly | $109.00 + $0 | 30 | 50% | 49% | 19 | $335 |
| FundedNext Futures | Rapid Daily | eod | one time | $169.99 + $0 | 40 | none | 50% | 17.0 | $340 |
| E8 Futures | Zero Starter | eod | one time | $141.70 + $0 | 40 | 40% | 38% | 21 | $368 |
| TradeDay | QuickPay EOD | eod | monthly | $78.75 + $0 | 50 | 30% | 43% | 36 | $380 |
| FundedNext Futures | Legacy | eod | one time | $179.99 + $0 | 30 | 40% | 47% | 22 | $380 |
| Traders Launch | Static 60% | static | one time | $191.20 + $0 | 20 | 50% | 44% | 20 | $436 |
| The5ers Futures | Swing Summer | eod | one time | $216.00 + $0 | 40 | 40% | 47% | 22 | $457 |
| Funded Futures Family | Prime Standard | eod | monthly | $179.00 + $0 | 40 | none | 50% | 17.0 | $511 |
| Hola Prime Futures | 1 Step Prime | eod | monthly | $159.00 + $0 | 30 | 40% | 47% | 22 | $542 |
| Traders Launch | Static 80% | static | one time | $239.20 + $0 | 20 | 50% | 44% | 20 | $545 |
| Earn2Trade | Gauntlet Mini | eod | monthly | $85.00 + $139 | 60 | 30% | 43% | 36 | $549 |
| E8 Futures | Zero Max | eod | one time | $213.20 + $0 | 40 | 40% | 38% | 21 | $554 |
| DayTraders | S2L | intraday | one time | $179.00 + $0 | 20 | 25% | 32% | 49.0 | $556 |
| Funded Futures Family | Prime Max | eod | monthly | $204.00 + $0 | 50 | none | 50% | 17.0 | $583 |
| Earn2Trade | Trader Career Path | eod | monthly | $95.00 + $139 | 60 | 30% | 43% | 36 | $597 |
| Traders Launch | Static 90% | static | one time | $271.20 + $0 | 20 | 50% | 44% | 20 | $618 |
| Trade The Pool | Day Trade Flex | static | monthly | $228.00 + $0 | 40 | 50% | 65% | 22.0 | $630 |
| Funded Futures Family | Premier Plus FastPass Intraday | intraday | monthly | $69.30 + $0 | 40 | none | 42% | 16 | $637 |
| Blueberry Futures | Accelerated | intraday | monthly | $73.60 + $0 | 20 | none | 42% | 16 | $677 |
| TradeDay | QuickPay Intraday | intraday | monthly | $58.95 + $0 | 50 | 30% | 36% | 36.0 | $734 |

Scripts: `scripts/y2026/prop_sim.py` (generic simulator), `prop_plans.py` (researched rules), `prop_run.py` (runs and JSON). Data: `knowledge/src/prop_firms.json`.
