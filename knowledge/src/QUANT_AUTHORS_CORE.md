# Quant and trading authors: core claims, evidence, and what transfers to intraday MNQ/MES

Purpose: evidence-first reference for a rules-based intraday futures scalper (MNQ/MES, Brooks/Wade price action, prop-firm daily loss limit, goal = most trading days green). Compiled 2026-10-21 from primary sources and well-known summaries. Numbers are quoted as the authors state them; "evidence" rates the quality of support behind the claims, not the author.

Legend for "Transfers": YES = directly usable on 1m/5m index futures; PARTIAL = needs adaptation; NO = daily/portfolio-only.

---

## 1. Ed Thorp (Kelly, edge first)

Core claims
- Never bet without a measured positive edge. Blackjack, warrants, stat-arb: in each case the edge was quantified first, size came second. [Thorp, The Kelly Criterion in Blackjack, Sports Betting and the Stock Market](https://sites.oxy.edu/lengyel/M330/thorp/paper.htm)
- Kelly fraction for a binary bet: f* = p - q/b (p = win prob, q = 1-p, b = win/loss ratio). For continuous returns approx f* = mu/sigma^2. Full Kelly maximizes long-run growth but produces violent drawdowns. [Thorp paper (eScholarship PDF)](https://escholarship.org/content/qt2sf6m38g/qt2sf6m38g.pdf)
- Betting more than Kelly is strictly worse: growth falls and risk rises. Betting 2x Kelly gives zero expected growth. Same source.
- Fractional Kelly (half or less) gives most of the growth with far less variance; Thorp and most practitioners use 1/2 or less because edge estimates are uncertain and errors are asymmetric (overestimating edge is lethal). Same source.
- Probability of ever halving the bankroll under full Kelly is 50%; under half Kelly roughly 1/8 (Thorp's blackjack numbers). Same source.
- "Pay-off is to be right over many trials": edge compounds only with a large number of independent bets. Same source.
- Thorp's Princeton Newport Partners: ~19.8% annual, 230 months, 3 losing months (a "most periods green" record built from many small hedged positions, not big calls). [Gwern copy of Thorp 2006](https://www.Gwern.net/doc/statistics/decision/2006-thorp.pdf)

Evidence: academic (peer-reviewed math) plus a verified 20-year live track record. Strongest tier.

Transfers: YES for sizing logic (Kelly ceiling, use a fraction), YES for "edge first, size second". The per-trade f* needs a stable p and b; on scalps those must come from a large out-of-sample sample, not from a backtest with 50 trades.

---

## 2. Jim Simons / Renaissance (public record only)

Core claims (what is publicly documented, mostly via Zuckerman's book)
- "We're right 50.75% of the time... but we're 100% right 50.75% of the time" (Robert Mercer). Edge per trade is tiny; profits come from applying it at huge scale and frequency. [Quartr: Renaissance and Medallion](https://quartr.com/insights/company-research/explore-renaissance-technologies-and-the-medallion-fund)
- Signals are statistical, not narrative. "We don't impose our own judgment on how the markets behave" (Peter Brown). Same source.
- Many weak, uncorrelated, non-intuitive signals combined in one model, rather than a few strong ones. Same source and [PWL Capital summary](https://pwlcapital.com/renaissance-technologies-medallion-fund-an-exception-to-the-indexing-rule/)
- Kelly-style sizing, heavy leverage (average ~12.5x, up to ~20x) because per-trade variance is low and bets are many and short. [Quartr](https://quartr.com/insights/company-research/explore-renaissance-technologies-and-the-medallion-fund)
- Enormous investment in clean data and execution cost modeling; signals that do not survive costs are discarded. Same.
- Medallion net CAGR ~39.9% 1988-2022, only one losing year on record; capital capped so that the edge is not diluted by size. Same.
- Hiring: scientists, not finance people; collaborative, one shared model, everything tested.

Evidence: anecdotal/journalistic (no papers, no public code). High credibility on the general shape, zero on specifics.

Transfers: PARTIAL. The transferable idea is the posture: tiny edges, many trials, strict stats, obsess over costs and data. The leverage and signal count do not transfer to a one-person prop account.

---

## 3. Marcos Lopez de Prado (backtest overfitting, DSR, walk-forward, meta-labeling)

Core claims
- Most published backtests are false positives because researchers run many trials and report the best. The Probability of Backtest Overfitting (PBO) is estimated with Combinatorially Symmetric Cross-Validation (CSCV): split the trial matrix into S sub-samples, test every in-sample/out-of-sample combination, measure how often the in-sample best is below-median out-of-sample. [Bailey, Borwein, Lopez de Prado, Zhu: The Probability of Backtest Overfitting](https://papers.ssrn.com/abstract=2326253)
- Deflated Sharpe Ratio: the expected maximum Sharpe of N random trials rises with N; subtract that before claiming significance. DSR also corrects for non-normal returns (skew, kurtosis) and short track records. [The Deflated Sharpe Ratio (SSRN)](https://papers.ssrn.com/abstract=2460551), [Wikipedia summary](https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio)
- Minimum backtest length: the number of years needed to trust a given Sharpe grows with the number of trials run. Same.
- Walk-forward is not enough on its own: use purged K-fold / CPCV (remove overlapping label windows between train and test, add an embargo after test) to kill leakage from autocorrelated bars. [Purged cross-validation summary](https://www.luxalgo.com/library/concept/purged-cross-validation.md)
- Triple-barrier labeling: label each entry by which of {profit barrier, stop barrier, time barrier} is hit first. This is exactly a scalper's PT/SL/time-exit structure. [Label definition summary](https://www.luxalgo.com/library/concept/label-definition-and-prediction-horizon.md)
- Meta-labeling: keep the primary rule (e.g. a price-action signal) to decide direction; train a secondary model only to decide whether to take the trade and how big. This raises precision without touching recall of the primary signal. Same source.
- Strategy risk vs portfolio risk: with hit rate p and payoff ratio, you can compute the probability that a strategy with true Sharpe x produces a losing year/month; most "losing days" are strategy variance, not a broken edge.

Evidence: academic (peer-reviewed papers, widely replicated; the R package `pbo` implements CSCV). Strongest tier.

Transfers: YES, all of it. Intraday scalps produce thousands of trades, the ideal regime for CPCV, DSR, and meta-labeling.

---

## 4. Ernest Chan (mean reversion vs momentum regimes, Kelly)

Core claims
- Every strategy is either mean-reverting or momentum; you must know which regime you are in. Test stationarity (ADF), Hurst exponent (H < 0.5 mean-reverting, H > 0.5 trending), and half-life of mean reversion (from an Ornstein-Uhlenbeck fit) to set the lookback and holding period. [Algorithmic Trading: Winning Strategies and Their Rationale (summary)](https://9natree.castos.com/episodes/review-algorithmic-trading-winning-strategies-and-their-rationale-ernest-p-chan-summarized), [QuantInsti webinar notes](https://blog.quantinsti.com/webinar-basics-of-mean-reversion-strategies-by-dr-ernest-p-chan/)
- Mean reversion has high win rate and small wins with rare large losses; momentum has low win rate, large wins. Risk control must be opposite: stops hurt mean reversion (they exit when expected return is highest), stops help momentum.
- Momentum on intraday timeframes comes from specific events (open, news, order flow imbalance, roll); it is short-lived and decays fast. Same.
- Kelly: optimal leverage f = mu/sigma^2 (per-strategy), and "half-Kelly" in practice. Use the Kelly formula to compare strategies: the one with the highest Sharpe deserves most capital, not the one with highest return.
- Risk management: a drawdown-triggered reduction of leverage (constant proportion) is consistent with Kelly; a fixed stop-loss is not necessarily.
- Backtest pitfalls: look-ahead bias, survivorship bias, data snooping; prefer simple models with few parameters.
- Regime switching: a strategy's statistics change with volatility; a VIX/ATR filter is often the single most useful "regime" variable.

Evidence: backtested (author's own, mostly daily equities/FX), plus live fund experience; some claims anecdotal.

Transfers: PARTIAL. Regime classification (trend vs range day) is directly relevant; Hurst/half-life can be computed on 1m/5m returns per session. Kelly comparison of sub-strategies transfers. His equity-pairs specifics do not.

---

## 5. Robert Carver (Systematic Trading)

Core claims
- Decide risk with one number: an annualised volatility target. Size every position by recent realised volatility of the instrument in account currency. [CXO notes on Systematic Trading](https://www.cxoadvisory.com/big-ideas/a-few-notes-on-systematic-trading)
- Realistic Sharpe ratios after costs rarely exceed 1.0; backtests showing 2-3+ are almost always overfit. Multiply a backtested Sharpe by ~0.75 to get a realistic expectation. Same.
- Use half-Kelly or less; full Kelly is "too aggressive because of the risk of a poor run of luck". Same.
- Combine many weak, diverse rules (he runs 8 rules, 30 variations, 45 instruments). Drop any two variations correlated above 95%. Same.
- Forecasts should be proportional to expected risk-adjusted return and capped; combined forecasts are scaled by a diversification multiplier. Same.
- Costs: total trading costs must be at most one-third of the conservative pre-cost Sharpe; set an explicit "speed limit" (max annual turnover). Same.
- Do not trade if the new position is within 10% of the current one (reduces churn). Same.
- Fit rules as little as possible; prefer "no fit" rules with sensible defaults and "handcrafted" equal-ish weights over optimised weights.

Evidence: backtested (35-year, 45-instrument system) plus his AHL/fund experience; principles consistent with academic literature.

Transfers: YES for vol-targeting (size by ATR so each trade risks a constant fraction), YES for cost-to-Sharpe ratio and speed limit (critical for scalping), PARTIAL for rule diversification (combine 2-4 independent intraday setups rather than one).

---

## 6. Van Tharp (expectancy, R-multiples, position sizing)

Core claims
- Express every trade as an R-multiple: profit or loss divided by initial risk (distance to stop). A system is a distribution of R-multiples. [NexusFi SQN article](https://nexusfi.com/a/risk-management/system-quality-number-sqn)
- Expectancy = mean R per trade = (win% x avg win R) - (loss% x avg loss R). You need expectancy > 0 after costs and a known number of opportunities per period; profit = expectancy x opportunities. Same.
- System Quality Number: SQN = sqrt(N) x mean(R) / stdev(R), N capped at 100 for comparison. Tharp's scale: < 1.6 poor, 1.6-1.9 below average, 2.0-2.4 average, 2.5-2.9 good, 3.0-5.0 excellent, 5-7 superb. [TradesViz SQN glossary](https://www.tradesviz.com/glossary/system-quality-number/)
- Position sizing is the main lever for meeting objectives; the entry is secondary. Risk a fixed % of equity per trade (he discusses 0.5-1% for most; 2% is aggressive). [Trade Your Way to Financial Freedom (publisher page)](https://www.eltraderfinanciado.com/nl/trading-books/reussir-en-trading)
- Simulate the R-distribution (Monte Carlo resample) to see drawdown ranges before trading live.
- Reduce size after a drawdown; the goal is to survive the worst run the R-distribution can produce.
- Psychology: you trade your beliefs; keep a written system with explicit objectives.

Evidence: anecdotal/practitioner (no rigorous studies), but the R-multiple and SQN math is just descriptive statistics and is sound.

Transfers: YES. R-multiples are the natural unit for a scalper with fixed stops; SQN on the last 100 trades is a decent "is the edge alive" monitor.

---

## 7. David Aronson (Evidence-Based Technical Analysis)

Core claims
- Only objective, programmable rules that output long/short/flat can be tested; subjective TA makes untestable claims and is "worse than wrong". [CXO chapter-by-chapter review](https://www.cxoadvisory.com/technical-trading/evidence-based-technical-analysis-applying-the-scientific-method-and-statistical-inference-to-trading-signals-chapter-by-chapter-review)
- Data-mining bias: the best of many tested rules looks good by selection alone. Correct with White's Reality Check or Monte Carlo permutation on the full set of rules tested, not just the winner. Same.
- Case study: 6,402 simple rules on the S&P 500 (trend, reversal, divergence); after correcting for data-mining bias, none was statistically significant. Same.
- Detrend the test data so a rule does not get credit for the market's drift. Same.
- Cognitive biases (confirmation, hindsight, overconfidence) make chart reading unreliable; humans plus computers beat humans alone. Same.
- The bar for a rule: beats a benchmark by a statistically significant margin after bias correction and out-of-sample.

Evidence: academic-grade methodology, one large backtest (daily S&P). Strongest tier for method.

Transfers: YES for method (permutation tests, count every variant you tried). His negative result is daily-bar S&P; it does not say intraday rules fail, only that the burden of proof is high.

---

## 8. Adam Grimes (The Art and Science of Technical Analysis)

Core claims
- Most price action is indistinguishable from a random walk; trading is negative-sum after costs, so any setup must point to a specific buying/selling imbalance. [Topstep summary of Grimes](https://topstep.com/blog/going-deep-on-adam-grimes-approach)
- Random lines mimic support/resistance as well as real ones; most chart patterns and S/R levels have no measurable edge on their own. Same.
- Markets alternate between trend (less-than-random, tradeable) and range (mostly random). Same.
- Core setup: pullback in a trend with momentum confirmation (3/10 oscillator making new highs with the trend; avoid entries after a momentum divergence). Same.
- Trend health rule: with-trend swings must be larger than counter-trend swings in both size and duration; a pullback nearly as big as the prior impulse signals the trend is ending. Same.
- A pullback that stalls into a sideways range is a poor trade (often exhaustion). Same.
- Higher timeframe against the trade "raises the failure rate significantly" (his words; no figure published). Same.
- Failed breakouts in ranges (Wyckoff springs/upthrusts) are the best range-reversal signals. Same.
- Grimes' book publishes his own tests of "pullback", "breakout" and "failure" patterns; his widely-cited result is that only a small handful show excess return (pullbacks after strong momentum and failed breakouts), and that outright breakouts without momentum context do not.
- Identifying conditions to NOT trade matters as much as setups.

Evidence: backtested (his own, in the book and blog) but not peer-reviewed; mix of quant tests and discretionary practice.

Transfers: YES. His pullback-with-momentum and "with-trend legs bigger than counter legs" rules are exactly Brooks' "second entry" and "channel vs range" ideas in testable form.

---

## 9. Toby Crabel (opening range breakout, NR4/NR7)

Core claims
- Opening Range Breakout: buy stop at open + Stretch, sell stop at open - Stretch; the first fill is the position, the other order is the stop. [OxfordStrat Narrow Range study](https://oxfordstrat.com/trading-strategies/narrow-range/)
- Stretch = 10-day average of min(High - Open, Open - Low) (the smaller side of the open). Crabel used ~1x; OxfordStrat tests 2x. Same, and [NexusFi ORB article](https://nexusfi.com/a/strategies/opening-range-breakout)
- Range contraction precedes expansion: NR4 (narrowest range of last 4 days), NR7 (of last 7), ID (inside day) and ID/NR4 flag high-probability ORB days. NR7 is "the single most important filter". [NexusFi](https://nexusfi.com/a/strategies/opening-range-breakout), [LuxAlgo NR4/NR7](https://www.luxalgo.com/library/concept/nr4-nr7-narrow-range-bars.md)
- The earlier in the session the ORB entry triggers, the better the odds; late entries are chases. [NexusFi](https://nexusfi.com/a/strategies/opening-range-breakout)
- Trend days are rare (commonly 20-30% of sessions) and ORB is a trend-day capture tool; on the other 70-80% it loses or scratches, so filters (NR7, ID) are what make it viable.
- Day structure stats: wide-range days after narrow days; the open is often near one extreme on trend days.
- OxfordStrat's portfolio test (42 futures, 1980-2013, 1% risk) rates the generic NR-N ORB strategy "C" with $50 round-turn costs: edge exists but is thin without filters. [OxfordStrat](https://oxfordstrat.com/trading-strategies/narrow-range/)

Evidence: backtested (Crabel's 1990 book is tables of win rates on 1980s futures; later replications are mixed). Numbers like "60-65% hit rate for NR7-filtered ES ORB" circulate unsourced.

Transfers: YES, directly. ORB and NR7/ID filters are built for index futures and daily-session structure. Must be re-tested on 2020s MNQ/MES.

Related primary evidence on ORB
- Zarattini & Aziz (2023): 5-min ORB on QQQ/TQQQ, stop at first-candle extreme, target 10R, 1% risk, 2016-2023: reported ~33%/yr with zero costs and 4x leverage. [SSRN](https://papers.ssrn.com/abstract=4416622), [CXO summary](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy)
- Independent replication on 5 index CFDs 2015-2026: gross +0.131R/trade on NQ (hit rate 23%), but net of realistic spread/slippage NQ falls to +0.002R (t = 0); 4 of 5 indices negative. The first 5-min candle direction has information worth ~+0.10 to +0.13R vs random, about equal to round-trip costs. [MQL5 replication](https://www.mql5.com/en/blogs/post/776235)

---

## 10. Linda Raschke (day types, trend days)

Core claims
- Decide before the open which day type you expect (trend vs mean-reversion/range) and trade the matching playbook; never average down on a trend day. [Raschke rules summary](https://optionstradingiq.com/linda-raschke-rules-for-trading/)
- Trend day signature: open near one extreme, close near the other, shallow pullbacks, early breakout of the first-hour range that does not come back. Same.
- On a trend day, hold with-trend positions to the close (MOC); the largest losses of range traders occur on trend days. Same.
- Range day playbook: fade the extremes of the first-hour range, target the midpoint/opposite side.
- Narrow-range days and inside days precede trend days (shares the Crabel view); also, a trend day frequently follows a day with a big gap that fails to fill.
- Take every signal of a mechanical system; size up when several independent systems agree; scale out when conviction drops. Same.
- Most profits come from a small share of trades (fat right tail); cutting losers fast is what keeps the distribution positive. Same.
- Her "Holy Grail" (ADX > 30 pullback to 20 EMA) and "Turtle Soup" (failed breakout of 20-day high/low) are the published, testable setups from Street Smarts.

Evidence: anecdotal/practitioner with some published backtests (Street Smarts). Day-type claims are widely observed but rarely quantified by her.

Transfers: YES. Day-type classification, first-hour range, and "trend days are where you must not fade" map directly onto MNQ sessions.

---

## 11. Perry Kaufman (Efficiency Ratio, trend vs noise)

Core claims
- Efficiency Ratio ER = |close_t - close_(t-n)| / sum(|close_i - close_(i-1)|, i over n). ER near 1 = clean trend, near 0 = noise. [TA-Lib ER](https://ta-lib.org/functions/er.html)
- Markets have become noisier over time and shorter timeframes are noisier than longer ones; so trend rules on fast bars need either an ER filter or a longer effective lookback. [KAMA notes](https://nexusfi.com/a/indicators/kaufman-adaptive-moving-average-kama)
- KAMA: smoothing constant SC = [ER x (fast - slow) + slow]^2 with fast = 2/(2+1), slow = 2/(30+1); the average speeds up when ER is high and flattens in noise. Same.
- Trend following works because of fat tails; it needs the few big moves. Mean reversion works in high-noise regimes. Use ER to switch between them.
- Robust systems have few parameters and perform similarly across neighbouring parameter values (a parameter "plateau", not a peak).
- Test across many markets and years; a rule that only works on one market in one period is noise.

Evidence: backtested (his encyclopedic Trading Systems and Methods), practitioner.

Transfers: YES. ER on 5m bars over the last 20-60 bars is a cheap regime filter for "trade breakouts vs fade".

---

## 12. Mark Douglas (probabilistic mindset)

Core claims
- Five fundamental truths: anything can happen; you don't need to know what happens next to make money; wins and losses are randomly distributed for any edge; an edge is just a higher probability of one outcome; every moment is unique. [Bookmap: 5 truths](https://bookmap.com/blog/5-truths-of-trading/)
- Think in samples: judge an edge over a series of at least 20 trades, never on one trade. [Trade That Swing takeaways](https://tradethatswing.com/key-takeaways-from-trading-in-the-zone-by-mark-douglas/)
- Predefine the risk on every trade and accept it fully before entry; the inability to accept the loss is what causes hesitation and revenge trading. Same.
- Take every valid signal without exception during the sample; pay yourself per the rules; evaluate only after the sample.
- Consistency comes from executing the same rules on each unique occurrence, not from being right.

Evidence: anecdotal (no data), but consistent with Kelly/expectancy math.

Transfers: YES as operating protocol: fixed risk, no discretion inside a sample, evaluate on blocks of 20-50 trades. For an automated system this becomes "do not touch parameters inside a review window".

---

## 13. Jack Schwager (Market Wizards common denominators)

Core claims
- Risk control first: avoiding large losses matters more than finding great entries; elite traders commonly risk 1% or less of equity per trade. [Lessons from Jack Schwager](https://www.antoinebuteau.com/lessons-from-jack-schwager.md)
- Know the exit before entry; cut losers fast; hold winners (the hardest habit). Same.
- Losses are a cost of business; being wrong is fine, staying wrong is not. Same.
- Process over outcome: a good trade can lose; judge decisions by rule adherence.
- Method must fit the trader's personality; no universal strategy.
- Reduce size when losing or unsure ("undertrade": halve what feels right). Same.
- Many wizards cut activity in bad periods or stop after a daily loss threshold; several describe stepping away after 2-3 consecutive losses.
- Years of study and repeated failure before finding one specific edge.

Evidence: anecdotal (interviews), but the sample is large and consistent across decades.

Transfers: YES. The daily-loss-limit discipline and 1%-ish per-trade risk are the prop-firm constraints restated.

---

## 14. Al Brooks (price action probabilities)

Core claims (as he states them; he says they are estimates, not measured)
- Most of the time the market is in breakout mode and the probability of a bull or bear move is 40-60% either way; it is rarely outside that band until a strong breakout is confirmed. [Brooks forum: probability of breakout](https://www.brookstradingcourse.com/support-forum/41-trading-breakouts/bo-has-60-probability-of-reaching-mm-target-but-is-it-really/)
- Trader's equation: probability x reward must exceed (1 - probability) x risk. With 40% probability you need reward at least 2x risk; with 60% you can take 1:1. [Brooks forum on trader's equation](https://www.brookstradingcourse.com/support-forum/general-trading-discussion/traders-equation-can-a-11-trade-have-higher-success-rate-than-60/)
- "80% of breakouts from a trading range fail" and "80% of reversal attempts in a trend fail". After a long range (20+ bars) the first breakout fails ~50% of the time; a breakout from a channel fails ~75%. [Brooks forum: breakout fail](https://www.brookstradingcourse.com/support-forum/12-market-cycle/breakout-fail/)
- A strong breakout (big trend bars, closes near extremes, follow-through) has ~60% probability of reaching a measured-move target equal to the breakout height; a member's backtest put it at 50-52% when taking every breakout. [Brooks forum](https://www.brookstradingcourse.com/support-forum/41-trading-breakouts/bo-has-60-probability-of-reaching-mm-target-but-is-it-really/)
- Three outcomes after a breakout: ~20% immediate reversal, else channel continuation or deep pullback into a range. Same.
- Second entries (High 2 / Low 2) beat first entries; do not take a third entry unless it is a wedge. Need two reasons for a with-trend trade. [Brooks probabilities compilation](https://www.slideshare.net/slideshow/brooksprobabilitiesdoc/258643754)
- Trends and ranges: a trading range is "sideways for 5-20 bars"; four or more trend bars against you means exit; climax corrections last at least an hour on the 5m. Same.
- Avoid the 11:00-13:00 CT doji zone; reversals cluster in the final two hours. Same.
- 50% rule: most moves retrace ~50%; most pullbacks in a strong trend are smaller than 1/3 of the daily average range. Same.
- Scalping: with 60%+ probability setups, 1:1 scalps work; otherwise swing part for 2R+.

Evidence: anecdotal (decades of discretionary observation; Brooks explicitly says the numbers are approximations). One member backtest contradicts his 60% figure.

Transfers: YES as hypotheses. Each percentage is a concrete test on 5m MNQ (breakout failure rate, second-entry win rate, measured-move hit rate).

Thomas Wade (same lineage) restates Brooks: only trade second entries with trend, stop beyond signal bar, 1:1 or 2:1 targets, max 2-3 trades, stop for the day after the daily loss limit. Evidence is anecdotal; treat as rule set to test. (Wade's YouTube material; no primary transcript could be fetched.)

---

## 15. Kevin Davey, Andreas Clenow, Larry Connors (concrete additions)

Kevin Davey
- Process: idea -> limited test -> walk-forward optimisation -> Monte Carlo of trade sequence -> incubation (paper trade 6+ months) -> live small. Most ideas die at step 2. [Algo Advantage: Davey part I](https://algoadvantage.substack.com/p/036-kevin-davey-part-i-its-all-about)
- Monte Carlo: resample trade PnL to get the distribution of max drawdown; size so the 95th percentile drawdown is survivable (his "risk of ruin" rule).
- Keep systems simple (few rules, few parameters), test on data the optimiser never saw, and accept a walk-forward efficiency above ~50%. Same.
- Evidence: practitioner, verified contest track record (World Cup Trading Championship wins).
- Transfers: YES, the whole validation pipeline.

Andreas Clenow
- Size positions by ATR so each position has the same daily dollar risk ("risk parity by ATR"); e.g. shares = risk_budget / ATR. Returns come from diversification across many markets, not from leverage. [R-bloggers: ATR position sizing](https://www.r-bloggers.com/2014/06/trend-vigor-part-iii-atr-position-sizing-annualized-sharpe-above-1-4-and-why-leverage-is-pointless/)
- Trend following has 30-40% win rate and makes its year in a few trades; daily/weekly timeframe only. [Meb Faber podcast with Clenow](https://mebfaber.libsyn.com/podcast/andreas-clenow)
- Evidence: backtested (Following the Trend, Stocks on the Move) plus fund track record.
- Transfers: PARTIAL. ATR sizing transfers (contracts = daily risk budget / (stop in points x point value)); trend-following timeframes do not.

Larry Connors
- Short-term mean reversion in index ETFs: buy pullbacks (RSI(2) < 10) above the 200-day MA, exit on a close above the 5-day MA or RSI(2) > 70. [Short Term Trading Strategies That Work (PDF)](https://thechartist.com.au/wp-content/uploads/2024/12/504/ShortTermTradingStrategiesThatWork.pdf)
- Stops hurt mean-reversion systems: across hundreds of tested strategies, adding stops "almost always lowered performance". Use time exits or opposite-signal exits instead. [Quantified Strategies on Connors and stops](https://quantifiedstrategies.substack.com/p/dont-use-a-stop-loss-do-this-instead)
- Buying after up-days underperforms buying after down-days in indices (short-term mean reversion dominates on daily index bars).
- Evidence: backtested (daily, 1990s-2000s), partly decayed; the "stops hurt MR" finding is widely replicated.
- Transfers: PARTIAL. Conflicts with a prop daily-loss limit (you cannot run stop-less MR), but the lesson applies: on range-day fades, use wide stops plus time exits rather than tight stops.

---

## The links

### What they agree on (recurring principles)
1. Edge first, then size. Thorp, Simons, Chan, Carver, Tharp, Douglas: no sizing scheme fixes a negative or unknown expectancy.
2. Think in large samples. Simons (50.75%), Douglas (20+ trades), Tharp (R-distribution), Lopez de Prado (DSR, min track length): one day or one trade is noise.
3. Fractional Kelly / constant fractional risk. Thorp, Chan, Carver, Tharp, Schwager, Clenow all converge on roughly half-Kelly or ~1% per trade.
4. Volatility-scaled sizing. Carver, Clenow, Tharp (R), Lopez de Prado (triple barrier in vol units): stops and size in ATR, not points.
5. Costs decide short-term strategies. Simons, Carver (costs <= 1/3 of Sharpe), the ORB replication (edge = costs): the faster you trade the more cost dominates.
6. Overfitting is the default failure. Lopez de Prado, Aronson, Harvey-Liu, Davey, Kaufman, Carver: count every variant tried, haircut the Sharpe, demand parameter plateaus and out-of-sample.
7. Regime matters more than setup. Chan (MR vs momentum), Raschke (day types), Kaufman (ER), Grimes (trend vs range), Brooks (breakout mode 40-60%): the same pattern has different expectancy by regime.
8. Most patterns have no edge in isolation. Aronson (0 of 6,402), Grimes (random S/R), Brooks (most breakouts fail): a pattern needs context (trend, momentum, range contraction) to carry edge.
9. Contraction precedes expansion. Crabel (NR7/ID), Raschke, Kaufman (noise then trend), Brooks (tight range then breakout).
10. Pullback with momentum beats first breakout. Grimes, Brooks (second entries), Raschke (Holy Grail), Connors (buy the dip): entries after a confirmed impulse and a retrace have the best documented stats.
11. Predefine exits and never widen them. Schwager, Douglas, Tharp, Brooks ("exit after 4 trend bars against").
12. Process over outcome; evaluate rules on blocks, not days. Douglas, Schwager, Davey (incubation), Tharp (SQN).

### Where they contradict
- Stops: Connors and Chan say stops hurt mean-reversion; Schwager, Brooks, Tharp and every prop firm say always use them. Resolution: stop type depends on strategy type (momentum = tight stop, MR = wide stop plus time exit), and the prop daily limit is a portfolio-level stop, not a per-trade one.
- Breakouts: Crabel/Zarattini say trade the opening breakout; Brooks/Grimes say most breakouts fail. Resolution: unfiltered breakouts are ~50/50 before costs (the replication confirms), filters (NR7, strong trend bars, first 30 min) are where the edge lives.
- Discretion: Grimes says he has never seen a fully mechanical trader succeed; Simons, Carver, Davey, Aronson say only mechanical rules are testable. Resolution: mechanise the setup and let "discretion" be explicit regime filters.
- Probabilities: Brooks states 60% for strong breakouts; a member's backtest found 50-52%. Treat Brooks numbers as priors to test, not facts.
- Win rate: Simons (50.75%, many trades) vs Clenow (30-40%, few big trades) vs Connors (70%+ MR). All are valid; the win rate must match the payoff ratio (trader's equation).

### Ranked principles for "most trading days green" on MNQ/MES
1. Size each trade at a fixed fraction well below Kelly, in ATR units: green-day frequency is driven by small, uniform R losses, not by win rate (Thorp, Carver, Tharp).
2. Trade only when a regime filter says the setup's expectancy is positive: the same ORB or pullback flips sign between trend and range days (Chan, Raschke, Kaufman).
3. Prefer second-entry/pullback-with-momentum over first breakouts: this is the one setup family both quants (Grimes) and price-action authors (Brooks) report an edge for.
4. Model costs before anything else: at 1-2 MNQ ticks of slippage the ORB edge is zero; every candidate rule must clear round-trip cost by a margin (Carver's 1/3 rule).
5. Validate with CPCV/walk-forward and deflate the Sharpe by the number of variants tried; otherwise the "green days" in the backtest are selection bias (Lopez de Prado, Aronson, Harvey-Liu).
6. Hard daily stop plus trade-count cap: Schwager's wizards and Douglas both describe stopping after a loss cluster; it converts a fat left tail into a bounded one, which is the whole prop-firm game.
7. Evaluate in blocks of 20-50 trades or weekly, never daily: a true 55%/1:1 edge still has ~30% red days; daily tinkering destroys the edge (Douglas, Tharp, Davey).
8. Exploit contraction: NR7/inside-day and tight pre-open ranges are the best-documented day-selection filters for breakout days (Crabel, Raschke).
9. Keep few parameters and require plateaus: robustness across neighbouring values beats peak performance (Kaufman, Carver, Davey).
10. Diversify across 2-4 uncorrelated intraday rules (e.g. ORB on NR7 days, pullback in trend, range fade) so the day's result is an average, not one bet (Carver, Simons).

---

## Numerically testable rules on our Databento 1m/5m MNQ+MES data

Regime and day types
- Classify each session by: open-to-close range / 20-day ADR, close location in range, number of first-hour range breaks that held. Measure the trend-day share (expect 20-30%) and whether NR7/ID/NR4 the prior day raises it (Crabel, Raschke).
- Compute Kaufman ER on 5m closes over 20, 40, 60 bars at 10:00, 10:30, 11:00 ET; test whether ER > 0.3-0.4 at 10:30 predicts a trend day and whether ER < 0.2 predicts a range day.
- Compute Hurst exponent / variance ratio on 1m returns per session; test H > 0.55 vs H < 0.45 as trend/range labels (Chan).
- Test whether the 11:00-13:00 CT window has lower absolute 5m returns and lower follow-through than other windows (Brooks).

Breakouts and ORB
- 5m ORB (Zarattini rules: stop at candle extreme, target 1R, 2R, 10R variants, flat at close) on MNQ and MES 2019-2026, with 0, 1, 2, 3 ticks of slippage per side. Report expectancy in R, hit rate, and the slippage level at which expectancy hits zero.
- Same ORB filtered by prior-day NR7, NR4, ID, and by first-5m range < 20th percentile of the last 20 sessions. Does the filter lift expectancy above costs?
- Crabel stretch ORB: entry at open +/- 10-day mean of min(H-O, O-L); test 1x and 2x stretch, time exit after N bars, trend-day-only exit at close.
- Breakout failure rate: for every 5m breakout of a 20-bar range, measure the fraction that reverses back inside within 1, 3, 5 bars. Compare with Brooks' 50% (long range) and 80% (general).
- Measured-move hit rate: for breakouts with 2+ consecutive 5m trend bars (close in top/bottom 25%, body > 60% of range), test the fraction that reaches a target equal to the breakout height before returning to the breakout point. Compare with Brooks' 60% vs the member's 50-52%.
- Entry time effect: ORB expectancy by entry time bucket (9:30-9:45, 9:45-10:00, 10:00-10:30, later). Crabel claims earlier is better.

Pullbacks and second entries
- High 2 / Low 2 second entries in a 5m trend (defined by 20 EMA slope and ER > 0.3): win rate and R at 1:1 and 2:1 targets vs first-entry (High 1 / Low 1). Brooks claims second entries are better.
- Grimes pullback: entry when 3/10 oscillator made a new high in the last 20 bars and price retraces to the 20 EMA or a 38-62% retrace; stop below pullback low; target 2R. Compare to random-entry baseline with the same stop/target.
- Trend-health filter: skip pullback entries when the pullback size exceeds 50% of the prior impulse or when its duration exceeds the impulse duration (Grimes). Does the filter raise expectancy?
- Higher-timeframe alignment: pullback trades on 5m with 30m/60m trend in the same direction vs opposed. Grimes says the failure rate rises "significantly" when opposed; measure it.

Fades and ranges
- Range-day fade: when ER < 0.2 after 10:30 and the first-hour range is at least 0.6x of 20-day ADR, fade touches of the first-hour high/low with a wide stop (1.5x 5m ATR) and a time exit of 12 bars. Compare tight stop vs wide stop plus time exit (Connors claim).
- Failed-breakout reversal (Turtle Soup / Wyckoff spring): after a 5m close beyond the first-hour range that returns inside within 2 bars, enter toward the range middle. Hit rate and R.

Sizing, exits, and daily structure
- Vol-scaled sizing: contracts = daily risk budget / (stop in points x point value), stop = k x 5m ATR(14); compare green-day frequency and max drawdown for k = 1, 1.5, 2 and risk = 0.25%, 0.5%, 1% of a $50K account (Carver, Clenow, Tharp).
- Triple-barrier labeling of every candidate entry (PT, SL, time) to build the R-distribution; compute expectancy, SQN (N = 100), and the fraction of days green as a function of trades per day.
- Daily-stop rules: stop after 2 losses, after -1.5R, after -2R, after first winner; stop at 11:30 ET; measure green-day share, expectancy per day, and drawdown for each (Schwager, Douglas, prop constraint).
- Trade-count cap: 1, 2, 3, unlimited trades per day; measure daily expectancy and variance.
- Win-rate/payoff pairing: for each setup, compute the probability needed by the trader's equation at 1:1 and 1:2 and compare to measured hit rate (Brooks).

Validation
- Count every rule/parameter variant tested; compute the Deflated Sharpe Ratio and PBO via CSCV (16 blocks) for the final candidates (Lopez de Prado).
- Walk-forward: optimise on 12 months, test on 3, roll; require walk-forward efficiency >= 50% and expectancy above 2x cost in every test window (Davey).
- Permutation test: shuffle intraday bar order within sessions and re-run the rule 1,000 times; the real result must sit above the 95th percentile of the shuffled distribution (Aronson).
- Parameter plateau: report expectancy over a grid around each chosen parameter (e.g. ATR multiple 0.75-2.0, ER threshold 0.2-0.5); reject rules whose performance collapses one step away (Kaufman, Carver).
- Cost sensitivity curve: expectancy vs slippage 0-4 ticks for each rule; keep only rules positive at 2 ticks per side on MNQ (Carver's cost rule, ORB replication).
- Monte Carlo resampling of the daily PnL series (10,000 paths): probability of hitting the prop daily limit and the trailing drawdown within 30, 60, 90 days (Davey, Tharp).
- Meta-labeling: train a simple classifier (session ER, NR7 flag, time of day, first-hour range ratio, 30m trend alignment) to predict whether a primary signal's trade will be a win; test whether filtering by predicted probability > 0.55 lifts expectancy out of sample (Lopez de Prado).
