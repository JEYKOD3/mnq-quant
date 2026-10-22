# Price Action in Practice: Rules With Numbers for an MNQ/MES Intraday Engine

Compiled 2026-10-21 from web sources. Scope: how practitioners in the Al Brooks / Thomas Wade / Grimes / Raschke lineage actually encode price action intraday, written as rules that can be coded, plus every measured number found.

Evidence tags:
- [DOC] measured: a backtest, sample, or published statistic with numbers.
- [DESC] described: a practitioner states the rule explicitly (book, course, forum, article) but gives no measurement.
- [FOLK] folklore: widely repeated, origin unclear or secondhand, no measurement.

Attribution caveat: most Brooks numbers online are student paraphrases of his course videos on brookstradingcourse.com forum threads. Treat those as [DESC] at best and verify against the books (Trading Price Action: Trends / Trading Ranges / Reversals, Wiley 2012; Reading Price Charts Bar by Bar, Wiley 2009).

Blocked during research: the TradingView "Price Action Brooks Pro" script page could not be fetched (permission not granted). Its numeric defaults are not included.

---

## 1. Trend identification

### EMA-based rules
- Brooks default: 20-bar EMA on the 5-minute chart. For scalping he drops to a 10-bar EMA. [DESC] [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/)
- Trend qualification used by NexusFi's Brooks write-up: 20 EMA "clearly sloped," price staying on one side of it; skip when the EMA is flat or recently crossed, or when bars overlap heavily with alternating closes. [DESC] [NexusFi: Two-Legged Pullback Trading](https://nexusfi.com/a/strategies/two-legged-pullback-trading)
- Pullback depth as a trend-strength proxy: in a strong trend, pullbacks are typically less than 50% of the prior impulse. [DESC] (same source)
- Raschke Holy Grail trend filter: 14-period ADX above 30 and rising. Note the original uses a 20-period EMA in Street Smarts; some restatements use a 20 SMA. [DESC] [Trading Setups Review: Holy Grail](https://tradingsetupsreview.com/the-holy-grail-trading-setup)
- Kaufman Efficiency Ratio: ER = |C_t - C_{t-n}| / sum of |C_i - C_{i-1}| over n bars; default n = 10. LuxAlgo explicitly refuses to give fixed cutoffs ("conventions to be tested, not constants") and recommends thresholds relative to the instrument's own recent ER distribution. The popular 0.3 trend / 0.2 chop cutoffs are [FOLK]. [DESC] [LuxAlgo: Kaufman Efficiency Ratio](https://www.luxalgo.com/library/concept/kaufman-efficiency-ratio/)

### Structural (swing) rules
- Brooks: a trend is defined by major higher lows (bull) or lower highs (bear). The always-in direction stays long until the relevant higher low breaks. [DESC] [Brooks forum: Always-in confusion](https://www.brookstradingcourse.com/support-forum/13-always-in/always-in-confusion-2/)
- Grimes rule of thumb: in an uptrend, upswings must be larger than downswings in both duration and magnitude. A retracement at least as large as the prior upswing means reduce exposure; the trend may be ending. [DESC] [Topstep: Going deep on Adam Grimes' approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)
- Grimes momentum filter: 3-10 oscillator (the Raschke modified MACD, 3 and 10 period SMAs of close, with a 16-period signal). Trade pullbacks only when the oscillator made a new high on the prior impulse; skip if the pullback itself prints a new oscillator low (momentum divergence against the trend). [DESC] (same source)
- NexusFi range vs trend heuristic: five or six consecutive same-color bars suggests a trend, not a range. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)

### Brooks' "always in"
- Definition: the direction you would have to be in if forced to hold a position right now. "The market is always either more likely bullish or more likely bearish." Brooks calls it a swing concept that applies to trends and is "dangerous within trading ranges." [DESC] [NexusFi: Signal Bars and Entry Bars](https://nexusfi.com/a/strategies/signal-bars-entry-bars-price-action), [Brooks forum: Always-in confusion](https://www.brookstradingcourse.com/support-forum/13-always-in/always-in-confusion-2/)
- Flip mechanics discussed by students: (a) a successful trading-range breakout with follow-through flips it; (b) in course video 13A, four bull bars are not enough, at least one more confirming bar is needed; (c) a short lookback (about 7 bars) vs a long one (about 20 bars) can give different always-in reads, which is the same as reading a lower vs higher timeframe. [DESC] (same forum thread)
- Book version, commonly encoded: a flip happens on a strong breakout, typically 2-3 consecutive trend bars with large bodies and closes near their extremes, closing beyond the prior swing. [FOLK] (student restatements of Trading Price Action: Trends)
- Mechanical "trend bar" implementation used by one open-source Brooks indicator: body at least 50% of range; bull close in top 40% of range (bear in bottom 40%); bar at least 50% larger than the average of the prior 3 bars. [DESC] [TradingView: Price Action Indicator](https://www.tradingview.com/script/hP0oDLG1-Price-Action-Indicator)

### Brooks probability framing (used to pick with-trend vs counter-trend)
- With-trend setups: at least 60% probability at 1:1 reward-to-risk. Most reversal setups: 40% or less at 1:1, so they need 2:1 potential to have a positive trader's equation. Stated by forum moderator Graeme Brindley summarizing the course. [DESC] [Brooks forum: Probability and risk/reward](https://www.brookstradingcourse.com/support-forum/general-trading-discussion/probability-and-riskreward/)
- Channels: a bull channel has roughly a 75% chance of an eventual bear breakout (course 14C slide 27). [DESC] [Brooks forum: 14C bull channel 75%](https://www.brookstradingcourse.com/support-forum/14-trends/14c-s27-bull-channel-75-chance-of-eventual-bear-bo/)

---

## 2. Pullback entries

### Brooks H1/H2/L1/L2 (exact definitions)
- H1: in a bull trend pullback (bars making lower highs), the first bar whose high exceeds the prior bar's high. H2: after the pullback continues lower again, the next bar whose high exceeds the prior bar's high. L1/L2 are the mirror on lows in a bear pullback. The count resets when the trend makes a new extreme. H3/L3 are wedge flags (three pushes); an H4/L4 means the pullback has lasted long enough to question the trend. [DESC] [LuxAlgo: Bar Counting H1/H2](https://www.luxalgo.com/library/concept/bar-counting-h1-h2/)
- Entry: buy stop 1 tick above the H2 signal bar high (sell stop 1 tick below the L2 signal bar low). Stop: below the H2 signal bar low or below the pullback low. [DESC] (same source)
- Brooks: H1 entries have lower probability than H2; the first attempt usually fails, so the second is the standard entry. A triggered H2/L2 that then trades through the signal bar's other end signals range or reversal. [DESC] (same source)
- In a strong trend (spike phase), Brooks takes H1/L1; in a channel or after a trend line break, he waits for H2/L2. In a trading range, H2/L2 become fades and are not trusted as with-trend entries. [FOLK] (student restatement of Trading Price Action: Trends)

### Two-legged pullbacks (NexusFi encoding of Brooks)
- Leg definition: directional momentum, a swing extreme that holds for at least 2-3 bars, a distinct bounce before the next leg. Bounce between legs in a strong trend: 2-4 bars with small bodies. Leg 2 should have smaller bars and shorter duration than Leg 1. [DESC] [NexusFi: Two-Legged Pullback Trading](https://nexusfi.com/a/strategies/two-legged-pullback-trading)
- Three entry styles: (A) limit near the Leg 2 zone (aggressive); (B) stop 1 tick beyond the H2/L2 signal bar (default); (C) late entry after a failed H1 once the second breakout succeeds. [DESC]
- Stop: beyond the Leg 2 extreme plus buffer: ES 1-2 ticks, NQ 2-4 ticks, CL 2-3 ticks. [DESC]
- Target: measured move D = C + (B - A) for longs; require entry-to-D at least 2x entry-to-stop, else find a closer entry or skip. [DESC]
- Checklist scoring: 5 criteria (trend confirmed, two legs counted with diminishing momentum, Leg 2 at a level such as 20 EMA / prior S-R / breakout zone, clear signal bar, 2:1 R:R). 5 pass = full size, 4 = half, 3 or fewer = skip. [DESC]

### Pullback to EMA
- Brooks scalp entry: after a bar closes near its low below the EMA, sell 1 tick below that bar's low, stop above the bar's high; mirror for longs. [DESC] [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/)
- Brooks' preferred second-entry version: a bar closing on its high at the moving average is higher probability than buying above the prior bar. [DESC] [Brooks: Breakout pullbacks, exit or hold](https://www.brookstradingcourse.com/?p=58515)
- Holy Grail (Raschke/Connors, Street Smarts 1995): 14 ADX > 30 and rising; price retraces to the 20 EMA; buy stop at the high of the bar that touched the EMA (sell stop at the low for shorts). The restatement cited gives no stop; the book places the stop under the swing low formed at the EMA and re-enters if stopped out while ADX still qualifies, taking profit at the prior swing high. No backtest numbers published. [DESC] [Trading Setups Review: Holy Grail](https://tradingsetupsreview.com/the-holy-grail-trading-setup)
- Grimes' own version: pullback to the 20 EMA inside Keltner channels; he uses a 20 EMA with bands at 2.25 ATR as his standard chart template. Entry on resumption; stop beyond the pullback extreme; first target at prior swing, second target at the opposite Keltner band. He reports no per-setup win rates in the book, only that pullbacks are the highest-probability trade class and that failure rates rise sharply when the higher timeframe trend opposes. [DESC] [Topstep: Grimes approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)
- A Capital.com article using the same template specifies Keltner middle = 20 EMA, bands = 2.5 ATR, and for a complex pullback: enter on a fakeout at the pullback extreme (break beyond support then close back inside), stop below the fakeout low, first target the pre-pullback swing, secondary target the Keltner band. [DESC] [Capital.com: Trading the complex pullback](https://capital.com/trading-the-complex-pullback)

### Pullback to VWAP (band-walk continuation)
- Band walk = three or more consecutive closes outside the +1 SD band without returning to VWAP. Long: VWAP sloping up, price pulls back to +1 SD and holds; enter at +1 SD or on the bounce; stop below +1 SD (or below VWAP for longer hold); target +2 SD or the prior high; exit when a bar closes back inside +1 SD. [DESC] [NexusFi: VWAP Standard Deviation Bands](https://nexusfi.com/a/indicators/vwap-standard-deviation-bands)

### First pullback after breakout
- NexusFi/Brooks: once a breakout holds above the prior range high for more than 5 bars, or prints two consecutive 5-minute closes above the prior range high, treat it as a trend. The first pullback that holds above the prior range high is "the lowest-risk trend entry." If price falls back into the range, the breakout failed, fade it. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)
- Brooks on holding through pullbacks: stay long while each pullback stays above the prior strong leg's low or the most recent breakout low; a break of that low invalidates the premise. [DESC] [Brooks: Breakout pullbacks](https://www.brookstradingcourse.com/?p=58515)

### Pullback stop/target conventions
- Brooks stop: 1 tick beyond the signal bar's opposite extreme. Keep it there even when the entry bar closes mid-range (do not tighten to the entry bar). [DESC] [NexusFi: Signal Bars and Entry Bars](https://nexusfi.com/a/strategies/signal-bars-entry-bars-price-action)
- Brooks targets: scalp = fixed target (he cites 2 points on ES; never scalp for under 1 point ES, 10 pips FX, 10 cents stocks). Swing = at least 2x initial risk, and reversal swings should run 20+ bars. [DESC] [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/), [dev.to: Brooks MTR supplement](https://dev.to/victorjia/price-action-major-trend-reversal-supplement-360f)
- Brooks "actual risk" rule: it is acceptable to take profit at 2x actual risk (distance from entry to the stop that would actually have been used, often much less than the initial stop). A student example: 5 points initial risk, 2 ticks actual risk, target 1 point, which needs about 83% winners to break even. [DESC] [Brooks forum: 2x actual risk](https://www.brookstradingcourse.com/support-forum/34-actual-risk/math-is-good-for-2x-actual-risk-profit/)

---

## 3. Breakouts and failed breakouts

### Breakout bar quality
- Strong breakout bar: large body, close near the extreme, small tail on the breakout side, exceeds the prior bar's extreme; follow-through bar should also close near its extreme and overlap the entry bar by no more than 50%. Two consecutive strong follow-through bars "materially raise the odds." [DESC] [NexusFi: Signal Bars and Entry Bars](https://nexusfi.com/a/strategies/signal-bars-entry-bars-price-action)
- Weak breakout = smaller bars, more overlap, or a strong opposite bar immediately after the breakout. Treat as a fade setup, not a continuation. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)

### Breakout pullback and breakout test
- Breakout pullback: after the breakout, a pullback that holds beyond the breakout level; enter on the first with-trend signal bar there (stop 1 tick beyond it). [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)
- Breakout test (Brooks): a later return to the breakout point that holds; "perfect" when it stops within about 2 ticks of the breakout price (student observation on course 33G) and the bulls' breakeven stop is not hit. The bodies of the test bars should not overlap the breakout area; a gap between them marks a measured-move reference. No official tick tolerance published. [DESC] [Brooks forum: 33G perfect breakout test](https://www.brookstradingcourse.com/support-forum/33-protective-stops/33g-what-constitutes-a-perfect-breakout-test/)
- Brooks scalp vs swing on breakouts: a breakout scalper "does not want the market to come back," exits fast; a swing trader "has to assume there'll be pullbacks." Brooks himself scales in on an acceptable pullback and exits on an unacceptable one. [DESC] [Brooks: Breakout pullbacks](https://www.brookstradingcourse.com/?p=58515)

### Failed breakouts / traps (Brooks lineage)
- Require at least 5 bars of range structure before the breakout; do not chase. Wait for the stall, then short when price drops back below resistance or below the high of the last bar still above it. Stop above the breakout high. Target the opposite side of the range. Common R:R 2:1 to 3:1. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)
- Timing of failures: student rule of thumb, failed breakouts usually resolve within 1-5 bars regardless of timeframe. [FOLK] [Brooks forum: Breakout fail](https://www.brookstradingcourse.com/support-forum/12-market-cycle/breakout-fail/)
- Brooks' probability framing (quoted from course video 13C slide 13): after about 20 bars of trading range, "50% of the time the first breakout fails." A student's derived figure for channel breakouts: 75% fail (50% fail outright, half of the rest reverse). The admin called breakout mode "50/50." [DESC] (same thread)
- "80% of breakouts fail" is the widely quoted version; the forum admin and NexusFi both call it a directional bias rather than a measured statistic. [FOLK] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies), [Brooks forum: Probability of breakout vs MTR](https://brookstradingcourse.com/support-forum/22-major-trend-reversals/probability-of-breakout-vs-mtr)
- Second-test rule: roughly 50% hold rate on a first test of a level vs roughly 80% on a second test (NexusFi's figure, unsourced). [FOLK] (same NexusFi article)

### Turtle Soup (Connors/Raschke, Street Smarts 1995, exact rules)
- Buy side: today makes a new 20-day low AND the previous 20-day low was at least 4 trading days earlier. Place a buy stop 5-10 ticks above the previous 20-day low. Initial stop 1 tick under today's low. Exit via trailing stop over hours to days; lock in profits when offered. Sell side mirrors at 20-day highs. [DESC] [Traders.com: Turtle Soup](https://technical.traders.com/tradersonline/display.asp?art=2414)
- Turtle Soup Plus One: previous 20-day low at least 3 days old; today closes at or below it; buy stop the next day at the earlier 20-day low. [DESC] (same source)
- Intraday translation commonly used: replace "20-day" with 20 bars of the trading timeframe. No published statistics; LuxAlgo notes the parameters have been public since 1995 and decay is expected. [FOLK] [LuxAlgo: Turtle Soup](https://www.luxalgo.com/library/concept/turtle-soup/)

### Wyckoff spring / upthrust
- Spring: price breaks below range support, finds little selling, and re-enters the range "within a few bars." Ideal: volume not expanding on the break (light = spring, heavy = shakeout). Requires a test: a quiet pullback holding above the spring low on lower volume than the spring. Entry long after the test; stop just below the spring low; invalidation = close back below the spring low. Upthrust is the mirror at resistance. No bar counts or thresholds published. [DESC] [LuxAlgo: Spring](https://www.luxalgo.com/library/concept/spring/)
- Grimes frames both as "a failed breakout that reverses back into the range within the same price bar." [DESC] [Topstep: Grimes approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)

### VWAP band trap (failed breakout beyond +/-2 SD)
- Price extends beyond +2 SD on below-average volume; a bar closes back inside +2 SD (trap close). Short at the trap bar close or sell stop below its low; stop above the breakout high plus buffer; targets +1 SD then VWAP. Abort if price keeps rising 3-5 bars after the breach. [DESC] [NexusFi: VWAP Bands](https://nexusfi.com/a/indicators/vwap-standard-deviation-bands)

### Measured failed-breakout statistics
- None found for intraday index futures. Bulkowski's daily-chart data on "busted" patterns is the closest: see section 10.

---

## 4. Trading ranges

### Mechanical definition (NexusFi encoding of Brooks)
- Both boundaries touched at least 2-3 times each; heavy bar overlap; no net progress; bull and bear bars roughly balanced; the higher timeframe shows no directional move (if the 5-minute "range" is resolving higher on the 15-minute, it is a pullback). [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)
- Barb wire (tight range): bars overlap roughly 75-90% and bar range under about 0.25-0.5x ATR. No new positions inside barb wire; at most second entries with small size. [DESC] (same source)
- Brooks: markets spend 70-80% of the time in some form of range. [DESC] (same source)
- Brooks' "20-bar range" convention: after about 20 bars of range, treat the structure as breakout mode; a breakout then has roughly a 20% chance of a breakout on the opposite side before the end of the day. If the range is about half the average recent daily range, expect the day's range to roughly double. The "18-bar rule" number is explicitly arbitrary per Brooks ("nothing magical about 18 bars"). [DESC] [Brooks forum: 18-bar rule](https://www.brookstradingcourse.com/support-forum/48-trading-the-open/18-bar-rule-for-oil-cfds-and-cryptocurrencies-etc/)

### Fade rules at edges
- Buy only in the lower third of the range, sell only in the upper third; never at the midpoint. Prefer second entries and prior failed breakouts. [DESC]
- Stop: beyond the structural swing that defined the level (example: support 4800 from a swing low at 4799.75, stop 4799.50 or lower). Never average down. [DESC]
- Target: opposite boundary; take 1/2 to 2/3 off at the midpoint and move the stop to breakeven or slightly better; exit in the far third rather than at the extreme. Range trades yield about 1-2 points on ES. [DESC]
- Counter-higher-timeframe fades: 50% size, target the midpoint only. [DESC]
- Measured move on a real breakout: range height projected from the breakout (30-point range breaking at 5830 targets 5860); scale out in thirds at the breakout point, midpoint of the projection, and the full target. [DESC] (all from [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies))

### 80% rule and when to stop fading
- Default in a confirmed range: assume the breakout fails (the "80%"). Failure is more likely with 2-3 tests per boundary, a weak breakout bar, and a balanced session; success more likely with a strong trend context, news driver, or higher-timeframe alignment. [DESC/FOLK] (same source; see section 3 for the 50% vs 80% discrepancy)
- Stop fading when: breakout holds beyond the range for more than 5 bars; two consecutive 5-minute closes beyond the range; a pullback holds beyond the old boundary. Reduce size 50% during range-to-trend transitions and expanding ranges. [DESC] (same source)
- Brooks via students: after several failed breakouts, odds of the next one succeeding drift toward 50% (random), so late-range fades lose their edge. One member's anecdote: 12 failed breakouts, the 13th succeeded. [FOLK] [Brooks forum: Breakout fail](https://www.brookstradingcourse.com/support-forum/12-market-cycle/breakout-fail/)

---

## 5. Reversals

### Major trend reversal (Brooks)
- Sequence: (1) a trend line break with a strong counter-trend leg, (2) a test of the old extreme (higher high, equal high, or lower high), (3) a strong reversal bar/breakout off that test, then a lower low (for a top). A minor but clear decline of 10-20 bars of counter-trend control must precede the "major" label. Most major tops are two-legged; typical path is wedge top, 50% pullback, then sideways at support. [DESC] [dev.to: Brooks MTR supplement](https://dev.to/victorjia/price-action-major-trend-reversal-supplement-360f)
- Probability: early MTR entries succeed roughly 40% of the time; waiting for the confirming breakout raises probability but worsens reward-to-risk. Course material as paraphrased by students: "probability of getting an MTR swing is 40%." [DESC] (same source; [Brooks forum: Probability of breakout vs MTR](https://brookstradingcourse.com/support-forum/22-major-trend-reversals/probability-of-breakout-vs-mtr))
- Target: at least 2x risk; a successful MTR swing typically lasts 20+ bars. Stop: based on current price action (beyond the signal bar / test extreme), not on the entry price. [DESC] (dev.to source)
- Channel rule: third touch of a broad channel's upper boundary is a short-on-breakout-failure setup; in a very tight channel the first counter move is usually minor. [DESC] (same source)

### Double top / bottom
- Brooks: every double bottom in a bull trend is an H2 (two-legged pullback); treat the second leg's signal bar as the entry trigger. [DESC] [Brooks forum: Why every double bottom is a High 2](https://brookstradingcourse.com/support-forum/general-trading-discussion/why-is-every-double-bottom-a-high-2)
- Bulkowski Adam & Adam double top (daily stocks, 1,114 trades): peaks differ by under 3%; valley between at least 10% deep; confirmation = close below the valley; failure rate 25% (confirmed), average decline 15%, pullback rate 64%, meets price target 64%. Unconfirmed twin peaks fail 60% of the time, which is why he requires confirmation. [DOC] [ThePatternSite: Adam & Adam double top](https://thepatternsite.com/aadt.html)

### Wedge reversal (Brooks three pushes, NexusFi encoding)
- Three same-direction legs with pullbacks between; push 3 must make a new extreme (otherwise it is a double top/bottom); at least two of the three pushes roughly equal in size, usually the first largest; pushes roughly equal in time. Illustrative push length on 5-minute ES: 8-12 bars. Prior leg of 40+ minutes (8+ bars) marks an extreme. [DESC] [NexusFi: Wedge Reversals](https://nexusfi.com/a/strategies/wedge-reversals-price-action)
- Entry: draw the trendline across the three push extremes; wait for a bar that closes beyond it (wick alone does not count); enter on the close of the second confirming bar or on a stop beyond the break bar. [DESC]
- Stop: 1-2 ticks beyond push 3 (ES 6-8 points on 5-minute, NQ 20-25 points), or tighter beyond the break bar. [DESC]
- Targets: (1) prior swing level, (2) wedge height projected from the break, (3) if the wedge fails (price re-enters within 1-4 bars after moving 1-3 bars in the reversal direction), reverse and target the failed-wedge measured move. Wedge reversals "fail roughly 40% of the time." Session: 9:30-10:30 ET best, 12:00-14:00 ET worst. [DESC/FOLK]
- Brooks' breakout-pullback shorthand: three pushes up are a wedge even when not wedge-shaped, and the third push is a failed breakout. [DESC] [dev.to: Brooks MTR supplement](https://dev.to/victorjia/price-action-major-trend-reversal-supplement-360f)

### Climax / exhaustion
- Brooks: an unusually large trend bar (climax) after a prolonged trend, especially one with a big tail or followed by a strong opposite bar, usually leads to at least a two-legged correction or a trading range, not an immediate reversal; do not fade the climax bar itself, wait for the second entry. [FOLK] (student restatements of Trading Price Action: Reversals)
- Wedge push-3 exhaustion cues used mechanically: tails at the extreme, overlapping bars, opposite-color closes. [DESC] [NexusFi: Wedge Reversals](https://nexusfi.com/a/strategies/wedge-reversals-price-action)

---

## 6. Signal bars and candles

### Brooks signal bar rules (NexusFi encoding)
- Bull signal bar: close in the upper 25-33% of its range; body large relative to recent bars; small upper tail; small lower tail for a reversal bar; range larger than recent bars (in quiet markets, 2-3x surrounding bars); stronger if its high exceeds the prior bar's high. Bear mirror. [DESC] [NexusFi: Signal Bars and Entry Bars](https://nexusfi.com/a/strategies/signal-bars-entry-bars-price-action)
- Weak signal bars: opposite tail larger than the body, close mid-range, or doji (one-bar range). "Never buy above a doji in a bear or sell below one in a bull." [DESC]
- Trigger: buy stop 1 tick above the signal bar high (sell stop 1 tick below its low). Nullified if the opposite extreme is taken out before the trigger fills. Initial stop 1 tick beyond the signal bar's opposite extreme. [DESC]

### Entry bar and follow-through
- Ideal entry bar: closes near its high, above midpoint, body at least 30-40% of range. Acceptable: fills but closes mid-range (keep the stop at the signal bar, not the entry bar). Failed: trades through the trigger then closes near or below the signal bar high, exit or go to breakeven. [DESC]
- Follow-through bar: strong = continues with meaningful range, closes near its extreme, overlaps the entry bar by no more than 50%. Weak = inside bar, doji, or reversal; tighten or exit. One strong follow-through then one reversal bar = move the stop to the entry bar's low. [DESC] (all same NexusFi article)

### Mechanical candle criteria used in code
- Trend bar (open-source Brooks indicator): body at least 50% of range; close in top/bottom 40%; range at least 1.5x the average of the prior 3 bars. Reversal bar: new low vs prior bar and close in upper half (bull), long tail on the reversal side; disabled when overlap with the prior bar exceeds 50%. ii / oo / ioi patterns with size ratios 0.5 and 1.2. [DESC] [TradingView: Price Action Indicator](https://www.tradingview.com/script/hP0oDLG1-Price-Action-Indicator)
- Pin bar convention: tail at least two-thirds of the high-low range; small body at the opposite end; tail protrudes beyond adjacent bars or through a level. Entry on a break of the nose-side extreme (or next bar closing in the direction); stop beyond the tail. No statistics. [DESC] [LuxAlgo: Pin Bar](https://www.luxalgo.com/library/concept/pin-bar.md)
- Engulfing bar (range convention): high above prior high, low below prior low, close beyond the prior bar's extreme in the new direction; common filters are a close in the top/bottom third and range above recent average. Entry on close or break of extreme; stop beyond the engulfing bar. [DESC] [LuxAlgo: Engulfing Bar](https://www.luxalgo.com/library/concept/engulfing-bar.md)

### Measured candle statistics (daily, stocks, not intraday futures)
- Bullish engulfing: 55% win, 3,735 trades, avg win 3.5%, avg loss -3.3%, +0.46% per trade (30 DJIA stocks, daily, 2003-2023, 10-day exit). Bearish engulfing: 57% win, 4,096 trades, +0.62% per trade. Other quoted win rates (no sample sizes): inverted hammer 60%, hammer 52.1%, shooting star 57.1%, doji 55.6%, tweezer top 44%. Note that 10-day holds in a bull decade bias everything long. [DOC] [Liberated Stock Trader: Chart Pattern Research](https://www.liberatedstocktrader.com/?p=26481)

---

## 7. Trade management

### Brooks' trader's equation and scalp/swing math
- Trader's equation: probability x reward must exceed (1 - probability) x risk. He wants either 60%+ at 1:1 (with-trend scalps) or 40% at 2:1 or better (swings). A 40% setup with only 2x reward is "marginal at best." [DESC] [Brooks forum: Probability and risk/reward](https://www.brookstradingcourse.com/support-forum/general-trading-discussion/probability-and-riskreward/), [Brooks forum: 2x actual risk](https://www.brookstradingcourse.com/support-forum/34-actual-risk/math-is-good-for-2x-actual-risk-profit/)
- Scalp geometry: profit about half an average bar, risk about one average bar, so you need about 67% winners to break even before costs and realistically 70%+. A great scalper wins 80-90%. Swings are profitable at 30-40% because wins are several R. "40% of the time you get several times your risk or get stopped out; 60% of the time you make a little and lose a little." [DESC] (same sources, [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/))
- Scalp minimums: ES 1 point minimum, 2 points typical fixed target; 10 pips FX; $0.10 stocks. "Scalping for a single tick loses money." [DESC]
- Sizing: same size most days; half size on extreme-range days; beginners use stop orders only and never scale in. [DESC]

### Scalp vs swing portions
- Brooks' standard: take partial (scalp) profit at about 1x risk or 2x actual risk, hold the remainder as a swing with the stop moved to breakeven once the scalp portion is secured. [FOLK] (student restatements; the forum thread above shows the 2x-actual-risk rule explicitly)
- NexusFi range trades: 1/2 to 2/3 off at the midpoint, stop to breakeven; remaining to the far third. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)

### Breakeven rules
- Convention: move to breakeven (entry plus a few ticks for costs) after +1R; variants use a fixed ATR distance or a new swing in the trade direction (then stop goes under that swing, not at entry). Never loosen once moved. LuxAlgo notes MAE/MFE studies "often show" that mechanical +1R breakeven reduces average profit per trade because scratches cost more than avoided losers save. [DESC] [LuxAlgo: Breakeven Move Rules](https://www.luxalgo.com/library/concept/breakeven-move-rules/)
- Measured comparison (daily charts, author's own entries, 265 trades): breakeven-after-1R with a 4R target gave 20% winners, 34% scratches, 46% losers, expectancy +0.33R, profit factor about 1.74. Replacing the breakeven move with an add-on at +1R (second unit, original entry as stop, 3R target) raised total to about +0.60R per trade. [DOC] [Trader Peter: Moving the stop to be safe](https://traderpeter.substack.com/p/there-might-be-more-potential-in)
- Brooks: if you scaled in, exit the first entry at breakeven when price returns to it and let the lower entries profit. [DESC] [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/)

### Trailing and time stops
- Brooks: stay in a swing until the trade is no longer valid (opposite strong reversal, or price beyond the last leg's start). He does not give a bar-count hold rule in the sources found. [DESC] [Brooks: Breakout pullbacks](https://www.brookstradingcourse.com/?p=58515)
- Brooks' "exit after a few bars without follow-through" (commonly quoted as 4-5 bars for a scalp): not found in a primary source during this research; treat as [FOLK] until verified against Reading Price Charts Bar by Bar.
- Follow-through-based management: one strong follow-through bar then a reversal bar = stop to the entry bar's low. Weak follow-through (inside bar/doji) = tighten or exit. [DESC] [NexusFi: Signal Bars and Entry Bars](https://nexusfi.com/a/strategies/signal-bars-entry-bars-price-action)
- VWAP band trades: trail with a 0.5 or 1.0 SD stop when holding for a breakout; exit band-walk longs on a close back inside +1 SD. [DESC] [NexusFi: VWAP Bands](https://nexusfi.com/a/indicators/vwap-standard-deviation-bands)
- Wedge fades: exit if price re-enters the wedge within 1-4 bars; never add to a losing fade. [DESC] [NexusFi: Wedge Reversals](https://nexusfi.com/a/strategies/wedge-reversals-price-action)
- ORB backtests use hard time exits: end of RTH session (Crabel, Zarattini) or the next session open (Backtests Not Signals). See section 10. [DOC]

### Scaling in and re-entry
- Brooks: scale in only as the market moves against you and only while price remains inside the signal bar or consecutive inside bars; professionals only. Limit-order reversal entries need wide stops and scaling. [DESC] [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/)
- Holy Grail: if stopped, re-enter on the next EMA touch while ADX still qualifies. [DESC] [Trading Setups Review: Holy Grail](https://tradingsetupsreview.com/the-holy-grail-trading-setup)
- Range trades: one entry, one stop; if stopped, reassess from scratch, no re-entry on the same thesis. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)
- Daily loss rule used in a measured ORB test: no further trades after one losing trade in the session. [DOC] [Backtests Not Signals: ORB](https://backtestsnotsignals.substack.com/p/opening-range-breakout-real-edge)

---

## 8. Key levels combined with price action

### VWAP and bands (NexusFi rules)
- Day classification in the first 30 minutes: balance day = at least one VWAP cross, flat VWAP, contained opening range (fade +/-2 SD); trend day = no VWAP crosses, gap or strong push, +/-1 SD acting as support/resistance (do not fade +/-2 SD, trade band-walk pullbacks). [DESC] [NexusFi: VWAP Bands](https://nexusfi.com/a/indicators/vwap-standard-deviation-bands)
- Mean reversion long from -2 SD on a balance day: one or more rejection bars (wick below -2 SD, close inside); buy stop above the rejection bar high or limit at -2 SD; stop 0.25-0.5 SD beyond the band (about 4-6 ES points, 8-12 NQ points); targets -1 SD (scalp), VWAP (standard), +1 SD (strong day). Community variant: enter between -1.25 and -1.5 SD, stop below -2 SD, target VWAP; skip if price has already traveled well past -0.25 SD. [DESC]
- Time windows: 9:30-10:00 classify only; 10:00-11:30 best mean reversion; 11:30-13:00 use VWAP as target; 13:00-14:30 most stable bands; 14:30-16:00 do not trust band touches. [DESC]
- Statistics: the article gives only theoretical coverage (68% within 1 SD, 95% within 2 SD) and admits excess kurtosis makes 3 SD touches more frequent; no measured touch or reversion rates. [DESC]

### Prior day high/low/close, overnight high/low
- Gap fill definition used in ES stats: price touches the prior 4:00 PM ET cash close; half gap = half the distance from the 9:30 open to that close. The 2009 study claims 60-80% fill probabilities in general but publishes no size breakdown in text. [DOC-weak] [Slope of Hope: 2009 ES gap fill summary](https://slopeofhope.com/?p=7636)
- Edgeful sells per-ticker reports (gap fill, previous day range breakout, opening stats, initial balance) but publishes no ES/NQ numbers on its public pages; the only figure is an illustrative "75% on Tuesdays vs 45% on Fridays." Common levels it cites for IB: 25% retracement and 0.5x extension. [DESC] [Edgeful: Previous day's range report](https://www.edgeful.com/blog/posts/previous-days-range-report), [Edgeful: Reports guide](https://www.edgeful.com/blog/posts/edgeful-reports-the-complete-guide)
- No independent, published touch/hold statistics for PDH/PDL/ONH/ONL on ES/NQ were found. The TradingView "Previous Day High and Low Count with Probabilities" script computes them locally per symbol; numbers depend on the lookback. [FOLK]

### Opening range
- Window choices in measured tests: first 5-minute bar (Zarattini/Aziz, Edgeful), first 30 minutes (Crabel). Edgeful's 5-minute version: stop at the opposite edge of the range, target 50% of the range height, skip when the range exceeds 0.55% of the open, hard max loss 14 ES points. [DOC] [Edgeful: 5-minute ORB on ES](https://www.edgeful.com/blog/posts/5-minute-opening-range-breakout-es-strategy)
- Brooks on the open: a range of about 20 bars sets up breakout mode; late-morning breakouts (11:00-12:00) after roughly two hours sideways are possible trend changes, not automatic continuations. [DESC] [Brooks: Breakout pullbacks](https://www.brookstradingcourse.com/?p=58515), [Brooks forum: 18-bar rule](https://www.brookstradingcourse.com/support-forum/48-trading-the-open/18-bar-rule-for-oil-cfds-and-cryptocurrencies-etc/)

### Round numbers and session structure
- Used only as confluence for measured-move targets (check whether D aligns with a prior swing, channel line, or round number). No stats found. [DESC] [NexusFi: Two-Legged Pullback Trading](https://nexusfi.com/a/strategies/two-legged-pullback-trading)
- Grimes: a level alone is not a reason to trade; "you must have a reason for expecting nonrandom price action off the level." [DESC] [Topstep: Grimes approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)

---

## 9. Timeframes

- Brooks: 5-minute chart is the default for most traders; 1- and 2-minute leave too little time to decide. His scalp examples are shown on the 2-minute. [DESC] [Brooks: Rules for Scalping](https://www.brookstradingcourse.com/es/operacoes-ao-vivo/rules-for-scalping/)
- Tick charts (Brooks course moderators): about 2,000 ticks resembled the 5-minute ES at the time of the thread; the admin considers 2,000 ticks "far too fast" in current volatility and runs about 8,000 ticks (2-3 minute equivalent), dropping to 6,000 then 4,000 in slow markets, set once per session. He keeps a small 5-minute chart beside it for context. A member who traded both reverted to 5-minute only because lower timeframes caused early exits and wide stops. [DESC] [Brooks forum: Tick chart](https://www.brookstradingcourse.com/support-forum/general-trading-discussion/tick-chart/)
- Higher-timeframe alignment: NexusFi rejects a 5-minute range that is resolving on the 15-minute; counter-HTF fades get 50% size and midpoint targets. [DESC] [NexusFi: Trading Range Strategies](https://nexusfi.com/a/strategies/trading-range-price-action-strategies)
- Grimes: pullback failure rates "rise significantly" when daily and weekly trends oppose the trading timeframe (his example: 15-minute pullback against daily/weekly). [DESC] [Topstep: Grimes approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)
- Brooks lookback equivalence: a 7-bar lookback reads like a lower timeframe, a 20-bar lookback like a higher one; a wider stop is equivalent to trading a higher timeframe. [DESC] [Brooks forum: Always-in confusion](https://www.brookstradingcourse.com/support-forum/13-always-in/always-in-confusion-2/)
- Session windows repeatedly cited: 9:30-10:30 ET best for reversals, 10:00-11:30 best for VWAP mean reversion, 12:00-14:00 lowest reliability. [DESC/FOLK] (NexusFi wedge and VWAP articles above)

---

## 10. Published backtests of price-action-style rules

### Opening range breakout
- Zarattini & Aziz (SSRN 4416622), QQQ, 2016-2023: direction of the first 5-minute candle, enter at open of the second, stop at the other side of candle 1, target 10R or session close. Reported 24% hit rate, +0.13R per trade, 33% annual return at 4x leverage, commissions only. [DOC]
- Independent replication on CFDs, Jan 2015 to Jun 2026 (~2,900 sessions per market): gross avg R: NQ +0.131 (t 2.9), SPX +0.119, DAX +0.116, Dow +0.048, FTSE +0.050; hit rates 20-23%. After spread plus slippage (NQ 2.5 pts, SPX 0.8, DAX 2.5): net NQ +0.002, SPX -0.081, Dow -0.081, DAX -0.038, FTSE -0.079. Conclusion: "no market is distinguishable from zero" net. The rule beats random direction by about +0.1R gross, which is roughly the cost. Rule was negative in all markets in 2015-2017. [DOC] [MQL5 blog: ORB paper replicated on five indices](https://www.mql5.com/en/blogs/post/776235)
- Backtests Not Signals, MNQ, 1 contract, Databento data: ORB with a daily SMA trend filter (base 200, optimized 150-300), stop at the opposite side of the range capped at 150 ticks, target 1.4-4.2x risk, exit at next session open, stop trading after one loss per day, $0.68/side commission. In-sample 2020-02 to 2022-12: +108.6%, Sharpe 1.37, max DD -10.9%, 451 trades, win 30.4%, PF 1.43. Out-of-sample 2023-01 to 2026-02: +94.6%, Sharpe 1.10, max DD -12.8%, 474 trades, win 24.9%, PF 1.32 (buy and hold +127.6%). No slippage modeled. [DOC] [Backtests Not Signals: ORB real edge](https://backtestsnotsignals.substack.com/p/opening-range-breakout-real-edge)
- Edgeful 5-minute ORB on ES (vendor, 6 months, 1 contract): 115 trades, win 72.2%, PF 1.62, +$10,825; filters: skip ranges above 0.55% of open, no Tuesdays, max loss $700. A second vendor page: 109 trades over 12 months, win 63.3%, PF 2.35. Vendor-optimized, no out-of-sample shown. [DOC-weak] [Edgeful: 5-minute ORB](https://www.edgeful.com/blog/posts/5-minute-opening-range-breakout-es-strategy), [Edgeful: ORB playbook](https://www.edgeful.com/orb-es-5min-free-playbook)
- Crabel 30-minute ORB on Nasdaq futures (Unger Academy): stop orders at the first 30-minute bar's high/low, exit on opposite break or session close, 6,190+ trades. Unfiltered average trade about $30 on shorts, not enough to cover costs; Friday-only filter raised the average trade to about $95 ($155 short side). [DOC] [Unger Academy: Crabel ORB on Nasdaq](https://ungeracademy.com/?p=7020)

### Breakout from compression (daily, non-index)
- Rogue Quant, copper futures daily, 2010-2026, $40 round-turn costs, train/validate/blind splits: base tight-range breakout PF 1.82 over 394 trades, 62% win; adding a declining-momentum filter PF 2.71 over 171 trades, 78.4% win, avg win $1,903 vs avg loss $2,543, max DD 25.6%, 13 of 16 years profitable. Rules are paywalled. [DOC] [Rogue Quant: Quiet breakout edge](https://roguequant.substack.com/p/the-quiet-breakout-edge-i-found-while)

### Chart and candle patterns (daily stocks, Bulkowski and others)
- Adam & Adam double top: 25% failure, 15% average decline, 64% pullback rate, 1,114 samples (see section 5). [DOC] [ThePatternSite](https://thepatternsite.com/aadt.html)
- Engulfing (30 DJIA stocks, 2003-2023, 10-day exit): bullish 55% win / +0.46% per trade (n = 3,735); bearish 57% / +0.62% (n = 4,096). [DOC] [Liberated Stock Trader](https://www.liberatedstocktrader.com/?p=26481)

### Trade management
- Breakeven-at-1R vs add-at-1R (265 daily-chart trades): +0.33R vs about +0.60R per trade. [DOC] [Trader Peter](https://traderpeter.substack.com/p/there-might-be-more-potential-in)

### What the published numbers say, condensed
- Raw first-candle ORB has a tiny gross edge (about +0.1R) that round-trip costs on NQ consume; filters (trend filter, range-size cap, one-loss-per-day, time exit) are what produced out-of-sample profit factors of 1.3 with 25-30% win rates. [DOC]
- Nobody found publishes measured win rates for H2/L2, wedge reversals, MTRs, or failed-breakout fades on intraday index futures. The 40% (reversals), 60% (with-trend), 50% (first breakout from a 20-bar range), 75% (channel breakouts fail), and 80% (range breakouts fail) figures are Brooks' heuristics or student paraphrases, not backtests. [DESC/FOLK]
- Candle-level stats that do exist (engulfing, hammer) sit at 52-60% on daily stock data with 10-day holds, barely above the long-bias baseline of that period; they say nothing about 1-5 minute MNQ bars. [DOC]
- Brooks' scalp arithmetic is the most useful measured-style constraint: half-bar reward vs one-bar risk requires about 67% winners before costs, 70%+ after. Any engine whose scalp leg targets less than 1 ES point (or its MNQ equivalent) is negative expectancy by his rule. [DESC]

---

## 11. Other Brooks and Grimes heuristics commonly encoded (secondary sources)

These are widely repeated restatements of the books and course. They are listed because engines in this lineage usually implement them, but every one is [FOLK] or secondhand [DESC] until checked against the primary text.

### Brooks structural heuristics
- Micro channel: 5 or more consecutive bars with no overlap of the prior bar's extreme (each low above the prior low in a bull micro channel). First break of a micro channel usually fails and becomes a with-trend entry (H1); only the second break is tradable counter-trend. [FOLK]
- Gap bars: a bar whose low is above the EMA (bull) during a trend is a "gap bar"; the first gap bar after a pullback to the EMA is a with-trend buy signal. Students count 20 consecutive gap bars as a strong trend requiring at least two legs down before a reversal is considered. [FOLK] (source: student forum discussions of Trading Price Action: Trends; not found in primary text during this research)
- Spike and channel: after a spike (2-4 consecutive strong trend bars), the subsequent channel usually gets tested back to its start; the "channel start" is a standard target for the first reversal. [FOLK]
- Second entry rule: any first reversal attempt against a strong trend is assumed to fail; only the second signal (H2/L2, or a second reversal bar at the same level) is taken. NexusFi's unsourced 50% first test vs 80% second test figure comes from this rule. [FOLK]
- Trend from the open: if the first 1-2 bars of the day are large trend bars that break the overnight range, Brooks assumes a trend-from-the-open day and takes H1/L1 pullbacks; otherwise the first hour is usually breakout mode. [FOLK]
- Trading range day heuristic: if the day's range is inside the prior day's range by mid-morning and bars overlap, assume a range day and fade; if the market makes a new high and a new low relative to the prior day in the first hour, assume a trend day. [FOLK]
- Opposite-side probability: Brooks' course quote that after a breakout from a 20-bar range there is a 20% chance of a breakout on the opposite side before the close is the only primary-sourced opening statistic found. [DESC] [Brooks forum: 18-bar rule](https://www.brookstradingcourse.com/support-forum/48-trading-the-open/18-bar-rule-for-oil-cfds-and-cryptocurrencies-etc/)

### Grimes setups (The Art and Science of Technical Analysis, 2012)
- Four setup classes: (1) failure test of a level (Wyckoff spring/upthrust), (2) pullback in a trend (simple and complex), (3) breakout from a range, (4) anti (first pullback after a momentum change, the "Anti" setup from Raschke). Pullbacks are his highest-probability class; breakouts his lowest. [DESC] [Topstep: Grimes approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)
- Failure test rules: price probes beyond a prior swing, closes back inside the range within the same bar; stop beyond the probe; target the opposite side of the range or the prior swing. [DESC] (same)
- Complex pullback: two countertrend legs (a failed resumption then a deeper pullback); treat the second leg's extreme as the entry point, stop beyond it, target the pre-pullback swing. [DESC] [Capital.com: Trading the complex pullback](https://capital.com/trading-the-complex-pullback)
- Anti setup (Raschke, Street Smarts): after a momentum change (3-10 oscillator crosses), the first pullback against the new momentum is bought; entry on the break of the pullback's prior bar high; stop beyond the pullback low. [DESC] (Street Smarts description, restated widely)
- Grimes' statistical stance: he publishes no per-setup win rates in the book; his measured claims are about the existence of serial correlation after strong impulse moves (prices tend to continue after large-range bars over 1-5 bars) and the absence of edge in naive support/resistance. [DESC] [Topstep: Grimes approach](https://topstep.com/blog/going-deep-on-adam-grimes-approach)

### Two-EMA scalp pattern (Wade-style, generic)
- Common form in MNQ/MES scalper scripts: fast EMA (8-10) over slow EMA (20-21) for bias; entry on the first bar that closes back on the trend side of the fast EMA after touching it; stop beyond the pullback low; target 1-2x risk or a fixed point count. One open-source MNQ 1-minute EMA strategy on TradingView describes itself as "not perfected" and publishes no stats. [FOLK] [TradingView: MNQ EMA Strategy](https://www.tradingview.com/script/rMt2CyH3-MNQ-EMA-Strategy)

### Brooks probability cheat sheet (all heuristics, none backtested)
| Context | Brooks' stated probability | Where it came from |
|---|---|---|
| With-trend pullback entry (H2/L2 in a trend) at 1:1 | 60% or better | moderator summary [DESC] |
| Any reversal setup at 1:1 | 40% or less | moderator summary [DESC] |
| MTR producing a real swing | 40% | course paraphrase [DESC] |
| First breakout from a ~20-bar range failing | 50% | course video 13C slide 13 [DESC] |
| Opposite-side breakout before close after a range breakout | 20% | course 48 series [DESC] |
| Bull channel eventually breaking out downward | 75% | course 14C slide 27 [DESC] |
| Channel breakout failing | 75% (derived by a student) | forum [FOLK] |
| Trading range breakout failing | 80% | folklore / NexusFi [FOLK] |
| Wedge reversal failing | 40% | NexusFi [FOLK] |
| Breakout mode generally | 50/50 | forum admin [DESC] |
| Great scalper win rate | 80-90% | Brooks scalping rules [DESC] |
| Swing trader win rate that still profits | 30-40% | Brooks scalping rules [DESC] |

---

## 12. Gaps in the evidence and what to measure yourself

- No published measurement exists for: H2/L2 win rate; wedge reversal hit rate; MTR 40%; 80% range breakout failure; first-test vs second-test hold rates; failed-breakout reversal distance; signal bar close-location effect on outcome; "exit after N bars" time stops. All of these are testable on the Databento MNQ/MES history already in the project.
- Suggested measurements, in the order they constrain an engine:
  1. Breakout failure rate conditional on range length (5, 10, 20 bars) and breakout bar quality (body %, close location), with failure defined as re-entry within 1-5 bars. Compare to Brooks' 50% (20-bar range) and 80% folklore.
  2. H1 vs H2 outcome at 1R and 2R targets with a 1-tick-beyond-signal-bar stop, split by EMA slope and by pullback depth (< 50% vs > 50% of impulse).
  3. Signal bar close location buckets (top 25%, 25-50%, bottom 50%) vs 1R hit rate; this is the single most-repeated Brooks rule with zero published numbers.
  4. Breakeven-at-1R vs no breakeven vs add-at-1R on the engine's own trades, since the only measured study (daily, +0.33R vs +0.60R) is on a different timeframe.
  5. VWAP +/-2 SD touch count per day and reversion-to-VWAP rate on balance vs trend days as classified at 10:00 ET.
  6. PDH/PDL/ONH/ONL touch rate during RTH and hold rate on first touch; Edgeful sells these but publishes none.
- Cost reality check from the ORB replication: a 2.5-point NQ round trip against a 25-point stop is 0.1R, which equals the entire gross edge of the first-candle rule. Any MNQ rule with a sub-20-point stop must beat roughly 0.1-0.15R per trade in gross expectancy just to cover spread and slippage. [DOC] [MQL5 blog: ORB replication](https://www.mql5.com/en/blogs/post/776235)

---

## Appendix: numeric defaults worth encoding first (consolidated)

| Item | Value | Source tag |
|---|---|---|
| Trend EMA | 20 (5m), 10 for scalps | Brooks [DESC] |
| Trend bar | body >= 50% range, close in top/bottom 40%, range >= 1.5x avg of prior 3 | TV indicator [DESC] |
| Signal bar close | top/bottom 25-33% of range | Brooks via NexusFi [DESC] |
| Entry | stop 1 tick beyond signal bar | Brooks [DESC] |
| Initial stop | 1 tick beyond signal bar opposite extreme | Brooks [DESC] |
| Entry bar body | >= 30-40% of range, close above midpoint | NexusFi [DESC] |
| Follow-through overlap | <= 50% of entry bar | NexusFi [DESC] |
| H2 stop buffer | ES 1-2 ticks, NQ 2-4 ticks beyond leg 2 low | NexusFi [DESC] |
| Swing target | >= 2x initial risk (or 2x actual risk) | Brooks [DESC] |
| Scalp target | ES 2 pts typical, 1 pt minimum | Brooks [DESC] |
| With-trend probability floor | 60% at 1:1 | Brooks [DESC] |
| Reversal probability assumption | 40%, needs 2:1 | Brooks [DESC] |
| Range definition | 2-3 touches per side, >= 5 bars before fading a breakout, ~20 bars = breakout mode | Brooks/NexusFi [DESC] |
| Barb wire | overlap 75-90%, bar range < 0.25-0.5 ATR | NexusFi [DESC] |
| Range breakout confirmed | > 5 bars outside, or 2 consecutive 5m closes outside | NexusFi [DESC] |
| Failed breakout window | 1-5 bars | forum [FOLK] |
| Wedge stop | 1-2 ticks beyond push 3; NQ 20-25 pts on 5m | NexusFi [DESC] |
| Wedge fail window | re-entry within 1-4 bars | NexusFi [DESC] |
| MTR pre-condition | 10-20 bars of counter-trend control | Brooks [DESC] |
| VWAP fade stop | 0.25-0.5 SD beyond +/-2 SD (NQ 8-12 pts) | NexusFi [DESC] |
| VWAP band walk | 3+ closes outside +/-1 SD | NexusFi [DESC] |
| Holy Grail | ADX(14) > 30 rising, buy stop at high of bar touching 20 EMA | Raschke [DESC] |
| Turtle Soup | new 20-bar low, prior low >= 4 bars old, buy stop 5-10 ticks above prior low, stop 1 tick under today's low | Connors/Raschke [DESC] |
| ORB (measured) | 5m range, stop opposite edge (cap 150 ticks MNQ), target 1.4-4.2R, exit next open, 1 loss/day, skip range > 0.55% of open | BNS/Edgeful [DOC] |
| Breakeven | after +1R, few ticks buffer; measured to reduce expectancy vs add-on | LuxAlgo/Trader Peter [DOC/DESC] |
| Chart | 5-minute; tick equivalent 4,000-8,000 (2026 volatility) | Brooks forum [DESC] |
