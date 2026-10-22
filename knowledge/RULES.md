# RULES.md — machine-first rule registry (my shorthand; not for humans)
fmt: ID | stmt (ticks/ATR/bars; MNQ tick=0.25pt=$0.50) | src | status | result
status: U untested · T tested · K keep · X rejected · P partial
ADR = 10d avg RTH range. ATR = per-bar avg range (n given). IB = 9:30-10:30 range. t = ET minutes.
friction MNQ = 3pt/rt (comm 2.37x2 + ~2tk). any rule must be PF_net>1 @3pt and survive @4pt.

## D. day-type / bias (known at time t)
D1 | t=945: committed = |gap|>=0.6ADR or |c15-o15|>=0.6*r15; skip if pdRange>1.2ADR; bias=sign(gap) else sign(first15) | ours (V4) | K | 2022-25 PF1.24 g117/r103; 2026 PF1.70 g23/r17
D1b| drop gap term, keep first15 dir only | tradingstats ORB (gap dir no effect; candle dir 76-80%) | U |
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
E3 | IB retest: after 1.1x IB reached, level retested 87% (NQ), then continued 71%; past 1.4x -> reversal odds > continuation. entry = first retest holding within 10% IB; stop .25IB beyond; tgt 1.3xIB | tradingstats IB | U |
E4 | depth curve: break extending <0.4x prior-bar range fails back inside 65-71%; >0.4x holds ~80% | tradingstats ext | U | fade/continue switch
E5 | Wade H2/L2 @EMA21: count from extreme, leg alive until 1tk break of last bar; 1st entry skip; 2nd entry = trade; reset on new extreme/pivot break/double top-bottom; no 3rd entries | wade | T | 1m/3m/5m all PF<0.8 unfiltered; 5m TREND days + ; RANGE days kill it
E5f| E5 on 5m, after 1030, only if D2 mv>=0.4 & pullback<0.4 | greenday_lab3 | P | PF1.14 n=67 +160pt (thin, 2024-carried)
E6 | failed break V1: poke 2-45pt beyond PDH/PDL within 5 bars, close back, stop beyond poke+5, max 60, tgt 1R, 10:00-13:00 | ours | P | +2023/2026, -2022/24/25
E7 | VWAP first touch after 1030 on D2-qualified days, 1m close back on trend side, stop .25ATR, tgt 1ATR | institutional | U |
E8 | first pullback after 1030 with D2 side, tgt ~0.1ADR, stop beyond pullback | greenday_lab4 | U | next
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
