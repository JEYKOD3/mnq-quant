# MNQ ORB: exits test, TradingView check, lab cleanup (2026-10-21)

## TradingView check (ORB Retest V2, Sep 21 - Oct 21 2026, MNQ 5m)
- TradingView: 21 trades, 8 winners, -$650. Engine same window: 21 trades, 8 winners, -$843. The TV script matches the engine.
- Saved in TV as "MNQ ORB Retest V2", on the chart with "MNQ ORB V1 - NY Open" (the ORB break).

## Monthly consistency (5 years, MNQ)
- ORB break ($300 risk, other-side stop, 2R, last entry 11:30): +$22.9K, 42 of 61 months positive. Aug 2026 -$2,770, Sep +$926, Oct -$590.
- ORB retest V2 ($400 risk, other-side stop, 2R): +$22.4K, 37 of 61 months positive. Last 3 months negative (Aug -$1,832, Sep -$747, Oct -$886).

## Exit test: can we capture more of each move?
Engine now supports TP1 partial, breakeven after TP1, runner target, trailing stop (last N bars after +X R).
Grid: target 1/1.5/2/3/none x TP1 0/0.5/1 (50%) x BE on/off x trail off/3/6 bars. Flex 25K, 30-day evals.
- Retest V2 baseline (2R, nothing else): +$22.4K, 37% pass / 60% fail. Best alternative TP1 1R + runner 2R: +$20.7K, 38/58. Everything else worse.
- ORB break baseline: +$22.9K, 43% pass / 51% fail. Best. TP1, BE and trailing all reduce net and passes.
- Why: about half of Retest V2 trades end at 15:55 (682 of 1,384) because the other-side stop is wide; early profit-taking and breakeven cut winners more than they save losers.
- Opening-range width filters (skip flat or huge ranges vs 20-day average) also did not beat no filter.
Conclusion: keep the plain 2R target. The missed opportunity is not in the exits.

## Eval Lab (version 11)
Cleaned to MNQ only, two strategies (ORB break, ORB retest V2), plus an "Exits" box (TP1, TP1 %, breakeven, trailing). Removed Wade 2E, Wade V10, Retest V1, ORB + Wade H2, MES.

## Moomoo (parked, user request)
Two Mai Language indicators written and checked by replay (retest replay: 1,396 trades, +$20.1K vs engine 1,384 / +$22.4K). LABEL_END must match how Moomoo labels 5m bars (09:35 for the first bar = 1).

### MNQ_ORB_BREAK
```
{====================================}
{ MNQ ORB BREAK - 5 MINUTE CHART     }
{ Opening range 9:30-9:45 ET         }
{ Buy stop 1 tick above range high   }
{ Sell stop 1 tick below range low   }
{ Stop = other side, target = 2R     }
{ Last entry 11:30 ET, flat 15:55 ET }
{====================================}

{===== PARAMETERS =====}
{ LABEL_END: 1 if the first bar after the 9:30 open shows 09:35, 0 if it shows 09:30 }
LABEL_END:=1;
RISK_USD:=300;
TGT_R:=2;
MAX_QTY:=20;
TK:=0.25;

{===== OPENING RANGE (last OR bar = 9:40-9:45) =====}
ORE:=IF(LABEL_END=1,945,940);
LASTE:=IF(LABEL_END=1,1135,1130);
ORH:=VALUEWHEN(TIME=ORE,HHV(H,3));
ORL:=VALUEWHEN(TIME=ORE,LLV(L,3));
N:=BARSLAST(TIME=ORE);
WINDOW:=TIME>ORE AND TIME<=LASTE;

{===== LEVELS =====}
BUY_STOP:ORH+TK,COLOR25B77B;
SELL_STOP:ORL-TK,COLORE79332;
R_PTS:=BUY_STOP-SELL_STOP;
LONG_TP:BUY_STOP+TGT_R*R_PTS,COLOR087A42;
SHORT_TP:SELL_STOP-TGT_R*R_PTS,COLORC93636;
QTY:MIN(MAX_QTY,FLOOR(RISK_USD/(R_PTS*2+4.74))),NODRAW;

{===== FIRST TOUCH EACH SIDE =====}
HIT_L:=WINDOW AND H>=BUY_STOP;
HIT_S:=WINDOW AND L<=SELL_STOP;
FIRST_L:=HIT_L AND COUNT(HIT_L,N)=1;
FIRST_S:=HIT_S AND COUNT(HIT_S,N)=1;

DRAWTEXT(FIRST_L AND QTY>=1,L-15,'ORB BUY'),COLOR25B77B;
DRAWTEXT(FIRST_S AND QTY>=1,H+15,'ORB SELL'),COLORE79332;
DRAWTEXT((FIRST_L OR FIRST_S) AND QTY<1,H+30,'SKIP: RANGE TOO WIDE'),COLORF2D365;

{ Outputs for the data window }
LONG_SIGNAL:IF(FIRST_L AND QTY>=1,1,0),NODRAW;
SHORT_SIGNAL:IF(FIRST_S AND QTY>=1,1,0),NODRAW;
```

### MNQ_ORB_RETEST_V2
```
{====================================}
{ MNQ ORB RETEST V2 - 5 MINUTE CHART }
{ Opening range 9:30-9:45 ET         }
{ 1. A 5m close outside the range    }
{    arms that side                  }
{ 2. A close back inside disarms it  }
{    (no trade while inside)         }
{ 3. Price comes back to touch the   }
{    range edge (retest)             }
{ 4. A strong candle away from the   }
{    range = signal bar              }
{ 5. Buy stop 1 tick above signal    }
{    bar high (sell stop 1 tick below}
{    its low), next bar only         }
{ Stop = other side of the range     }
{ Target = 2R, last signal 13:00 ET  }
{====================================}

{===== PARAMETERS =====}
{ LABEL_END: 1 if the first bar after the 9:30 open shows 09:35, 0 if it shows 09:30 }
LABEL_END:=1;
RISK_USD:=400;
TGT_R:=2;
MIN_STOP:=4;
MAX_QTY:=20;
SIG_FRAC:=0.5;
MIN_BODY:=0.3;
TK:=0.25;

{===== OPENING RANGE =====}
ORE:=IF(LABEL_END=1,945,940);
LASTE:=IF(LABEL_END=1,1300,1255);
ORH:VALUEWHEN(TIME=ORE,HHV(H,3)),COLOR25B77B;
ORL:VALUEWHEN(TIME=ORE,LLV(L,3)),COLORE79332;
WINDOW:=TIME>ORE AND TIME<=LASTE;

{===== SIGNAL CANDLES =====}
RNG:=H-L;
BULL:=RNG>0 AND C>O AND (C-L)>=SIG_FRAC*RNG AND ABS(C-O)>=MIN_BODY*RNG;
BEAR:=RNG>0 AND C<O AND (H-C)>=SIG_FRAC*RNG AND ABS(C-O)>=MIN_BODY*RNG;

{===== ARMED SIDE + RETEST =====}
{ bars in the current run of closes above the high / below the low }
KU:=BARSLAST(C<=ORH);
KD:=BARSLAST(C>=ORL);
RT_UP:=C>ORH AND COUNT(L<=ORH,KU)>=1;
RT_DN:=C<ORL AND COUNT(H>=ORL,KD)>=1;

LSIG:=WINDOW AND RT_UP AND BULL;
SSIG:=WINDOW AND RT_DN AND BEAR;

{===== ORDER LEVELS FOR THE SIGNAL BAR =====}
L_ENTRY:=H+TK;
L_R:=MAX(L_ENTRY+TK-(ORL-TK),MIN_STOP);
L_STOP:=L_ENTRY+TK-L_R;
L_TP:=L_ENTRY+TK+TGT_R*L_R;
L_QTY:=MIN(MAX_QTY,FLOOR(RISK_USD/(L_R*2+4.74)));

S_ENTRY:=L-TK;
S_R:=MAX((ORH+TK)-(S_ENTRY-TK),MIN_STOP);
S_STOP:=S_ENTRY-TK+S_R;
S_TP:=S_ENTRY-TK-TGT_R*S_R;
S_QTY:=MIN(MAX_QTY,FLOOR(RISK_USD/(S_R*2+4.74)));

DRAWTEXT(LSIG AND L_QTY>=1,L-15,'RT BUY STOP'),COLOR25B77B;
DRAWTEXT(SSIG AND S_QTY>=1,H+15,'RT SELL STOP'),COLORE79332;
DRAWTEXT((LSIG AND L_QTY<1) OR (SSIG AND S_QTY<1),H+30,'SKIP: STOP TOO WIDE'),COLORF2D365;

{ Last signal levels (read them in the data window) }
LAST_ENTRY:VALUEWHEN(LSIG OR SSIG,IF(LSIG,L_ENTRY,S_ENTRY)),NODRAW;
LAST_STOP:VALUEWHEN(LSIG OR SSIG,IF(LSIG,L_STOP,S_STOP)),NODRAW;
LAST_TARGET:VALUEWHEN(LSIG OR SSIG,IF(LSIG,L_TP,S_TP)),NODRAW;
LAST_QTY:VALUEWHEN(LSIG OR SSIG,IF(LSIG,L_QTY,S_QTY)),NODRAW;
LONG_SIGNAL:IF(LSIG AND L_QTY>=1,1,0),NODRAW;
SHORT_SIGNAL:IF(SSIG AND S_QTY>=1,1,0),NODRAW;
```
