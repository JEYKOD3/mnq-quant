# MNQ scalp-rules test + Retest V3 Levels (2026-10-21)

Jey's review (Oct 19 10:55 long held 3.5h into Oct 16 resistance; Oct 6 10:05 long at top; Oct 8 10:20; Sep 23 9:45 short = ideal) asked for:
40-min max hold, 10-30 pt targets, preset stop/target, exit on first pullback, take profit at prior resistance, more contracts / add to winners, best Wade setup redone.

All tested on 5 years MNQ (5m and 1m bars), Lucid Flex 25K, vs random entries.

## Results
- Max hold 20/30/40 min: turns both ORB strategies negative (ORB break -$3.5K to -$7.5K; Retest V2 -$9.5K to -$11K).
- Point targets 8-30 pts: win 60-90% but every combination loses (-$7K to -$33K), almost no passes.
- Point stops 10-30 pts: lose heavily (ORB 30-pt stop wins 20-36%). Breakouts retrace into the range before running.
- On 5m bars the engine counts the breakout candle's earlier low as a stop hit (pessimistic for tight stops); rerun on 1m bars gave the same conclusion.
- Exit at first pullback, exit on 3 shrinking bodies: lose.
- More size (risk $400 -> $800, ~2x contracts): profit up ($23K -> $35K), passes faster (7 days), but fails 60% -> 74%, evals per pass 2.5 -> 3.8.
- Add to winners at +0.5R/+1R on a strong candle: every variant raises fail rate; evals per pass worse (ORB 2.1 -> 3.3+).
- Wade 2E redone (start 10:00, level targets, room filter, 40-min, swing trend, HL/LH): 16 of 192 combos profitable, all ~1 trade/month. Not viable.

## The one rule that helped: room to the next level (Jey's "clear stop + clear target or no trade")
Retest V2 + target just before the next support/resistance (3-bar pivots of last 3 days + prior day high/low, ignore levels < 4 pts) + skip if room < 1R.
- 470 trades in 5 yrs, +$17K, 54% win, positive 6/6 years.
- Flex 25K, no time limit (60-day window): PASS 38 / FAIL 33 (random 20/65), 1.9 evals per pass (best of anything), median 33 days.
- 20-day window: most evals unfinished (trades ~1 day in 3).
- ORB break unchanged for comparison: 48/52, 2.1 evals per pass, median 14 days.

## TradingView
"MNQ ORB Retest V3 Levels" saved and on the chart (with ORB V1). Sep 20 - Oct 21 2026: TV 4 trades +$615, engine 4 trades +$616 (Sep 21 L, Oct 2 L, Oct 6 L, Oct 14 S). Verified.

## Eval Lab v12
Retest V2 box: "Target = next support/resistance" + "Skip if room < x risk". Exits box: max time in trade (10-60 min).

## Pine: MNQ_ORB_RETEST_V3.pine
```
//@version=5
strategy("MNQ ORB Retest V3 Levels", overlay=true, initial_capital=25000, commission_type=strategy.commission.cash_per_contract, commission_value=2.37, slippage=1, margin_long=0, margin_short=0, max_bars_back=500)

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
useLvl   = input.bool(true, "Target = next support/resistance (pivots of last 3 days + prior day high/low)")
lvlGap   = input.float(4, "Ignore levels closer than (points)")
minRoomR = input.float(1.0, "Skip if room to next level < (x risk, 0 = off)")

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

// ===== Support / resistance levels =====
var float[] lvP = array.new_float()
var int[]   lvD = array.new_int()
var int dayN = 0
var float rthHi = na
var float rthLo = na
var float pdH = na
var float pdL = na
inRTH = m >= orS and m < 16 * 60
if newDay and not na(rthHi)
    pdH := rthHi
    pdL := rthLo
    rthHi := na
    rthLo := na
    dayN += 1
    while array.size(lvD) > 0 and array.get(lvD, 0) < dayN - 3
        array.shift(lvD)
        array.shift(lvP)
if inRTH
    rthHi := na(rthHi) ? high : math.max(rthHi, high)
    rthLo := na(rthLo) ? low : math.min(rthLo, low)
ph = ta.pivothigh(high, 3, 3)
pl = ta.pivotlow(low, 3, 3)
pm = hour(time[3], tz) * 60 + minute(time[3], tz)
pivInRTH = pm >= orS and pm < 16 * 60 and dayofmonth(time[3], tz) == dayofmonth(time, tz)
if not na(ph) and pivInRTH
    array.push(lvP, ph)
    array.push(lvD, dayN)
if not na(pl) and pivInRTH
    array.push(lvP, pl)
    array.push(lvD, dayN)

nextLevel(side, px) =>
    float best = na
    if not na(pdH) and (pdH - px) * side >= lvlGap
        best := pdH
    if not na(pdL) and (pdL - px) * side >= lvlGap
        best := na(best) ? pdL : (side > 0 ? math.min(best, pdL) : math.max(best, pdL))
    if array.size(lvP) > 0
        for k = 0 to array.size(lvP) - 1
            v = array.get(lvP, k)
            if (v - px) * side >= lvlGap
                best := na(best) ? v : (side > 0 ? math.min(best, v) : math.max(best, v))
    best

if m >= orS and m < orE
    orHi := na(orHi) ? high : math.max(orHi, high)
    orLo := na(orLo) ? low : math.min(orLo, low)

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

canTrade = afterOR and pos == 0 and m + 5 <= lastM and m < flatM and dayTrades < maxTrades and (dayLoss <= 0 or dayPnl > -dayLoss) and (dayTgt <= 0 or dayPnl < dayTgt)
mid = math.round(((orHi + orLo) / 2) / tick) * tick

stopFor(side) =>
    stopMode == "Other side" ? (side > 0 ? orLo - tick : orHi + tick) : stopMode == "Middle" ? (side > 0 ? math.min(mid, rtExt) - tick : math.max(mid, rtExt) + tick) : stopMode == "Signal bar" ? (side > 0 ? low - tick : high + tick) : (side > 0 ? math.min(rtExt, orHi) - bufTicks * tick : math.max(rtExt, orLo) + bufTicks * tick)

placedL = false
placedS = false
if canTrade and dir == 1 and sawRt and not inside and bull
    e   = high + tick
    stp = stopFor(1)
    r   = math.max(e + tick - stp, minStopT * tick)
    stp2 = e + tick - r
    q   = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
    tgt = e + tick + tgtR * r
    lv  = useLvl ? nextLevel(1, e + tick) : na
    room = na(lv) ? 1e9 : lv - (e + tick)
    if not na(lv)
        tgt := math.min(tgt, lv - tick)
    if q >= 1 and (not useLvl or minRoomR <= 0 or room >= minRoomR * r)
        strategy.entry("L", strategy.long, qty=q, stop=e)
        strategy.exit("XL", "L", stop=stp2, limit=tgt)
        placedL := true
if canTrade and dir == -1 and sawRt and not inside and bear
    e   = low - tick
    stp = stopFor(-1)
    r   = math.max(stp - (e - tick), minStopT * tick)
    stp2 = e - tick + r
    q   = math.min(maxQty, math.floor(riskUSD / (r * pv + 2 * comm)))
    tgt = e - tick - tgtR * r
    lv  = useLvl ? nextLevel(-1, e - tick) : na
    room = na(lv) ? 1e9 : (e - tick) - lv
    if not na(lv)
        tgt := math.max(tgt, lv + tick)
    if q >= 1 and (not useLvl or minRoomR <= 0 or room >= minRoomR * r)
        strategy.entry("S", strategy.short, qty=q, stop=e)
        strategy.exit("XS", "S", stop=stp2, limit=tgt)
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
plotshape(placedL, "Long setup", shape.triangleup, location.belowbar, color.teal, size=size.tiny)
plotshape(placedS, "Short setup", shape.triangledown, location.abovebar, color.maroon, size=size.tiny)
```
