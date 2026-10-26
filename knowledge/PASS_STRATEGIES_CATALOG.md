# Pass Strategies Catalog: what people credit for passing futures prop evals (researched 2026-10-26)

Scope: NQ/MNQ and ES/MES evals at Topstep, Apex, Lucid, Tradeify, MFFU. Goal: concrete, testable rules, not advice.

Evidence tags (used on every entry):
- [ANEC] anecdotal: a person says it worked; no data shown.
- [STAT] descriptive statistics only (base rates), no P&L.
- [BT-A] backtested by the author or vendor, in-sample or optimized, not reproducible from the page.
- [BT-I] backtested independently or with out-of-sample split.
- [VERIFIED] none. No pass or payout claim found was independently verified (firm statement, audited statement). Treat every "passed N accounts" claim as a claim.

Facts vs claims: lines starting "Fact:" are things the source states about its own method or data. "Claim:" lines are performance or pass claims made by the source. "Ours:" lines cross-reference results already in `knowledge/RULES.md`.

Access note: reddit.com, old.reddit.com and redlib search pages were blocked by the fetch tool (provenance rule). Reddit content below comes from mirror pages that search returned (r.til.io, reddit.sentinel-team.org). YouTube pages gave titles and descriptions only; no transcripts were retrievable except via a third-party AI summary site.

---

## 1. Strategy catalog

### S1. 15-minute ORB, long-only, 50% range target (TradeThatSwing, NQ)
- Fact: Range = 9:30 to 9:45 ET high/low. Entry = first 5m candle CLOSE above OR high. If a 5m close below OR low happens first, no trade that day. One trade per day.
- Stop: opposite side of OR, capped at $1,000 (50 NQ pts); July 2026 update says $1,500 cap works better.
- Target: 50% of OR height beyond entry.
- Filters: skip if OR > 0.8% of price (original test 0.5%). July 2026 update: skip Mondays and Thursdays.
- Instrument/sizing: 1 NQ on $10K; suggests MNQ for small accounts.
- Claim: 1 year, 114 trades, WR 74.56%, PF 2.512, net $43,310, max DD $2,725, avg win ~$846 vs avg loss ~$987, before commissions and slippage. Long-only, uptrend year.
- Evidence: [BT-A], optimized, no OOS, no costs.
- Source: https://tradethatswing.com/opening-range-breakout-strategy-up-400-this-year
- Ours: not tested in this exact form (high-WR, sub-1R target). E1/V4 is a 2R retest variant.

### S2. 5-minute ORB, both sides, 50% range target (Edgeful, ES)
- Fact: Range = 9:30 to 9:35 ET. Entry = break of range (order type not stated). Stop = opposite edge. Target = 50% of range from breakout level. Skip if range > 0.55% of open. Tuesdays off. Max loss $700 (14 ES pts) per trade.
- Claim: "last 6 months", 115 trades, WR 72.17%, PF 1.623, net $10,825 on 1 ES.
- Evidence: [BT-A], article admits settings are optimized.
- Source: https://www.edgeful.com/blog/posts/5-minute-opening-range-breakout-es-strategy

### S3. First-5m-candle direction ORB, 10R or EOD (Zarattini and Aziz paper)
- Fact: Direction = color of 9:30 to 9:35 candle (doji = no trade). Entry at 9:35 open. Stop = opposite extreme of first candle. Target = 10x risk, else exit at close. Sizing 1% of equity per trade, leverage cap 4x.
- Claim (paper, QQQ 2016 to 2023): 24% hit rate, +0.13R per trade, no spread/slippage, no OOS.
- Independent replication (NQ CFD 2015 to 2026, n=2,934): gross +0.131R, 23.2% hit; net of 2.5 pt cost +0.002R (t=0.0). Conclusion: "net of costs no market is distinguishable from zero."
- Evidence: [BT-I], replicated gross, fails net.
- Sources: https://papers.ssrn.com/abstract=4416622 , https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy , https://www.mql5.com/en/blogs/post/776235
- Ours: X9 (high-R ORB) rejected for eval use: WR 8 to 24%, DD 25 to 200R.

### S4. ORB with daily SMA trend filter, stop after 1 loss (Backtests Not Signals, MNQ)
- Fact: Long only above daily SMA(150 to 300), short only below. Stop = opposite side of OR, capped at 150 ticks (37.5 pts, ~$75). Target = RR multiple optimized 1.4 to 4.2. Forced exit next US open. Stop for session after one loss. 1 MNQ, $0.68/side, no slippage.
- Claim: IS 2020-02 to 2022-12: 451 trades, WR 30.4%, PF 1.43. OOS 2023-01 to 2026-02: 474 trades, WR 24.9%, PF 1.32, max DD 12.8%. OOS lagged buy and hold.
- Evidence: [BT-I] (has OOS split), no slippage. OR length not stated in visible text.
- Source: https://backtestsnotsignals.substack.com/p/opening-range-breakout-real-edge

### S5. Crabel 30-minute ORB with stop orders, Friday filter (Unger Academy, NQ)
- Fact: OR = first 30m bar of cash session. Buy stop at OR high, sell stop at OR low. Reverse on opposite break. $2,000 stop, $5,000 target (1 NQ), exit on close.
- Claim: unfiltered >6,190 trades, average trade "not large enough to cover trading costs". Friday-only: ~$95 avg trade ($84 long, $155 short).
- Evidence: [BT-A], one-variable filter chosen from seasonality (data-mined).
- Source: https://ungeracademy.com/?p=7020

### S6. Other ORB mechanics seen in scripts credited for evals (no results)
- 9:30 Breakout (TradingView): OR = 5/15/30m; entry = 5m BODY close beyond OR; stop = opposite extreme of the breakout candle (not OR edge); target default 6R; one trade/day; optional filters NR7/NR4, daily EMA21 side, body >= 60% of range, BE at 1R. [no results] https://il.tradingview.com/script/XYRRdJpV-9-30-Breakout/
- ORB NQ Dynamic Risk: OR = first three 5m candles (9:30 to 9:45); entry = first 5m close outside; stop = OR midpoint + 5 pts; target 2R; 1% equity risk. [no results] https://www.tradingview.com/script/RMpC1oXB-Opening-Range-Breakout-NQ-Dynamic-Risk
- 20-minute ORB credited for an Apex 50K pass after "many attempts". No rules given. [ANEC] https://community.tickblaze.com/passing-evaluations/post/finally-passed-a-50k-apex-evaluation-YPBVTyb2xQc2CG4
- ASFX "Double Break" (Austin Silver): OR 9:30 to 9:45, VWAP trigger, size by OR width, "take profit where you used to enter". Exact rules only in video. [ANEC] https://www.youtube.com/watch?v=20Aaz-nrZe8

### S7. 10:00 to 11:00 symmetric scalp, 15 pt stop / 15 pt target (Reddit "Passed 20 x 250Ks", Apex)
- Fact (as stated by OP u/Severe-Ad8289, r/Daytrading): NQ and ES only, trades only 10:00 to 11:00 ET. Confluence = FVG + order block + VWAP + 200 EMA. NQ stop 15 pts, target 15 pts. ES 3 pts / 3 pts. Move stop to BE "once green". Scale out 75% at first target, runner on rest.
- Sizing: ~10% (of drawdown, implied) per trade in evals, 2.5% when funded.
- Claim: passed 20 Apex 250K evals; last $8,000 payout took ~38 trading days. Commenters note Apex 30% consistency, no news, no flipping make payouts harder than passes. OP refused to give size or trades/day.
- Evidence: [ANEC].
- Source: https://r.til.io/r/Daytrading/comments/1dewzvp/passed_20_x_250ks
- Ours: X3 says <20 pt MNQ targets are structurally losing at 3 pt cost unless WR is high; needs WR > ~60% at 15/15 net.

### S8. ICT Silver Bullet 10:00 to 11:00
- Rules version A (TTrades, NQ): at 10:00 mark the 9:00 hourly candle high/low. During 10:00 to 11:00, wait for a sweep of one side. Swept high -> short targeting 9:00 low; swept low -> long targeting 9:00 high. Entry needs confirmation (displacement back into range, FVG, OB, breaker). Stop beyond the swing that caused displacement. No sweep in window = no trade. [no results] https://ttrades.com/the-am-silver-bullet-strategy-on-nq/
- Rules version B (GitHub mechanical, NQ): windows 3-4, 10-11, 14-15 ET; sweep = bar takes out prior 2h extreme and closes back inside (scan from 30m before window); first FVG >= 0.5 pt after sweep on displacement candle; limit at near FVG edge, must fill in window; stop 1 tick beyond sweep extreme, skip if risk > 60 pts; target 2R; 2h time exit; same-bar ambiguity = loss.
- Claim B: Jun to Sep 2026, 27 trades, WR 25.9%, avg -0.39R, PF 0.51. Author: not statistically meaningful.
- Evidence: A [ANEC], B [BT-I] tiny sample, negative.
- Source B: https://github.com/cjosh4toyotas-stack/silver-bullet-backtest
- Ours: X15 silver bullet 10-11 FVG 1m/5m PF .79 to 1.10, test <= 1.02, rejected. Version A (9:00 hour range sweep, target opposite side) was not the X15 definition.

### S9. Initial Balance 25% retracement continuation (Edgeful "ultimate bullish setup", NQ)
- Fact: Conditions: open inside yesterday's range; 9:30 to 10:30 IB closes green (10:30 close > 9:30 open); price breaks above IB high after 10:30; then retraces. Entry = limit at IB high minus 25% of IB height. Stop = just below IB high minus 50% of IB height. Target = previous day high. Mirror for bearish.
- Stats (6 months NQ): IB single break 82%, double 16%, none 1.55%. On IB-high break days, 25% retrace level hit 65%, 50% level hit 26.67%. First hour green -> day closes green 84%.
- Claim: "80% win rate", calculation not shown. One example ~4R.
- Evidence: [STAT] plus [ANEC] for the trade claim. 6-month window only.
- Source: https://edgeful.com/blog/posts/ultimate-bullish-setup-trading-NQ
- Ours: E3 (IB retest at 1.1x IB) PF 0.97 after cost. S9 is a different entry (inside IB, before extension); not tested.

### S10. IB "by rejection" first-break bias (Edgeful, NQ)
- Stat: if the IB low prints first (earlier in 9:30 to 10:30), the IB high breaks first after 10:30 78.46%; if IB high prints first, IB low breaks first 77.42%. 6 months, 5m, by wick. GC does not show it.
- Use: directional filter for breakout after 10:30, not a standalone entry.
- Evidence: [STAT], short window, no sample size given.
- Source: https://www.edgeful.com/blog/posts/ib-by-rejection-deep-dive

### S11. Liquidity sweep and reclaim of PDH/PDL and session highs/lows (EdgeSweep MNQ)
- Fact: Levels = prior-day H/L, Asia/London/NY session H/L, 60m swing pivots. Long setup = trade below level then close back above; short mirror. Confirmation on 5m (FVG, MSS, displacement). Stop beyond sweep extreme + ATR buffer. TP1 ~0.90R (all but 1 contract), runner 1.5 to 4.0R to opposing liquidity, fallback 2.2R. Stop to half-risk at 50% of TP1, BE at 75% of TP1. Sizing = $250 / stop risk per contract. Specific v13.19 setups: PDL sweep/reclaim long; Monday London low long; PDH sweep short only Mon/Thu/Fri 10:00 to 13:59.
- Claim: MNQ 5m, ~333 setups (~3.85/month), net ~$10,753, PF ~1.405, max DD ~$3,078. Dataset dates not stated.
- Evidence: [BT-A], heavy day/time/source filtering (overfit risk), closed source.
- Source: https://in.tradingview.com/script/32hpjD0T-EdgeSweep-MNQ-System/
- Ours: X15 generic PDH/PDL and ON H/L sweep (turtle soup) PF .54 to .95, all rejected. E19 failed break fade loses every year.

### S12. Asia range sweep, London kill zone reversal
- Fact (TradingView open-source): Asia range = 20:00 to 00:00 NY. London kill zone 02:00 to 05:00 NY. Raid beyond Asia high -> only shorts; below Asia low -> only longs. Entry after confirmation (MSS + FVG, CISD, FVG tap). Stop at protective structure. Target 1 = opposite Asia extreme. Skip high-impact US news days. NY continuation 07:00 to 10:00 on 0.5 to 0.79 retracement of London impulse.
- Related (TradeZella, NQ 1m): London 02:00 to 05:00, sweep of Asia/previous session/equal H/L, displacement, FVG inverts to IFVG (body close through), enter on retrace into IFVG, stop beyond sweep (example 20 to 25 pts London, 30 to 40 NY), min 1:2.
- Related stat (ALN Sessions, 10y NQ, nqstats): after London closes, price revisits London high 81.1% / London low 74.9% (example figures; "sweep" not precisely defined).
- Evidence: [ANEC] for rules, [STAT] for revisit odds. No P&L anywhere.
- Sources: https://vn.tradingview.com/script/1ZcOyqs5-Asian-Range-Liquidity-Sweep-Kill-Zone-Reversal/ , https://www.tradezella.com/strategies/nq-liquidity-sweep-reversal-scalping-strategy , https://in.tradingview.com/script/KNTFWlm2-ALN-Sessions-NQ-Stats-x-CantoLab/
- Ours: X12 rejected Asia-range London BREAKOUT (PF <= 1.03). The sweep-REVERSAL variant is untested.

### S13. Hourly range sweep, retrace to hour open (NQ Hourly Retracements)
- Stat: setup = hour opens inside previous hour's range, then sweeps prior hour high or low (1m data, 2013 to 2025, 30,000+ events). After sweep, retrace back to swept level "90%+", to current hour open "60 to 70%". Sweep probability 9 AM hour "80%+", 5 PM hour "30 to 50%".
- Evidence: [STAT], full tables not published; "touch" stats, not P&L.
- Source: https://de.tradingview.com/script/oJunuDml-NQ-Hourly-Retracements-12y-Stats-with-Levels

### S14. VWAP reclaim / retest / band fade
- VWAP Reclaim (TradingView): close above VWAP, pullback to VWAP closes back above (retest), entry on break of retest candle high; stop beyond retest swing + 0.5 ATR; target 1.5R; longs only if VWAP slope over 10 bars flat/up. [no results] https://il.tradingview.com/script/glll4xvz-VWAP-Reclaim/
- VWAP 2SD fade (CrossTrade): session VWAP +/- 2SD; skip news days, ADX(14,5m) > 25, or opening hour > 2x 20-day average; trigger = rejection candle at band; entry next bar open; stop 1 ATR beyond trigger bar; target VWAP. Windows 10:00 to 11:30 and 13:30 to 14:30. Claim (explicitly "expectations", not backtest): WR 55 to 65%, PF 1.2 to 1.6. [ANEC] https://crosstrade.io/learn/trading-strategies/vwap-reversion
- NexusFi: do not use VWAP for first 90 minutes; fade only when bands contracting and VWAP flat. [ANEC] https://nexusfi.com/a/strategies/vwap-trading-strategies
- Ours: E7 (VWAP first touch after 10:30) U; Q5 (VWAP +/-2SD touch behavior) unmeasured.

### S15. EMA 9/21/50 trend pullback (PickMyTrade, "Clement Ang" adaptation, NQ)
- Fact: Long when EMA9 > EMA21 > EMA50 (mirror short). Pullback = touch of EMA21 within last 5 bars. Signal bar body >= 40% of range and close beyond EMA9. Entry next bar. Stop 1.5 ATR(14). Target 2.5R. Trail 1 ATR after 1R. Entries 9:30 to 15:45, flat 15:55. 3-bar cooldown.
- Claim: 1H, 2025-01 to 2026-10, 300 trades, WR 48.7%, PF 1.133, max DD 28.5%. 15m: 101 trades, +5.6%, DD 18%.
- Evidence: [BT-A], weak. Link to Ang's 520% unverified.
- Source: https://blog.pickmytrade.trade/clement-ang-us-trading-championship-nq-strategy-pine-script-v6/
- Ours: X17 EMA9/21 cross and EMA20 pullback on all days PF .78 to .97 (lose).

### S16. 8:30 red-folder news, "fair price" (JJ Simon video summary)
- Fact: Fair price reference = body of 8:29 candle. News close to forecast -> trade reversion to pre-news price; surprise -> treat post-news consolidation as new fair price, trade continuation. Entry on break and close of structure. Stops and targets "arbitrary", sized to firm rules. Done by 11:00.
- Claim: ~$889K payouts across Topstep, Lucid, E8, etc. in 12 months (title says $1.3M).
- Evidence: [ANEC], AI-generated summary of video.
- Source: https://youtubesummary.com/summary/8lbkj0PF1uM
- Ours: already tested in `NEWS_TRADING_JJ_SIMON_AND_TESTS.md` (one variant PF ~1.5, ~13 trades/yr, kept as module NEWS; spike fade break-even).

### S17. News straddle (bracket both sides before release)
- Fact: pending buy and sell stops outside expected range before release; example (forex) stop = 0.5x target distance. Risk: both sides fill in whipsaw; slippage.
- Firm rules: Apex prohibits placing opposing orders around news; Topstep blocks new SIM fills 5 min before/after CPI on index minis; MFFU funded 2 min before/after Tier 1 events; Tradeify allows. So the straddle is mostly not permitted as designed.
- Evidence: [ANEC], no futures results.
- Sources: https://proptraderedge.beehiiv.com/p/news-bracketing-strategy , https://traderssecondbrain.com/guides/futures-prop-firms-news-trading

### S18. Discretionary levels with tiny fixed stop and asymmetric R (Topstep combine passers)
- Brian Weber (Topstep 50K, NQ, 2020): max stop 5 NQ pts; 1 lot default; add 2nd lot only after +$100 to $150 banked that day; back to 1 lot after a 2-lot loss; min target 2R; claimed WR 65 to 70%; quit after +$200 to $300 early. Levels = daily pivots, fibs, trendlines on 30m/1H, entries on 5m/512-tick. [ANEC] https://www.brianwweber.com/blog/2020/2/22/how-to-pass-step-1-and-step-2-of-topsteptraders-combine
- Topstep blog author (50K, ES, passed in 15 days): 2 ES with 2 pt stop (~$200 risk), min 2.5:1 RR, 3:1 in volatility; stop day once > +$300. Claim: avg win $321 vs avg loss $64. [ANEC] https://www.topstep.com/blog/3-things-to-pass-a-trading-combine

### S19. Signal-service "passes" (for completeness, low value)
- Falcon AI "passed 5 evals in 4 days" (4 Topstep, 1 Apex, MNQ, 15m, 9:00 to 13:00 or 10:00 to 13:00): rules not disclosed; paused strong days to stay under Topstep 50% consistency; worst day ~-$1,02x. Commercial. [ANEC] https://thefalconai.com/blog/how-we-passed-5-prop-evals-in-4-days
- Tradesharpe "Passed 5 Topstep 50K in 4 days": rules not in description. [ANEC] https://www.youtube.com/watch?v=k1dvB5ZE46E

---

## 2. Eval-passing risk frameworks (exact numbers people use)

| Framework | Numbers | Source / tag |
|---|---|---|
| Risk per trade as fraction of drawdown | 1/20 of DD ($125 on $2,500); 10% of DD ($200 on $2K, $250 on $2.5K), adjust $50 per $500 DD gained/lost; 2% of DD ($50 on $2,500) conservative | r/Daytrading 50K MNQ thread [ANEC]; NexusFi Academy [3P] |
| Aggressive eval risk | ~10% per trade in eval, 2.5% once funded | "20 x 250K" OP [ANEC] |
| Fixed $ per trade | $100 to $150 (Lucid 50K guide); $200 to $300 with stop after 1 win; $500 max | Falcon Lucid guide; Reddit [ANEC] |
| Stop after first win | 1 to 2 trades/day, stop after first winner | Reddit (shadowergoat) [ANEC] |
| Stop after first loss | one loss per session then stop | S4 backtest rule [BT-I] |
| Daily profit cap | quit at > +$300 (50K ES); +$200 to $300 early then close platform; $100 to $200/day pre-trail-lock | Topstep blog, Weber [ANEC]; NexusFi [3P] |
| Personal daily loss | 20 to 25% of trailing DD ($500 to $625 on $2,500); or 60 to 70% of firm DLL; $500 self-cap on $1,000 firm DLL | NexusFi [3P]; Weber [ANEC] |
| Cool-off | lose 50% of daily budget -> pause 30 min; 75% -> stop | NexusFi [3P] |
| Contracts from DLL | max = DLL / (stop ticks x tick value) x 0.6 | NexusFi [3P] |
| Contracts from DD | max = cushion / (bad days 5 to 8 x trades/day x stop cost) | NexusFi [3P] |
| Step-down by cushion ($50K NQ, $2,500 trail) | > $2,200: 1 NQ; > $1,500: 5 MNQ; > $1,200: 4; > $900: 3; > $600: 2; < $600: 1 MNQ | NexusFi @trekke [ANEC] |
| Scale up on cushion | add 1 micro per $500 of cushion; add 2nd lot only after +$100 to $150 that day | Reddit, Weber [ANEC] |
| Phase plan (Topstep 50K) | days 1 to 5: 1 MES; 6 to 10: 2 MES; within $500 of target: back to 1 MES; trade 9:30 to 11:30 only; 1 to 3 trades/day | propjournal [3P] (its $ math is wrong for MES) |
| Lock-then-size | stay at min size until trailing DD locks (Topstep $2,000, Apex $2,500 + $100 on 50K), then scale | propjournal, NexusFi [3P] |
| Consistency pacing | best day < 30 to 45% of total target depending on firm (Topstep 50%, Lucid Flex 40% default, Apex 30% at payout); pause strong days | Falcon, NexusFi, Reddit [3P/ANEC] |
| Volatility/news | x0.75 size when ATR > 1.5x 20d avg; 50% size or flat before CPI/FOMC/NFP | NexusFi [3P] |
| Trades must hold > 10 s (Tradeify funded) | > 50% of trades and profit from > 10 s holds | Tradeify [OFF] |

Fact (math): two separate NexusFi/propjournal pages mis-state micro point values. MNQ = $2/pt, MES = $5/pt, NQ = $20/pt, ES = $50/pt.

---

## 3. Shortlist: 6 testable rule sets for MNQ 1m/5m OHLC

Common conventions: times ET; RTH = 9:30 to 16:00; ON = 18:00 to 9:30. OR15 = high/low of 1m bars 9:30:00 to 9:44:59. IB = 9:30 to 10:29:59. VWAP = session VWAP from 9:30 (needs volume; skip S14 if no volume). Cost = 3 pts round trip per contract (project standard, R5 sweep 2 to 5). Same-bar stop and target = stop. Fill on stop-entry = trigger price + 1 tick; limit fills only if price trades through by 1 tick. Flat at 15:55 unless stated. One position at a time. Report: trades, WR, PF, avgR, max DD in R, yearly split, and Lucid 50K pass sim (existing tools).

### SL1. ORB15 high-WR, 50% target (S1/S2), untested here
```
OR = OR15. W = ORH - ORL.
skip day if W > 0.8% of 9:30 open (also grid 0.5%, 0.55%, 1.0%) or W < 10 pts.
from 9:45 to 11:00: on first 5m bar CLOSE > ORH -> long at next bar open;
                    on first 5m bar CLOSE < ORL -> short (variant: long-only; variant: if first close is below ORL, no trade at all).
stop = opposite OR side, capped at entry -/+ min(W, 50 pts) (grid cap 30/40/50/75).
target = entry +/- 0.5*W (grid 0.33, 0.5, 0.75, 1.0).
max 1 trade/day. exit at 15:55 if open.
day-of-week filter: report by weekday, do NOT pre-apply Mon/Thu/Tue skips (those were fit in-sample by the sources).
```
Why: sources claim 72 to 75% WR, PF 1.6 to 2.5. Test of whether the sub-1R target survives 3 pt cost (target must exceed ~10x cost: W >= ~40 pts).

### SL2. IB green-hour 25% retrace continuation (S9), untested here
```
precondition: 9:30 open inside [PDL, PDH] (PD = prior RTH 9:30-16:00).
at 10:30: IB_H, IB_L, W = IB_H - IB_L. bull if close(10:29 bar) > open(9:30 bar); bear if <.
bull: wait for first 1m trade > IB_H (after 10:30, before 13:00). then place limit long at E = IB_H - 0.25*W.
      stop = IB_H - 0.5*W - 1 tick. target = PDH if PDH - E >= 1.0*(E - stop) else 2R (variant: fixed 1R, 2R).
      cancel limit if not filled by 14:00 or if price first trades below IB_H - 0.5*W.
bear: mirror with IB_L, PDL.
max 1 trade/day. exit 15:55.
```
Why: 65% touch of the 25% level, 84% green-hour-green-day. Distinct from E3 (entry inside IB, not at 1.1x extension).

### SL3. 9:00 hour range sweep, 10:00 to 11:00 reversal to opposite side (S8 version A)
```
at 10:00: H9 = high, L9 = low of 9:00-9:59 1m bars (includes pre-RTH 9:00-9:29 ON data).
10:00-11:00: sweep_high = 1m high > H9 and that 1m bar or one of the next 5 bars closes < H9.
             on sweep_high: short at close of the first 1m bar that closes back below H9.
             stop = highest high since 10:00 + 1 tick. target = L9 (variant: midpoint of H9/L9; 2R).
             skip if target distance < 1.0R or risk > 40 pts.
sweep_low: mirror (long, target H9).
first qualifying sweep only, 1 trade/day. time exit 12:00.
```
Why: TTrades rule set; differs from X15 (2h extreme + FVG). Cheap to test, uses ON data for 9:00 to 9:29.

### SL4. Asia range sweep, London kill zone reversal (S12), uses overnight data
```
Asia: AH/AL = high/low of 20:00-23:59 bars (session date d-1 evening).
02:00-05:00: if 1m high > AH and 5m bar closes back < AH -> short at next 1m open.
             stop = sweep extreme (highest high since 02:00) + 2 pts.
             target = AL (variant: Asia midpoint; 2R). skip if target < 1.0R or risk > 40 pts.
             if 1m low < AL and 5m close back > AL -> long, mirror.
first trigger only; if both sides swept before any trigger, no trade.
exit at 09:25 if open (avoid RTH open), variant 09:29 hold to 10:00.
skip days with 8:30 red-folder release (calendar from RED_FOLDER_NEWS_STUDY).
```
Why: X12 rejected Asia breakout; reversal variant untested and is the version people actually credit.

### SL5. Hourly sweep, retrace to hour open (S13), 1m
```
for each hour h in {9:00, 10:00, 11:00, 13:00, 14:00} (variant: all ON hours):
  Ph/Pl = prior hour high/low; Oh = open of hour h; require Pl < Oh < Ph.
  if price trades > Ph during hour h (first side swept): enter short at the close of the first 1m bar closing back < Ph,
     only if (Ph - Oh) >= 10 pts.
     stop = high since sweep + 1 tick (cap 25 pts). target = Oh. time exit = end of hour h.
  mirror for sweep of Pl.
  max 1 trade per hour, 3 per day.
```
Why: published 60 to 70% "touch hour open after sweep" base rate over 13y. Checks if touch rate converts to PF > 1 after cost. Measure base rate first (cheap), then P&L.

### SL6. 10:00 to 11:00 VWAP-side FVG scalp, 15/15 with BE (S7, Reddit 20 x 250K)
```
bias long at 10:00-11:00 if 5m close > session VWAP AND 5m close > EMA200(5m, continuous incl. ON); short if both below; else none.
trigger (1m): bullish FVG = low[0] > high[2] with bar[1] body >= 0.6*range and gap >= 2 pts, formed 10:00-10:55.
entry: limit at high[2] (top of gap edge nearest price) valid 10 bars.
stop = entry - 15 pts. target = entry + 15 pts (variant: 75% at +15, runner stop to BE, runner target 2R or 11:30 exit).
BE: when price reaches +8 pts, stop to entry + 1 pt (grid +5/+8/+10).
max 2 trades/day; stop day after first win (framework from section 2).
```
Why: most specific anecdotal rule found from a claimed multi-pass trader. Expect cost pressure (X3): needs net WR > ~60%. Quick kill or keep.

Alternates if any of the six is blocked: S10 IB-by-rejection as a filter on V4/E1 after 10:30; London H/L revisit (S12 stat) as a 9:30 to 11:00 magnet target; S14 VWAP 2SD fade on contracting-band days 10:00 to 11:30 (also answers Q5).

Already tested in this repo, do not re-test as-is: generic PDH/PDL/ON sweep (X15), silver bullet FVG (X15), gap fill (X15), high-R Zarattini ORB (X9), Asia breakout (X12), EMA 9/21 and EMA20 pullback on all days (X17), IB 1.1x retest (E3), JJ Simon news (NEWS module).

---

## 4. Takeaways (ours)
1. Fact: every high-WR ORB claim (S1, S2) uses a target smaller than the stop and was optimized in-sample on 6 to 12 months; none report OOS or costs. Only S3 and S4 have independent or OOS checks, and they show gross edge of ~0.1R that costs mostly eat.
2. Fact: no pass claim found is verified. The specific rules people credit cluster in 9:30 to 11:00 ET, use one trade or stop-after-first-win, and size at 5 to 12% of drawdown per trade.
3. The repeated eval mechanic is not the entry: it is small fixed risk until the trail locks, a daily profit cap, and pausing strong days to satisfy consistency.
</content>
</invoke>
