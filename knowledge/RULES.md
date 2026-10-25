# RULES.md — machine-first rule registry (my shorthand; not for humans)
fmt: ID | stmt (ticks/ATR/bars; MNQ tick=0.25pt=$0.50) | src | status | result
status: U untested · T tested · K keep · X rejected · P partial
ADR = 10d avg RTH range. ATR = per-bar avg range (n given). IB = 9:30-10:30 range. t = ET minutes.
friction MNQ = 3pt/rt (comm 2.37x2 + ~2tk). any rule must be PF_net>1 @3pt and survive @4pt.

## D. day-type / bias (known at time t)
D1 | t=945: committed = |gap|>=0.6ADR or |c15-o15|>=0.6*r15; skip if pdRange>1.2ADR; bias=sign(gap) else sign(first15) | ours (V4) | K | 2022-25 PF1.24 g117/r103; 2026 PF1.70 g23/r17. VALIDATED scripts/v4_validate.js: cost-insensitive (slip 0-4tk: PF 1.25->1.21, 2026 1.82->1.69); plateau smooth, PF rises with stricter thresholds (gap.7/dir.8 PF1.51 n134) = no cherry-pick; by year PF 1.50/1.38/1.10/0.99/1.70 -> 2024-25 weak (2025 flat 22/28 days); tgt 2R best for 2026, 1.5-3R all PF~1.3; pd 1.0-1.5 all fine
D1b| drop gap term, keep first15 dir only | tradingstats ORB | X | scripts/d1b_v4_nogap.js: dir-only .6 = 2022-25 PF1.28 g107/r91, 2026 PF1.80 but 29tr +1905 (vs V4 40tr +2684). gap-only .6 = PF1.41/1.37, 66+21 tr: gap component is real on MNQ, keep V4 as is. dir>=.7 PF1.34 but half the trades. pdRel<=1.2 filter helps 2026 (no-pd: 2026 PF1.35). gap-agrees variant 2026 PF2.02 n=25 (watch, not adopt)
D2 | t=1030: mv=|c1030-o|/ADR. mv>=0.4 -> P(close same side)=90%; 0.6-1 -> 93%; <0.2 -> 60% & P(range)=51%; >1.0 -> exhaustion (n=18, further move negative) | greenday_lab4 | T | median further move 0.07-0.13ADR (20-45pt)
D3 | t=1030: IB<0.35ADR -> P(range2)=66%, P(trend2)=7% (narrow IB ≠ trend on MNQ). IB>0.7ADR -> P(trend2)=27% | greenday_lab4 | T |
D4 | honest labels: TREND2 = cl>=.8|<=.2 & rng>=1ADR & |o-c|>=.6rng (19%); RANGE2 = rng<=.7ADR | .35<=cl<=.65 (40%) | ours | K | use for post-hoc attribution only (lookahead)
D5 | trend-day early signs (no numbers): open outside pd range & first test holds; first pullback holds > midpoint of first push; VWAP sloping w/ price one side; IB small vs ATR; vol > recent first hours | wayofthetrader | U |
D6 | weekday: Wed worst (double-break 55%, cont 61%); Mon/Fri cleanest | tradingstats | U | test on ours
D7 | ATR regime does not change continuation (<2pt diff); size by ORB width instead | tradingstats | U |
D8 | last 30min momentum: sign(c1530 - pdClose) -> 55% hit, only on neg-gamma/high-vol days; dead in calm | Baltussen 2021 | U | low priority

## E. entries
E1 | ORB retest V2: 5m close outside OR(9:30-9:45), retest touches OR edge, signal bar (close top/bottom .5, body>=.3r) -> stop order 1tk beyond; stop other side OR, min 16tk; tgt 2R; 9:45-13:00 | ours | K | base for V4
E2 | ORB second break: first OR break fails, opposite side breaks -> continuation 68% ES30 / 72% NQ30, median gap 90min | tradingstats | U | range-day play
E3 | IB retest: after 1.1x IB reached, level retested 87% (NQ), then continued 71%; past 1.4x -> reversal odds > continuation. entry = first retest holding within 10% IB; stop .25IB beyond; tgt 1.3xIB | tradingstats IB | X | scripts/e3_ib_retest.py: 1026 tr, win 57% @0.3W tgt but PF 0.97 (cost). Split: TREND +3.6k, MID +4.7k, RANGE -9.2k (5/140 green: by construction). No 10:30-known filter fixes it (IB/ADR buckets, mv/ADR: PF 0.91-1.19, 2026 negative in all). base rate confirmed, edge absent after 3pt cost
E4 | depth curve: break extending <0.4x prior-bar range fails back inside 65-71%; >0.4x holds ~80% | tradingstats ext | U | fade/continue switch
E5 | Wade H2/L2 @EMA21: count from extreme, leg alive until 1tk break of last bar; 1st entry skip; 2nd entry = trade; reset on new extreme/pivot break/double top-bottom; no 3rd entries | wade | T | 1m/3m/5m all PF<0.8 unfiltered; 5m TREND days + ; RANGE days kill it
E5f| E5 on 5m, after 1030, only if D2 mv>=0.4 & pullback<0.4 | greenday_lab3 | P | PF1.14 n=67 +160pt (thin, 2024-carried)
E6 | failed break V1: poke 2-45pt beyond PDH/PDL within 5 bars, close back, stop beyond poke+5, max 60, tgt 1R, 10:00-13:00 | ours | P | +2023/2026, -2022/24/25
E7 | VWAP first touch after 1030 on D2-qualified days, 1m close back on trend side, stop .25ATR, tgt 1ATR | institutional | U |
E8 | first pullback after 1030 with D2 side, tgt ~0.1ADR, stop beyond pullback | greenday_lab4 | X | scripts/e8_first_pullback_1030.py: all 9 variants lose every year (PF 0.61-0.84, win 33-49% < random for geometry). X=.6 best PF0.74 n=133. D2 persistence (90% close same side) is a FILTER not an entry: the drift after 1030 (~0.1ADR) < pullback stop (~0.125ADR)+3pt cost
E9 | gap fade: gap<0.5% opening inside pd range -> tgt pd close, stop .5gap; fill 84% same day; skip >1% (55%) | nexusfi | U |
E10| buildup: tight consolidation at level, 20MA reaching its lows -> breakout w/ stop other side of buildup | teo | U |

## F. filters (apply to any E)
F1 | signal bar: close in top/bottom .5 (ours) / .25-.33 (Brooks); body>=.3r; no doji | wade/brooks | K |
F2 | signal bar strength: r>=1.5*ATR20 & close top/bottom .25 ; or r>=2x avg prior 3 | teo/TV | U | test on E1/E5
F3 | room to first obstacle (swing/PDH/PDL/OR/VWAP) >= 0.8-1.0R else skip | teo / ours V3 | P | V3 levels 1R room: fewer, better (2026 PF2.86)
F4 | no entry if dist(signal bar, EMA21) > 0.5*ATR20 ("far from EMA") | wade | T | used in E5
F5 | congestion: >=K bars overlapping >70% w/ EMA inside bodies -> no trade | wade | U |
F6 | correction played out: counter-trend 2-swing trendline broken by close + new extreme (or attempt within 2tk) before with-trend count | wade | U | hard part
F7 | two legs to new extreme after TL break -> stop trading that direction | wade | U |
F8 | overshoot (break on trend side of channel) -> skip next 2nd entry, wait LH/HL | wade | U |
F9 | wedge/both-sides-tempting -> no trade | wade | U |
F10| no shorts into LOD / longs into HOD; need deeper correction | wade | U | define: within 0.15ADR of extreme
F11| lunch 11:00-13:00 no new entries | seasonality (ns) | U |
F12| pullback depth class: <=38% strong, <=50% healthy, >=62% weak (no breakouts) | teo | U |

## X. exits / management
X1 | plain 2R best under V4 filter; caps/BE/trail/struct stops worse 2022-25 | ours | K |
X2 | next-level target w/ 1R room (V3) fewer but better | ours | K |
X3 | wade: scalp = median signal-bar stop (~1:1), runner BE trailed under swings; MNQ cost makes <20pt tgt structurally losing -> runner model only | wade+cost math | U |
X4 | min avg trade >= 25-30pt on MNQ (friction <=10-12% of avg win) | cost math | K | hard constraint
X5 | breakeven at +1R reduces expectancy vs add-on (daily TF study) | luxalgo | U |
X6 | time stop: exit after 4 bars against (Brooks) / 1h congestion scratch (Wade) | brooks/wade | U |

## R. risk / session
R1 | 2 losses in row -> 15min pause; 3rd loss -> stop; 2-3 wins -> stop (except trend day) | wade | U | test green-day effect
R2 | daily stop 550, daily tgt 600 (eval) | ours | K | parked w/ eval
R3 | size = risk/(stop*pv+2comm), risk 300-400, max 20 | ours | K |
R4 | evaluate in blocks of 20-50 trades; 55%/1:1 edge still ~30% red days | quants | K | expectation setting
R5 | deflate: log every variant; walk-forward 12m fit/3m test; plateau check; cost sweep 2-5pt | lopez de prado/carver | U | must do before trusting any K

## Q. open questions
Q1 trend-day frequency by month on ours (D4 says 19%); Q2 H1 vs H2 hit rate split by EMA slope & pullback depth; Q3 signal-bar close-location buckets vs 1R hit; Q4 PDH/PDL/ONH/ONL first-touch hold rate; Q5 VWAP ±2SD touches balance vs trend days.


# ---- Brooks (Trading Price Action Reversals) candidates, 2026-10-22; full ref knowledge/book/brooks_reversals.md ----

### D. day-type / bias
D9 | t=935: bar1 range -> ADR_est = 5*r1; bar1 is HOD/LOD 20% (30% if |body|>=.6r & tails<.2r; 50% if also |gap|>=.5ADR) -> never fade bar1 breakout for swing; fade bar1 w/ tails>=.4r as 1-bar range (scalp) | brooks ch17/19 | U | contradicts nothing; D1 gap term consistent
D10| large gap = |gap|>=0.5ADR or max of last 5d: P(gap-dir channel)=.50, range .20, counter .30; expect 5-10 bars TR then trend; sideways 5-10 bars after gap-up -> P(bull day)>=.60, tgt ADR ext, risk gap mid | brooks ch20 | U | confirms D1 gap term; adds TR-first expectation (delay D1 entry 5-10 bars?)
D11| OR = max(range 9:30-10:15, largest leg first 30-90m). OR/ADR<=.25 -> breakout mode both ways 1tk beyond, opp side=stop; .33-.5 -> P(trend-ish)=.67, tgt=1 OR MM from break, retest of break expected; close back inside past opp side = reversal day; OR>=.6ADR -> spike&channel, trail | brooks ch19 | T | scripts/q6_or_definition.py: same answer at 15/30/60m windows: narrow OR = range day (OR15<.25ADR: P(range) 52-72%, double-break 61%; OR60<.35: range 63-78%). Wide OR15 .5-.7ADR: P(trend) 29%, double-break 31%. First-break continuation flat ~55% at all sizes. Brooks 'breakout mode' on MNQ = fakeout both ways, not a trade. Keep D3; D11 reversed for MNQ
D12| day-type by bar 12: bar1 doji (body<.3r) inside pd last-hour range & |EMAslope|<.1ATR -> RANGE; >=5 direction reversals or >=4 overlapping (>70%) tailed bars in first 60m -> RANGE; 3-4 consecutive trend bars body>=.6r, overlap<.3 -> TREND; large gap + 4 trend bars -> TREND | brooks ch17/19 | X | scripts/d12_daytype_tells.py: NONE of the bar-shape tells move P(trend)/P(range) off base (19%/40%) on MNQ 5m: doji bar1 19/41, strong bar1 19/39, >=3 trend bars 25/39 (n=44), >=5 reversals 18/41, overlapping tailed bars 21/40, combos same. Only D2 (move/ADR by 10:30) and D3 (IB/ADR) carry information
D13| always-in state: flip when 2 consecutive bars body>=.5r same dir AND next bar close not opposite; follow-through ext <=2tk beyond breakout bar -> failed-breakout bias; tie-break = majority of last 10 closes vs EMA; pre-open state = pd last-hour state | brooks ch15 | U | feeds E5/E5f side; cf D2 (mv>=.4ADR) as a cruder version
D14| time windows: midday reversal 11:00-12:30 (modal 11:30) flag; pullback 13:30-14:00 ending ~14:30; last 60m with-trend only, no new countertrend; report blackout 1-3 bars after 8:30/10:00/14:00 | brooks ch11 | U | overlaps F11 (lunch 11-13 no entries): Brooks says 11:30 is a reversal/trend-start window, not dead -> test F11 vs D14
D15| daily bias into close: 10d trend up (close>EMA20d & slope>0) -> P(close>open)~.65, bias long 15:00-16:00; down mirror | brooks ch11 | U | relates D8 (last-30m momentum); Brooks adds daily-trend condition
D16| HOD/LOD timing: formed by 9:55 (5 bars) 50%, by 11:00 90% -> after 11:00 any new extreme is a breakout of established range; treat first-hour reversals as possible extremes (swing part) | brooks ch16/19 | U | supports F10 (no shorts into LOD) after 11:00
D17| low-range day: range at 11:00 < 0.3ADR and sub-.5ADR days rare -> expect 2-3x expansion by close; allow 2x-tgt entries w/ tight stop | brooks ch24.E | U | pairs with D3/E2

### E. entries
E11| H2/L2 at EMA on TREND day (Brooks "single most reliable"): after >=2-bar spike & D13 flip, pullback touches EMA (within .25ATR), 2nd push (H2) w/ signal bar body>=.5r same side -> stop 1tk beyond; stop other side; tgt 1R scalp + runner; claimed P>=.60 1:1, post-spike L2 w/ bear bar >=.70 | brooks ch24 | X | scripts/e11_h2_trendday.py: with D2 side filter + spike prereq the setup is too rare on 5m (7-12 trades in 5y, PF 1.3-2.0, meaningless n). Without spike: 34 tr PF1.39 but 12/22 green days. Without D2 filter: 48 tr PF0.75. Pullback family on MNQ 5m = rare-or-negative after 3pt cost; park
E12| H1/L1 only in spike: first pullback after >=3 consecutive trend bars (body>=.6r, overlap<.3), no climax bar (r>2*ATR20) in spike -> stop 1tk beyond pullback bar; stop beyond spike start; tgt test of extreme | brooks ch24 | U | contradicts E5 "1st entry skip" (Wade) in spike context only
E13| MTR: prior trend >=20 bars; counter leg closes beyond EMA (>=.25ATR) & breaks 2-swing TL, leg >=5 bars (or 2-3 bars w/ 1 bar r>=2x median); test = extreme +/-.1ADR (HH/DT/LH); signal bar body>=.5r, close beyond mid; stop 1tk beyond; tgt 2R; P .40-.60; cancel if test leg >5 bars beyond old extreme or tight channel (overlap<.3) | brooks ch3/24 | U | formalizes F6/F7 (Wade correction played out / two legs) into one entry
E14| climax fade: bar r>=2*ATR20 & body>=.7r & largest of last 20, after >=10 bars one-directional (or 3rd consecutive climax w/ <=2 pause bars between) -> fade at close, stop = bar range, tgt1 = bar extreme, tgt2 = +1 bar range (MM); P~.60 tgt1; no with-trend H1/H2 for 10 bars after | brooks ch4 | U | new; X6-like lockout after
E15| wedge/3-push reversal: 3 swing extremes each beyond prior over >=20 bars; ext3<ext2 (shrinking) or TCL overshoot on push3; 2nd signal (LH/HL within 5 bars) stop 1tk beyond; stop beyond push3; tgt1 = pullback extreme after push1, tgt2 = wedge height from tgt1; fail = 1tk beyond push3 -> reverse, tgt = wedge height beyond; no entry if tight channel (overlap<.3) or <20 bars (flag, with-trend only) | brooks ch5 | U | F9 says wedge = no trade (Wade); Brooks: wedge reversal is a trade after 2nd signal. Conflict; test both
E16| final flag: trend >=24 bars, flag 5-10+ bars horizontal (slope<.1ATR/bar), >=50% overlap, >=2 opposite bodies; breakout beyond flag then reversal bar closing back inside -> stop 1tk beyond reversal bar; stop beyond breakout extreme; tgt 2 legs/10 bars, min = flag far side; 1-bar flag after climax = countertrend scalp only (extreme retested 10-20 bars) | brooks ch7 | U | new
E17| DB/DT pullback: bottom2 <= bottom1 (+2tk tol); rally >=2 bars; HL pullback above bottom2; signal bar body>=.5r -> stop 1tk above; stop below bottom2; tgt 2R if prior TL break else 1R; skip if bottom2 > bottom1+2tk in strong bear | brooks ch8 | U | new; relates E6 (failed break)
E18| expanding triangle: >=5 alternating swings each beyond prior; entry 1tk beyond 5th-leg signal bar; stop beyond 5th extreme; tgt1 = opposite side of pattern (usually all); tgt2 = last leg height; tgt1 fails -> flip to 7-leg continuation | brooks ch6 | U | new, rare
E19| 1-tick failed breakout fade: new extreme beyond PDH/PDL/swing/OR by <=2tk (MNQ: <=.03ADR) and close back within 1-2 bars -> stop 1tk beyond failure bar; stop beyond poke; tgt 1R / opposite side of range; TR days only | brooks ch9/21 | X | scripts/e19_failed_break_depth.py: generic failed break of PDH/PDL/OR15 on 1m, all depth classes lose every year: <=0.5pt PF0.89 n=93, <=2pt PF0.55 n=284, <=10pt PF0.75, >10pt PF0.84 (n=1755). The tiny-poke class is the WORST on MNQ. E6 (V1, 10:00-13:00, poke 2-45, 1R) stays the only partially positive version
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

E26| inside bar (3 sources converged: LPA, Jhunjhunwala, generic PDF + friend): EMA21 trend, mother bar + >=1 inside bars, box alive until close beyond opposite side, trigger close beyond MB (or IB / full body / touch), skip if S/R <1R away, stop other side of MB(+1pt), tgt next S/R in 1-3R else 2R | sources + friend | X | scripts/ib_converged.py + ib_robust.py, 2022-2026 RTH, cost 3pt: 1m all PF .73-.85 (cost floor), 5m .82-1.05, 10m .99-1.09, 15m .90-1.03, 20m 1.02-1.22, 30m 1.14-1.26 but stops 90-160pt, a losing year in every 20/30m config, no TF plateau. A 15m PF 1.18 found first was an artifact (EMA reset each day = no trades before 11:15); with continuous EMA it is .96. Location filter helps every TF (+.05-.10 PF); full-body helps on 5m. Not tradable as a standalone edge on MNQ intraday

E27| friend's exact inside bar (voice notes 2026-10-24): bias = H4/H1/M15 trend majority 2 of 3; 5m mother-bar box; FULL BODY breakout in bias dir; stop other side of box; tgt 1R (bot) or 2R (manual); his bot trades forex M5, Telegram report 1 day 32 tr 65.6% +10.9R gross | friend | X | scripts/ib_friend_mtf.py, MNQ ETH 5m 2021-10..2026-10, no-lookahead HTF, cost 3pt: RTH 5m 1R n=2236 WR 51.9% gross +0.04R/tr, net PF .99 (EMA bias) / .96 (structure bias); 2R PF 1.04/.98; London session PF .78-.87; 24h PF .88-.95; 15m exec structure-bias RTH PF 1.16 (n=381, 2023 & 2025 <1). 27/61 months green. A 21/32 day happens ~1 in 12 days at 52% WR by chance; 1-day report is not evidence. Gross R ignores cost (3pt = .05R at 62pt risk)

X2 | V4 exits: maxHold 60m + tgt 1.5R = PF1.20 (vs 1.26), DD -38%, avg hold 55m (vs 4h20), years 1.28/1.16/.95/1.10/1.71; <=30m kills edge (PF~1.0); 90/120m worse than 60 and 180 = noisy, not a plateau | ours | T | scripts/v4_maxhold.js
X3 | Lucid Flex 50K eval sim (target 3k, EOD trail 2k, 50% consistency, DLL 1.2k), 54 monthly starts 2022-01..2026-06: V4 hold $400 risk pass 70%/fail 22% median 262 trading days; $1000 pass 33%/fail 67% median 41d; 60m/1.5R $400 pass 72%/fail 0% but median 772d; $800 pass 70%/fail 30% median 212d. V4 alone is too slow or too risky for a 2k max loss: needs more uncorrelated trades | ours | T | scripts/v4_lucid_evalsim.js

E28| D2 as a trade: at 10:30 if |price-open|>=th*ADR enter with move, stop at open (or half-way), hold to close / 1R / 1.5R / 60m | ours | T | scripts/d2_trade.py 2022-26: th.4 stop=open hold-to-close PF1.28 n361 (75/yr) DD 9.8R but 2026 .82; th.5 tgt1R PF1.31 n230; V4-off days th.4 PF1.38 n200 (24 .80, 26 .91). ANY 60m cap -> PF .83-1.10 (edge needs the afternoon). Stops 160-190pt. Candidate 2nd edge only as hold-to-close; weak 2026

X4 | V4 entry TF + exits (dev 2022-24 / test 2025-26): 1m retest entry 2R hold-close PF 1.47/1.41, all yrs>=1.14 (best); 5m 2R close 1.34/1.08; 1m 2R 60min 1.20/1.40 DD lower; 3m .45-.97 dev (signal-bar rule is TF-sensitive, caution); 10/15m <1.2 and fail test | ours | T | scripts/v4_tf_grid.js
X5 | eval sizing: risk = 50% of (balance - trailing max-loss line) ('cushion 0.5') dominates fixed risk: 1m 2R close dev pass 74%/fail 0% (30% within 60 trading days, median 85d), test 14% within 60d / 0% fail (rest still running); fixed $1000-1200: ~31-35% within 60d but fail 48-57% dev, 53-68% test. Fast pass (<1 month) not achievable without ~50%+ fail | ours | T | scripts/v4_eval_sizing.js

X6 | V4 diagnosis (1m, 2022-26, n216): stopped trades rarely reach 1R first (6%), 23% reach .5R -> BE stops useless; 71% of winners never go -.5R but tighter stops (OR mid, x*ADR, retest extreme) all FAIL out-of-sample; OR-opposite stop stays. Exit 15:00 ~= close (PF 1.36/1.56). Wide stops >=130pt PF 1.06 | ours | T | scripts/lab/diag_v4.py, opt_v4.py
X7 | V4 DAILY TREND FILTER (biggest gain): trade only when side == daily trend. 4 definitions agree. with SMA20 (prior close vs mean of prior 20 closes): DEV PF1.95 / TEST(25-26) 5.32; against: 1.21 / 0.59. with r5 (prior close vs close 5 days earlier): 2.27 / 3.48, every year >=1.51; against 1.11 / 0.80 | ours | T | scripts/lab/regime2.py
E29| D2 refined: entry 10:30-11:30, |price-open|>=.5 ADR, stop at open (or LOD/HOD), exit 15:00 or close: 10:30/open/15:00 PF 1.42 dev/1.27 test, yrs 1.13-1.43; 11:30/LOD/close 1.39/1.48. With SMA20 trend: 1.82/1.80. Skip FOMC days. 79% of D2 days are non-V4 days. move-from-prior-close variant = bug artifact (wrong-side stop), rejected | ours | T | scripts/lab/cont.py cont2.py
X8 | late-day (15:00/15:30/15:45) momentum AND fade both lose dev 2022-24 (costs); rejected | ours | X | scripts/lab/late.py

X9 | high-R ORB (first 5/15m candle dir, stop .05-.15 ADR, EOD/10R): avgW 4-13R, >=5R winners ~60/5yr, but WR 8-24%, DD 25-200R, PF<=1.28; portfolio optimizer gives it 0 weight for eval | lit (Zarattini) | X(eval) | scripts/lab/hir.py
X10| big-move anatomy: largest 30m move/day median .48 ADR, 62% start 9:30-10:30; direction vs SMA20 trend 44/56, vs first-15m 60/40, vs gap 49/51 -> fast big moves not directionally predictable | ours | T | scripts/lab/anatomy.py
X11| V4+ = V4 with SMA20 trend filter + loosened thresholds gap>=.4 or dir>=.4, no pd filter, 1m entry, 2R: n219 (46/yr) PF1.65, yrs 1.70/1.74/1.14/2.51/1.80, max losing streak 5. Plateau gap/dir .4-.8 all PF1.66-2.0 dev, 2-5 test | ours | K | scripts/lab/v4max.py
X12| sessions: Asia/London/overnight direction do NOT predict RTH direction (49-51%). But trades WITH London direction: V4+ PF1.72/2.78 vs against 1.2/1.87; D2 1.66/2.26 vs 1.28/.69. Asia-range London breakout and 3:00-8:00 pre-market breakout: PF<=1.03 rejected | ours | T | scripts/lab/sessions.py eth.py
X13| news days (data/macro_dates.csv): D2 on CPI days PF .59 (n11) -> skip; V4+ CPI ~1.0, NFP/PPI/FOMC strong (small n). FOMC 14:00 range breakout PF .46-.76 -> never | ours | T | scripts/lab/news.py
X14| EVAL FRONTIER (Lucid Flex 50K, +8pt stop slippage, cushion sizing, every combo/filter tried): pass <=10 trading days ~5%, <=20d 13-19%, <=40d 25-37%, <=60d 33-51%, fail 0-5% at f .5-.8; f=1 -> fail 15-37% without faster passes. Hard ceiling = expectancy x frequency | ours | T | scripts/lab/portfolio.py evalsess.py

X15| community NQ strategies, mechanical: liquidity sweep/turtle soup of PDH/PDL and overnight H/L (9:35-12, 12-15; 2R / opposite level / EOD; +-trend): PF .54-.95 ALL rejected; ICT silver bullet 10-11 FVG 1m/5m: PF .79-1.10, test <=1.02 rejected; gap fill .1-.8 ADR: PF .85-1.02 rejected; IB30/IB60 break with trend stop opp: PF 1.29/1.31 overall but on V4-off days test .80-.96 -> V4+ already captures it | community | X | scripts/lab/community.py

X16| VERIFIED-SOURCE strategies (agent catalogue, credibility-filtered) on MNQ 2022-26 with SMA20 trend filter: Raschke Momentum Pinball (RSI3 of daily closes <30 & trend up -> buy stop first-hour high, stop first-hour low, exit close; mirror) n83 PF2.85 DEV3.10 TEST1.98 DD2.3R -> ADD; Williams vol breakout k.4 trend PF1.36 (1.40/1.26) but V4-off days .99 test -> reject; Fisher ACD A.1 OR15 trend 1.29 (V4-off test 1.00) reject; Williams Oops gap>.15 trend n53 PF1.35 (adds fails in eval) hold; Crabel stretch 1.1-1.3 / NR7 fails test; Raschke 80-20 test PF 0-.25 reject; Crabel early entry n19 too rare. Eval: V4+ & D2 + PIN f.65: DEV p20 14% p40 29% fail 1%, TEST 18%/33% fail 0% (small gain); adding WVB/ACD/OOPS raises fails | Crabel/Williams/Raschke/Fisher | T | scripts/lab/pros.py evalpros.py

X17| SHORT-TERM after 9:45 (5m signals, 1m mgmt): EMA20 pullback, EMA9/21 cross, 30m squeeze break, H2 second entry on ALL days: PF .78-.97 (lose). On TREND DAYS only (|10:29 price-open|>=.4 ADR, trade in that dir, entries after 10:30, daily SMA20 trend agrees): H2 2R no cap max3/day n143 (30/yr) PF1.44 DEV1.30 TEST1.82 yrs 1.34/1.20/1.37/1.18/2.53, hold 74m, risk 39pt; plateau th.3-.6 x tgt 2-3R all 1.2-1.9. Squeeze 2R trend-day PF1.78 but 2024 .79. Earlier trend-day runs that let trades start before 10:30 had lookahead (fixed). Eval: H2 must be HALF size (small stops + 8pt slip stress -> fails 13-18% at full); at half size fail 0-4%, pass<=20d 17-18%. Last 4 months H2: 9 tr, 8 wins, +$1,038/MNQ | Brooks H2 / ours | T | scripts/lab/shortterm.py evalh2*.py h2recent.py

### Q. new open questions
Q6 RESOLVED: instrument/behaviour, not definition. Narrow OR at any window = range + double break on MNQ. Q7 count anchor: Brooks H2 (from pullback start) vs Wade (from extreme, reset at DT) hit-rate on same bars. Q8 climax bar frequency (r>=2*ATR20 after 10 bars) and post-climax drift on MNQ. Q9 1-2tk failed-breakout fade (E19) vs E6 deep pokes. Q10 11:30 ET reversal window frequency on MNQ (D14 vs F11).

## X18 (2026-10-25) Exit review after Oct 22 walkthrough
- V4+: 2R + move stop to breakeven after +1R beats current (PF 1.61 -> 1.74, maxDD 7.8R -> 5.7R, total R +5%). "Exit at prior low after first pullback" cuts total R 28% (PF 1.51). Time caps 60/90m cut total R 50%+.
- Pinball: no-target hold to 15:55 is best (PF 2.85). 120-min cap keeps PF 2.77, halves hold (256 -> 115m), costs 30% of total R. Stretch-at-entry filter not supported (0.35-0.5 ADR bucket was best).
- Missed Oct 22 afternoon moves: day was -0.37 ADR at 10:29 (H2 needs 0.40). H2 at 0.25-0.30: PF 1.24-1.29 (test 1.38-1.41), 46-52/yr vs 30. TWAP rejection PF 1.1-1.3 but ~1.0 in 2025-26 (reject). EMA20 pullback PF < 1 (reject).

## X19 (2026-10-25) Four approved changes tested (rules2.py)
- Sep 1 - Oct 23 2026 eval sizing: current +$2,660, updated +$3,375 (still not a pass: Sep 21 = 59% of profit, breaks the 50% consistency rule).
- 2022 - Oct 2026 eval sim (+8pt stop slip), pass within 40 days: current 34% / 26% (22-24 / 25-26), updated 22% / 20%. Failure 4-5% / 0% both.
- Each change alone: shared budget neutral; V4+ BE 34->30 / 26->25; Pinball 2h 34->32 / 26->24; H2 0.30 34->32 / 26->21. None speeds the eval; the gain is shorter holds and smaller give-backs.
- Pine v4 (TradingView, script version 4) carries all four as inputs: v4BE, pinCap, h2Th, shared dayCap budget. Pine on Oct 19-23 bars matches Python (Pinball +22, H2 +53.25).
