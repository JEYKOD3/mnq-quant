# Thomas Wade price action: first principles (first draft)

Date: 2026-10-21. Sources: 18 of 55 videos from the playlist "Trading Tutorial For Beginners" (transcripts pulled and read in full; list at the end), plus web research on the method's origin (Al Brooks), institutional practice and academic intraday-momentum work. 1 video had no captions. The remaining 37 videos will be folded in; sections that may change are marked [open].

Everything in sections 1 to 9 is what Wade says, in his words or a close paraphrase. Section 10 is the research outside his channel. Section 11 is the translation into numbers we will test on the Databento MNQ data.

---

## 1. The whole method in one paragraph

Institutions move the market; retail follows their footprints. Markets move in pairs of twos because of human behaviour: traders try something once, fail, try again, and give up after the second failure. So the one setup is the **second entry of a two-legged pullback, with the trend, at a key entry point**, triggered one tick beyond a good signal bar, stop one tick beyond the other side of that bar, never moved, target about 1:1 (a scalp), with a runner left on at breakeven. Every other rule exists to decide whether that setup is allowed right now.

Four-step filter, in order, every time: **bias -> key entry point -> high probability setup -> signal bar quality and no congestion**. "You just decide if rules are being met and either take the setup or don't."

## 2. The five price action rules (video 1)

1. **Trendline rule.** After price closes outside a trendline or channel, expect a correction and then, "8 or 9 times out of 10", a retest and new extreme of the old trend. A break is not a reversal. Only after the new extreme do you look for a correction or reversal. Applies to the big channel and to every short-term correction channel.
2. **No counter-trend trading.** No tops or bottoms, no matter how good the bar looks. Trade the other way only after a proven reversal pattern (section 6). "With-trend pullbacks are designed to look weak, counter-trend entries are designed to look strong."
3. **Trading range rule.** Most breakouts fail (he says ~90%). Never trade the breakout; trade the breakout pullback or fade the breakout. In a range, buy low, sell high, avoid the middle ("no man's land"), stay out of congestion.
4. **High probability setup rule.** The only setups: (a) second entry with the trend at a key entry point, (b) failed second entry against the trend, (c) failed breakout, (d) higher-low / lower-high confirmation, (e) double top / double bottom, (f) "double trap" (trapped traders at two key entry points). A setup away from a key entry point is not a setup.
5. **Signal bar rule.** Longs only above a bullish bar, shorts only below a bearish bar. The bar must show direction and momentum; never a doji; wait for the bar to close ("never sneak in early").

## 3. Counting entries (the mechanical core)

This is the part that becomes code with no interpretation.

- **Where the count starts.** For longs: at the highest high of the most recent move. For shorts: at the lowest low. "Where the trend is starting, that's when we start counting."
- **Trigger.** "Entry is when the bar breaks the previous bar's high just by one tick" (longs), or the low by one tick (shorts).
- **Leg.** A bullish leg is a run of bars making higher highs and higher lows; bar colour inside it does not matter. It ends the moment a bar trades one tick below the low of the last bar of the leg. Mirror for bearish legs.
- **First entry.** Counting from the extreme, the first bar whose high is taken by one tick (looking for longs) is the first entry long. He does not trade it: "first entries are 50/50".
- **Second entry.** After the first entry fails (price makes a lower push without breaking the start of the count), the next bar whose high is taken by one tick is the second entry long. That is the two-legged pullback. This is the trade.
- **Reset rules.** The count restarts (a) at every new extreme, even by one tick; (b) when a swing breaks the previous pivot's high (uptrend) or low (downtrend); (c) at double tops and double bottoms, even to the tick; (d) after a "significant event" such as a first or second entry on the other side playing out.
- **Pivot definition.** A pivot exists only when a bullish move is followed by a bearish move that triggers one tick below a prior bar's low. No tick below, no pivot, no restart.
- **Trend end.** "It remains a downtrend until the bar or the move breaks the previous pivot's high."
- **Nesting.** Two-legged moves sit inside bigger two-legged moves. He counts only where he expects a setup: at a key entry point, in the direction of the bias. "I'm not looking for two-legged moves all over the chart."
- **Measured legs.** Sometimes leg 2 equals leg 1 in size, sometimes not. He projects leg 1 to anticipate where the setup will appear, nothing more.
- **Edge cases he states.** A first entry can be stopped and the second entry trigger on the same bar. An inside bar in the second leg is itself a key entry point. A high "so close" to the prior high may not be accepted as a new extreme; "the attempt is often enough to count as the new high" when it happens at a key entry point.
- **Third entries do not exist.** "A failed third entry long, that's really not a thing, not a reliable setup." After the second attempt the count is finished; wait for a new extreme and a fresh count.
- **Dual counting at double tops/bottoms.** The same bar can be read as a failed second entry long and a second entry short (count from the previous low as a second entry, or from the new low as a first entry). He trades it when both readings agree with the bias.
- **Two legs to a new extreme.** After a trendline break, one leg to a new extreme may still carry momentum; after two legs to the new extreme "there is at least a correction or maybe a straight-up reversal", so stop trading in that direction.
- **First entry exceptions.** He takes a first entry only when it is a lower high / higher low at two key entry points with a strong reversal bar while the trendline rule still expects a new extreme; otherwise first entries are ignored by rule.

## 4. Key entry points

- Trendline or channel line, support/resistance (prior swing highs/lows, range edges, prior day levels), and the **21-bar EMA**. "Two key entry points" (EMA plus trendline, or EMA plus level) is the best case.
- EMA is a supportive tool only: direction of slope = bias; price far from the EMA ("multiple points") snaps back, so entries far from the EMA are skipped ("you're risking without reason"); EMA flat through the bodies of stacked bars = congestion = no trade; in a strong trend every touch of the EMA bounces ("hard mode", more aggressive entries allowed).
- A second entry that "hasn't quite touched the EMA" or is "still inside the channel" is skipped. Having room to the prior swing is a condition for a failed-second-entry trade.

## 5. Stop loss (the only rigid rule)

One tick beyond the signal bar: below its low for longs, above its high for shorts. On every instrument and timeframe. Never moved. Never placed in the middle of the bar. If the stop is too large: fewer contracts, a limit order deeper inside the bar, micros instead of minis, or skip the trade (but mark it and track it). "You can move your target, you cannot move your stop."

## 6. Targets, exits, trade management

- **Target is a scalp of about 1:1, slightly less.** ES: 8 to 10 ticks (2 to 2.5 points) against a typical 2-point stop. NQ (1500-tick chart): 10, 12, 14 points. Procedure for any instrument: measure the signal-bar size of high probability setups over many days (or use ATR), set target = average stop, then slightly below.
- Minimum scalp he will accept: ES 1 point, stocks 10 cents, forex 10 pips, but he argues against small targets: at a 1-point target one 12-tick loss wipes three 4-tick wins after commissions.
- **Runner.** Once the scalp fills, the remaining contract goes to breakeven and is trailed below each swing. "Scalp is the main portion, runner is gravy." Split: start with 1 contract; later 2/3 scalp, 1/3 runner.
- **Early exit.** Beginners never exit early. Advanced: scratch at breakeven only after about one hour of congestion with no direction.
- **Missed fill.** If price reaches the scalp target without filling the entry, cancel the order and wait for the next setup.
- **Orders.** He uses limit orders placed after the trigger prints, slightly back inside the bar (smaller stop, more fills at target, some missed entries). Stop orders never miss but can slip 1-2 ticks.
- **No chasing.** After the scalp, no new entries at the highs; wait for the next pullback to a key entry point. "Market can go higher 20, 50, 100 points, I don't care."
- Claimed statistics (his, unverified): 95%+ of high probability setups reach 8-10 ticks; taking every with-trend second entry blindly gives ~70% wins; waiting for the retest of the new extreme gives ~90%.

## 7. Risk, money management, session rules

- Risk capital only; prove it on sim for a few months first. Start ES with $2,500-3,000 (20-25 trades of runway), $10,000 ideal; risk 1-2% per trade; never so big that one loss gives "jitters".
- **Daily rules:** two losing trades in a row -> 15-minute break; third losing trade -> done for the day; two or three winners in a row -> stop for the day (except easy trend days). If 30 trades on $3,000 do not make money -> back to sim.
- Pre-market: identify the pattern and bias from the prior session; unclear bias -> wait for the open. If late or upset: no trades for the first minutes. Print the chart at the end of the day and mark every setup. "Not taking a trade is a trading error as well."

## 8. Trendlines and channels (how he draws them)

- Two swings set the line, the third touch confirms it. Copy the line to the other side to form the channel. A valid line fits "from the highs as well as from the lows".
- Draw short-term trendlines on every correction, including corrections inside the main trend. The trendline rule applies to them: a correction is "played out" only after its own break and new extreme (or a clear attempt at one). Until then, no with-trend entries even on a perfect second entry.
- Break = close outside the line on the counter-trend side. Overshoot = break on the trend side; "unnatural", often followed by a trendline break or a straight reversal. After an overshoot, do not take the second entry at the key level; wait for the lower-high / higher-low confirmation.
- Widen the channel when the trend keeps making new extremes against a line ("five legs to a new extreme" means the line is wrong). Losing momentum = price stops reaching the channel line, barely reaching the middle.
- Spike and channel: strong spike, congestion at the EMA, then an orderly channel with the EMA holding; a break of it still expects a new extreme. A near-90-degree move "won't last long".
- Fit strictness: big channels may be approximate ("close is enough, tweak during the day"); short-term lines must fit "neatly, hugging" the swings, and the copied parallel must fit the other side too, otherwise the line is wrong and gets deleted.
- Short-term lines are trusted over an uncertain bigger pattern: "they'll give you more trades than the bigger patterns." When the big picture is unreadable, trade only the short-term trendline rule.
- Overshoot exception to the trendline rule: after an overshoot the momentum on the other side can be so strong that the retest of the new extreme never comes; it is the one case he lists where break -> new extreme failed. After an overshoot, lean the other way.
- Wedges: never trade inside a wedge ("tempting to go short and tempting to go long = no trade"). Trade only its resolution, usually the failed breakout back to the prior support/resistance. General rule: take a trade only when "there's only one possibility that can happen."

## 9. Market reading: trend, range, reversal

- **Trend:** EMA pointing up, higher highs and higher lows, trendline fitting -> longs only (second entry long at key entry point, failed second entry short). Mirror for downtrends.
- **Range:** series of highs and lows, price swinging through a flat EMA; confirmed by "a move down, a move up, a move down". Range highs/lows come from the prior day's levels and the first bounces. Buy the lows, sell the highs, skip the middle, fade breakouts of small and medium ranges (a failed break back inside the range is "the safest setup of the day"; the entry trigger is still 1 tick beyond a proper signal bar, not the breakout bar). Once the range is big enough to contain real trends (his example: a 60-point downtrend inside it), stop fading and trade the internal trends with second entries. Direction of the move INTO the range hints at the break direction. Do not buy the lows blindly: the short-term down-trendline must break and retest first. Warning sign: a selloff that stops short of support (a "gap" to the level) means buyers are early and the next second entry short will fail; switch sides. Expected travel: from one side of the range to the other.
- **Skip rules he repeats on every chart:** no shorts into the low of the day / longs into the high ("you need a deeper correction"); no entries while the counter-trend correction's trendline is intact (wait for its break and new extreme); after a break and new extreme of the main trend, be "leery" of continuation entries; no setups when the EMA is flat and price chops around a level.
- **Regime shift:** two big legs through the EMA with volume, tails and dojis on the far side, failure to reach the old resistance/support, and price struggling to get back across the EMA = the range is no longer normal, bias has flipped. Steepness rule: big steep corrections are safe to trade with the trend; a grinding move with small corrections is not.
- **Reversal (three conditions, all required):** (1) trendline break then new extreme (trendline rule satisfied); (2) two failed attempts in the old direction (failed first and failed second entry); (3) price spikes through the 21 EMA and the EMA then holds as a "stepping stone" (bars closing through it). EMA rejecting = no reversal, sit on your hands. Top/bottom picking is allowed only inside trading ranges, and only for experienced traders.
- **Congestion:** overlapping bars stacked side by side, EMA flat through the bodies -> no trades; wait for the breakout and fade it or trade its pullback.
- **Depletion:** very large bars at the end of a long trend = exhaustion; expect a larger correction.

## 10. Charts, instruments, time

- Avoid anything under 1 minute. 1-minute is the optimal time chart for scalping; tick charts are preferred because they are more symmetrical. His picks: ES 2000-tick (NQ 1500-tick, CL 500-tick, GC 500-tick). Micros are matched to the mini's chart, not to 1 minute: **MNQ 2500-tick ~ NQ 1500-tick**, MES 950-tick ~ ES 2000-tick.
- Rule for picking a chart: too few bars or setups -> lower the tick count; too many fakeouts -> raise it; watch and backtest several days before trading it. Master one market, one timeframe.
- Holidays: the prior day's price action carries into the next day (he does not otherwise use the prior day's structure). His scalp on ES is stated as 10 ticks = 2.5 points; bars of 6-7 points are "unenterable" for that target, so on volatile days many setups are skipped.
- [open] Session times and the "trend vs trading range day" day-type calls are expected in the remaining live-session videos.

## 11. Where this comes from, and what the outside world says

- **Al Brooks lineage.** Wade cites Brooks' logic for second entries. Every element here (H2/L2 second entries, two-legged pullbacks, trendline break then test of the extreme, breakout pullbacks, failed second entry as a with-trend setup, signal bar rule, "most breakouts fail", 20-bar EMA) is Brooks' Trading Price Action framework with a 21 EMA and tick charts. Brooks' books are the primary source if we want the complete and numeric version.
- **NexusFi / Brooks community rules** (from earlier web research): entry on a stop one tick beyond the signal bar; stop beyond the leg-2 extreme (2-4 ticks on NQ); measured-move target with a minimum of 2:1 for swing portions; skip in ranges, flat EMA, no key level, bad signal bar. Note the difference: Wade targets ~1:1 scalps; the Brooks swing variant targets 2:1 measured moves.
- **Academic.** Intraday momentum exists in equity index futures: the first-half-hour return predicts the last half hour; gamma hedging by option dealers is the main explanation. NDX futures show both momentum and reversal depending on conditions. This supports Wade's "trade with the day's bias, not against it" but says nothing about pullback counting.
- **Institutions.** Portfolio managers and quant desks do not trade trendlines. They work orders against VWAP over time, which is why pullbacks to VWAP/EMA get bought in trend days and why price "snaps back" to the average. Wade's "EMA as a magnet" is the retail-visible version of that behaviour.

## 12. Translation into numbers (proposal to test, not yet tested)

Definitions for the engine, on 1-minute MNQ bars (his 2500-tick MNQ chart is close to 1-minute in RTH) with a 5-minute cross-check:

- Bias: 21 EMA slope over the last N bars (sign of EMA[t] - EMA[t-3]); plus prior-session close relative to its open [open: refine with the day-type videos].
- Extreme and count start: highest high (for longs) since the last confirmed pivot; pivot = a bar whose low is taken by 1 tick after an up move.
- Leg state machine: track legs by the 1-tick-break rule; first entry = first bar whose high is taken by 1 tick after the extreme; second entry = the next bar whose high is taken after the first entry fails without a new extreme; reset on new extreme, pivot break, double top/bottom within 1 tick.
- Key entry point test at the signal bar: distance from 21 EMA <= X ticks (X from signal-bar statistics, start with 1 average bar range), or touching a prior swing / prior day level within Y ticks, or touching a channel line (channel = 2 swings + 3rd touch within Z ticks; start Z = 2 ticks).
- Signal bar: close in the top half for longs, body >= 30% of range, close above the EMA, not a doji (body >= 1 tick and >= 20% of range).
- Congestion filter: no trade if the last K bars overlap (each bar's range inside the prior bar's range by more than 70%) with the EMA inside their bodies.
- Correction played out: the correction's own 2-swing trendline must be broken by a close, then a new extreme of the correction printed (or attempted within 2 ticks) before the with-trend count is accepted.
- Entry: stop order 1 tick beyond the signal bar; stop loss 1 tick beyond the other side; target = median signal-bar stop over the sample (measure first; his NQ number is 10-14 points), with a 2-contract variant: half at target, half to breakeven and trailed under each swing.
- Session rules: 2 consecutive losses -> 15-minute pause; 3 losses -> stop; 3 wins -> stop (test on and off).
- Report format as agreed: net, max drawdown, % profitable, profit factor, green/red days, monthly, why each loser lost, common denominator of losers, why winners won.

## Videos covered in this draft

TegF3yYjnng 5 Price Action Rules; GrRbOItgLgc The ONLY Price Action Setup; 4w-gpvgjE2A Beginner's Guide; JGULPdDOWbw Best Chart; NNzCegosXu8 How To Count Entries; Q4UFvxWB0AU Two-Legged Pullback Master Setup; L7G19gc2C9Y Reading A Price Chart; mS1920Y-o3Q Trendline Mastery; zOhx-tuXR4k Scalping Money Management; ObLZtYJ_sAg 3 Simple Patterns; hWjUp_Df_t0 All Markets And Timeframes; LCm3VvhkQxI Market Rules Explained; 6MQeh50nW5s How To Trade Reversals; lgIrZDR6uxs Moving Average. 3xmV5IJIlTg Short-term Trendlines; rmmLXeYivk8 Wedge Patterns; ebULiDW6O70 How to Read a Price Chart; qo0ebM_yyZY Trading Ranges. No captions: u2qt9yPySLY Tick Charts.
