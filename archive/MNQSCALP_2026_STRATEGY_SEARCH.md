# 2026 strategy search (started 2026-10-21 16:10 ET)

Brief from Jey: forget the eval for now; find strategies that are green most days, weeks and months. Test on Databento 5m, focus on 2026 (Jan 1 to Oct 20) and the last 6 months; correlate with the TradingView month. Two families: Thomas Wade price action, and ORB made adaptable to market structure. Don't mix strategies. Report TradingView-style: net P&L, max drawdown, % profitable trades, profit factor, plus daily green/red.

Method: every variant must be positive in BOTH halves of 2026 (Jan-May, Jun-Oct). Costs: $2.37/side, 1 tick slippage. Sizing: $300-400 risk per trade, max 20 micros.

## ORB family (1,632 variants, 2026)
- Only 25 of 1,632 positive in both halves; the best 2026 variant (30-min range, 15m break, structure stop, 1R at next level) is a 2026-only fit: it loses $3K to $11K every year 2022-2025. Rejected.
- Retest V2 as is: ~50% green days every year, last 6 months negative (-$3.2K).

## ORB adapted to market structure (the finding that holds in 2022-25 AND 2026)
Trade the opening-range break only on a "committed open": |gap| >= 0.6 x avg daily range (10 days) OR first 15 min |close-open| >= 60% of its range; skip if prior day range > 1.2 x ADR.
- ORB break, committed days: 2022-25 net +$15.1K PF 1.37 win 48% green 168/135 months+ 30/48 DD $2.7K; 2026 +$1.9K PF 1.29 win 47% green 23/19 months+ 7/10 (58 trades).
- Skipped days: PF 1.05 (2022-25) and 0.80 (2026). Last 6 months of 2026 skipped days PF 0.56.
- + skip Mon/Fri: PF 1.59 / 1.66, green 58%, but fewer trades (~1/week) and a weaker rationale.
- Same filter on Retest V2 (Jey's rules): 2022-25 PF 1.20; 2026 PF 1.46 green 31/24; last 6 months PF 1.37 green 18/16.
- Pine written: pine/MNQ_ORB_V2_ADAPTIVE.pine (inputs gapADR, dirFrac, pdMaxADR, skipMonFri). To verify in TradingView.

## Wade setup #3, failed breakout of the prior day high/low
Poke beyond PDH/PDL by 2-45 pts within 5 bars, signal bar closes back inside, stop order beyond it, stop beyond the poke + 5 pts, target 1R, 10:00-13:00.
- 2026-tuned version: +$3.1K, 26 trades, 81% win, 21 green / 5 red days, 9/9 months. But it lost in 2022, 2024, 2025 (won 2023). Whipsaw-regime setup.
- Robust version (the parameters above): positive 4 of 5 years, 56% green days, PF 1.3-1.6 in good years, ~2 trades/month in 2026 (+$823). Too few trades to be the main strategy.
- Does NOT improve by restricting to non-committed days. Regime switching on the last 10-40 days of follow-through does not predict.
- Pine written: pine/MNQ_FAILED_BREAK_V1.pine.

## Wade price action (V10 Python engine, 480 variants, 2026) - DONE
Setups: 2nd entries (H2/L2), lower high / higher low, breakout pullback, failed 2nd entry; sessions: full, RTH 10:00-15:30, NY 9:30-12:00, London+NY, evening; exits: TP1 1R + 3R runner/key level, 1R + 2R, 1.5R + 3R, single 2R; filters: ATR cap 1.5 + 15m trend, 15m only, none. 2 contracts, $150 risk.
- Among variants with >= 40 legs per half (about 2/week): 30 of 333 positive in both halves, 5 with >= 55% green days in both. Family green-day ratio 0.44-0.49.
- Best active: V10(+F2), NY 9:30-12:00, TP1 1R + 2R runner, 15m filter: Jan-May +$802 PF 1.36, Jun-Oct +$495 PF 1.25, green 35/32. Its edge is concentrated in 9:30-9:45 entries (9 of 9 legs won in H1); after 9:45 it is PF ~1.1.
- By session (avg over active variants): NY 9:30-12:00 is the only session positive in both halves. RTH 10:00-15:30: 0 of 71 positive in both halves. Full session: -$2.0K avg in Jan-May.
- By setup: nothing stands out; LH wins in H1 and loses in H2, BP longs the reverse. The loser pattern flips between halves = noise, not a rule.
- "Committed open" filter applied to Wade entries after 9:45: no help (avg net -$181 / -$427). Wade setups are not the ORB.
- Evening 18:00-24:00 variants show 70-90% win rates but 11-15 trades per half and $40-60 per leg: too small to trade.
- Next: same setups on 1m / 2m / 3m bars (closer to Wade's 2000-tick ES chart).

## Wade on 1m / 2m / 3m bars (144 variants, 2026)
- 1m: 0 of 48 positive in both halves (avg -$4K per half). 2m: 5 of 48. 3m: 4 of 48.
- Best (2m, 2nd entries + failed 2nd entries, NY 9:30-12:00, 15m trend filter): 2026 PF 2.5 / 1.7, but 2025 PF 0.55 (13 green / 16 red). A 2026 fit. Rejected.
- Conclusion for the mechanical Wade family: no edge in 2026 on any timeframe/session once entries after 9:45 are required; the only positive pocket is 9:30-9:45 entries, which is the opening range, not a Wade setup.

## THE CANDIDATE: ORB Retest V4 Adaptive (Jey's retest rules + committed open + with-bias)
Rules: 15-min opening range; a 5m close outside arms that side, a close back inside disarms; retest of the edge + bull/bear signal bar; stop order 1 tick beyond the signal bar; stop beyond the other side of the range; target 2R; last entry 13:00; flat 15:55; $400 risk, max 20 micros.
Day filter at 9:45: committed open = |gap vs prior RTH close| >= 0.6 x 10-day avg daily range OR first 15 min |close-open| >= 60% of its range; skip if prior day range > 1.2 x ADR. Direction: only the side of the gap (if any), else of the first 15 min.
| Period | Net | Trades | % profitable | PF | Days G/R | Months+ | Max DD | Worst day |
| 2022-2025 | +$6,148 | 225 | 52% | 1.24 | 117/103 | 24/48 | $2,162 | -$644 |
| 2026 (Jan 1-Oct 20) | +$2,684 | 40 | 58% | 1.70 | 23/17 | 7/10 | $1,081 | -$400 |
| Last 6 months | +$2,009 | 27 | 59% | 1.77 | 16/11 | 5/7 | $1,081 | -$400 |
| TradingView month (Sep 20-Oct 21) | +$1,310 | 9 | 67% | 3.60 | 6/2 | 2/2 | $467 | -$467 |
Trades against the open's direction: last 6 months PF 0.66, 3 green / 8 red. Non-committed days: PF 0.56 (16 green / 36 red).
Exit variants under the same filter (2026 / last 6m / 2022-25 PF): 2R no limit 1.70/1.77/1.24 (keep); max 60 min 1.47/1.47/1.07; max 90 min 1.66/1.47/1.03; TP1 50% + BE + 2R 1.71/1.75/1.15; 3R 1.44/1.37/1.28; structure stop 1.10/0.90/1.02 (no).
Fewer-but-better: target at the next support/resistance with 1R of room (the V3 Levels idea) under the same filter: 2022-25 PF 1.67 green 68/41; 2026 PF 2.86 green 11/4; last 6m PF 3.03 green 8/2, 6/6 months; but only ~1.5 trades/month.
Pine: pine/MNQ_ORB_RETEST_V4_ADAPTIVE.pine (not yet verified in TradingView). ORB break version: pine/MNQ_ORB_V2_ADAPTIVE.pine (2026 PF 1.29; with-bias PF 1.34, last 6m 1.42).
Expected trades since Sep 20 with both filters (for the TV check), 1 contract each: Sep 21 9:50 L 30372.25 -> 30684.25 target +619; Sep 23 9:50 S 30860.25 -> 30769.75 close +176; Sep 28 10:05 S 30593 -> 30567 close +47; Oct 2 10:05 L 31253 -> 31055.5 stop -400; Oct 5 10:25 L 31237.5 -> 31338.25 close +197; Oct 12 10:10 S 30880 -> 30896 close -37; Oct 14 10:10 S 30475.5 -> 30174 target +598. Net +$1,200, 7 trades, 5 winners.

### Pine: MNQ_ORB_RETEST_V4_ADAPTIVE.pine
```
//@version=5
strategy("MNQ ORB Retest V4 Adaptive", overlay=true, initial_capital=25000, commission_type=strategy.commission.cash_per_contract, commission_value=2.37, slippage=1, margin_long=0, margin_short=0, max_bars_back=500)

// ===== Inputs =====
orMins   = input.int(15, "Opening range minutes", options=[5, 10, 15, 30])
brkTF    = input.string("5m", "Breakout = candle close of", options=["5m", "15m"])
stopMode = input.string("Other side", "Stop at", options=["Other side", "Middle", "Structure", "Signal bar"])
bufTicks = input.int(4, "Structure stop buffer (ticks)")
minStopT = input.int(16, "Min stop (ticks)")
tgtR     = input.float(2.0, "Target (R multiple)")
riskUSD  = input.float(400, "Risk per trade ($)")
maxQty   = input.int(20, "Max contracts")
lastEnt  = input.int(1300, "Last entry time (HHMM ET)")
maxTrades = input.int(6, "Max trades per day (safety cap)")
dayLoss  = input.float(550, "Stop for the day at loss $ (0 = off)")
dayTgt   = input.float(600, "Stop for the day at profit $ (0 = off)")
sigFrac  = input.float(0.5, "Signal bar: close in top/bottom fraction")
minBody  = input.float(0.3, "Signal bar: min body / range")
comm     = input.float(2.37, "Commission per contract per side (sizing)")
// Market-structure filter: trade only on a committed open, and only in its direction
gapADR   = input.float(0.6, "Committed if |gap| >= x avg daily range (0 = off)")
dirFrac  = input.float(0.6, "...or first 15 min |close-open| >= x of its range (0 = off)")
pdMaxADR = input.float(1.2, "Skip if prior day range > x avg daily range (0 = off)")
withBias = input.bool(true, "Trade only in the direction of the open (gap first, else first 15 min)")
adrLen   = input.int(10, "Average daily range: days")

tz    = "America/New_York"
m     = hour(time, tz) * 60 + minute(time, tz)
orS   = 9 * 60 + 30
orE   = orS + orMins
lastM = int(lastEnt / 100) * 60 + lastEnt % 100
flatM = 15 * 60 + 55
tick  = syminfo.mintick
pv    = syminfo.pointvalue

var float orHi = na
var float orLo = na
var int   dir = 0
var bool  sawRt = false
var float rtExt = na
var int   dayTrades = 0
var float dayStart = 0.0

newDay = ta.change(dayofmonth(time, tz)) != 0
if newDay
    orHi := na
    orLo := na
    dir := 0
    sawRt := false
    rtExt := na
    dayTrades := 0
    dayStart := strategy.netprofit

if m >= orS and m < orE
    orHi := na(orHi) ? high : math.max(orHi, high)
    orLo := na(orLo) ? low : math.min(orLo, low)

// ----- prior day stats (RTH), average daily range, committed-open check at 9:45
var float dHi = na
var float dLo = na
var float dCl = na
var float pdH = na
var float pdL = na
var float pdC = na
var float[] ranges = array.new_float()
var float adr = na
var float dayOpen = na
var bool  dayOK = false
var int   bias = 0
inRTH = m >= orS and m < 16 * 60
if newDay and not na(dHi)
    pdH := dHi
    pdL := dLo
    pdC := dCl
    array.push(ranges, dHi - dLo)
    if array.size(ranges) > adrLen
        array.shift(ranges)
    adr := array.avg(ranges)
    dHi := na
    dLo := na
    dCl := na
if inRTH
    dHi := na(dHi) ? high : math.max(dHi, high)
    dLo := na(dLo) ? low : math.min(dLo, low)
    dCl := close
if m == orS
    dayOpen := open
    dayOK := false
    bias := 0
if m == orE - 5 and not na(adr) and not na(pdC)
    gap = (dayOpen - pdC) / adr
    dr  = (close - dayOpen) / math.max(orHi - orLo, tick)
    gapOK = gapADR > 0 and math.abs(gap) >= gapADR
    dirOK = dirFrac > 0 and math.abs(dr) >= dirFrac
    pdOK  = pdMaxADR <= 0 or (pdH - pdL) <= pdMaxADR * adr
    dayOK := (gapOK or dirOK) and pdOK
    bias := gapOK ? (gap > 0 ? 1 : -1) : dirOK ? (dr > 0 ? 1 : -1) : 0

pos  = strategy.position_size
prev = nz(pos[1])
if pos != 0 and prev == 0
    dayTrades += 1
if pos == 0 and prev != 0
    sawRt := false
    rtExt := na
dayPnl = strategy.netprofit - dayStart + strategy.openprofit

afterOR = m >= orE and not na(orHi)
rng   = high - low
bull  = close > open and rng > 0 and (close - low) >= sigFrac * rng and math.abs(close - open) >= minBody * rng
bear  = close < open and rng > 0 and (high - close) >= sigFrac * rng and math.abs(close - open) >= minBody * rng
inside = close <= orHi and close >= orLo
span   = brkTF == "15m" ? 15 : 5
closesSpan = (minute(time, tz) + 5) % span == 0

// breakout state: close outside arms that side; close back inside only disarms (no day cancel)
if afterOR and closesSpan and close > orHi and dir != 1
    dir := 1
    sawRt := false
    rtExt := na
else if afterOR and closesSpan and close < orLo and dir != -1
    dir := -1
    sawRt := false
    rtExt := na
if afterOR and inside and dir != 0
    dir := 0
    sawRt := false
    rtExt := na

// retest tracking
if dir == 1 and low <= orHi
    sawRt := true
    rtExt := na(rtExt) ? low : math.min(rtExt, low)
if dir == -1 and high >= orLo
    sawRt := true
    rtExt := na(rtExt) ? high : math.max(rtExt, high)

canTrade = dayOK and afterOR and pos == 0 and m + 5 <= lastM and m < flatM and dayTrades < maxTrades and (dayLoss <= 0 or dayPnl > -dayLoss) and (dayTgt <= 0 or dayPnl < dayTgt)
mid = math.round(((orHi + orLo) / 2) / tick) * tick

stopFor(side) =>
    stopMode == "Other side" ? (side > 0 ? orLo - tick : orHi + tick) : stopMode == "Middle" ? (side > 0 ? math.min(mid, rtExt) - tick : math.max(mid, rtExt) + tick) : stopMode == "Signal bar" ? (side > 0 ? low - tick : high + tick) : (side > 0 ? math.min(rtExt, orHi) - bufTicks * tick : math.max(rtExt, orLo) + bufTicks * tick)

placedL = false
placedS = false
if canTrade and dir == 1 and (not withBias or bias == 1) and sawRt and not inside and bull
    e   = high + tick
    stp = stopFor(1)
    r   = math.max(e + tick - stp, minStopT * tick)
    stp2 = e + tick - r
    q   = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
    if q >= 1
        strategy.entry("L", strategy.long, qty=q, stop=e)
        strategy.exit("XL", "L", stop=stp2, limit=e + tick + tgtR * r)
        placedL := true
if canTrade and dir == -1 and (not withBias or bias == -1) and sawRt and not inside and bear
    e   = low - tick
    stp = stopFor(-1)
    r   = math.max(stp - (e - tick), minStopT * tick)
    stp2 = e - tick + r
    q   = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
    if q >= 1
        strategy.entry("S", strategy.short, qty=q, stop=e)
        strategy.exit("XS", "S", stop=stp2, limit=e - tick - tgtR * r)
        placedS := true
if not placedL
    strategy.cancel("L")
if not placedS
    strategy.cancel("S")

if m >= flatM and m < 16 * 60 + 30
    strategy.close_all(comment="EOD", immediately=true)

// ===== Visuals =====
plot(afterOR and m < flatM ? orHi : na, "OR high", color=color.teal, style=plot.style_linebr)
plot(afterOR and m < flatM ? orLo : na, "OR low", color=color.maroon, style=plot.style_linebr)
bgcolor(m >= orS and m < orE ? color.new(color.blue, 90) : na)
bgcolor(dayOK and m >= orE and m < flatM ? color.new(bias > 0 ? color.green : color.red, 94) : na)
plotshape(placedL, "Long setup", shape.triangleup, location.belowbar, color.teal, size=size.tiny)
plotshape(placedS, "Short setup", shape.triangledown, location.abovebar, color.maroon, size=size.tiny)
```

### Pine: MNQ_ORB_V2_ADAPTIVE.pine
```
//@version=5
strategy("MNQ ORB V2 Adaptive", overlay=true, initial_capital=25000, commission_type=strategy.commission.cash_per_contract, commission_value=2.37, slippage=1, margin_long=0, margin_short=0, max_bars_back=500)

// Inputs
orMins   = input.int(15, "Opening range minutes", options=[5, 10, 15, 30])
lastEnt  = input.int(1130, "Last entry time (HHMM ET)")
flatT    = input.int(1555, "Flatten time (HHMM ET)")
riskUSD  = input.float(300, "Risk per trade ($)")
maxQty   = input.int(20, "Max contracts")
tgtR     = input.float(2.0, "Target (R multiple)")
both     = input.bool(true, "Allow other side after first trade")
comm     = input.float(2.37, "Commission per contract per side (for sizing)")
// Market-structure filters (trade the break only when the open shows commitment)
gapADR   = input.float(0.6, "Take the day if |gap| >= x avg daily range (0 = off)")
dirFrac  = input.float(0.6, "...or if first 15 min |close-open| >= x of its range (0 = off)")
pdMaxADR = input.float(1.2, "Skip if prior day range > x avg daily range (0 = off)")
skipMonFri = input.bool(false, "Skip Mondays and Fridays")
adrLen   = input.int(10, "Average daily range: days")

tz   = "America/New_York"
m    = hour(time, tz) * 60 + minute(time, tz)
orS  = 9 * 60 + 30
orE  = orS + orMins
lastM = int(lastEnt / 100) * 60 + lastEnt % 100
flatM = int(flatT / 100) * 60 + flatT % 100
tick = syminfo.mintick
pv   = syminfo.pointvalue

var float orHi = na
var float orLo = na
var bool usedL = false
var bool usedS = false
var int prevClosed = 0
var int trades = 0

newDay = ta.change(dayofmonth(time, tz)) != 0
if newDay
    orHi := na
    orLo := na
    usedL := false
    usedS := false
    trades := 0

if m >= orS and m < orE
    orHi := na(orHi) ? high : math.max(orHi, high)
    orLo := na(orLo) ? low : math.min(orLo, low)

// ----- prior day stats (RTH 9:30-16:00) and the average daily range
var float dHi = na
var float dLo = na
var float dCl = na
var float pdH = na
var float pdL = na
var float pdC = na
var float[] ranges = array.new_float()
var float adr = na
var float dayOpen = na
var bool  dayOK = false
inRTH = m >= orS and m < 16 * 60
if newDay and not na(dHi)
    pdH := dHi
    pdL := dLo
    pdC := dCl
    array.push(ranges, dHi - dLo)
    if array.size(ranges) > adrLen
        array.shift(ranges)
    adr := array.avg(ranges)
    dHi := na
    dLo := na
    dCl := na
if inRTH
    dHi := na(dHi) ? high : math.max(dHi, high)
    dLo := na(dLo) ? low : math.min(dLo, low)
    dCl := close
if m == orS
    dayOpen := open
    dayOK := false
if m == orE - 5 and not na(adr) and not na(pdC)
    gapOK = gapADR > 0 and math.abs(dayOpen - pdC) >= gapADR * adr
    dirOK = dirFrac > 0 and math.abs(close - dayOpen) >= dirFrac * (orHi - orLo)
    pdOK  = pdMaxADR <= 0 or (pdH - pdL) <= pdMaxADR * adr
    dowOK = not skipMonFri or (dayofweek(time, tz) != dayofweek.monday and dayofweek(time, tz) != dayofweek.friday)
    dayOK := (gapOK or dirOK) and pdOK and dowOK

// mark sides used (catches same-bar entry+exit too)
if strategy.position_size > 0
    usedL := true
if strategy.position_size < 0
    usedS := true
if strategy.closedtrades > prevClosed
    for i = prevClosed to strategy.closedtrades - 1
        if strategy.closedtrades.entry_id(i) == "L"
            usedL := true
        if strategy.closedtrades.entry_id(i) == "S"
            usedS := true
    trades += strategy.closedtrades - prevClosed
    prevClosed := strategy.closedtrades

// orders are placed at bar close and fill from the next bar (open time m+5)
canPlace = dayOK and m >= orE - 5 and m + 5 <= lastM and not na(orHi) and (both or trades == 0)
flat = strategy.position_size == 0

if flat and canPlace and not usedL
    e  = orHi + tick
    s  = orLo - tick
    r  = e + tick - s
    q  = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
    if q >= 1
        strategy.entry("L", strategy.long, qty=q, stop=e, oca_name="orb", oca_type=strategy.oca.cancel)
        strategy.exit("XL", "L", stop=s, limit=e + tick + tgtR * r)
else
    strategy.cancel("L")

if flat and canPlace and not usedS
    e  = orLo - tick
    s  = orHi + tick
    r  = s - (e - tick)
    q  = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
    if q >= 1
        strategy.entry("S", strategy.short, qty=q, stop=e, oca_name="orb", oca_type=strategy.oca.cancel)
        strategy.exit("XS", "S", stop=s, limit=e - tick - tgtR * r)
else
    strategy.cancel("S")

if m >= flatM and m < 16 * 60 + 30
    strategy.close_all(comment="EOD", immediately=true)

// visuals
plot(m >= orE and m < flatM ? orHi : na, "OR high", color=color.teal, style=plot.style_linebr)
plot(m >= orE and m < flatM ? orLo : na, "OR low", color=color.maroon, style=plot.style_linebr)
bgcolor(m >= orS and m < orE ? color.new(color.blue, 90) : na)
bgcolor(dayOK and m >= orE and m < flatM ? color.new(color.green, 94) : na)
```

### Pine: MNQ_FAILED_BREAK_V1.pine
```
//@version=5
strategy("MNQ Failed Break V1 (prior day high/low)", overlay=true, initial_capital=25000, commission_type=strategy.commission.cash_per_contract, commission_value=2.37, slippage=1, margin_long=0, margin_short=0, max_bars_back=500)

// Wade setup #3: price pokes through yesterday's high (or low), a bearish (bullish) signal bar closes back inside,
// sell stop 1 tick below that bar (buy stop above), stop beyond the poke extreme + buffer, target 1R.
pokeMin  = input.float(2, "Poke beyond the level: at least (points)")
pokeMax  = input.float(45, "Poke beyond the level: at most (points)")
within   = input.int(5, "Poke happened within the last N bars")
bufPts   = input.float(5, "Stop buffer beyond the poke (points)")
minStop  = input.float(4, "Min stop (points)")
maxStop  = input.float(60, "Max stop (points)")
tgtR     = input.float(1.0, "Target (R multiple)")
riskUSD  = input.float(300, "Risk per trade ($)")
maxQty   = input.int(20, "Max contracts")
firstEnt = input.int(1000, "First entry time (HHMM ET)")
lastEnt  = input.int(1300, "Last entry time (HHMM ET)")
maxTrades = input.int(4, "Max trades per day")
sigFrac  = input.float(0.5, "Signal bar: close in top/bottom fraction")
minBody  = input.float(0.3, "Signal bar: min body / range")
comm     = input.float(2.37, "Commission per contract per side (sizing)")

tz   = "America/New_York"
m    = hour(time, tz) * 60 + minute(time, tz)
tick = syminfo.mintick
pv   = syminfo.pointvalue
flatM = 15 * 60 + 55
firstM = int(firstEnt / 100) * 60 + firstEnt % 100
lastM  = int(lastEnt / 100) * 60 + lastEnt % 100
inRTH  = m >= 9 * 60 + 30 and m < 16 * 60

// prior day RTH high / low
var float rthHi = na
var float rthLo = na
var float pdH = na
var float pdL = na
var bool usedH = false
var bool usedL = false
var int dayTrades = 0
newDay = ta.change(dayofmonth(time, tz)) != 0
if newDay and not na(rthHi)
    pdH := rthHi
    pdL := rthLo
    rthHi := na
    rthLo := na
if newDay
    usedH := false
    usedL := false
    dayTrades := 0
if inRTH
    rthHi := na(rthHi) ? high : math.max(rthHi, high)
    rthLo := na(rthLo) ? low : math.min(rthLo, low)

pos = strategy.position_size
if pos != 0 and nz(pos[1]) == 0
    dayTrades += 1

rng  = high - low
bull = close > open and rng > 0 and (close - low) >= sigFrac * rng and math.abs(close - open) >= minBody * rng
bear = close < open and rng > 0 and (high - close) >= sigFrac * rng and math.abs(close - open) >= minBody * rng
hiN  = ta.highest(high, within)
loN  = ta.lowest(low, within)

canTrade = inRTH and m >= firstM and m <= lastM and pos == 0 and dayTrades < maxTrades and not na(pdH)

placedS = false
placedL = false
// failed break of the prior day HIGH -> short
if canTrade and not usedH and bear and close < pdH and close[1] <= pdH + pokeMax
    poke = hiN - pdH
    if poke >= pokeMin and poke <= pokeMax
        e   = low - tick
        stp = hiN + bufPts
        r   = math.max(stp - (e - tick), minStop)
        q   = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
        usedH := true
        if r <= maxStop and q >= 1
            strategy.entry("S", strategy.short, qty=q, stop=e)
            strategy.exit("XS", "S", stop=e - tick + r, limit=e - tick - tgtR * r)
            placedS := true
// failed break of the prior day LOW -> long
if canTrade and not usedL and bull and close > pdL and close[1] >= pdL - pokeMax
    poke = pdL - loN
    if poke >= pokeMin and poke <= pokeMax
        e   = high + tick
        stp = loN - bufPts
        r   = math.max((e + tick) - stp, minStop)
        q   = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
        usedL := true
        if r <= maxStop and q >= 1
            strategy.entry("L", strategy.long, qty=q, stop=e)
            strategy.exit("XL", "L", stop=e + tick - r, limit=e + tick + tgtR * r)
            placedL := true
if not placedS
    strategy.cancel("S")
if not placedL
    strategy.cancel("L")
if m >= flatM and m < 16 * 60 + 30
    strategy.close_all(comment="EOD", immediately=true)

plot(inRTH ? pdH : na, "Prior day high", color=color.orange, style=plot.style_linebr)
plot(inRTH ? pdL : na, "Prior day low", color=color.aqua, style=plot.style_linebr)
plotshape(placedS, "Short setup", shape.triangledown, location.abovebar, color.maroon, size=size.tiny)
plotshape(placedL, "Long setup", shape.triangleup, location.belowbar, color.teal, size=size.tiny)
```
