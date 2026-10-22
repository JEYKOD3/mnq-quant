# brooks_reversals.md — Al Brooks, Trading Price Action Reversals (2012), machine-first reference
src: /home/claude/books/brooks/NOTES_A-D.md (25 ch). units: ES tick=0.25pt; "bar"=5m ES; MA=20 EMA; ADR_ES 2011 ~10-15pt; times converted PST->ET (+3h).
scale note for MNQ: ES 2pt stop (8tk) ~ 0.15-0.2 ADR; map Brooks tick numbers by ratio to ADR, not literal ticks.
cross-ref: RULES.md (D/E/F/X/R), wade_first_principles.md s3/s12/s15.

## 1. Brooks core model in 25 lines
1. Always-in (ch15): the side you would hold if forced to be in at all times; market is always-in long or short; differs from "trend" (trend trader goes flat, always-in never).
2. Always-in flip (ch15): >=2 consecutive strong trend bars in new direction; follow-through bar close must not oppose; single avg-range bar flips only with context (failed breakout of channel at a likely extreme).
3. Flip tie-breaker (ch15): majority of recent closes vs 20EMA -> side; else direction of move leading into range; else hoping-to-buy-pullback = long; still unsure = trading range -> fade only.
4. Trader's equation (ch24): edge iff P(target)*reward > (1-P)*risk by margin. Defaults: setup looks good P=0.60; confluent P=0.70; uncertain P=0.50 and require reward>=2x risk.
5. Equidistant rule (ch24): in good context, P(move = stop size before stop hit)=0.60 for any stop that is neither > tallest bar on screen nor tiny (2tk when bars 50tk).
6. Clear always-in (ch15): assume >=60% to reach target >= risk; strongest ~70% (fig15.6); strong breakout follow-through often >70% (ch24).
7. Inertia (ch24, ch25 #17): market in strong trend <=20% of time; 80% of reversal attempts in a trend fail (become flags); 80% of breakout attempts in a range fail; 80% of topping patterns resolve up (ch22); tight range after trend P(trend-side breakout)<=55%.
8. Reversal base rates (PI, ch3): avg MTR setup 40% swing / 30% small win / 30% stop -> 70% at least small profit; strong MTR >=60% swing, 30-40% stop; avg MTR -> TR not opposite trend ~70%; earliest reversal entries 40-50%; waiting for flip -> >=60% but smaller reward.
9. 40/60 rule (ch24, ch16, ch25 #57-58): reward>=2x risk works at P>=0.50 (acceptable 0.40 at 3:1); reward=risk needs P>=0.60; reward<risk needs P>=0.70-0.80 (nobody sustains); scalp = 1:1 at 60%+, swing = 2:1 at 40-50%; low-P swings taken as a basket, 60%+ setups may be cherry-picked.
10. What fails (ch9): "common good setups" succeed ~60%, fail ~40%; first countertrend attempt vs a spike fails usually; countertrend scalps inside a channel lose >=70% with avg loss > avg win (PI, ch24); 1m countertrend reversals net losing (ch3); first bar of day is HOD/LOD 20% (30% strong trend bar, 50%+ large-gap trend bar) (ch17/19).
11. Two requirements for reversal (PI, ch3): (a) countertrend leg breaks TL and reaches/exceeds 20EMA; (b) test of old extreme (HH/DT/LH at top; LL/DB/HL at bottom) then second reversal with strong signal bar. TL break alone = first sign only, keep trading with-trend until test.
12. Leg size (PI): TL-break leg and test leg each >=5 bars preferred (min 2-3; one 2-bar leg needs the other >=5 or 1-2 bars with range >=2x median); 2-bar break + 2-bar test rarely starts a trend; after reversal expect >=2 legs and >=10 bars.
13. Restart rule (ch3, ch24): test leg goes >=5 bars beyond old extreme or runs in tight steep channel -> cancel, require new TL break + new test; violent reversal leg -> expect HL not LL on test; countertrend leg >1h needs second leg before final extreme.
14. H1/H2 L1/L2 counting (PI, ch3, ch9, ch24): H1 = first bar whose high is exceeded after the pullback starts in a bull; H2 = second such occurrence after a renewed pullback (two legs); H3 = third = wedge flag; count anchored to pullback start, not the extreme; micro DT = failed H1/H2; micro DB = failed L1/L2.
15. H1/L1 validity (ch16, ch24): H1 only in a strong bull spike and not after a buy climax; L1 only with strong bear spike AND clear bear trend, never after a possible sell climax or after a reversal pattern.
16. H2/L2 reliability (PI, ch24): L2/L3 short in strong bear reaches stops below prior HL ~80%; "single most reliable day trade" = H2/wedge/triangle at EMA on a strong trend day; post-spike L2 at EMA with bear signal bar P>=0.70 at 1:1; H2 alone is not a buy at the top of a range.
17. Signal bar (ch2, ch9, ch16, ch24, ch25 #55): trend bar in trade direction, close in top/bottom 25-33%, small tails; reversal bar min = close beyond midpoint; dojis = one-bar TR, terrible signal bars; buy only above bull bars, sell only below bear bars; large signal bar -> risk its height, cut size; 2-bar reversal with a large bar -> enter beyond the larger bar; outside bar entries rarely.
18. Entry (ch24.D): stop order 1 tick beyond signal bar; protective stop 1 tick beyond opposite end (risk = signal bar range + 2tk); normal ES stop ~8tk (5m), 6tk (3m), 4tk (1m) (ch13); stop entry needs 6tk beyond signal bar to pay a 4tk scalp.
19. Stop management (ch1, ch13, ch24): after strong entry bar closes -> stop 1tk beyond entry bar; swing stop beyond start of most recent spike; trail below each new HL after each new HH; breakeven only after open profit >=0.5x target AND resumption after a test of entry (or halfway + several closes beyond prior range); never let a 9tk+ excursion become a loss.
20. Targets (ch1, ch3, ch5, ch24): scalp = risk (ES 2pt) at P>=0.60; swing >= 2x risk (ES 4pt); measured moves: leg1=leg2, spike height, TR/flag height, wedge height, measuring-gap midpoint projection; within 3tk of MM = incomplete (expect retest), >=4tk beyond = ignored, next target.
21. Target-failure ticks (ch9): 5tk failure (max excursion exactly +5 then reverse) = reversal signal; 9/13/17/21tk failures = failed 2/3/4/5pt targets -> expect at least a scalp the other way; 16tk reached -> 80% reaches 17-18, hold unless price trades below prior bar low; reversal 1tk shy of round target = weakness.
22. Scalp vs swing (ch24.E, ch25 #71-72): decide before entry, never convert; ES ADR 10-15: risk ~2pt, swing tgt 4pt, scalp 2-4pt then swing balance; range traders 2-3pt, reversal traders >=4pt; OCO bracket then walk away; beginners swing 1-3 trades/day only.
23. Sizing (ch15, ch24, ch25 #27-29): fixed dollar risk; stop k x normal -> size 1/k (floor 10-20% on extreme days); first hour 1/2-1/4 size; "I don't care" size; too large if you skipped 2 winners in a row.
24. Second entries (ch13, ch24): "always worth taking"; after first signal against strong momentum fails, second within ~5 bars gets +0.10 P; two failed attempts at same thing -> opposite usually follows.
25. Climax (ch4): any unsustainable run; 2 consecutive climaxes = DT/DB, 3 = wedge; after 3rd expect >=10-bar 2-leg correction, no H1/H2 for ~10 bars; largest bar of move after 10-20+ bars = exhaustion; steeper-trend after it <30%.

### 1b. Reversal strength scorecard (ch2) — booleans, more = higher P, swing more (bull reversal; mirror bear)
- reversal bar: large bull body, tails small/none; spends most of bar near high, intrabar pullbacks <1/4 range.
- next 2-3 bars bull bodies >= avg recent body size.
- spike 5-10 bars with <=1 pullback bar; reverses many bars / swing highs / bear flags.
- >=1 spike bar low at or 1tk below prior close; >=1 opens above prior close (gap); >=1 closes on high or 1tk below.
- breakout bar closes above highs of many prior bars (5 to 20+; closes reversed count more than highs).
- first pullback only after >=3 bars; lasts 1-2 bars; does not hit entry price; follows a non-reversal bar.
- spike breaks several levels (EMA, swing highs, TLs) by many ticks.
- urgency: no pullback comes.
- second signal within few bars; began as TCL overshoot reversal; reverses a significant swing low.
- H1/H2 pullbacks have strong bull signal bars; trending closes/highs/lows/bodies; small sideways pullbacks.
- prior bear TL breaks earlier (not first sign); test of bear low: overlap, bull bodies, fails at EMA / old bear TL.
- required strength scales with trend strength: very strong bull needs many; two-sided bull accepts weaker; rally to TR top may need no reversal bar.
- TL break strength: momentum, surge well past EMA, beyond prior-trend swing points -> more points, longer, >=2 legs.
- countertrend requires TL break or climactic TCL overshoot; in TR trade both ways.

### 1c. Pullback / continuation mechanics he relies on (PI, ch3, ch9, ch16)
- strong bull: bulls buy limit few tk down, at/below prior bar low, stop above prior bar high, above swing highs, closes of bull and bear bars; bears step aside; pullbacks allow at most 1 bar against (rarely 2).
- trend maturing: larger bear bars, tails on tops, bulls stop buying above swing highs, take profits at new highs -> TR -> 50/50 -> bears.
- once a pullback is well below TL and EMA: new high = short opportunity (tipping point).
- retracement rule: <=50% pullback in swing: P>=.60 reward=risk (target spike bottom); >50%: P~.50 -> need 2x, enter ~67% (61.8% not special).
- first big pullback in strong trend usually tests 15m EMA; first pullback after TL break tests signal bar / entry bar / TL / swing / EMA.
- breakout bar close 1tk beyond EMA = weak; strong breakouts close several ticks beyond.
- consecutive closes beyond EMA that fail (2) -> trend intact.
- eager-trader tells (with-trend): pullback turns 1tk short of prior swing; stops 2tk short of EMA (not 1); L1 after a bottom fails to make new low.
- magnet rule: pullback not complete until magnet (EMA) touched; within 1tk is not enough.
- stop cascade: shorts' stops above breakout bar high / triple top / LH / climax high / PDH within 1-2tk -> rapid cascade.
- market "races" to top/bottom of a 20-bar range to trap stop entries (middle third).
- big bars + 2x bars: size/2-/3, stop beyond signal bar often 2x normal; if then weak, exit at 1-2pt.
- 1m: never countertrend; use 1m H2/L2 only to enter a runaway 5m trend; 1m countertrend stop = with-trend entry location.

## 2. Day structure (Part II + III)
### 2.1 Time windows (ET)
- Thirds (ch11): first 9:30-~11:30/12:30; middle ~11:30-14:00/14:30 (sometimes 15:30); final to 16:00.
- First 1-2h: best odds of 2-3x risk; "most important time"; HOD or LOD formed in first third ~90% of days; within first 5 bars 50% of days; first 90 min 90% (ch16/19).
- Reports: 8:30 ET premarket (quick trends/reversals); 10:00 ET (often sets trend of day, market acts as if a report exists even when none); FOMC 14:00/14:15 ET (large bars, outside bars, several reversals for 30 min). Blackout 1-3 bars after; P~50% inside; slippage doubles risk (8tk -> 16tk).
- Midday reversal window 11:00-12:30 ET, modal 11:30; trend often begins or reverses ~11:30 after conventional OR (ch11, fig19.6/19.8).
- Middle third = TR/tight TR/dojis/no follow-through; worst for stop entries; institutions buy low sell high on limits; if middle-third losses > first-third gains, do not trade it (ch11, ch24.G).
- Pullback 13:30-14:00 ending ~14:30; later pullbacks deeper after 14:00; move ~14:30 often carries into close (resumption or breakout) (ch11, fig15.3).
- Final 30-60 min: daily bull -> most days close above open, rally into close (21/32 example); daily bear -> sells into close. Type1 relentless: enter at bar close, stop other end of bar. Type2 big tails + 2-3 stop runs: swing with wide stop. Dojis appear -> stop under 2nd big bar of spike. No new reversal trades in last hour you would not take in first (ch25 #65).
- 3-period shapes: up-down-up or down-up-down; final third usually resumes first-third trend (resumption day) sometimes reverses.
- 15m bar check (ch17): breakout of bar 3 (close of first 15m bar) after bars 1-2 trended and bar 3 is a pause bar -> significant; confirmation flag only.
- Holiday weeks: only first hour normal, tight TR after.

### 2.2 First bar / first-hour patterns
- "First hour" = time before first good swing, 15 min to 2 h = opening range (OR).
- Bar 1 ~20% of day range (range_est = bar1 x 5); bar 1 is extreme 20%; strong trend bar 30%; large gap + strong trend bar 50%+. High-P first-bar trades ~1/month; swing on bar 2 rarely worth it.
- Bar 1 breakout math: ADR 10, bar1 2pt -> buying its break ~20% to make 8 risking ~2 = negative.
- Bar 1 trend bar with prominent tails = one-bar TR; fade its breakouts, scalp, <=2 scale-ins; reversal within 1-2 bars expected.
- Bar 1 doji inside yesterday's final-hour tight range with flat EMA -> range day odds up.
- First several bars overlapping with tails / >=5 reversals in first hour / barbwire first 90 min -> range day.
- Gap + 3-4 bar spike, large bodies, small tails, little overlap -> trend day (may be spike of spike-and-channel).
- 2 consecutive bull trend bars in first hour -> always-in long at least for a scalp; 2 bear -> sell scalps.
- First-hour scalp template: 2 strong bull bars then doji -> limit buy at/below doji low; risk ~bar height (2pt ES at ADR 15) to make same, ~60%.
- First-hour reversals: each has ~30% for 2:1 swing, ~60% for 1:1; "only ~25% of first-hour reversals result in swings"; one per day ~60%; reasonable swing setup exists >80% of days; setup for HOD/LOD typically 30-50% (ok for swing); never >30% certain a reversal is NOT the extreme.
- Opening reversal equation (ADR 10-15): 4pt swing 40% (50-60% very strong), 2pt stop hit first ~30% -> ~1.6 pt/trade over 10 trades.
- HOD usually imperfect double top; LOD imperfect double bottom; once DT/DB forms, 40-50% to be the day's extreme; wait for DT/DB before swinging a reversal.
- Reversal often looks bad for 5+ bars (2-3 weak dojis) then breaks out; do not scratch.
- First 5-10 bars sideways -> institutions enter breakout of that range, often trend day; prefer EMA-test entry before breakout.
- Steep/tight wedge in first 1-2 h can be a reliable opening reversal; never fade such a wedge later in the day (ch5).
- First-hour DB/DT flags mostly tradable but scalp part + breakeven (ch9); first ~90 min opening reversals with big tails justify longs without prior rally (ch8).
- Bond trader anecdote: 85% of profits in first hour; stopped 10:30-11:00 ET.

### 2.3 Opening range (ch19)
- OR = TR height or largest leg of first 30-90 min (6-18 bars); S/R and MM projector for rest of day.
- OR ~25% ADR -> breakout mode either direction, 1tk beyond OR, opposite side = stop; a couple times/month trend-from-open.
- OR 1/3-1/2 ADR -> expect growth to ~ADR; 2/3 trend day (usually trending TR day): breakout reaches ~1 OR-height MM, later retests breakout point, often re-enters; strong re-entry closing past opposite side = reversal day ("most common reversal-day form"); other 1/3 small range day.
- OR large (strong spike) -> spike-and-channel; trail, do not target; sometimes climactic reversal after small final flag.
- Tiny range >30 min (6+ bars) on large-gap day -> breakout mode stops 1tk beyond; if reversed after entry double stop and reverse.
- Early TR in first 3-10 bars with 2+ reversals and small vs ADR -> breakout likely; enter breakout for MM, or fade small bars at extremes, or wait failed breakout/breakout pullback.
- Day range at ~half ADR anytime -> expect MM extension; right after bears cover, up more likely for few bars (ch16).
- Low-range day: range 2pt vs ADR >10 -> expect 2-3x expansion before close; take 50% / 4tk risk / 16tk reward lower-high short (ch24.E).

### 2.4 Gaps (ch18, ch20)
- Gap (any TF) = bar closes without overlapping prior bar; most days have a 5m gap open; treat as breakout of yesterday's last bar.
- Large gap = largest of past ~5 days OR > 0.5 ADR. Large gap up: ~50% bull channel, ~20% TR, ~30% bear. Larger gap -> trend day more likely, gap = invisible spike then channel.
- Large gap: assume strong trend will come but may take ~1h; often begins with 2-legged countertrend to EMA / DT / DB, sometimes 3rd push; first 5-10 bars usually TR behavior.
- Large gap up then sideways -> 60%+ bull trend day; target ~ADR (20pt example); risk gap close (~10pt) or gap midpoint (~6pt) to make 15-20.
- Gap up + bull bar 1 -> trend-from-open bull; gap up + doji bar 1 -> two-sided drift down hours then bulls; gap down + bull bar 1 -> trend-from-open bull; gap down + doji bar 1 -> sideways hours then bear spike.
- Large gap down + strong bear bar 1 -> possible trend-from-open bear; + strong bull reversal bar 1 -> failed breakout, possible LOD.
- Large gap up + strong bear reversal bar 2 = reliable always-in short, but often sideways-down ~1h then bull breakout; stay willing to reverse (fig15.3).
- Gap often has 2-legged pullback to EMA (DT bear flag, gap=flagpole) then breakout (fig19.6).
- Gap up to EMA in strong bear = breakout pullback short; gap up breaking yesterday's steep bear TL = breakout pullback long; both -> TR start.
- Gap down out of yesterday's bear flag + below EMA = strong bears, expect MM down (ch16).
- Swing part of every trade on gap days (one swing = 10 scalps); EMA unreliable first ~60 min on gap days; use momentum (Globex and day-session EMAs diverge for 1-2 h).
- Gap proxy: bar 1 entirely above EMA = gap up, below = gap down.
- Market usually tries to test gaps -> look for trades in that direction (fig13.7).
- Daily chart (ch22): gap open -> do not enter on the gap; wait pullback into gap, buy opening reversal, stop below today's low, at most one retry. Open inside yesterday's range -> stop 1tk beyond the range.

### 2.5 Overnight / yesterday levels (ch14, ch17, ch18)
- Globex H/L are targets tested in day session; Globex patterns complete within first many day-session bars; pick Globex or RTH chart, not both; day-session TL/TCL spanning 2+ days very reliable.
- Yesterday's high always resistance, low always support; reversals and targets cluster there; need >=4-5tk room between signal bar and PDH/PDL/EMA for a 1pt scalp.
- Pre-open: inspect yesterday's final 1-2 h (trend/TR/channel/flag); yesterday's final always-in direction carries into open until the 2-bar flip rule fires.
- Yesterday's final-hour channel is a flag (bull channel = bear flag); today often gaps beyond or breaks out of it.
- Every open: (1) breakout: follow-through? (2) failed breakout? (3) failed failure -> breakout pullback.
- Opening reversal reversing PDH/PDL often = HOD/LOD -> swing most; second failed break of PDH -> opposite direction; market often reverses breakout of PDH/PDL (fig19.9).
- Bear follow-through few bars then strong bull reversal = failed breakout, possible LOD; rally 1-2 bars then strong bear bar = breakout pullback short.
- Double bottom with yesterday's closing low / first bar of day -> LOD candidate (fig PIII.2, 18.6).
- Yesterday's close = first leg: opening LL test of yesterday's bear low = H2 + DB with yesterday's last bar (fig18.6).

### 2.6 Guessing day type early
- Trend day: large gap + trend first 4 bars; 3-4 bar spike w/ small tails; OR 1/3-1/2 ADR then breakout (2/3 trend); daily chart strong trend; 2 large bear bars in first 15 min then DT bear flag = reliable bear day (stocks).
- Range day: bar 1 doji in yesterday's close range + flat EMA; barbwire first 90 min; 5 reversals first hour; big up + big down (climactic) = confusion = TR.
- "Most reversal days begin as trending TR days"; OR ~half ADR -> breakout to trending TR, then pullback test; reversal day = strong re-entry past OR opposite side.
- A strong bear leg on a not-yet-bear day does not make it a bear day (still TR) (ch21).
- Small OR -> small pullbacks all day; final ~2 h usually has one pullback ~2x earlier pullbacks.
- After a strong first-hour trend: reversal often at start of middle third (11:00-12:30), else range for hours then breakout final 1-2 h.
- Always-in decision ~11:30 ET (8:30 PST, ch25 #54): decide which trend pattern the day resembles; trade only that way.
- Beginner EMA rule (ch25 #73): 7 of last 10 bars above EMA -> buy only; 7 of 10 below -> short only.

### 2.7 Always-in flips (ch15)
- Flip = breakout + follow-through; after breakout bar, close of next bar decides: min for flip short = follow-through bar NOT bull close (small bear/doji = weak flip -> sell L1/L2, not closes); min for flip long = not bear close.
- Follow-through extends few ticks beyond breakout bar -> failed-breakout bias; many ticks -> trend. Opposite strong body = failed breakout (trap) signal.
- Weak drift against always-in (channel, no opposite spike) does not flip; keep stop, scalp mode.
- Range days: flip only on strong breakout of entire range + follow-through; sharp move inside range toward an edge is not a flip = where to fade; sell vacuum spikes near LOD -> buy failed breakout, do not short.
- Wondering whether it flipped = uncertain = TR.
- Strong trend -> TR: always-in unchanged, scalp only with trend; tight TR: do not use always-in.
- Once always-in: enter at least small position at market or tiny pullback (low-momentum trends run without pullbacks); strong 3-bar reversal spike off open: buy at market, if stop 8pt vs normal 2 -> 1/4 size, "must get long".
- Always-in long entries: close of any bear bar, below prior bar low, below prior swing low, below bull TL; shorts mirror.
- Near-flip = with-trend entry (buy close of strong bear bar in bull; buy if next close not bearish; buy above its high).
- Breakeven rule: pullback that would have hit BE then resumption for several bars -> move to BE; second pullback hitting it with uncertain direction -> stay flat.
- Expect trend after always-in to last >=2 h and cover >=1/3 ADR (friend); bracket stop beyond signal bar, target MM/SR >=2x stop; 2pt stop -> 4+pt target, >=60% equidistant, ~50% for 2x.
- General: trend continues about the same ticks as required stop with P>50%, >=60% if always-in confident.
- Scale-in (ADR 12-15, largest 2h pullback 2pt): buy 1pt down, add 1 and 2 lower (10-20% ADR), whole-position stop couple pts lower; exit on flip.
- Timing: always-in mode usually entered in first hour; 3-10 significant swings/day; take strongest 2-5.
- Most exit some at 2-3x risk; institutional profit taking creates the pullback where they re-enter.
- Daily/weekly signals ignored intraday except PDH/PDL (ch22).

### 2.8 Charts, markets, multi-TF (ch12, ch13, ch16)
- 5m ES: ~81 bars/day, ~12 good entries (3m ~20, 1m ~30); 20+ reversals/day most too small; 30-40 scalp setups/day (1/3 stop, 2/3 limit); half of all bars have a scalp setup.
- smaller TF -> more missed trades, lower win %; "pick one TF, do not wait for alignment"; 15m / 10k-tick: 3-5 decisions/day.
- tick/volume charts: same patterns; more bars in first and last hour (volume); TLs less precise; close unexpectedly fast.
- 1 ES = 500 SPY; ES tick = 2.5 SPY tk; SPY hits 1tk stops ES does not (use 2-3tk); QQQ = NQ; stocks: ADR >= several $, vol >= 5M.
- 60m filter variant: 5m longs only when 60m above its EMA (or stochastic rising).
- 60m 1-tick trap: 5m reversal 2 bars after a 1tk break of prior 60m high usually reverses back before 60m bar closes.
- 15m bar = 3 x 5m; 60m = 12 x 5m; last 5m bar of higher-TF bar decides breakout vs failure.
- VIX/16 = expected ADR % (VIX 32 -> 2%, 50 -> 3%); scale stops/targets by it (ch23).
- Emini volume: unreliable intraday; exceptions: bar with 10-20x recent volume -> more follow-through; spike with 10-20x vol and range >=5x -> MM up usually.

## 3. Reversal catalogue
format: def -> entry -> stop -> target -> P -> invalidates. mirror for opposite side.

### 3.1 Major trend reversal (MTR, ch3, ch24)
- def: (1) trend on screen; (2) countertrend leg breaks TL and reaches/exceeds EMA; (3) test of extreme: HH/DT/LH at top, LL/DB/HL at bottom (tests often 2-legged; exact-tick DT rare); (4) second reversal with strong signal bar; usually begins as micro DT/DB or final flag.
- entry: stop 1tk beyond reversal signal bar at the test; prefer second entry (LH after a top, HL after a bottom); after strong follow-through enter at market/pullback.
- stop: 1tk beyond signal bar (bear: above signal/strong bear bar after it); after flip tighten to start of new spike.
- target: >=2x risk; test of prior-trend swing points; MM = leg1=leg2 / spike height / TR height; expect >=2 legs >=10 bars; higher high test -> 2 legs down; lower high test -> may be 1 leg.
- P: avg 0.40-0.50 swing (0.70 at least small profit); strong 0.60+; waiting for flip >=0.60 with less reward; ~70% end as TR not opposite trend; P>60% versions a few/week, 50-60% almost daily; bears fail to reverse bull 80%.
- invalidates: TL break leg does not reach EMA; test leg tight steep channel, no pullbacks; HH >=5 bars above old high (restart); any of the 4 components missing = no trade; test with too much momentum -> wait for channel breakout + breakout pullback.

### 3.2 Climactic / spike reversal (ch4)
- def: climax = trend bar(s) with large range, little overlap, often largest body of move (~2x other bars, opens near one end closes near other); climactic reversal = climax then sharp opposite spike = failed breakout; parabolic/V = TCL overshoot + reversal; 2 consecutive climaxes = DT/DB, 3 = wedge; third climax usually most dramatic.
- entry: short buy-climax bar at its close / above its high / close of next 1-2 bars (esp. bear body) / below prior bar low; or stop below bear reversal bar; buy exhaustive bear bar at close / below low / close of next smaller or bull bar / above prior bar high; strong bull bar after -> buy close and above high; small bar after large climax = abating = trigger.
- stop: ~height of climax bar in ticks (or usual 2pt); P(test of bar extreme before stop) >=0.60; wider stop -> smaller size.
- target: bar extreme (T1), MM = bar height (T2), EMA test, new HOD/LOD; expect >=2 legs >=10 bars to EMA; after TCL overshoot failure min target = opposite TL.
- P: ~0.60 for 2 legs + 10 bars; 3 consecutive climaxes >=0.60 of complex correction; 40-bar trend w/o pullback + largest bull bar -> steeper trend <30%; TCL breakouts fail within ~5 bars usually.
- invalidates: climax bar breaks support/resistance with follow-through (MM first); reversal leg does not break TL (TR/continuation more likely); small entry bar in strong trend (becomes flag); no countertrend momentum; consecutive climaxes each worked off by ~10 sideways bars (no exhaustion); with-trend spike tops get tested and exceeded. Sell climax after >=10 bars down -> good reversal chance; before that, pause only.
- post-climax: no re-entry with trend until >=10 bars + 2 legs; no setup after 10-20 bars -> trend reversed.

### 3.3 Wedge / three-push (ch5)
- def: 3 pushes (3 swing extremes each beyond prior), converging TL/TCL (may be parallel stairs or expanding); family: micro wedge, parabolic wedge, wedge flag, triple top/bottom, H&S, DT/DB pullback, failed DT breakout; reversal wedge needs >=20 bars + clear TCL; flag wedge 10-20 bars (take first signal, with-trend); wedge in TR = flag.
- entry: stop 1tk beyond signal bar at push 3; countertrend default = wait second signal (LH after top, HL after bottom, within ~5 bars); first signal only if exceptionally strong (TCL overshoot, shrinking stairs, parabolic 3rd push); strong breakout -> trade it as breakout / enter breakout pullback.
- stop: beyond push-3 extreme; to breakeven after first strong leg + LH.
- target: T1 = wedge bottom (pullback low after push 1); T2 = wedge height projected from T1; expect >=2 legs ~10 bars; ES often retests wedge top to the tick (second-entry short).
- P: majority of 3-push reversals happen after TCL overshoot; first-entry countertrend ~0.40 at 2:1; breakout-bar entry >=0.60 at 1:1; 3 climaxes >=0.60 complex correction; stairs push 3 extension < push 2 extension (7tk vs 10tk) raises odds.
- invalidates: price beyond wedge extreme after entry -> failed wedge -> MM = wedge height beyond extreme (breakout usually strong bear/bull bar); unusually strong push 2 -> count reset, expect 4th push; no prior TL break / small pattern (3 pushes alone rarely reverse); tight channel (wait breakout + pullback); >=4 overlapping bars at push 3 = acceptance; steep bear channel -> require HL; failure that reverses again = HH/LL breakout pullback of wedge -> new trend >=10 bars 2 legs.

### 3.4 Expanding triangle (ch6)
- def: >=5 swings (7, rarely 9), each extreme beyond prior (HH and LL); bottom = 3 pushes down with HHs between; always an MTR variant (push-2 rally breaks bear TL); 5th-leg LL = breakout pullback + LL MTR.
- entry: buy stop 1tk above the bar at the 5th-leg LL; mirror top. Second-chance: many bars between leg 5 and next LL -> treat as DB reversal.
- stop: beyond 5th-leg extreme (reduce size if large).
- target: T1 = breakout of opposite side (new swing high) "usually as far as it goes"; T2 (if T1 breakout holds) = MM ~ height of last leg; dojis mid-leg -> midpoint = rough target.
- P: not stated numerically; "always" MTR setups; TCL failed breakout + ET -> usually 2 legs.
- invalidates: T1 breakout fails -> 7-leg continuation ET flag, target = new extreme in original trend then MM = last leg; bad proportions (one leg far wider); in possible new bull with strong momentum, wait for LH before shorting the ET top.

### 3.5 Final flag (ch7, ch24)
- def: last flag before reversal; likelihood up when trend ran dozens of bars, flag horizontal with 2-sided bars (opposite bodies, tails, >=50% overlap), tight TR after trend, flag after climax; size any (1-bar pause after big spike = 1-bar final flag; usually 5-10+ bars); usually H1/H2/L1/L2/triangle/ii; barbwire often a final flag.
- 3 resolutions (bull flag): (1) breakout above old high then reverse = HH reversal; (2) weaker breakout reverses below prior high = LH reversal; (3) no breakout: H2/H3 triggers, entry bar reverses after 1-2tk, or flag breaks down -> spike then bear channel to MM = flag height.
- entry: stop 1tk beyond reversal bar after the flag breakout; after bear flag failed L2/L3 + large bull bar = flip long; limit fades of first flag after a reversal (buy at/1-3tk below L1/L2 signal bar low, risk ~4tk ES).
- stop: beyond reversal bar; breakeven after first leg.
- target: >=2 legs sideways-to-opposite, ~10 bars; back into flag (magnet); climax 1-bar flag: 2-legged pullback >=10 bars but extreme frequently retested within 10-20 bars (countertrend trade, not reliable reversal); best: first leg beyond flag, sideways flag above old flag, continue -> swing.
- P: strong final flag reversal after swing in TR/weak channel 0.50-0.60 at 2:1; trend 50-100 bars -> outcome more likely large flag/TR than opposite trend; monthly Dow 13 cases: 4 reversals, 4 pullbacks, 3 ordinary flags, 2 failed.
- invalidates: failed final flag = reversal entry fails within ~2 bars -> breakout pullback in trend (short entry bar becomes bull reversal bar -> buy above); resumption only 1-2 bars then reverses = second entry; second failure -> channel mode, stop fading; flag only ~4 bars after strong momentum w/o TL break -> expect sideways then new extreme; breakout confirmation needs trend bar close several ticks beyond flag boundary, else pullback premise survives.

### 3.6 Double top / bottom pullback (ch8)
- def: DB pullback = sell-off -> DB (2nd bottom preferably slightly below 1st; also H&S bottom) -> rally -> HL pullback testing just above DB -> buy; = 3-push bottom / breakout pullback / two failed attempts (L2); inside bar after small DB counts as the pullback; push-3 location irrelevant (above = DB pullback/triangle, at = triple bottom, below reversing = failed breakout/final flag).
- entry: buy stop 1tk above signal bar at pullback low (outside-up bar / close of or above next bull trend bar); DT pullback: sell stop 1tk below low of pullback-high bar.
- stop: beyond signal bar / pullback extreme; breakeven after scalp.
- target: swing >=2x if prior TL break/rally exists; else scalp only (reversal w/o prior rally -> TR); MM = pattern height.
- P: good shape + strong reversal bars at all 3 bottoms = "one of most reliable buy setups"; range fade with good setup ~0.60 at 1:1; strong breakout of tight range 0.70+ at 1:1.
- invalidates: 2nd bottom fails to reach 1st in strong bear (5c above "usually negates") -> scalp or skip; strong bear w/o prior TL break = bottom picking; weak DB -> short L2 at EMA instead; DT and DB in same range -> triangle, breakout mode, usually resolves with prior trend; DT bear flag in bear = always an L2 short (fast move).

### 3.7 Failed breakout (ch9, ch19, ch15)
- def: breakout beyond swing/TL/TCL/range/PDH/PDL/magnet that reverses; 1-tick failed breakout (1-2tk ES; 1-10c stocks) = reliable opposite sign; 5m 1tk failure often a 15/60m 1tk failure while that bar forms; most breakout attempts fail (80% in TR); 1-tick new extreme that immediately reverses = failed breakout + DT/DB -> fade.
- entry (TR day, modest momentum): price above prior swing high -> sell stop 1tk below prior bar low; unfilled at close -> move to 1tk below the bar just closed; repeat until momentum too strong, then wait pullback breaking minor TL and short next swing high; mirror longs. Entry stop at trapped traders' stops (1tk beyond their signal/entry bar) -> at least scalp, usually 2 legs; trapped shorts off doji entry bar exit 1tk above it = buy there.
- stop: beyond failure bar extreme / breakout extreme.
- target: scalp minimum; opposite side of range (fade P 0.60-0.80 of test); failed DT breakout = wedge top -> at least scalp, sometimes MM = range height; channel re-entry -> 0.50 chance of reaching opposite channel line; failed TCL breakout -> opposite TL, 2 legs ~10 bars.
- P: range fade good setup 0.60 at 1:1; 1tk failures common in ES; outside-bar entries mostly fail.
- invalidates: strong trend (buy stop above range top instead, expect another leg); breakout with follow-through many ticks; trend day -> fade new extremes only after minor TL break + strong reversal bar; 3 one-tick failures in a row is rare -> next move runs; successive 1tk breakouts (2x 1tk w/ 3-20 bar pullbacks, then 3rd break) -> real breakout, target = range height; huge no-tail trend bar -> expect stop run 1tk beyond within 5-10 bars then resumption.

### 3.8 Failed failure / breakout pullback (ch9, ch18, ch25 #35)
- def: failed breakout that itself fails = breakout pullback in original direction; best "countertrend" trade is with-trend on higher TF; after a failed-breakout reversal, enter opposite only if the failure fails; "all patterns fail and failures often fail, high probability".
- entry: stop 1tk beyond pullback bar (e.g. short 1tk below bar after a 1-2 bar rally following strong bear bar; small bar above middle of breakout outside bar = low-risk short); breakout test: pullback to entry price within 1-2tk missing BE stops by 1tk and reversing -> enter with trend above that bar.
- stop: 1tk beyond pullback bar and beyond prior swing (wedge low).
- target: test of trend extreme (first pullback almost always followed by test of extreme); MM.
- P: breakout pullback after a flag breakout = named best trade; stop run then resumption "as reliable as traders trapped in", at least scalp; after strong breakout bar expect >=2 more attempts in its direction (L2 right after it likely fails -> breakout pullback long).
- invalidates: pullback breaks a significant TL and reaches EMA (then it is a test, not a pullback); second failure of the pullback -> channel/TR.

### 3.9 Head and shoulders (PI, ch3, ch9)
- def: H&S top = triangle/triple bottom/wedge bull flag; head-to-neckline leg = bull flag, right shoulder rally = its breakout; two right shoulders common; most H&S bottoms fail.
- entry: short LH right shoulder only if head-to-neckline leg broke the whole bull TL + reached EMA; else buy neckline test (triple-bottom bull flag).
- target: break above right shoulder -> MM up = right shoulder height or whole pattern; neckline break usually fails.
- P: shape alone insufficient; require prior countertrend strength.
- invalidates: weak head-to-neckline sell-off; neckline break without follow-through -> MM up.

### 3.10 Micro double top/bottom, ii, two-bar reversal (ch3, ch9, ch21, ch24)
- def: micro DT = failed H1/H2/triangle buy (bar with big lower tail after a high = first bar of micro DT); micro DB = failed L1/L2; both = small final flag reversals; most tradable reversals begin as one; ii = often final flag before 2-leg countertrend, valid only after earlier TL break; 2-bar reversal = opposite climax on higher TF.
- entry: short below low of micro-DT second bar; buy above ii / 2-bar reversal (beyond larger bar); untriggered 2-bar reversals ignored.
- stop: beyond pattern extreme; micro DB MM ~2x its height.
- target: scalp min; swing if TL break context; 2 legs >=10 bars for large bottoms.
- P: second-entry 2-bar reversal at ET bottom + final flag + strong bar ~0.60 swing (fig24.3).
- invalidates: strong trend without prior TL break (becomes flag); ii after reversal bar with false breakout of ii top -> continuation.

### 3.11 TL / TCL break reversals and stairs (PI, ch4, ch24)
- TCL overshoot + reversal: most TCL breakouts fail within 1-5 bars, re-enter, poke opposite TL; expect >=10 bars 2 legs; second failed TCL breakout more reliable; drawing many TCLs = blindness, assume channel lasts.
- TL break (no overshoot) in bull -> >=2 legs down ~2/3, fail 1/3; TL break must reach EMA; first spike through TL in strong trend = "sale" (buy its close), first attempt almost always followed by new high.
- Stairs: bear stairs buy 3rd/4th push down, target = prior push low; bull stairs sell 3rd/4th push, target = prior push high.
- 5-10 bars hugging a TL -> break soon (ch22); 30+ consecutive EMA gap bars -> >95% EMA touch within 10 bars (ch23); 15 consecutive bull bars = climactic -> >=10-bar 2-leg correction below EMA.
- Huge-volume daily reversal (ch10): volume 5-10x avg in steep bear + gap down + strong bull close -> buy close; expect >=2 legs to EMA over days; climactic volume w/o bull close = no fade (BSC -80%); never use volume on 5m.

### 3.12 Spike-and-channel and channel ends (ch4, ch5, ch21, ch24)
- def: spike then channel; channel commonly 3 pushes w/ wedge shape; spike-and-channel bear usually ends on 3rd push; tight channel before final low = final flag.
- after channel ends: retrace to ~start of channel (tested within 1-2 days); bulls take profit there, bears re-short there.
- after 20-30 bar channel, correction lasts >= half as many bars.
- channel re-entry after TCL break: ~50% reaches opposite side; most TCL breakouts fail within 5 bars; re-entry pokes opposite TL.
- bear channel = bull flag; bull channel = bear flag (higher TF); breakout above a bear channel on open -> breakout pullback buy.
- first break above a bear channel has no follow-through; second attempt (breakout pullback) does.
- steep bear channel: buying every TCL overshoot reversal loses; wait for strong breakout (gap up) then breakout pullback / 2nd attempt to reverse PDL.
- micro channel (>=4 bars no overlap of prior extreme): do not fade first breakout; enter first pullback after breakout; counter micro channel's failed breakout in strong trend = with-trend breakout pullback.
- channel with large swings (two-sided) is not a strong trend -> first-entry wedge reversal acceptable.
- invalidates: 3rd push extends well beyond 2nd and holds (TCL overshoot that does not reverse within 5 bars) -> trend stronger; expect test of opposite side only after reversal.

### 3.13 Trading-range reversals (ch8, ch9, ch15, ch24)
- def: TR = most of the time (>=80% non-trend); swings 5-10+ bars then TL break then opposite swing; HOD/LOD of range days from DT/DB.
- entry: fade second entries at extremes; short below bear bar near top (more reliable than below bull bar); buy above bull bar near bottom; limit fades of weak H1/H2 at top (experienced).
- stop: beyond signal bar.
- target: opposite side (P .60-.80 test), middle for scalp; successful breakout -> MM = range height.
- P: fade good setup .60 at 1:1; mid-range ~.50; strong breakout of tight range .70+.
- invalidates: strong breakout with follow-through (then trade the pullback); up/down >=5 bars rule applies (no longs after 5-10 bars up in a range).
- after a strong move a TR is usually continuation; 2 failed breakouts same side -> breaks other side; DT + DB in same range -> triangle -> usually breaks with prior trend.

### 3.14 Opening reversal (ch18, ch19)
- def: sharp move off open into a level (EMA, PDH/PDL, Globex H/L, TL, MM, swing) then reversal (vacuum mechanics); often HOD/LOD.
- entry: stop 1tk beyond reversal bar; stronger if DT/DB with bar 1 or yesterday's extreme, second attempt, final flag, bar closing beyond midpoint.
- stop: beyond reversal bar; first hour size 1/2-1/4.
- target: swing >=2x (4pt ES), scalp 1:1; partial 1/3-1/2 at 1-2x risk; rest to opposite always-in / BE / close.
- P: 4pt swing .40 (.50-.60 strong), stop hit first .30; 2:1 per reversal .30, 1:1 .60; strong checklist setup >=.60 for several x.
- invalidates: reversal lasts few bars then resumes = failed reversal = breakout pullback -> channel (spike-and-channel day); strong spike + weak reversal bar -> assume failure, buy stops above prior bar high.

## 4. Best trades (ch24) ranked as he ranks them
rank | trade | entry | stop | target | P
1 | High-probability swing (very best): always-in reversal or pullback in strong trend | stop 1tk beyond signal bar; or at market once always-in clear | beyond signal bar / spike start | >=2x risk | >=0.60; 2-3/day
2 | Strong breakout follow-through (his preferred) | close of bar 2-4 of spike or 1-2tk pullback; limit at/below prior bar low in bull spike | spike bottom (far end), smaller size; very strong: risk <0.5 spike height | = risk min; MM = spike height | >=0.60 at 1:1; ~0.70 at 2x when very strong; often >0.70
3 | H2/L2 (wedge, triangle) at EMA on strong trend day = "single most reliable day trade" | stop above bull signal bar at EMA (bull) / below bear bar (bear) | beyond signal bar | scalp = risk, swing part; 5-10/day scalp version | >=0.60 at 1:1; post-spike L2 at EMA with bear signal bar >=0.70
4 | H1 in strong bull spike (not after climax) / L1 in strong bear spike (not after sell climax) | stop 1tk beyond first pullback bar | beyond signal bar | test of extreme, MM | ~0.60 (ideal when no climax)
5 | Opening reversal, strong setup (e.g. gap up, EMA pullback, DB with bar 1, strong bull reversal bar) | stop 1tk beyond reversal bar | beyond signal bar; first hour size 1/2-1/4 | swing >=2x; scalp = risk | swing 0.50-0.60; scalp 0.60-0.70; example >=0.60 for several x risk
6 | MTR (all 4 components) | stop beyond second-reversal signal bar | beyond signal bar, then start of new spike | >=2x; expect pullback before target | 0.50-0.60; >0.60 a few/week
7 | Final flag reversal after a swing in TR / weak channel | stop 1tk beyond reversal bar after flag breakout | beyond reversal bar | 2 legs ~10 bars, >=2x | 0.50-0.60
8 | Breakout pullback after breakout from bull/bear flag; breakout test running BE stops | stop beyond pullback bar; limit below bull bar that broke the flag | beyond pullback bar / signal bar | new trend / MM | high (reliable scalp min)
9 | Range fade at top/bottom, esp. second entries; best when move into extreme was strong | stop 1tk beyond signal bar at extreme; limit at/beyond weak H1/H2 (experienced) | beyond signal bar | opposite side of range | 0.60 at 1:1; 0.60-0.80 test of opposite side; mid-range P~0.50
10 | Not clearly trending: L2 at ~prior swing high / H2 near prior swing low; up 5-10 bars -> shorts only, down 5-10 -> longs only | stop beyond signal bar | beyond signal bar | prior swing / opposite side | ~0.50-0.60
11 | Stairs 3rd/4th push fade; spike-and-channel MM fade when weakening | stop beyond push extreme | beyond signal bar | prior push extreme / channel start | not stated
12 | Consecutive buy climaxes short (2nd-4th climax) | climax close / next bear bar / below doji; small size, scale in higher | beyond climax high | 2-leg pullback to EMA | experienced only
13 | Low-range mid-range short (2pt range day, ADR>10) | stop below 3rd fall below prior bar low | 4tk | 16tk OCO | 0.50
avoid: countertrend scalps; tight TR / barbwire / midday flat-EMA mid-range; stop-entry range breakouts; 1m/tick execution; reversal missing any component; doji signal bars; sudden big bar after 30-60 min of nothing; reports; after a losing month no reversals.

### 4b. Limit/market-order best trades (ch24.C; experienced; always with always-in direction)
- buy bull spike at market or at/below prior bar low (wider stop, smaller size); sell bear spike at market / at or above prior bar high.
- sell close of bar 2/3/4 of strong bear spike; stop above spike top; P>=.60 at 1:1; very strong spike: risk < half spike height, P~.70 for >=2x.
- buy at/below weak L1/L2 signal bar in possible new bull after strong reversal, or at range bottom; short at/above weak H1/H2 at range top or after strong reversal down.
- buy at/below prior bar in quiet bull flag at EMA; short at/above prior bar in quiet bear flag at EMA.
- buy below a bull bar that breaks above a bull flag (anticipating breakout pullback); sell above bear bar breaking below bear flag.
- swing add on breakout test (attempt to run BE stops).
- buy pullback in strong bull at fixed tick count = or slightly less than avg prior pullback (GS: max prior pullback $1 -> limit $1 above last low; ES: 7 and 11tk below swing high catch 2- and 3-pt pullbacks).
- bear needing one more bull bar to confirm flip, breakout bar weak -> sell its close expecting no follow-through.
- never limit countertrend; never buy to scalp then short L2 while always-in short; surprises are with-trend.
- bull reversal bar at new low in weak bear channel = bear scalpers covering; stop-buy above it loses ~70%, avg loss > avg win.

### 4c. Beginner list (ch24.D) one line each
- reward >= risk (2x when starting); assume P>=.60 if setup looks good; stops only; stop and limit always in market; buy above bull bars / short below bear bars; tiny size (1 contract); 3-5 trades/day; simple; best starts = opening-range trends, strong reversals, pullbacks in strong trends; same size/stop/target; never convert swing<->scalp; patience: 3 trades/day, pullbacks not breakouts; EMA side rule; no countertrend scalps, no 1m; no tight TR; worst = midday mid-range flat EMA; no stop-entry range breakouts; confused = TR; do the math before entry or wait.

### 4d. Numbers he gives for management (ch24.E)
- ES ADR 10-15: risk 2pt; swing 4pt; scalp 2-4pt then swing rest; range traders 2-3pt; reversal traders >=4pt; OCO 2-4pt limit / <=2pt stop.
- once trend established: scalp most with-trend entries 2pt risking ~2pt; swing some if strong.
- stocks: stop beyond signal bar (<$0.60 usually) until entry bar closes; after with-trend bar move to beyond entry bar; BE at $0.60-0.80 open profit (ADR $3); half off at $1; trail 5m swing lows; more at $2.
- ES bull example: initial 14tk below signal bar; after strong 2-bar reversal tighten to 11tk below entry; P .60 -> min target = actual risk -> limit >=12tk above signal bar high (reached 15).
- compressed ADR / small initial risk: set limit 1tk short of obvious target (15 not 16) or at 3pt.
- scale-in lower in strong trend / range bottom turns 60% into 80%+; wide stop + long hold turns "60% for 2 vs 2" into "~90% for 4 vs 8".
- extreme days (2008, 30pt bars, 10pt risk): size 20% normal, same setups.
- hold through pullbacks while premise valid; BE only after trend resumes following a test of entry.
- after final flag in bull: wait >=10 bars + 2 legs to EMA before re-buying.
- buying a low in bear: scalp part at EMA test / prior swing low; BE; exit if 2 bear bars follow unless TL break strong.
- cautious bulls skipping H1: buy stop 1tk above trend high so resumption is not missed.
- minor top short then H2 w/ bull bar at EMA -> exit or reverse; mirror.

## 5. Guidelines (ch25) condensed
1. Knowledge necessary not sufficient; skill is hard work.
2. Gray fog; close is close enough; looks like a pattern -> trades like one.
3. No easy rules; zero-sum; small fleeting edge; need positive equation >50% of the time.
4. Edge never large; no high P of big reward relative to risk.
5. Reading charts half the job; trading the other half.
6. Edge exists both ways; when clear it is fleeting; trade then.
7. Skill = spotting positive-equation trades (stop above, limit above, limit below, stop below).
8. After every close: more buyers or sellers above/below prior bar; critical at breakouts/failed breakouts (set always-in).
9. Every stop buy meets a limit seller; nothing certain.
10. Every bar is a signal bar both ways; stay open to the opposite.
11. For each setup consider the opposite breakout of the signal bar (trap).
12. Judge each breakout bar: succeed / profit-taking pullback / reverse.
13. Weigh strength vs weakness; setup that failed to be strong is weaker.
14. If you are certain, do not take it; arrogance inflates P.
15. Nothing as it seems; most strong range breakouts fail; 60% is 60% only 90% of the time; scale-in/wide stop turn 60 into 80-90 on bigger targets.
16. Main daily job = talking yourself out of bad trades (no H1 near range top, no L1 near range bottom).
17. Inertia: trend 80% reversals fail; range 80% breakouts fail.
18. Pullback "too far" feels twisted -> trend probably reversed.
19. Trade the trade you have, not the expected one.
20. Price is truth; fundamentals useless intraday; market rarely >60% certain.
21. Everything makes sense; read fast enough in real time.
22. "Not fair" = take a break; emulate computers: tireless, memoryless, objective.
23. Price action = human behavior; all markets, all TFs.
24. Always a protective stop in the market; you are the danger.
25. No savior (TV, newsletters, rooms, indicators).
26. Those who talk don't know; no TV/news.
27. Skipped 2 winners in a row = too large; 3 comfortable -> trade 1; size for 2-3 consecutive losses; cherry-picking blows accounts.
28. "I don't care": small size, one chart, no 1/3m/tick/volume, no indicators/divergence without TL break.
29. Far stop -> cut size ~1/4, same dollar risk; find setup first.
30. Market never certain it went far enough, always certain when too far; reversals need excess.
31. Reversing is hard; exit then look for new setup.
32. No reliable countertrend patterns; need strong TL break + always-in reversal setup; 80% fail.
33. Any reversal setup justifies partial/full profit taking; each top = bull flag start, each bottom = bear flag start.
34. Too early always worse than too late; most reversals/breakouts fail; trends go far.
35. All patterns fail, failures fail -> breakout pullback, high P.
36. One side suddenly trapped -> opposite scalp reliable.
37. Stop run then resumption = at least scalp, reliable.
38. No signals 30-60 min then sudden big bar -> wait; trap.
39. Goal is money not trades; no boredom trades.
40. Simple: one chart, no indicators; two charts = reject good signals.
41. Hobby or job; hobby too expensive.
42. Start 5m: buy above bull bar at EMA in bull, short below bear bar at EMA in bear; part off near prior extreme; rest BE.
43. Start 200-500 SPY; ES at 1,000-1,500 SPY.
44. Buy low sell high except clear strong trend (buy H2 at HOD, sell L2 in bear); if you cannot name the trend pattern, do not buy high.
45. Profitable = uncertainty + urgency; urgency = strong trend -> small market entry rather than wait.
46. Confused = TR: buy low sell high; up 5-10 bars shorts only; down 5-10 longs only.
47. In range: buy low = cover + buy on strong signal; sell high = take profits + short good setup.
48. Good fill, bad trade: suspect better-than-expected fills.
49. First 1-2 h easiest to make and lose; wait for swing setup (P<50%, >=2x); experienced scalp.
50. Down in 2nd half: same rules, no size-up, no lower-P setups.
51. Avoid midday / mid-range / flat EMA / barbwire; ask "is this one of the best of the day?"
52. Tight TR worst for stop entries; institutions do the opposite.
53. Tight TR trumps everything; sense one forming -> no trades, even hours.
54. Everything is trend or range; pick always-in, trade only that way; ~11:30 ET decide day pattern; take every with-trend trade before any countertrend.
55. Best signal bars = trend bars in your direction; dojis terrible; buy above / sell below a TR loses.
56. Most countertrend setups fail, most with-trend succeed; trends make great-looking countertrend and lousy with-trend setups.
57. No money until countertrend scalps stop; 1:1 needs 60%+; beginners scalp with-trend only if at all.
58. Until profitable reward>=risk; 2 to make 1 needs 80%.
59. Three variables; any positive combo is a good trade.
60. Experienced scale in/out; later entries higher P.
61. No money until you trade with-trend pullbacks.
62. No money on reversals until significant TL break + strong reversal bar on test of extreme.
63. Print 5m ES daily, annotate every setup, for years.
64. Style must fit personality; stress = wrong style.
65. No final-hours risk you would not take in first hours.
66. Computers: speed, no emotion, no fatigue; no trading during reports, upset, distracted, tired.
67. Always look for two legs; two failed attempts -> opposite succeeds.
68. Never cherry-pick: swing best 2-3/day or scalp every valid setup.
69. Avoid losers: mid-range weak signal bars; early reversals (wait 2nd entry); 1/3m denial; TV bottoms.
70. If not doing what expected, pretend flat; would not put it on now -> exit.
71. No scalp when should swing / swing when should scalp; until profitable swing 1-3/day, no scalping.
72. Converting swing->scalp or exiting scalps below risk loses; brackets + walk away 1 h.
73. Lost last month: no reversals; 7/10 bars above EMA buy only, 7/10 below short only.
74. Beginners take only the best trades, hours without a trade ok.
75. Discipline most important; if not all day, first hour and grow size.
76. Second trait: do nothing for hours.
77. Grow size, not trade count or setup variety; 2pt/day x 50 contracts = seven figures.
78. Perfected skills fund dreams.

## 6. Brooks vs Wade: differences
- Targets: Wade scalp 8-10 ES tk vs ~8tk stop (1:1) + runner; Brooks swing min 2x risk (ES 2pt stop -> 4pt), scalp 1:1 only at P>=0.60, beginners never scalp. Wade = Brooks' "scalp version of H2/L2 at EMA" (ch24 rank 3) run as the whole method.
- EMA: Wade 21 EMA, Brooks 20 EMA (5m); Brooks 1m surrogate = 90 EMA. Negligible; keep 20/21 as one param.
- Chart: Wade 2000-2500 tick (~1m RTH), Brooks 5m time bars (precise TLs, sees bar close coming, ch13); Brooks: tick users shrink stops, win rate falls, lose (ch13, ch25 #28). Brooks stated 1m stop 4tk / 5m 8tk; Wade 8tk on tick chart = Brooks 5m stop size at 1m-ish resolution.
- Counting anchor: Wade counts from the extreme (new high resets), 1-tick break of prior bar = entry, leg ends on 1-tick break of last bar low; Brooks counts H1/H2 from the start of the pullback (first bar whose high is exceeded after pullback begins), legs by swing structure. Wade's "first entry" ~ Brooks H1, Wade's "second entry" ~ Brooks H2, but Wade resets at double tops / pivot breaks, Brooks does not reset at exact-tick DT (he treats DT as the setup itself).
- First entries: Wade never (50/50) except listed exceptions; Brooks H1 is a best trade in a strong spike w/o climax (ch24), L1 only strong bear spike. Both skip H1 after a climax.
- Third entries: Wade "not a thing"; Brooks H3/L3 = wedge flag, valid, often more reliable than H2 in a tight channel (ch9); after 3rd buy climax no H1/H2.
- Reversal gating: Wade "correction played out" = counter-trend 2-swing TL broken by close + new extreme (or attempt within 2tk) before with-trend count; Brooks MTR = TL break reaching EMA + test of extreme + strong signal bar + always-in flip by >=2 trend bars with follow-through. Brooks adds explicit probability (40-60%) and the EMA-reach requirement; Wade adds the "new extreme after break" requirement (Brooks: test may be HL/LH without new extreme).
- Always-in: Brooks central (flip = 2 consecutive strong bars + follow-through, 60% rule); Wade has no always-in, uses bias = structure + EMA + trendline state, flat when unclear.
- Overshoot: Wade overshoot -> skip next 2nd entry, wait LH/HL (F8); Brooks: TCL overshoot + reversal is the setup (expect 2 legs 10 bars) but first attempt vs spike usually fails -> also wait second signal. Agree.
- Key entry point: Wade requires EMA / TL / level touch (2+ coinciding preferred); Brooks: EMA for H2/L2, but also enters at market in always-in trends and on bar closes in spikes (no KEP needed).
- Limit entries: Wade limit 1-2tk back from trigger (missed fills); Brooks beginners stop orders only, experienced limit at/beyond weak signal bars with-trend only.
- Stop: both 1tk beyond signal bar; Wade never moves it; Brooks tightens to 1tk beyond entry bar after strong close, BE after resumption/half target, trails under HLs.
- Session rules: Wade 2 losses pause / 3 stop / 2-3 wins stop; Brooks no win-stop, 3-5 (beginner) to 5-10 trades/day, no reversals after losing month.
- Measured legs: Wade leg2 = leg1 as runner target; Brooks same MM plus spike height / flag height / gap midpoint.
- Congestion: Wade K overlapping bars with EMA inside -> no trade (F5); Brooks barbwire (3+ sideways bars, >=1 doji) and tight TR lockout, "trumps everything". Agree.
- Day structure: Wade no time-of-day model beyond news windows and last 2h; Brooks explicit thirds, 11:30 reversal, OR categories, gap stats.
- Trader's equation: Wade claims 65-70% blind / 90% with retest; Brooks caps realistic at 60% (70% strongest), "60% is 60% only 90% of the time".

## 7. New rule candidates for RULES.md
fmt: ID | stmt | src | status | note. Units MNQ; ES ticks mapped as fraction of ADR (ES 8tk ~0.15ADR; 1tk ~0.02ADR; MNQ 1tk=0.25pt).

### D. day-type / bias
D9 | t=935: bar1 range -> ADR_est = 5*r1; bar1 is HOD/LOD 20% (30% if |body|>=.6r & tails<.2r; 50% if also |gap|>=.5ADR) -> never fade bar1 breakout for swing; fade bar1 w/ tails>=.4r as 1-bar range (scalp) | brooks ch17/19 | U | contradicts nothing; D1 gap term consistent
D10| large gap = |gap|>=0.5ADR or max of last 5d: P(gap-dir channel)=.50, range .20, counter .30; expect 5-10 bars TR then trend; sideways 5-10 bars after gap-up -> P(bull day)>=.60, tgt ADR ext, risk gap mid | brooks ch20 | U | confirms D1 gap term; adds TR-first expectation (delay D1 entry 5-10 bars?)
D11| OR = max(range 9:30-10:15, largest leg first 30-90m). OR/ADR<=.25 -> breakout mode both ways 1tk beyond, opp side=stop; .33-.5 -> P(trend-ish)=.67, tgt=1 OR MM from break, retest of break expected; close back inside past opp side = reversal day; OR>=.6ADR -> spike&channel, trail | brooks ch19 | U | compare D3 (IB<.35ADR -> range 66% on MNQ: contradicts Brooks .25 breakout-mode claim; test OR vs IB defn)
D12| day-type by bar 12: bar1 doji (body<.3r) inside pd last-hour range & |EMAslope|<.1ATR -> RANGE; >=5 direction reversals or >=4 overlapping (>70%) tailed bars in first 60m -> RANGE; 3-4 consecutive trend bars body>=.6r, overlap<.3 -> TREND; large gap + 4 trend bars -> TREND | brooks ch17/19 | U | extends D5 with numbers; validate vs D4 labels
D13| always-in state: flip when 2 consecutive bars body>=.5r same dir AND next bar close not opposite; follow-through ext <=2tk beyond breakout bar -> failed-breakout bias; tie-break = majority of last 10 closes vs EMA; pre-open state = pd last-hour state | brooks ch15 | U | feeds E5/E5f side; cf D2 (mv>=.4ADR) as a cruder version
D14| time windows: midday reversal 11:00-12:30 (modal 11:30) flag; pullback 13:30-14:00 ending ~14:30; last 60m with-trend only, no new countertrend; report blackout 1-3 bars after 8:30/10:00/14:00 | brooks ch11 | U | overlaps F11 (lunch 11-13 no entries): Brooks says 11:30 is a reversal/trend-start window, not dead -> test F11 vs D14
D15| daily bias into close: 10d trend up (close>EMA20d & slope>0) -> P(close>open)~.65, bias long 15:00-16:00; down mirror | brooks ch11 | U | relates D8 (last-30m momentum); Brooks adds daily-trend condition
D16| HOD/LOD timing: formed by 9:55 (5 bars) 50%, by 11:00 90% -> after 11:00 any new extreme is a breakout of established range; treat first-hour reversals as possible extremes (swing part) | brooks ch16/19 | U | supports F10 (no shorts into LOD) after 11:00
D17| low-range day: range at 11:00 < 0.3ADR and sub-.5ADR days rare -> expect 2-3x expansion by close; allow 2x-tgt entries w/ tight stop | brooks ch24.E | U | pairs with D3/E2

### E. entries
E11| H2/L2 at EMA on TREND day (Brooks "single most reliable"): after >=2-bar spike & D13 flip, pullback touches EMA (within .25ATR), 2nd push (H2) w/ signal bar body>=.5r same side -> stop 1tk beyond; stop other side; tgt 1R scalp + runner; claimed P>=.60 1:1, post-spike L2 w/ bear bar >=.70 | brooks ch24 | U | = E5 restricted to TREND days + EMA touch + spike prereq; E5f partial confirms (PF1.14); Brooks count anchor differs from Wade (see s6)
E12| H1/L1 only in spike: first pullback after >=3 consecutive trend bars (body>=.6r, overlap<.3), no climax bar (r>2*ATR20) in spike -> stop 1tk beyond pullback bar; stop beyond spike start; tgt test of extreme | brooks ch24 | U | contradicts E5 "1st entry skip" (Wade) in spike context only
E13| MTR: prior trend >=20 bars; counter leg closes beyond EMA (>=.25ATR) & breaks 2-swing TL, leg >=5 bars (or 2-3 bars w/ 1 bar r>=2x median); test = extreme +/-.1ADR (HH/DT/LH); signal bar body>=.5r, close beyond mid; stop 1tk beyond; tgt 2R; P .40-.60; cancel if test leg >5 bars beyond old extreme or tight channel (overlap<.3) | brooks ch3/24 | U | formalizes F6/F7 (Wade correction played out / two legs) into one entry
E14| climax fade: bar r>=2*ATR20 & body>=.7r & largest of last 20, after >=10 bars one-directional (or 3rd consecutive climax w/ <=2 pause bars between) -> fade at close, stop = bar range, tgt1 = bar extreme, tgt2 = +1 bar range (MM); P~.60 tgt1; no with-trend H1/H2 for 10 bars after | brooks ch4 | U | new; X6-like lockout after
E15| wedge/3-push reversal: 3 swing extremes each beyond prior over >=20 bars; ext3<ext2 (shrinking) or TCL overshoot on push3; 2nd signal (LH/HL within 5 bars) stop 1tk beyond; stop beyond push3; tgt1 = pullback extreme after push1, tgt2 = wedge height from tgt1; fail = 1tk beyond push3 -> reverse, tgt = wedge height beyond; no entry if tight channel (overlap<.3) or <20 bars (flag, with-trend only) | brooks ch5 | U | F9 says wedge = no trade (Wade); Brooks: wedge reversal is a trade after 2nd signal. Conflict; test both
E16| final flag: trend >=24 bars, flag 5-10+ bars horizontal (slope<.1ATR/bar), >=50% overlap, >=2 opposite bodies; breakout beyond flag then reversal bar closing back inside -> stop 1tk beyond reversal bar; stop beyond breakout extreme; tgt 2 legs/10 bars, min = flag far side; 1-bar flag after climax = countertrend scalp only (extreme retested 10-20 bars) | brooks ch7 | U | new
E17| DB/DT pullback: bottom2 <= bottom1 (+2tk tol); rally >=2 bars; HL pullback above bottom2; signal bar body>=.5r -> stop 1tk above; stop below bottom2; tgt 2R if prior TL break else 1R; skip if bottom2 > bottom1+2tk in strong bear | brooks ch8 | U | new; relates E6 (failed break)
E18| expanding triangle: >=5 alternating swings each beyond prior; entry 1tk beyond 5th-leg signal bar; stop beyond 5th extreme; tgt1 = opposite side of pattern (usually all); tgt2 = last leg height; tgt1 fails -> flip to 7-leg continuation | brooks ch6 | U | new, rare
E19| 1-tick failed breakout fade: new extreme beyond PDH/PDL/swing/OR by <=2tk (MNQ: <=.03ADR) and close back within 1-2 bars -> stop 1tk beyond failure bar; stop beyond poke; tgt 1R / opposite side of range; TR days only | brooks ch9/21 | U | E6 poke window 2-45pt is far wider; Brooks says 1-2tk is the reliable class -> test E6 split by poke depth (cf E4 depth curve)
E20| breakout pullback / breakout test: after breakout bar body>=.6r, first pullback 1-3 bars not reaching EMA, or pullback to within 2tk of original entry/signal bar extreme that turns back -> stop 1tk beyond pullback bar; stop beyond breakout bar; tgt MM = breakout leg; P>=.60 | brooks ch9/24 | U | relates E1 (ORB retest) and E3 (IB retest): Brooks' version is per-breakout, not per-level
E21| 2nd-entry rule: any E after a failed first signal in same direction within <=5 bars (first signal stopped or 5tk failure) -> take; P += .10 vs first | brooks ch13/24 | U | Wade second entry generalized to all setups
E22| stop-run entry: price trades 1tk beyond a prior entry/signal bar extreme (where stops sit) then reverses back within 1 bar -> enter with original direction above/below the run bar; at least scalp | brooks ch9/25#37 | U | new
E23| spike entry (experienced): >=2 consecutive trend bars body>=.6r, small tails, breaking range/level -> enter close of bar 2-4; stop spike start; size /2; tgt = risk (P~.60), 2x if very strong (P~.70) | brooks ch24.C | U | contradicts Brooks' own beginner rule (pullbacks only); test as runner-only
E24| range fade: TR (D4 RANGE2 or D13 unsure) and up >=5 bars into top third -> shorts only at signal bar body>=.5r (L2 near prior swing high); down >=5 bars into bottom third -> longs only; P .60 at 1R; require 2nd entry if move into extreme strong | brooks ch24 | U | relates E2/E6; Wade FB trades (s15: 7/53)
E25| first-hour scalp: 2 consecutive bull bars body>=.6r then doji -> limit at doji low, stop = bar height, tgt = bar height, P~.60; mirror | brooks ch17 | U | likely fails X4 on MNQ (tgt ~bar height <20pt); runner variant only

### F. filters
F13| MTR gate: no countertrend entry unless counter leg closed beyond EMA and broke 2-swing TL (F6 variant) AND signal bar close beyond midpoint; 1m reversal bars do not count (5m only) | brooks ch3/14 | U | confirms F6; adds EMA-reach + 5m-bar requirement
F14| restart: after TL break, if test leg runs >5 bars beyond old extreme or in tight channel (<=1 pullback bar, overlap<.3) -> reset reversal state, require new TL break | brooks ch3 | U | confirms F7/F8 (two legs to new extreme / overshoot)
F15| climax lockout: after E14 climax or 3rd consecutive climax, no with-trend H1/H2 (E5/E11/E12) for 10 bars and until 2 legs printed | brooks ch4 | U | new
F16| equation gate: P_est .60 default (good setup), .70 if 2nd entry + with-trend signal bar + trend ctx, .50 if unsure (then tgt>=2R); reject if P_est*tgt < (1-P_est)*stop*1.1 | brooks ch24 | U | formalizes X4-like constraint; P_est labels need calibration from Q3
F17| stop sanity: reject entry if stop > tallest bar of last 20 or stop < .25*median bar range; on large-bar days allow 2-3x normal stop w/ tgt>=stop and size/k | brooks ch24 | U | with R3
F18| tight-range lockout: >=5 consecutive bars each >70% inside union of prior 2-3 bars & |EMAslope|<.1ATR -> no stop entries until a close outside + pullback; P(trend-side breakout)<=.55 | brooks ch15/25#53 | U | sharpens F5 (Wade K bars); "trumps everything"
F19| midday mid-range: no entry when t in 11:30-14:00 & price within middle third of day range & |EMAslope|<.1ATR & not TREND (D12/D13) | brooks ch24.G/25#51 | U | overlaps F11; F11 is time-only, F19 adds location + EMA
F20| signal bar reversal min: countertrend signal bar must close beyond its midpoint; with-trend in TR may be weaker; 2-bar reversal w/ a large bar -> trigger beyond the larger bar; no outside-bar entries | brooks ch9/19 | U | confirms F1 (.5 close) exactly for reversals; Brooks .25-.33 only for strong trend countertrend
F21| room: signal bar extreme must be >=4-5 ES tk (MNQ ~.08ADR) from PDH/PDL/EMA/OR edge in trade direction for a scalp | brooks ch16 | U | confirms F3 (0.8-1R room) in tick terms
F22| H2 location: no H2 long in top third of a range or after bull trend ended (bear channel after 2-bar reversal from HH, >=5 bear bars, no TL break); no L2 short at bottom of range | brooks ch9/23 | U | confirms F10; adds "trend over" condition
F23| doji signal: reject body<.3r unless 2nd entry at TCL overshoot or counter-move had many opposing bodies | brooks ch24/25#55 | U | = F1 "no doji" with the two exceptions
F24| EMA-slope side rule: >=7 of last 10 closes above EMA -> longs only; >=7 below -> shorts only; else range mode (E24 only) | brooks ch25#73 | U | simpler alt to D13; compare on E5
F25| gap-day EMA: ignore EMA-distance filters (F4) first 60m on large-gap days (D10); use bar count/body ratio instead | brooks ch17 | U | exception to F4
F26| post-report: no entries 1-3 bars after 8:30/10:00/14:00 ET releases | brooks ch11/17 | U | same as Wade news window but shorter (Brooks 1-10 min vs Wade +/-15)

### X. exits / management
X7 | tick-failure exits: excursion exactly 5tk (ES; MNQ ~.1ADR) then reversal -> exit/fade; 2/3/4/5pt-target failures (9/13/17/21 tk) -> exit on next opposing bar; never let a >=9tk excursion become a loss (stop to BE) | brooks ch9 | U | contradicts X1 (plain 2R best) and X5 (BE at 1R worse): Brooks' BE trigger is excursion-based, not R-based; test as "BE after .5*tgt AND resumption after test of entry"
X8 | 16-tick hold: excursion >= tgt-1tk -> hold for tgt (P .80) unless price trades below prior bar low | brooks ch9 | U | pairs X7
X9 | stop ladder: initial 1tk beyond signal bar; after entry bar closes w/ body>=.5r in direction -> 1tk beyond entry bar; after new extreme -> trail 1tk beyond last HL/LH; swing stop = spike start | brooks ch13/24 | U | relates X3 (Wade runner trailed under swings); X1 says struct stops worse 2022-25 -> retest with Brooks' sequencing
X10| swing scale template (stop ~3 ES pt): 25-50% off at +2..+4, 25-50% at +4..+6, rest to opposite flip or BE; BE once move >= 2x stop | brooks ch19 | U | alt to X3 half/half
X11| MM targets: leg1=leg2; spike height; flag/range height; measuring-gap midpoint; test within 3tk = incomplete (expect retest), >=4tk beyond = next target; OR-height MM from OR break | brooks ch1/5/9/19 | U | extends X2 (next-level target) with projected levels
X12| premise exit: countertrend long in bear -> exit on L2 at EMA w/ bear body (reverse unless trend already flipped); minor-top short -> exit on H2 w/ bull bar at EMA; climax entry -> exit after 2 bear bars unless TL break was strong | brooks ch21/24.E | U | structural alt to X6 (4-bar time stop)
X13| opening-reversal hold: swing portion survives pullbacks (2-3 doji bars common) as long as stop not hit; exit only on strong opposite signal | brooks ch17/19 | U | contradicts X6 (4 bars against) in first hour

### R. risk / session
R6 | size by stop: contracts = floor(risk$/(stop_tk*0.5+2*comm)); stop k x normal -> size/k, floor .2 normal; first 60m size x.5-.25 | brooks ch15/24 | U | = R3 with explicit first-hour haircut
R7 | trade budget: 3-5/day (beginner), 5-10 standard; 2-3 swings/day for the "very best"; no cherry-picking within a P-class (take all low-P 2R setups or none) | brooks ch24/25#68 | U | relates R1 (Wade win-stop); Brooks has no win-stop -> test R1 win-stop vs none
R8 | losing month -> next month no reversal entries (E13/E14/E15/E16), EMA-side only (F24) | brooks ch25#73 | U | new regime rule
R9 | report/holiday: no trades during 8:30/10:00/14:00 windows; holiday weeks first hour only | brooks ch11/17 | U | overlaps F26
R10| expectation: 60% setups lose 40%; a stop hit is doing its job; evaluate per 20-50 trades (R4); "60% is 60% only 90% of the time" -> deflate P_est by ~.05 in F16 | brooks ch24/25#15 | U | with R4/R5

### Q. new open questions
Q6 Brooks OR categories (D11) vs our IB (D3): MNQ narrow IB = range 66%, Brooks narrow OR = breakout mode; is the difference definition (15m vs 60m) or instrument? Q7 count anchor: Brooks H2 (from pullback start) vs Wade (from extreme, reset at DT) hit-rate on same bars. Q8 climax bar frequency (r>=2*ATR20 after 10 bars) and post-climax drift on MNQ. Q9 1-2tk failed-breakout fade (E19) vs E6 deep pokes. Q10 11:30 ET reversal window frequency on MNQ (D14 vs F11).
