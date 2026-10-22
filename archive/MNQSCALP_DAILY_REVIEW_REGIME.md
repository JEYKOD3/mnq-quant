# Daily review, regime check, key-level test, Moomoo engine plan (2026-10-21)

Jey's direction: judge by daily green/red P&L and what losing trades share; stops/targets at key swing levels (not the opening range);
compare a month with the same month last year instead of 5-year totals; contracts only matter for pass/fail; scalp with momentum.

## Oct 2026 vs Oct 2025 (daily)
- ORB break: Oct 2026 -$590 (3 green / 5 red days); Oct 2025 +$1,274 (13 / 8).
- Retest V2: Oct 2026 -$886 (4 / 7); Oct 2025 +$2,334 (13 / 6).
- Retest V3 Levels: Oct 2026 -$4 (1 / 2); Oct 2025 +$33 (5 / 3).

## The market changed (same month last year)
First break of the 9:30-9:45 range: did it run one more range-width before coming back to the other side?
- Oct 2024 14 followed / 9 failed; Oct 2025 8 / 15; Oct 2026 2 / 12. Aug 2025 11 / 10; Aug 2026 5 / 16.
- Avg 5m candle after 10:00: Oct 2025 29.5 pt, Oct 2026 34.6 pt; avg day range 320 vs 385 pt. A 10-pt target is a third of one candle.
- Fading the failed break (Wade-style trap) also loses (Oct 2026 -$785, Aug-Oct 2026 -$2.2K): breaks fail both ways (whipsaw).
- By Jey's rule (same trend as last year = same strategy), the ORB strategies should not be traded in this regime.

## What losing trades share (Oct 2025 - Oct 2026)
- ORB break: against/no trend -$5.4K (win 34%) vs with trend +$3.5K (51%); entries 9:45-10:00 -$5.0K; wrong side of EMA21 -$3.8K.
- Retest V2: stretched > 2 candles from EMA21 -$2.9K vs 0-2 candles +$7.6K; < 50 pt room to prior-day H/L -$1.8K.
Turning them into rules, checked on the year before (Oct 2024 - Sep 2025):
- ORB start at 10:00: worse in both years (waiting = worse fills).
- Retest V2 not-stretched filter: better in the year found (+$6.9K vs +$3.6K), worse the year before (+$2.3K vs +$5.4K). Not kept.
- ORB trend filter: first result (+$7.7K / +$16K) was an artifact of filling late orders at the level; with realistic fills:
  "wait for trend" ~ no gain; "skip the side if trend disagrees" PF 1.45 in both recent years, eval fail 6-7%, but ~6 trades/month and PF 1.11 in 2021-24.

## Key-level scalper (stops/targets at swing levels, momentum break or retest, after 10:00)
Engine simKL: levels = swing highs/lows (3, 6, 12 bars each side) of the last 1-3 days + prior day H/L; stop beyond level/retest wick; target next level; room filter.
- 5m: 11 of 96 versions profitable over 13 months, all ~2 trades/month. 1m: 0 of 96. Not viable as built.

## Eval Lab v13
New "Day by day" card: month picker; the month and the same month last year as green/red calendars (P&L, trades, win, avg win/loss, PF,
market: day range and opening-range follow-through/fail); "What the losing trades have in common" table (trend, entry time, stretch, gap,
prior day, side, time in trade) for the month, last 12 months, or the whole period. Click a day to open it on the chart.

## Moomoo engine plan (not built yet)
Two pieces: (1) Mai Language signal indicator with numeric outputs; (2) Custom Algo strategy (cards) that reads them.
Indicator draft: MNQ_ORB_SIG (below). Outputs: LONG_ENTRY, SHORT_ENTRY, ENTRY/STOP/TARGET prices, QTY, FLAT_NOW.
Algo cards (5m bar close): if position = 0 and LONG_ENTRY = 1 -> buy QTY; if long and (low <= STOP_LONG_PX or high >= TARGET_LONG_PX) -> close;
mirror for shorts; FLAT_NOW = 1 -> close all; one trade per side per day.
To check in Moomoo before building: can an Algo place a stop order at an indicator price (else market at bar close, re-test the difference);
can TP/SL use indicator prices (vs fixed %); does backtest run on bar close; are futures shorts supported in backtest;
does the chart EMA include overnight bars (engine used 9:30-16:00 bars only).
Verification: apply indicator, compare its signals with TradingView for Oct 2026 day by day, then build cards, then compare one month of trades.

### MNQ_ORB_SIG (Mai Language draft)
```
{====================================}
{ MNQ_ORB_SIG - signals for the      }
{ moomoo Engine (Custom Algo)        }
{ 5 minute MNQ chart                 }
{ ORB break, trend side only         }
{====================================}

{===== PARAMETERS =====}
{ LABEL_END: 1 if the first bar after the 9:30 open shows 09:35, 0 if it shows 09:30 }
LABEL_END:=1;
RISK_USD:=300;
TGT_R:=2;
MAX_QTY:=20;
TK:=0.25;
USE_TREND:=1;

{===== OPENING RANGE 9:30-9:45 =====}
ORE:=IF(LABEL_END=1,945,940);
LASTE:=IF(LABEL_END=1,1135,1130);
FLATT:=IF(LABEL_END=1,1600,1555);
ORH:=VALUEWHEN(TIME=ORE,HHV(H,3));
ORL:=VALUEWHEN(TIME=ORE,LLV(L,3));
N:=BARSLAST(TIME=ORE);
WINDOW:=TIME>ORE AND TIME<=LASTE;

{===== TREND (EMA 21, last 3 completed candles) =====}
EM:=EMA(C,21);
UP_T:=REF(EM,1)>REF(EM,4) AND REF(C,1)>REF(EM,1);
DN_T:=REF(EM,1)<REF(EM,4) AND REF(C,1)<REF(EM,1);

{===== LEVELS =====}
BUY_STOP:=ORH+TK;
SELL_STOP:=ORL-TK;
R_PTS:=BUY_STOP-SELL_STOP;

{===== FIRST TOUCH OF EACH SIDE; TAKEN ONLY IF THE TREND AGREES =====}
HIT_L:=WINDOW AND H>=BUY_STOP;
HIT_S:=WINDOW AND L<=SELL_STOP;
FIRST_L:=HIT_L AND COUNT(HIT_L,N)=1;
FIRST_S:=HIT_S AND COUNT(HIT_S,N)=1;
QTYV:=MIN(MAX_QTY,FLOOR(RISK_USD/(R_PTS*2+4.74)));
GO_L:=FIRST_L AND QTYV>=1 AND (USE_TREND=0 OR UP_T);
GO_S:=FIRST_S AND QTYV>=1 AND (USE_TREND=0 OR DN_T);

{===== OUTPUTS THE ENGINE READS =====}
LONG_ENTRY:IF(GO_L,1,0),NODRAW;
SHORT_ENTRY:IF(GO_S,1,0),NODRAW;
ENTRY_LONG_PX:BUY_STOP,NODRAW;
ENTRY_SHORT_PX:SELL_STOP,NODRAW;
STOP_LONG_PX:SELL_STOP,NODRAW;
STOP_SHORT_PX:BUY_STOP,NODRAW;
TARGET_LONG_PX:BUY_STOP+TGT_R*R_PTS,NODRAW;
TARGET_SHORT_PX:SELL_STOP-TGT_R*R_PTS,NODRAW;
QTY:QTYV,NODRAW;
FLAT_NOW:IF(TIME>=FLATT AND TIME<1700,1,0),NODRAW;

{===== CHART LABELS =====}
DRAWTEXT(GO_L,L-15,'ORB BUY'),COLOR25B77B;
DRAWTEXT(GO_S,H+15,'ORB SELL'),COLORE79332;
DRAWTEXT((FIRST_L AND NOT(GO_L)) OR (FIRST_S AND NOT(GO_S)),H+30,'SKIP: AGAINST TREND OR TOO WIDE'),COLORF2D365;
```
