# MNQ/NQ outside 9:30-11:30 ET: research and testable rules (Oct 25, 2026)

Scope: how NQ/MNQ behaves in five off-hours windows, what is documented versus popular, and mechanical rules to backtest on 5-minute ETH bars.

## Conventions for every rule below
- **Times:** America/New_York. Asia/Europe opens shift by 1 hour against ET around DST changes (Tokyo 9:00 JST = 20:00 EDT / 19:00 EST; Hong Kong 9:30 HKT = 21:30 EDT / 20:30 EST; London 8:00 UK and Xetra 9:00 CET = 03:00 ET except in the 2-3 mismatch weeks each spring and fall). Code the opens in local exchange time and convert, do not hard-code ET.
- **ADR:** mean of the last 14 completed ETH day ranges (18:00 to 17:00). All stops/targets in ADR fractions so rules survive regime changes.
- **Bars:** 5m ETH. "Close back inside" means a 5m bar close. Entries at next bar open unless a limit is stated.
- **Costs:** 1 tick slippage per side plus commission. Several documented edges below are smaller than the spread on a per-trade basis, so costs are decisive.
- **Baselines:** for every "probability of level X hit" claim, compare against a random-time or mirrored-level baseline. Our Sunday study showed gap "fill" rates below a fake level at the same distance, which is the trap here.
- **Split:** test 2022-2024 vs 2025-2026 at minimum. Several A-grade effects (overnight drift, pre-FOMC drift) decayed after publication.

## Grading
- **A:** peer-reviewed or central-bank research, or a large, reproducible quant sample.
- **B:** experienced practitioner or data vendor with specific numbers and a stated sample.
- **C:** anecdotal, untested, or numbers without method.

---

## Window 1: Sunday 18:00 reopen (first 2 hours)

### (a) Behavior
- **Our own data (A for us, 247 Sundays, 2022-2026, MNQ 5m):**
  - Median gap 18 pts (7% ADR).
  - Gaps do not fill more than chance: 26% fill by 20:00 for 10-20% ADR gaps, versus 63% for a fake level at the same distance.
  - The first 2 hours continue in the gap direction 59% of the time, and 18:00-20:00 range is 29% ADR versus 17% on weekday evenings.
  - Sunday direction predicts Monday RTH at 52%, a coin flip.
- **Janse van Rensburg & Van Zyl (2025), via Harbourfront Quant:** no predictable fill-the-gap bias for small and medium weekend gaps in NASDAQ-100/DJIA/DAX. Larger gaps raise both TP and SL hit rates (more volatility, not more direction). Grade A-/B, summary only.
- **Practitioner claims (C):** the first print often overshoots and partly retraces before Monday (TradingSim), but no numbers. "Gaps always fill" is popular and contradicted by the data above.

### (b) Candidate setups
1. **W1-S1 Sunday Gap Pullback (already found, PF 1.95, 64 trades).**
   - Gap = 18:00 open minus Friday 16:59 close. Require |gap| >= 0.05 ADR.
   - Limit entry in the gap direction at Friday close + 0.5 x gap; must fill by 19:30.
   - Stop 0.15 ADR. Exit 20:00 (or 2R).
   - To-do: forward test only. Neighbourhood already checked.
2. **W1-S2 Gap failure continuation.**
   - If price retraces >= 75% of the gap before 19:30, enter toward Friday close at the 75% level (stop order).
   - Target: Friday close + 0.05 ADR beyond. Stop 0.12 ADR. Time exit 20:00.
   - Rationale: our data says a 3/4 retrace means the gap is failing. Untested as an entry.
3. **W1-S3 Sunday range sweep on Monday.**
   - Mark the 18:00-20:00 Sunday high and low.
   - Monday 02:00-10:30: if a 5m bar trades beyond one extreme by >= 0.03 ADR and the next 1-3 bars close back inside, fade toward the Sunday range midpoint.
   - Stop: sweep extreme + 0.03 ADR. Target: midpoint, then the far extreme. Time exit 11:30.
   - Grade C idea (ICT-style "weekly opening range"); test against the same rule on a random 2-hour range.
4. **W1-S4 First-60-minute breakout with gap filter.**
   - Range 18:00-19:00. Trade only the break in the gap direction, 19:00-21:00.
   - Stop: opposite side of range or 0.12 ADR, whichever is smaller. Exit 21:00.
   - Our generic first-range breakout had median PF 1.01, so this needs the gap filter to add something. Low prior.

### (c) Sources
| Source | URL | Grade |
|---|---|---|
| Internal Sunday study | knowledge/SUNDAY_OPEN_2026-10-25.md | A (ours) |
| Harbourfront Quant on Janse van Rensburg & Van Zyl 2025 weekend gaps | https://harbourfrontquant.substack.com/p/are-weekend-gaps-always-filled-a | A-/B |
| TradingSim, Nasdaq weekend futures | https://www.tradingsim.com/blog/nasdaq-weekend-futures | C |
| TradingView "Gap Fill Probability Statistics ES/NQ" (protected source) | https://it.tradingview.com/script/32pGGSWx-Gap-Fill-Probability-Statistics-ES-NQ | C (method hidden) |

---

## Window 2: Evening/Asia 18:00-24:00 (Tokyo and HK opens)

### (a) Behavior
- **Low range:** weekday 18:00-20:00 range is about 17% ADR (ours). Edgeful's 19:00-04:00 NQ "overnight/Asian" range exceeded its own ATR only 11.8% of days in a 6-month sample (B).
- **Closing imbalance reversal (A):** Boyarchenko, Larsen & Whelan (NY Fed SR917). A 1-sd sell-side imbalance at 15:15-16:15 predicts about +1.15 bp in the 2:00-3:00 hour. The reversal is much stronger after sell-offs than rallies, and stronger with high VIX. This is mainly a London-hour effect (Window 3), but the trade is set up in this window.
- **Tokyo open:** CXO's summary of the paper says dealers have increasingly corrected imbalances at the Tokyo open, and that activity shifts by an hour with US DST. No magnitude given (A- mechanism, no number).
- **Night long bias:** about 52.5% up for ES night session over 10 years (NexusFi forum, C). Edgeful ES Jun-Dec 2024: red overnight was followed by a green RTH day 62% of the time (B, short sample).
- **HK/China open:** no quantitative source found for NQ. Treat any "21:30 fade" claim as C.

### (b) Candidate setups
1. **W2-A1 Sell-off evening long (closing imbalance proxy).**
   - Proxy for sell imbalance: 15:00-16:00 RTH return <= -0.15 ADR AND the RTH day return < 0.
   - Long at 18:05 open. Stop 0.30 ADR. Exit 03:30.
   - Variant A1b: enter 01:30 instead of 18:05 (the NY Fed "buy-the-dip 1:30-3:30" form).
   - Variant A1c: require ADR in the top tercile of the last 250 days (VIX proxy).
2. **W2-A2 Tokyo-open range fade.**
   - T = Tokyo open in ET. Range = 18:00 to T.
   - From T to T+120 min: if a 5m bar closes back inside after trading >= 0.03 ADR beyond the range, fade.
   - Target: range midpoint. Stop: extreme + 0.03 ADR. Time exit T+180 min.
   - Low-volatility session favors fades over breakouts. Grade C idea.
3. **W2-A3 Tokyo-open breakout (control for A2).**
   - Same range. Enter on a 5m close beyond the range, T to T+90.
   - Stop: range midpoint. Target 1.5x range height. Time exit 02:00.
   - Run with A2 to see which side of the coin the session sits on.
4. **W2-A4 Evening VWAP reversion.**
   - Anchor VWAP at 18:00. From 19:00 to 23:30, if price is >= 0.10 ADR from VWAP and a 5m bar closes back toward VWAP, enter toward VWAP.
   - Target VWAP. Stop: session extreme + 0.03 ADR. Time exit 00:00.
5. **W2-A5 HK open first-30 fade.**
   - H = HK open in ET. If the H to H+30 move is >= 0.06 ADR, fade at H+30.
   - Target: price at H. Stop 0.06 ADR beyond H+30 extreme. Exit H+120.
   - No evidence either way (C). Include only because it is cheap to test.

### (c) Sources
| Source | URL | Grade |
|---|---|---|
| Boyarchenko, Larsen, Whelan, "The Overnight Drift," NY Fed SR917 | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | A |
| CXO Advisory summary of the overnight drift (Tokyo-open note) | https://www.cxoadvisory.com/?p=33743 | A- |
| NexusFi intraday seasonality (forum stats) | https://nexusfi.com/a/strategies/intraday-seasonality-futures-trading | C |
| Edgeful, NQ futures data guide (session ATR) | https://www.edgeful.com/blog/posts/nq-futures-trading | B |
| Edgeful, overnight continuation (ES) | https://www.edgeful.com/blog/posts/overnight-continuation-trading-strategy | B (6 months) |
| NinjaTrader, Asia session hours | https://ninjatrader.com/futures/blogs/asia-session-futures-trading-hours | C (hours only) |

---

## Window 3: London 02:00-05:00 and Europe/pre-market 05:00-09:30 (incl. 8:30 data)

### (a) Behavior
- **Overnight drift (A, now decayed).**
  - ES 1998-2020: the 2:00-3:00 hour earned about 3.7%/yr, t = 7.1, positive in 20 of 23 years, and was the only hour significant after multiple-testing correction.
  - Long 2:00-3:00 had a Sharpe of 1.1 gross but -0.5 after spreads. Long 1:30-3:30 conditioned on a negative close had a Sharpe of 1.1 after costs (2004-2020).
  - **NY Fed, July 2026:** the 2-3 a.m. window has averaged near zero since 2021 in ES, NQ, and YM. The authors attribute this to smaller end-of-day imbalance dispersion (sd of closing RSV fell from 6.5% to 2.9%). They expect it to return if imbalance dispersion widens. So: test conditioned on big closing moves only.
- **US open drag (A-):** CXO reports negative average returns around 8:30-10:00 ET in the same paper, largest Thursday/Friday.
- **Asia/London patterns (B, nqstats.com via TradingView indicators, NQ about 10 years, n about 2,542):**
  - London breaks only the Asia high 41% of days. The NY session then breaks the London high 80.8% of the time.
  - London breaks only the Asia low 30.2%. NY then breaks the London low 75%.
  - When NY 8:00 opens above the London midpoint, the London high is hit before the London low 76.7% of the time (mirror 73.3%).
  - Skeptic note: price above the midpoint is already closer to the high, so a big part of 76.7% is geometry. Needs a baseline (same test on a random 6-hour window).
- **ICT windows:** Silver Bullet 03:00-04:00 and Judas swing off the 00:00 open have concrete-ish rules but no published stats (LuxAlgo says so outright). A YouTube study (video KML09tRtHM8, 25,000 configurations, 16 years of NQ/ES 1m) found the special hours performed no better than other hours, and only the "sweep before entry" rule consistently added edge. Only about 1.7% of configurations survived its full robustness funnel (B).
- **8:30 data (A for us):** our MNQ test 2022-2026: CPI/PPI/NFP reversion toward the 8:29 price after displacement, PF about 1.5, positive every year, about 13 trades a year. Other 8:30 releases lose. Fading unexpected spikes is break-even. Pre-FOMC drift (the day before through 2pm) disappeared after 2015 (Kurov, Wolfe, Gilbert), so do not build on it.

### (b) Candidate setups
1. **W3-L1 Conditional overnight drift.**
   - Condition: 15:00-16:00 return <= -0.15 ADR (sell-imbalance proxy). Optionally, ADR in the top tercile.
   - Long at 01:30. Stop 0.20 ADR. Exit 03:30.
   - Report 2021+ separately. Expect weak results unless the closing sell-off was large.
2. **W3-L2 Asia range London sweep-and-reclaim.**
   - Asia range = 20:00-02:00 high/low (nqstats definition).
   - Between 02:00 and 05:00: if a bar trades >= 0.02 ADR beyond the Asia high, and within 3 bars a bar closes back inside the range, short at that close. Mirror for the low.
   - Stop: sweep extreme + 0.02 ADR. T1 Asia midpoint (half off), T2 the opposite Asia extreme. Time exit 08:00.
   - Only one trade per night (the first sweep).
3. **W3-L3 London pattern continuation into NY.**
   - At 08:00 classify: London = 02:00-08:00. Only "London Partial Up" (broke Asia high, not low) with the 08:00 price above the London midpoint.
   - Long at 08:05 open. Target London high + 1 tick. Stop at entry minus (London high minus entry), so 1:1. Time exit 11:00. Mirror for "Partial Down."
   - Skip if the target is < 0.04 ADR away (no room) or > 0.25 ADR (too far for a 1:1 stop).
   - The baseline test (random 6h range) decides whether this is real or geometry.
4. **W3-L4 Silver Bullet 03:00-04:00 with mandatory sweep.**
   - Precondition: between 02:00 and 04:00, price sweeps the Asia high or low (trades beyond it).
   - Inside 03:00-04:00, a 3-bar fair value gap forms against the sweep (for a long after a low sweep: bar3 low > bar1 high).
   - Limit at the FVG edge nearest price. Stop: sweep extreme + 1 tick. Target 2R. Time exit 05:00.
   - Note: the 16-year test found the 1m version beat the 5m version, so 5m results are a lower bound.
5. **W3-L5 8:30 news reversion (existing NEWS module).**
   - CPI/PPI/NFP only. Enter toward the 8:29 price after a displacement or break of structure, 8:30-9:30, 50/50 bracket.
   - Already PF about 1.5. Keep and forward test; do not re-optimize.

### (c) Sources
| Source | URL | Grade |
|---|---|---|
| NY Fed SR917, The Overnight Drift | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | A |
| Liberty Street Economics, "The Disappearing Overnight Drift" (Jul 2026, ES/NQ/YM) | https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/ | A |
| CXO summary (US open drag, tradability) | https://www.cxoadvisory.com/?p=33743 | A- |
| Kurov, Wolfe, Gilbert, The Disappearing Pre-FOMC Announcement Drift | https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf | A |
| NQ Statistical Mapper (nqstats data, 2013-2025, 3,132 days) | https://ar.tradingview.com/script/OxnWYkkY-NQ-Statistical-Mapper | B |
| ALN Sessions NQ 8am Prediction Model (nqstats, n=2,542) | https://in.tradingview.com/script/URlpwdDy-ALN-Sessions-NQ-8am-Prediction-Model-v3/ | B |
| ALN Sessions NQ Stats x CantoLab | https://in.tradingview.com/script/KNTFWlm2-ALN-Sessions-NQ-Stats-x-CantoLab/ | B/C |
| LuxAlgo, Silver Bullet concept (states no audited stats) | https://www.luxalgo.com/library/concept/silver-bullet/ | C |
| LuxAlgo, Judas Swing concept | https://www.luxalgo.com/library/concept/judas-swing/ | C |
| YouTube "I backtested 25,000 ICT Silver Bullet trades" (video KML09tRtHM8), summary page | https://www.youtube.com/watch?v=KML09tRtHM8 ; https://gist.ly/youtube-summarizer/i-backtested-25000-ict-silver-bullet-trades | B |
| YouTube "ICT Silver Bullet Strategy - No Daily Bias, With Backtest" (likely TTrades, 15 trades on FX Replay) | https://videohighlight.com/v/o0v4KQxZbpU | C |
| Internal 8:30 tests | knowledge/NEWS_TRADING_JJ_SIMON_AND_TESTS.md | A (ours) |

---

## Window 4: Midday 11:30-14:00 and afternoon/close 14:00-16:00

### (a) Behavior
- **Lunch:** ES lunch (11:30-13:30) range is about 10% of the daily range on about 11% of volume. The day's high or low forms there only 12-14% of the time (NexusFi forum compilation, C). The same page warns NQ trends through lunch more than ES.
- **Lunch effect (B):** Quantpedia, SPY 2010-2024: short 11:00-12:00, long 12:00-14:00. Only the long leg is recommended for long-only traders. Numbers are in images not reproduced; the direction was robust in their test.
- **Afternoon trend (A):** Zarattini, Aziz, Barbon (SPY 2007-2024): trend continuation pauses at lunch and "resume[s] strongly from 14:00 until market close." Noise-area strategy with VWAP trailing stop: Sharpe 1.24 net, max DD 12%, 43% hit rate.
- **Last half-hour momentum (A):**
  - Gao, Han, Li, Zhou (SPY 1999-2012): the first half-hour return (prior close to 10:00) predicts the last half-hour. R2 about 1.6-2.7%, 6.3%/yr gross for long-or-flat timing. QQQ was weaker. Costs likely eat most of it per CXO.
  - Baltussen, Da, Lammers, Martens (JFE 2021): the rest-of-day return (prior close to 15:30) predicts the last 30 minutes across more than 60 futures, 1974-2020, Sharpe 0.87-1.73 by asset class. **Momentum is concentrated on negative dealer gamma days and absent on positive gamma days.** Effect partly reverses over the next few days.
  - Li, Sakkas, Urquhart (JFM 2022): replicated in 12 of 16 developed markets, 2005-2017, gross.
- **Power hour NQ (B):** in the last 6 months, 15:00-16:00 made a new high of day 21% and a new low 13% (Edgeful).
- **MOC imbalance:** Nasdaq research says imbalance news moves individual Nasdaq-100 stocks about 5.5 bp, 80% within 300 ms. No study found on the 15:50 imbalance and NQ futures direction. Retail "MOC edge" posts have no results (Siram Capital, C). The end-of-day reversal is a single-stock cross-sectional effect, not an index effect.
- **Skeptic flag:** the Edgeful "green at 15 min and noon, closes green 87%" stat is mostly mechanical, because the noon return is part of the close return. It is not a tradable edge on its own.

### (b) Candidate setups
1. **W4-M1 Last-half-hour momentum (Baltussen form).**
   - At 15:30 compute R = close(15:30) / close(prior day 16:00) - 1.
   - If |R| >= 0.15 ADR, enter in the sign of R at 15:30. Exit 15:59 close (before the 16:00 settlement wick). Stop 0.12 ADR.
   - Variant M1b (Gao form): require sign(09:30-10:00 return) = sign(15:00-15:30 return).
   - Variant M1c (gamma proxy): only when the day's range is already >= 1.0 ADR (proxy for a negative-gamma, trending day). Real GEX data is better if available.
2. **W4-M2 Afternoon noise-area trend (Zarattini, 14:00-16:00 only).**
   - For each 30-min slot, sigma = average |close(slot) / open(09:30) - 1| over the prior 14 days.
   - Upper = max(open 09:30, prior close) x (1 + sigma). Lower = min(open, prior close) x (1 - sigma).
   - Check at 14:00, 14:30, 15:00, 15:30. Long if close > upper, short if close < lower.
   - Trailing stop: long stop = max(upper, RTH VWAP), short stop mirrored, checked on 5m closes. Exit 15:59.
3. **W4-M3 Post-lunch long.**
   - Long 12:00 open, exit 14:00 close. Stop 0.20 ADR.
   - Variant M3b: only if 11:00-12:00 return < 0. Variant M3c: add the 11:00 short leg.
4. **W4-M4 Lunch VWAP fade (with trend guard).**
   - 11:30-13:30. If price is >= 0.12 ADR from RTH VWAP and a 5m bar closes back toward VWAP, fade toward VWAP.
   - Target VWAP. Stop: extreme + 0.04 ADR. Exit 13:45.
   - Skip if the morning (09:30-11:30) range is >= 0.8 ADR (a trend day, where NQ trends through lunch).
5. **W4-M5 15:50 imbalance follow.**
   - Signal: the 15:45-15:50 5m bar return (a proxy, since real MOC prints are not in our data).
   - If it is >= 0.04 ADR in size, enter in its direction at 15:50. Exit 15:59.
   - Grade C. Run only as a cheap check; do not trade without real imbalance data.

### (c) Sources
| Source | URL | Grade |
|---|---|---|
| Gao, Han, Li, Zhou, Market Intraday Momentum (Alpha Architect summary) | https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/ | A |
| CXO, first and last half-hours linked (costs, QQQ weaker) | https://cxoadvisory.com/calendar-effects/first-and-last-half-hours-of-trading-linked | A- |
| Baltussen, Da, Lammers, Martens, Hedging Demand and Market Intraday Momentum (JFE 2021) | https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/ ; https://alphaarchitect.com/hot-topic-does-gamma-hedging-actually-affect-stock-prices/ | A |
| Li, Sakkas, Urquhart, Intraday Time Series Momentum: International Evidence | https://reading-9.eprints-hosting.org/95566/1/Accepted-Version.pdf | A |
| Zarattini, Aziz, Barbon, Beat the Market (SPY intraday momentum) | https://alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/content | A |
| Quantpedia, Lunch Effect in US indices | https://quantpedia.com/lunch-effect-in-the-u-s-stock-market-indices | B |
| NexusFi, intraday seasonality | https://nexusfi.com/a/strategies/intraday-seasonality-futures-trading | C |
| Edgeful NQ guide (power hour) | https://www.edgeful.com/blog/posts/nq-futures-trading | B |
| Edgeful, first 15 min continuation (mechanical-stat caveat) | https://www.edgeful.com/blog/posts/opening-candle-continuation-15-minutes | C |
| Nasdaq, How much does the MOC imbalance matter | https://www.nasdaq.com/articles/how-much-does-the-moc-imbalance-matter-2019-09-27 | A (stocks only) |
| Alpha Architect, end-of-day reversal (stocks) | https://alphaarchitect.com/end-of-trading/ | A (stocks only) |
| Siram Capital, MOC imbalance edge part 1 (no results) | https://siramcapitalresearch.substack.com/p/moc-imbalance-is-there-an-edge-part | C |

---

## Window 5: 16:00-17:00 post-close and post-earnings

### (a) Behavior
- Liquidity drops sharply after 16:00 (16:00-16:15 still has some cash-index hedging). The 17:00-18:00 halt forces flat or overnight risk.
- **Mega-cap earnings** (NVDA, MSFT, AAPL, AMZN, GOOGL, META, AVGO, TSLA) print about 16:00-16:10 and move NQ directly. News coverage exists, but **no systematic study of NQ continuation or reversal after these prints was found.** Treat all claims as C.
- **Partial reversal (A, stocks):** intraday momentum partly reverts over the next days (Baltussen). Closing sell imbalances reverse overnight (SR917). Neither paper measures 16:00-17:00 specifically.
- **Our spike data:** fading unscheduled spikes was break-even (PF 0.76-1.23), and following them lost (PF 0.35-0.94). Prior for earnings spikes: no edge unless a filter adds one.

### (b) Candidate setups
1. **W5-P1 Earnings-night range break.**
   - Only on mega-cap earnings days (calendar list above). Range = 16:00-16:15.
   - Enter on a 5m close beyond the range, 16:15-16:40. Stop: range midpoint. Target 1.5x range. Exit 16:55.
2. **W5-P2 Earnings-night overreaction fade.**
   - Same days. If the 16:00-16:15 move is >= 0.25 ADR, fade at 16:15 close.
   - Target: 50% retrace toward the 16:00 price. Stop: 16:00-16:15 extreme + 0.05 ADR. Exit 16:55.
   - Run P1 and P2 together; they are opposite hypotheses on the same event.
3. **W5-P3 Big-day post-close drift.**
   - If the RTH return is >= +0.6 ADR (or <= -0.6), fade at 16:15 open with a 0.10 ADR stop, exiting 16:55.
   - Variant: hold to 03:30 for the down-day case only (links to W2-A1). Grade C.

### (c) Sources
| Source | URL | Grade |
|---|---|---|
| Baltussen et al. (next-day reversal of intraday momentum) | https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/ | A (indirect) |
| NY Fed SR917 (closing imbalance reversal) | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf | A (indirect) |
| Newsquawk, NQ after NVDA earnings (example only) | https://www.newsquawk.com/headlines/market-update-es-and-nq-futures-tick-higher-and-nvidia-extends-on-gains-pre-market-now-69-vs-5-post-earnings-yesterday | C |
| Internal spike tests | knowledge/NEWS_TRADING_JJ_SIMON_AND_TESTS.md | A (ours) |

---

## What is documented versus popular
- **Documented (A):** the overnight drift at 2-3 a.m. (now near zero since 2021, NQ included); closing sell-off leading to an overnight rebound; last-half-hour momentum, stronger on negative-gamma days; the afternoon (14:00+) trend leg; no weekend gap-fill bias; the pre-FOMC drift gone after 2015.
- **Practitioner stats with samples (B):** nqstats Asia/London patterns (large n, but geometric bias); the 16-year Silver Bullet sweep (only "sweep first" added edge); Quantpedia lunch effect; Edgeful session ATR/power hour.
- **Popular but untested (C):** Silver Bullet and Judas swing as named; "gaps always fill"; HK-open fades; MOC 15:50 direction trades; post-earnings rules; most YouTube P&L claims. The "Live Day Trading Losing $95,250" type videos show London-level sweeps but have no backtest.

## Ranked shortlist: 8 most testable ideas
| Rank | ID | Idea | Why it ranks here |
|---|---|---|---|
| 1 | W4-M1 | Last-half-hour momentum: at 15:30, trade the sign of the prior-close-to-15:30 return if >= 0.15 ADR, exit 15:59 | A-grade in 60+ futures; one trade a day; trivial to code; gamma proxy variant |
| 2 | W4-M2 | Afternoon noise-area trend 14:00-16:00 with VWAP trailing stop | A-grade, net Sharpe 1.24 on SPY; the 14:00+ leg is where they found most of the trend |
| 3 | W1-S1 | Sunday Gap Pullback (half-gap limit, 0.15 ADR stop, exit 20:00) | Already PF 1.95 in our data; needs forward test, not more research |
| 4 | W3-L3 | London Partial Up/Down continuation 08:05-11:00 to the London extreme, 1:1 | Large-n B-grade stats; one clear test against a random-window baseline settles it |
| 5 | W3-L2 | Asia range sweep-and-reclaim 02:00-05:00, target Asia midpoint then far side | Concrete ICT-style rule; the 16-year test found "sweep first" was the only edge that held |
| 6 | W2-A1 / W3-L1 | Sell-off evening/overnight long (15:00-16:00 <= -0.15 ADR, long 18:05 or 01:30, exit 03:30) | A-grade mechanism, but unconditional version decayed since 2021; test 2021+ separately |
| 7 | W4-M3 | Post-lunch long 12:00-14:00 (plus "11:00-12:00 down" filter) | B-grade, 14 years SPY, one trade a day, long-only friendly |
| 8 | W5-P1/P2 | Mega-cap earnings night: 16:00-16:15 range break versus fade, exit 16:55 | No evidence either way; small event set (about 30 nights a year) but clean A/B test |

Not ranked but already live: W3-L5 8:30 CPI/PPI/NFP reversion (PF about 1.5). Lowest priority: W4-M5 (15:50 imbalance proxy) and W2-A5 (HK fade), since there is no evidence and no real data for them.

## Blocked or unread sources
- The Baltussen et al. full PDF (academicweb.nd.edu/~zda/intramom.pdf) was blocked by the fetch provenance check. Its numbers above come from the Alpha Architect summary.
- nqstats.com primary tables were not fetched. Its figures come via TradingView indicator pages.
