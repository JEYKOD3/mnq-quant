```pine
//@version=5
// MNQ Playbook v6 (2026-10-25): NEWS / V4+ / D2 / TDP / Pinball / H2 on one shared daily risk budget.
// One engine, several charts: every chart runs ALL six strategies and the shared budget, so sizes and "budget left" match everywhere.
// The "Show on this chart" input only decides which strategies draw markers and fire alerts on that chart.
//   Chart 1  Open & News   : NEWS (8:30-9:30), V4+ (9:45-13:00), D2 (10:30)
//   Chart 2  Trend & Swing : TDP (10:30-12:00), H2 (10:30-15:00, half size), Pinball (10:30-15:00)
// Use MNQ1! 1-minute, extended hours ON (needed for NEWS and the 8:29 price). Not an auto-trader: markers, sizes, alerts.
// Hover any marker for the full reason, entry, stop, target, size and risk.
indicator("MNQ Playbook v6", shorttitle="Playbook", overlay=true, max_lines_count=400, max_labels_count=400, max_boxes_count=200)

// ---------- chart group ----------
G_ALL = "All strategies"
G_1 = "Chart 1: Open & News (NEWS, V4+, D2)"
G_2 = "Chart 2: Trend & Swing (TDP, H2, Pinball)"
grp = input.string(G_1, "Show on this chart", options=[G_ALL, G_1, G_2], group="Chart")
g1 = grp != G_2
g2 = grp != G_1
showPD = input.bool(true, "Prior-day high / low / close lines", group="Chart")
showOR = input.bool(true, "Opening range (9:30-9:45) lines", group="Chart")
showPanel = input.bool(true, "Show panel", group="Chart")
showLog = input.bool(false, "Show last trades table", group="Chart")
showStats = input.bool(false, "Show results table (loaded bars)", group="Chart")
emaLen = input.int(20, "EMA length (0 = off)", group="Chart")
plot(emaLen > 0 ? ta.ema(close, emaLen) : na, "EMA", color=color.new(color.fuchsia, 40))

// ---------- strategy switches (switching one OFF removes it from the shared budget on this chart) ----------
useNW  = input.bool(true, "NEWS 8:30 reversion to the 8:29 price (CPI/PPI/NFP)", group="Strategies")
useV4  = input.bool(true, "V4+ opening-range retest with the daily trend", group="Strategies")
useD2  = input.bool(true, "D2 10:30 continuation", group="Strategies")
useTD  = input.bool(true, "TDP trend-day pullback", group="Strategies")
usePin = input.bool(true, "Momentum Pinball", group="Strategies")
useH2  = input.bool(true, "H2 trend-day pullbacks (half size)", group="Strategies")
gapTh  = input.float(0.4, "V4+ gap threshold (x ADR)", group="V4+")
dirTh  = input.float(0.4, "V4+ first-15m threshold (x OR range)", group="V4+")
tgtR   = input.float(1.25, "V4+ target (R)", group="V4+")
v4BE   = input.bool(true, "V4+ stop to breakeven at +1R", group="V4+")
d2Th   = input.float(0.5, "D2 move at 10:30 (x ADR)", group="D2")
tdEff  = input.float(0.6, "TDP first-hour efficiency min", group="TDP")
tdK    = input.float(0.33, "TDP pullback depth (x first-hour range)", group="TDP")
tdStop = input.float(0.4, "TDP stop (x ADR)", group="TDP")
tdTgt  = input.float(1.5, "TDP target (R)", group="TDP")
pinCap = input.int(0, "Pinball time cap (min after entry, 0 = hold to 15:55)", group="Pinball")
h2Th   = input.float(0.4, "H2 trend-day threshold at 10:30 (x ADR)", group="H2")
h2Tgt  = input.float(2.0, "H2 target (R)", group="H2")
h2Max  = input.int(3, "H2 max trades per day", group="H2")
nwStop = input.float(50, "NEWS stop (pts)", group="NEWS")
nwTgt  = input.float(50, "NEWS target (pts)", group="NEWS")
evStart= input.float(50000, "Eval starting balance ($)", group="Prop firm (update each morning)")
acct   = input.float(50000, "Balance at last close ($)", group="Prop firm (update each morning)")
peakEOD= input.float(50000, "Highest end-of-day balance so far ($)", group="Prop firm (update each morning)")
bestDay= input.float(0, "Best day profit so far ($)", group="Prop firm (update each morning)")
pfTgt  = input.float(3000, "Profit target ($)", group="Prop firm (update each morning)")
pfDD   = input.float(2000, "Trailing max loss, end of day ($)", group="Prop firm (update each morning)")
pfCons = input.float(0.5, "Consistency: best day max share of profit", group="Prop firm (update each morning)")
mllLine= math.min(peakEOD - pfDD, evStart)
frac   = input.float(0.65, "Risk = fraction of room", group="Sizing")
dayCap = input.float(1100, "Daily budget ($): open risk + today's losses, shared by all strategies", group="Sizing")

// ---------- news calendar (yyyy-mm-dd HHMM NAME, comma separated, no spaces after commas) ----------
calStr = input.text_area("2026-09-04 0830 NFP,2026-09-10 0830 PPI,2026-09-11 0830 CPI,2026-09-16 1400 FOMC,2026-10-02 0830 NFP,2026-10-14 0830 CPI,2026-10-15 0830 PPI,2026-10-28 1400 FOMC,2026-11-03 1000 JOLTS,2026-11-06 0830 NFP,2026-11-10 0830 CPI,2026-11-13 0830 PPI,2026-12-01 1000 JOLTS,2026-12-04 0830 NFP,2026-12-09 1400 FOMC,2026-12-10 0830 CPI,2026-12-15 0830 PPI", "Economic calendar", group="News")
showSpike = input.bool(true, "Mark unexpected spikes", group="News")
spikeK = input.float(4.0, "Spike = 1m range >= K x median of last 30 bars", group="News")
spikeA = input.float(0.06, "... and >= this x ADR", group="News")

tz = "America/New_York"
mnt = hour(time, tz) * 60 + minute(time, tz)
mi  = minute(time, tz)
dom = dayofmonth(time, tz)
tick = syminfo.mintick
inRTH = mnt >= 570 and mnt < 960
newDay = inRTH and (not inRTH[1] or dom != dayofmonth(time[1], tz))

// colours
cNW = color.rgb(255, 193, 7)
cV4 = color.rgb(0, 150, 136)
cD2 = color.rgb(33, 150, 243)
cTD = color.rgb(233, 30, 99)
cPn = color.rgb(255, 120, 0)
cH2 = color.rgb(0, 188, 212)

fmt(x) => str.tostring(x, "#.##")
usd(x) => (x < 0 ? "-$" : "$") + str.tostring(math.abs(math.round(x)), "#,###")
hhmm() => str.format_time(time, "HH:mm", tz)

// ---------- RTH daily context (prior completed day, no repaint) ----------
rthStats() =>
    tz2 = "America/New_York"
    m2 = hour(time, tz2) * 60 + minute(time, tz2)
    inR = m2 >= 570 and m2 < 960
    var float h = na
    var float l = na
    var float c = na
    var float pH = na
    var float pL = na
    var float pC = na
    var rngs = array.new_float()
    var cls = array.new_float()
    if inR
        h := na(h) ? high : math.max(h, high)
        l := na(l) ? low : math.min(l, low)
        c := close
    if m2 == 930 and not na(h)
        pH := h
        pL := l
        pC := c
        array.push(rngs, h - l)
        array.push(cls, c)
        h := na
        l := na
        c := na
    n = array.size(rngs)
    adr = n >= 10 ? array.avg(array.slice(rngs, n - 10, n)) : na
    nc = array.size(cls)
    sma = nc >= 20 ? array.avg(array.slice(cls, nc - 20, nc)) : na
    rsi = 50.0
    if nc >= 4
        c1 = array.get(cls, nc - 1) - array.get(cls, nc - 2)
        c2 = array.get(cls, nc - 2) - array.get(cls, nc - 3)
        c3 = array.get(cls, nc - 3) - array.get(cls, nc - 4)
        up = math.max(c1, 0) + math.max(c2, 0) + math.max(c3, 0)
        dn = math.max(-c1, 0) + math.max(-c2, 0) + math.max(-c3, 0)
        rsi := dn == 0 ? 100.0 : 100.0 - 100.0 / (1.0 + up / dn)
    [pH, pL, pC, adr, sma, rsi]
[pdh0, pdl0, pdc0, adr0, sma0, rsi0] = request.security(syminfo.tickerid, "30", rthStats(), lookahead=barmerge.lookahead_off)
var float pdh = na
var float pdl = na
var float pdc = na
var float adr10 = na
var float sma20 = na
var float rsi3 = na
if not inRTH or newDay
    pdh := pdh0
    pdl := pdl0
    pdc := pdc0
    adr10 := adr0
    sma20 := sma0
    rsi3 := rsi0
trendDir = pdc > sma20 ? 1 : -1

var line lH = na
var line lL = na
var line lC = na
if showPD and barstate.islast and not na(pdh)
    line.delete(lH)
    line.delete(lL)
    line.delete(lC)
    lH := line.new(bar_index - 300, pdh, bar_index + 10, pdh, color=color.new(color.green, 30))
    lL := line.new(bar_index - 300, pdl, bar_index + 10, pdl, color=color.new(color.red, 30))
    lC := line.new(bar_index - 300, pdc, bar_index + 10, pdc, color=color.new(color.orange, 30), style=line.style_dotted)

// ---------- today's calendar ----------
var int[] evM = array.new_int()
var string[] evN = array.new_string()
var string nextEv = "none listed"
var bool news830 = false
var bool cpiOrFomc = false
dChg = barstate.isfirst or dom != dayofmonth(time[1], tz)
if dChg
    dStr = str.format("{0,number,0000}-{1,number,00}-{2,number,00}", year(time, tz), month(time, tz), dom)
    dNum = year(time, tz) * 10000 + month(time, tz) * 100 + dom
    array.clear(evM)
    array.clear(evN)
    news830 := false
    cpiOrFomc := false
    nextEv := "none listed"
    bool found = false
    for p in str.split(calStr, ",")
        if str.length(p) >= 16
            pNum = str.tonumber(str.replace_all(str.substring(p, 0, 10), "-", ""))
            hm = str.tonumber(str.substring(p, 11, 15))
            nm = str.substring(p, 16)
            if str.startswith(p, dStr)
                array.push(evM, int(math.floor(hm / 100) * 60 + (hm - math.floor(hm / 100) * 100)))
                array.push(evN, nm)
                if hm == 830 and (nm == "CPI" or nm == "PPI" or nm == "NFP")
                    news830 := true
                if nm == "CPI" or nm == "FOMC"
                    cpiOrFomc := true
            if not found and pNum > dNum
                nextEv := nm + " " + str.substring(p, 5, 10) + " " + str.substring(p, 11, 13) + ":" + str.substring(p, 13, 15)
                found := true
todayEv() =>
    s = ""
    for k = 0 to array.size(evN) - 1
        if array.size(evN) > 0
            m0 = array.get(evM, k)
            s := s + (s == "" ? "" : ", ") + array.get(evN, k) + " " + str.format("{0,number,00}:{1,number,00}", math.floor(m0 / 60), m0 % 60)
    s
nearEvent(m, w) =>
    bool r = false
    if array.size(evM) > 0
        for k = 0 to array.size(evM) - 1
            if math.abs(m - array.get(evM, k)) <= w
                r := true
    r
// event marker at release time (all charts)
if array.size(evM) > 0
    for k = 0 to array.size(evM) - 1
        if mnt == array.get(evM, k) and mnt != nz(mnt[1], -1)
            line.new(bar_index, low, bar_index, high, extend=extend.both, color=color.new(color.red, 50), style=line.style_dotted)
            label.new(bar_index, high, array.get(evN, k), color=color.new(color.red, 15), textcolor=color.white, style=label.style_label_down, size=size.tiny, tooltip="Scheduled release: " + array.get(evN, k) + " at " + hhmm() + " ET")

// ---------- day state ----------
var float rOpen = na
var float orH = na
var float orL = na
var float ibH = na
var float ibL = na
var int bias = 0
var bool biasSet = false
if newDay
    rOpen := open
    orH := high
    orL := low
    ibH := high
    ibL := low
    bias := 0
    biasSet := false
if inRTH and mnt < 585 and not newDay
    orH := math.max(orH, high)
    orL := math.min(orL, low)
if inRTH and mnt < 630 and not newDay
    ibH := math.max(ibH, high)
    ibL := math.min(ibL, low)
if inRTH and mnt >= 585 and not biasSet and not na(rOpen) and not na(adr10)
    gapA = (rOpen - pdc) / adr10
    odir = (close[1] - rOpen) / math.max(orH - orL, tick)
    bias := math.abs(gapA) >= gapTh ? (gapA > 0 ? 1 : -1) : math.abs(odir) >= dirTh ? (odir > 0 ? 1 : -1) : 0
    biasSet := true
plot(showOR and inRTH and mnt >= 585 ? orH : na, "OR high", color=color.new(color.yellow, 60), style=plot.style_linebr)
plot(showOR and inRTH and mnt >= 585 ? orL : na, "OR low", color=color.new(color.yellow, 60), style=plot.style_linebr)

// ---------- shared daily budget (resets at 8:00 ET, or at the first bar after it) ----------
var float rkNW = 0.0
var float rkV4 = 0.0
var float rkD2 = 0.0
var float rkTD = 0.0
var float rkPn = 0.0
var float rkH2 = 0.0
var float dayLoss = 0.0
var float dayPnl = 0.0
var int budDay = -1
if mnt >= 480 and mnt < 960 and budDay != dom
    budDay := dom
    rkNW := 0.0
    rkV4 := 0.0
    rkD2 := 0.0
    rkTD := 0.0
    rkPn := 0.0
    rkH2 := 0.0
    dayLoss := 0.0
    dayPnl := 0.0
perC(riskPts) => riskPts * 2 + 0.5 + 4.74
usedNow() => rkNW + rkV4 + rkD2 + rkTD + rkPn + rkH2 + dayLoss
sizeFor(riskPts, w) =>
    room = acct - mllLine
    used = usedNow()
    pc = perC(riskPts)
    budget = math.min(w * frac * room, frac * room - used, dayCap - used)
    q = budget > 0 ? math.floor(budget / pc) : 0
    if q < 1 and w >= 1 and pc < 0.9 * (room - used) and pc < dayCap - used
        q := 1
    math.max(0, q)
lossOf(q, pts) => pts < 0 ? q * (-pts * 2 + 4.74) : 0.0
pnlOf(q, pts) => q * (pts * 2 - 4.74)

// ---------- drawing helpers ----------
// entry: small tag "V4+ ▲ 4" (strategy, direction, contracts); hover for the full story. Zones: green to target, red to stop.
entryTag(show, nm, side, e, s, t, q, exitRule, why, col) =>
    if show
        rp = math.abs(e - s)
        tgtLine = na(t) ? "Target: none, time exit" : "Target: " + fmt(t) + "  (" + fmt(math.abs(t - e)) + " pts · +" + usd(q * (math.abs(t - e) * 2 - 4.74)) + ")"
        head = nm + (side > 0 ? " LONG" : " SHORT") + " · " + str.tostring(q) + " MNQ" + (q > 0 ? "" : " · SKIP, budget full")
        tip = head + "\n――――――――――――\nEntry: " + fmt(e) + "  at " + hhmm() + "\nStop: " + fmt(s) + "  (" + fmt(rp) + " pts · risk " + usd(q * perC(rp)) + ")\n" + tgtLine + "\nBracket: SL " + str.tostring(math.round(rp / tick)) + " ticks · " + (na(t) ? "no TP (time exit)" : "TP " + str.tostring(math.round(math.abs(t - e) / tick)) + " ticks") + "\nExit: " + exitRule + "\nBudget left today: " + usd(math.max(0, dayCap - usedNow())) + "\n――――――――――――\nWhy\n• " + str.replace_all(why, " | ", "\n• ")
        label.new(bar_index, side > 0 ? low : high, nm + (side > 0 ? " ▲ " : " ▼ ") + str.tostring(q), color=q > 0 ? col : color.new(col, 60), textcolor=color.white, style=side > 0 ? label.style_label_up : label.style_label_down, size=size.small, tooltip=tip)
    true
// while a trade is open: thin dotted stop (red) and target (green) lines; at the exit they are replaced by one line entry -> exit
zone(show, e, lvl, good) => show and not na(lvl) ? line.new(bar_index, lvl, bar_index + 1, lvl, color=color.new(good ? color.lime : color.red, 30), style=line.style_dotted, width=1) : line(na)
grow(b) =>
    if not na(b)
        line.set_x2(b, bar_index)
    true
exitTag(show, nm, side, x, pts, q, why, e, bS, bT) =>
    if show
        x1 = na(bS) ? bar_index : line.get_x1(bS)
        line.delete(bS)
        line.delete(bT)
        if q > 0
            line.new(x1, e, bar_index, x, color=color.new(pts >= 0 ? color.lime : color.red, 10), style=line.style_dashed, width=1)
            label.new(bar_index, x, (pts >= 0 ? "✓ " : "✗ ") + fmt(pts), color=color.new(pts >= 0 ? color.teal : color.maroon, 20), textcolor=color.white, style=side > 0 ? label.style_label_down : label.style_label_up, size=size.tiny, tooltip=nm + " EXIT · " + why + "\n――――――――――――\nResult: " + (pts >= 0 ? "+" : "") + fmt(pts) + " pts × " + str.tostring(q) + " MNQ = " + usd(pnlOf(q, pts)) + "\nExit: " + fmt(x) + "  at " + hhmm())
    true

// trade log (last 8 closed, all strategies)
var string[] lgD = array.new_string()
var string[] lgS = array.new_string()
var string[] lgX = array.new_string()
var float[] lgP = array.new_float()
logTrade(nm, side, eT, why, pts) =>
    array.push(lgD, str.format_time(time, "MMM dd", tz))
    array.push(lgS, nm + (side > 0 ? " LONG " : " SHORT ") + eT)
    array.push(lgX, why + " " + hhmm())
    array.push(lgP, pts)
    if array.size(lgP) > 8
        array.shift(lgD)
        array.shift(lgS)
        array.shift(lgX)
        array.shift(lgP)
    true

// results counters
var float[] sPts = array.new_float(6, 0.0)
var int[] sN = array.new_int(6, 0)
var int[] sW = array.new_int(6, 0)
addRes(k, pts) =>
    array.set(sPts, k, array.get(sPts, k) + pts)
    array.set(sN, k, array.get(sN, k) + 1)
    array.set(sW, k, array.get(sW, k) + (pts > 0 ? 1 : 0))
    true

// ===================== NEWS: 8:30 reversion to the 8:29 price (CPI / PPI / NFP), 5m signals built from 1m =====================
// Fair price = close of the 8:29 candle. Signal on a 5m close from 8:30 to 9:29: candle toward the 8:29 price that is a displacement
// (bigger body than the previous candle, closes beyond its wick, previous candle opposite colour) or a break of structure
// (close beyond the latest 5m swing). Needs >= 0.8 x target of room. Entry next bar open. Stop/target 50/50. Max 4, stop after 3 losses. Flat 10:30.
var float nwF = na
var float[] nO = array.new_float()
var float[] nH = array.new_float()
var float[] nL = array.new_float()
var float[] nC = array.new_float()
var float nbO = na
var float nbH = na
var float nbL = na
var int nwPos = 0
var int nwPend = 0
var int nwN_ = 0
var int nwLossRow = 0
var float nwE = na
var float nwS = na
var float nwT = na
var int nwQ = 0
var string nwET = ""
var line nwBT = na
var line nwBS = na
if dChg
    nwF := na
    array.clear(nO)
    array.clear(nH)
    array.clear(nL)
    array.clear(nC)
    nbO := na
    nwPos := 0
    nwPend := 0
    nwN_ := 0
    nwLossRow := 0
if useNW and news830 and mnt >= 360 and mnt < 640
    if mnt == 509
        nwF := close
        if g1
            line.new(bar_index, nwF, bar_index + 120, nwF, color=color.new(cNW, 20), style=line.style_dotted, width=2)
            label.new(bar_index, nwF, "8:29 price", color=color.new(cNW, 30), textcolor=color.black, style=label.style_label_right, size=size.tiny, tooltip="JJ Simon: on CPI/PPI/NFP days the price just before 8:30 is the fair price. After the spike, look for a 5m displacement or break of structure back toward it.")
    // manage
    if nwPos != 0
        grow(nwBT)
        grow(nwBS)
        hS = nwPos > 0 ? low <= nwS : high >= nwS
        hT = nwPos > 0 ? high >= nwT : low <= nwT
        x = hS ? nwS : hT ? nwT : mnt >= 630 ? close : na
        if not na(x)
            pts = (x - nwE) * nwPos
            addRes(0, pts)
            rkNW := 0.0
            dayLoss += lossOf(nwQ, pts)
            dayPnl += pnlOf(nwQ, pts)
            nwLossRow := pts < 0 ? nwLossRow + 1 : 0
            logTrade("NEWS", nwPos, nwET, hS ? "stop" : hT ? "target" : "10:30", pts)
            exitTag(g1, "NEWS", nwPos, x, pts, nwQ, hS ? "stop" : hT ? "target" : "10:30 time exit", nwE, nwBS, nwBT)
            if g1
                alert("NEWS exit " + fmt(pts) + " pts", alert.freq_once_per_bar)
            nwPos := 0
    // fill a pending signal at this bar's open
    if nwPend != 0 and nwPos == 0
        e = open + nwPend * tick
        dist = (nwF - e) * nwPend
        if dist >= 0.8 * nwTgt
            nwE := e
            nwS := e - nwPend * nwStop
            nwT := e + nwPend * nwTgt
            nwPos := nwPend
            nwN_ += 1
            q = sizeFor(nwStop, 1.0)
            nwQ := q
            nwET := hhmm()
            rkNW := q * perC(nwStop)
            entryTag(g1, "NEWS", nwPend, nwE, nwS, nwT, q, "target, stop or 10:30", "CPI/PPI/NFP day: price spiked away from the 8:29 price (" + fmt(nwF) + ") | 5m candle back toward it (displacement or break of structure) | " + fmt(dist) + " pts of room to the 8:29 price", cNW)
            nwBT := zone(g1, nwE, nwT, true)
            nwBS := zone(g1, nwE, nwS, false)
            if g1
                alert("NEWS " + (nwPend > 0 ? "LONG " : "SHORT ") + fmt(nwE) + " stop " + fmt(nwS) + " target " + fmt(nwT) + " size " + str.tostring(q) + " MNQ", alert.freq_once_per_bar)
        nwPend := 0
    // build 5m bars
    if na(nbO)
        nbO := open
        nbH := high
        nbL := low
    else
        nbH := math.max(nbH, high)
        nbL := math.min(nbL, low)
    if (mi + 1) % 5 == 0
        array.push(nO, nbO)
        array.push(nH, nbH)
        array.push(nL, nbL)
        array.push(nC, close)
        nbO := na
        k = array.size(nC) - 1
        st5 = mnt - 4
        if k >= 3 and st5 >= 510 and st5 < 570 and not na(nwF) and nwPos == 0 and nwN_ < 4 and nwLossRow < 3
            c = array.get(nC, k)
            o = array.get(nO, k)
            pc = array.get(nC, k - 1)
            po = array.get(nO, k - 1)
            ph = array.get(nH, k - 1)
            pl = array.get(nL, k - 1)
            s = c < nwF ? 1 : c > nwF ? -1 : 0
            col = c > o ? 1 : c < o ? -1 : 0
            if s != 0 and col == s
                disp = math.abs(c - o) > math.abs(pc - po) and (s > 0 ? c > ph : c < pl) and (pc - po) * s < 0
                float sw = na
                for j = k - 2 to math.max(1, k - 29)
                    if j + 1 <= k and j - 1 >= 0 and na(sw)
                        if s < 0 and array.get(nL, j) < array.get(nL, j - 1) and array.get(nL, j) < array.get(nL, j + 1)
                            sw := array.get(nL, j)
                        if s > 0 and array.get(nH, j) > array.get(nH, j - 1) and array.get(nH, j) > array.get(nH, j + 1)
                            sw := array.get(nH, j)
                bos = not na(sw) and (s < 0 ? (c < sw and pc >= sw) : (c > sw and pc <= sw))
                if disp or bos
                    nwPend := s

// ===================== V4+: opening-range retest with the daily trend =====================
var int dr = 0
var bool saw = false
var bool v4Done = false
var float pLvl = na
var float pStp = na
var int pSide = 0
var int pBar = na
var int v4Pos = 0
var float v4E = na
var float v4S = na
var float v4T = na
var float v4R = na
var int v4Q = 0
var bool v4AtBE = false
var string v4ET = ""
var line v4BT = na
var line v4BS = na
if newDay
    dr := 0
    saw := false
    v4Done := false
    pSide := 0
    v4Pos := 0
if useV4 and inRTH
    if v4Pos != 0
        grow(v4BT)
        grow(v4BS)
        hitS = v4Pos > 0 ? low <= v4S : high >= v4S
        hitT = v4Pos > 0 ? high >= v4T : low <= v4T
        xP = hitS ? v4S : hitT ? v4T : mnt >= 955 ? close : na
        if na(xP) and v4BE and not v4AtBE and (v4Pos > 0 ? high >= v4E + v4R : low <= v4E - v4R)
            v4S := v4E + v4Pos * 1.25
            v4AtBE := true
            rkV4 := 0.0
            if g1
                label.new(bar_index, v4S, "BE", color=color.new(color.gray, 30), textcolor=color.white, style=label.style_label_left, size=size.tiny, tooltip="V4+ reached +1R: stop moved to breakeven " + fmt(v4S) + ". Its risk is freed from the daily budget.")
                alert("V4+ +1R: move stop to breakeven " + fmt(v4S), alert.freq_once_per_bar)
        if not na(xP)
            pts = (xP - v4E) * v4Pos
            why = hitS ? (v4AtBE ? "breakeven" : "stop") : hitT ? "target" : "15:55"
            addRes(1, pts)
            rkV4 := 0.0
            dayLoss += lossOf(v4Q, pts)
            dayPnl += pnlOf(v4Q, pts)
            logTrade("V4+", v4Pos, v4ET, why, pts)
            exitTag(g1, "V4+", v4Pos, xP, pts, v4Q, why, v4E, v4BS, v4BT)
            if g1
                alert("V4+ exit " + why + " " + fmt(pts) + " pts", alert.freq_once_per_bar)
            v4Pos := 0
    if pSide != 0 and bar_index == pBar + 1 and v4Pos == 0 and not v4Done
        if mnt <= 780 and (pSide > 0 ? high >= pLvl : low <= pLvl)
            v4E := pSide > 0 ? math.max(open, pLvl) : math.min(open, pLvl)
            v4S := pStp
            r = math.abs(v4E - v4S)
            v4T := v4E + pSide * tgtR * r
            v4Pos := pSide
            v4Done := true
            v4R := r
            v4AtBE := false
            q = sizeFor(r, 1.0)
            v4Q := q
            v4ET := hhmm()
            rkV4 := q * perC(r)
            entryTag(g1, "V4+", pSide, v4E, v4S, v4T, q, "1.25R target · stop to breakeven at +1R · else 15:55", "Daily trend and today's bias agree (" + (pSide > 0 ? "UP" : "DOWN") + ") | Price broke the 9:30-9:45 range, then retested it | Strong candle: stop order just beyond it | Stop on the other side of the range", cV4)
            v4BT := zone(g1, v4E, v4T, true)
            v4BS := zone(g1, v4E, v4S, false)
            if g1
                alert("V4+ " + (pSide > 0 ? "LONG " : "SHORT ") + fmt(v4E) + " stop " + fmt(v4S) + " target " + fmt(v4T) + " size " + str.tostring(q) + " MNQ", alert.freq_once_per_bar)
            if pSide > 0 ? low <= v4S : high >= v4S
                pts = (v4S - v4E) * pSide
                addRes(1, pts)
                v4Pos := 0
                rkV4 := 0.0
                dayLoss += lossOf(v4Q, pts)
                dayPnl += pnlOf(v4Q, pts)
                logTrade("V4+", pSide, v4ET, "stop", pts)
                exitTag(g1, "V4+", pSide, v4S, pts, v4Q, "stop (same bar)", v4E, v4BS, v4BT)
        pSide := 0
    if not v4Done and v4Pos == 0 and biasSet and bias != 0 and bias == trendDir and mnt >= 585 and mnt <= 780
        closes5 = (mi + 1) % 5 == 0
        if closes5 and close > orH
            if dr != 1
                dr := 1
                saw := false
        else if closes5 and close < orL
            if dr != -1
                dr := -1
                saw := false
        inside = close <= orH and close >= orL
        if inside and dr != 0
            dr := 0
            saw := false
        if dr != 0
            touch = dr > 0 ? low <= orH : high >= orL
            if touch
                saw := true
            rg = high - low
            bull = close > open and rg > 0 and (close - low) >= 0.5 * rg and math.abs(close - open) >= 0.3 * rg
            bear = close < open and rg > 0 and (high - close) >= 0.5 * rg and math.abs(close - open) >= 0.3 * rg
            if saw and not inside and (dr > 0 ? bull : bear) and dr == bias
                pLvl := dr > 0 ? high + tick : low - tick
                stp0 = dr > 0 ? orL - tick : orH + tick
                if math.abs(pLvl - stp0) < 4
                    stp0 := pLvl - dr * 4
                pStp := stp0
                pSide := dr
                pBar := bar_index

// ===================== D2: 10:30 continuation =====================
var int d2Pos = 0
var float d2E = na
var float d2S = na
var float d2W8 = 1.0
var bool d2Done = false
var int d2Q = 0
var line d2BS = na
if newDay
    d2Pos := 0
    d2Done := false
if useD2 and inRTH
    if d2Pos != 0
        grow(d2BS)
        hit = d2Pos > 0 ? low <= d2S : high >= d2S
        xP = hit ? d2S : mnt >= 900 ? close : na
        if not na(xP)
            pts = (xP - d2E) * d2Pos
            addRes(2, pts)
            rkD2 := 0.0
            dayLoss += lossOf(d2Q, pts)
            dayPnl += pnlOf(d2Q, pts)
            logTrade("D2", d2Pos, "10:30", hit ? "stop" : "15:00", pts)
            exitTag(g1, "D2", d2Pos, xP, pts, d2Q, hit ? "stop" : "15:00 time exit", d2E, d2BS, line(na))
            if g1
                alert("D2 exit " + fmt(pts) + " pts", alert.freq_once_per_bar)
            d2Pos := 0
            d2Done := true
    if mnt == 629 and d2Pos == 0 and not d2Done and not na(adr10) and not cpiOrFomc
        mv = (close - rOpen) / adr10
        if math.abs(mv) >= d2Th
            s = mv > 0 ? 1 : -1
            d2E := close
            d2S := rOpen - s * tick
            d2Pos := s
            d2W8 := s == trendDir ? 1.0 : 0.5
            r = math.abs(d2E - d2S)
            q = sizeFor(r, d2W8)
            d2Q := q
            rkD2 := q * perC(r)
            entryTag(g1, "D2", s, d2E, d2S, float(na), q, "15:00, or stop", "At 10:30 price is " + fmt(math.abs(mv)) + " ADR " + (s > 0 ? "above" : "below") + " the open: continuation | Stop at the opening price" + (d2W8 < 1 ? " | HALF size: against the daily trend" : ""), cD2)
            d2BS := zone(g1, d2E, d2S, false)
            if g1
                alert("D2 " + (s > 0 ? "LONG " : "SHORT ") + fmt(d2E) + " stop " + fmt(d2S) + " exit 15:00 size " + str.tostring(q) + " MNQ", alert.freq_once_per_bar)

// ===================== TDP: trend-day pullback =====================
var int tdS = 0
var float tdExt = na
var float tdFhr = na
var int tdPos = 0
var bool tdDone = false
var float tdE = na
var float tdSt = na
var float tdT = na
var int tdQ = 0
var string tdET = ""
var line tdLn = na
var line tdBT = na
var line tdBS = na
if newDay
    tdS := 0
    tdPos := 0
    tdDone := false
if useTD and inRTH
    if tdPos != 0
        grow(tdBT)
        grow(tdBS)
        hS3 = tdPos > 0 ? low <= tdSt : high >= tdSt
        hT3 = tdPos > 0 ? high >= tdT : low <= tdT
        x3 = hS3 ? tdSt : hT3 ? tdT : mnt >= 955 ? close : na
        if not na(x3)
            p3 = (x3 - tdE) * tdPos
            addRes(3, p3)
            rkTD := 0.0
            dayLoss += lossOf(tdQ, p3)
            dayPnl += pnlOf(tdQ, p3)
            logTrade("TDP", tdPos, tdET, hS3 ? "stop" : hT3 ? "target" : "15:55", p3)
            exitTag(g2, "TDP", tdPos, x3, p3, tdQ, hS3 ? "stop" : hT3 ? "target" : "15:55", tdE, tdBS, tdBT)
            if g2
                alert("TDP exit " + fmt(p3) + " pts", alert.freq_once_per_bar)
            tdPos := 0
    if mnt == 629 and not na(adr10) and not na(rOpen)
        fhr = ibH - ibL
        eff = fhr > 0 ? math.abs(close - rOpen) / fhr : 0.0
        sd = close > rOpen ? 1 : -1
        outside = sd > 0 ? close > pdh : close < pdl
        if eff >= tdEff and outside
            tdS := sd
            tdFhr := fhr
            tdExt := sd > 0 ? ibH : ibL
            if g2
                label.new(bar_index, sd > 0 ? high : low, "TDP armed", color=color.new(cTD, 50), textcolor=color.white, style=sd > 0 ? label.style_label_down : label.style_label_up, size=size.tiny, tooltip="Trend day " + (sd > 0 ? "UP" : "DOWN") + ": first hour moved " + str.tostring(math.round(eff * 100)) + "% efficiently and price is outside the prior-day range. Limit order waits on the dashed line until 12:00.")
                alert("TDP armed: " + (sd > 0 ? "buy" : "sell") + " limit " + fmt(tdExt - sd * tdK * fhr) + " until 12:00", alert.freq_once_per_bar)
    if tdS != 0 and tdPos == 0 and not tdDone and mnt >= 630 and mnt < 720
        lvl3 = tdExt - tdS * tdK * tdFhr
        if tdS > 0 ? low <= lvl3 - tick : high >= lvl3 + tick
            line.delete(tdLn)
            tdE := tdS > 0 ? math.min(open, lvl3) : math.max(open, lvl3)
            tdSt := tdE - tdS * math.max(10.0, tdStop * adr10)
            r3 = math.abs(tdE - tdSt)
            tdT := tdE + tdS * tdTgt * r3
            tdPos := tdS
            tdDone := true
            q3 = sizeFor(r3, 1.0)
            tdQ := q3
            tdET := hhmm()
            rkTD := q3 * perC(r3)
            entryTag(g2, "TDP", tdS, tdE, tdSt, tdT, q3, "1.5R target, else 15:55", "Trend day " + (tdS > 0 ? "UP" : "DOWN") + ": first hour clean and outside the prior-day range | Pullback of 1/3 of the first-hour range from the day's " + (tdS > 0 ? "high" : "low") + " | Stop 0.4 x ADR", cTD)
            tdBT := zone(g2, tdE, tdT, true)
            tdBS := zone(g2, tdE, tdSt, false)
            if g2
                alert("TDP " + (tdS > 0 ? "LONG " : "SHORT ") + fmt(tdE) + " stop " + fmt(tdSt) + " target " + fmt(tdT) + " size " + str.tostring(q3) + " MNQ", alert.freq_once_per_bar)
            if tdS > 0 ? low <= tdSt : high >= tdSt
                p3 = (tdSt - tdE) * tdS
                addRes(3, p3)
                tdPos := 0
                rkTD := 0.0
                dayLoss += lossOf(tdQ, p3)
                dayPnl += pnlOf(tdQ, p3)
                logTrade("TDP", tdS, tdET, "stop", p3)
                exitTag(g2, "TDP", tdS, tdSt, p3, tdQ, "stop (same bar)", tdE, tdBS, tdBT)
        else
            tdExt := tdS > 0 ? math.max(tdExt, high) : math.min(tdExt, low)
            line.delete(tdLn)
            if g2
                tdLn := line.new(bar_index - 1, tdExt - tdS * tdK * tdFhr, bar_index + 3, tdExt - tdS * tdK * tdFhr, color=cTD, style=line.style_dashed)
    if tdS != 0 and mnt == 720 and not tdDone
        line.delete(tdLn)

// ===================== Momentum Pinball =====================
var int pnPos = 0
var float pnE = na
var float pnS = na
var bool pnDone = false
var int pnQ = 0
var int pnT0 = 0
var string pnET = ""
var line pnBS = na
if newDay
    pnPos := 0
    pnDone := false
pinSide = rsi3 < 30 and trendDir > 0 ? 1 : rsi3 > 70 and trendDir < 0 ? -1 : 0
if usePin and inRTH
    if pnPos != 0
        grow(pnBS)
        hit = pnPos > 0 ? low <= pnS : high >= pnS
        capHit = pinCap > 0 and mnt >= pnT0 + pinCap
        xP = hit ? pnS : (mnt >= 955 or capHit) ? close : na
        if not na(xP)
            pts = (xP - pnE) * pnPos
            addRes(4, pts)
            rkPn := 0.0
            dayLoss += lossOf(pnQ, pts)
            dayPnl += pnlOf(pnQ, pts)
            logTrade("PIN", pnPos, pnET, hit ? "stop" : capHit ? "time cap" : "15:55", pts)
            exitTag(g2, "PIN", pnPos, xP, pts, pnQ, hit ? "stop" : capHit ? "time cap" : "15:55", pnE, pnBS, line(na))
            if g2
                alert("PINBALL exit " + fmt(pts) + " pts", alert.freq_once_per_bar)
            pnPos := 0
    if not pnDone and pnPos == 0 and pinSide != 0 and mnt >= 630 and mnt <= 900
        lvl = pinSide > 0 ? ibH + tick : ibL - tick
        if pinSide > 0 ? high >= lvl : low <= lvl
            pnE := pinSide > 0 ? math.max(open, lvl) : math.min(open, lvl)
            pnS := pinSide > 0 ? ibL - tick : ibH + tick
            pnPos := pinSide
            pnDone := true
            pnT0 := mnt
            r = math.abs(pnE - pnS)
            q = sizeFor(r, 1.0)
            pnQ := q
            pnET := hhmm()
            rkPn := q * perC(r)
            entryTag(g2, "PIN", pinSide, pnE, pnS, float(na), q, "15:55, or stop", "3-day RSI " + fmt(rsi3) + (pinSide > 0 ? " (oversold)" : " (overbought)") + " with the daily trend " + (trendDir > 0 ? "UP" : "DOWN") + " | Price broke the first-hour " + (pinSide > 0 ? "high" : "low") + " | Stop on the other side of the first hour", cPn)
            pnBS := zone(g2, pnE, pnS, false)
            if g2
                alert("PINBALL " + (pinSide > 0 ? "LONG " : "SHORT ") + fmt(pnE) + " stop " + fmt(pnS) + " size " + str.tostring(q) + " MNQ", alert.freq_once_per_bar)
            if pinSide > 0 ? low <= pnS : high >= pnS
                pts = (pnS - pnE) * pinSide
                addRes(4, pts)
                pnPos := 0
                rkPn := 0.0
                dayLoss += lossOf(pnQ, pts)
                dayPnl += pnlOf(pnQ, pts)
                logTrade("PIN", pinSide, pnET, "stop", pts)
                exitTag(g2, "PIN", pinSide, pnS, pts, pnQ, "stop (same bar)", pnE, pnBS, line(na))

// ===================== H2: second-entry pullbacks on trend days (half size) =====================
var float[] bH = array.new_float()
var float[] bL = array.new_float()
var float[] bC = array.new_float()
var float[] bE = array.new_float()
var float bO_ = na
var float bH_ = na
var float bL_ = na
var float twSum = 0.0
var int twN = 0
var float e5 = na
var int tdDir = 0
var int h2Pos = 0
var int h2N_ = 0
var bool h2Pend = false
var int h2PSide = 0
var float h2PStp = na
var float h2E = na
var float h2S = na
var float h2T = na
var int h2Q = 0
var string h2ET = ""
var line h2BT = na
var line h2BS = na
if newDay
    array.clear(bH)
    array.clear(bL)
    array.clear(bC)
    array.clear(bE)
    bO_ := na
    twSum := 0.0
    twN := 0
    e5 := na
    tdDir := 0
    h2Pos := 0
    h2N_ := 0
    h2Pend := false
if useH2 and inRTH
    if mnt == 629 and not na(adr10) and not na(rOpen)
        mv2 = (close - rOpen) / adr10
        tdDir := math.abs(mv2) >= h2Th ? (mv2 > 0 ? 1 : -1) : 0
    if h2Pend and h2Pos == 0
        h2E := open
        h2S := h2PStp
        r2 = math.abs(h2E - h2S)
        if (h2PSide > 0 and h2S < h2E) or (h2PSide < 0 and h2S > h2E)
            h2T := h2E + h2PSide * h2Tgt * r2
            h2Pos := h2PSide
            h2N_ += 1
            q2 = sizeFor(r2, 0.5)
            h2Q := q2
            h2ET := hhmm()
            rkH2 := q2 * perC(r2)
            entryTag(g2, "H2", h2PSide, h2E, h2S, h2T, q2, "2R target, else 15:55", "Trend day: moved >= " + fmt(h2Th) + " ADR by 10:30 | 5m pullback after a new " + (h2PSide > 0 ? "high" : "low") + " | 5m close back through the prior bar (second entry) | HALF size", cH2)
            h2BT := zone(g2, h2E, h2T, true)
            h2BS := zone(g2, h2E, h2S, false)
            if g2
                alert("H2 " + (h2PSide > 0 ? "LONG " : "SHORT ") + fmt(h2E) + " stop " + fmt(h2S) + " target " + fmt(h2T) + " size " + str.tostring(q2) + " MNQ", alert.freq_once_per_bar)
        h2Pend := false
    if h2Pos != 0
        grow(h2BT)
        grow(h2BS)
        hS2 = h2Pos > 0 ? low <= h2S : high >= h2S
        hT2 = h2Pos > 0 ? high >= h2T : low <= h2T
        x2 = hS2 ? h2S : hT2 ? h2T : mnt >= 955 ? close : na
        if not na(x2)
            p2 = (x2 - h2E) * h2Pos
            addRes(5, p2)
            rkH2 := 0.0
            dayLoss += lossOf(h2Q, p2)
            dayPnl += pnlOf(h2Q, p2)
            logTrade("H2", h2Pos, h2ET, hS2 ? "stop" : hT2 ? "target" : "15:55", p2)
            exitTag(g2, "H2", h2Pos, x2, p2, h2Q, hS2 ? "stop" : hT2 ? "target" : "15:55", h2E, h2BS, h2BT)
            if g2
                alert("H2 exit " + fmt(p2) + " pts", alert.freq_once_per_bar)
            h2Pos := 0
    if na(bO_)
        bO_ := open
        bH_ := high
        bL_ := low
    else
        bH_ := math.max(bH_, high)
        bL_ := math.min(bL_, low)
    if (mi + 1) % 5 == 0
        c5 = close
        o5 = bO_
        array.push(bH, bH_)
        array.push(bL, bL_)
        array.push(bC, c5)
        twSum += (bH_ + bL_ + c5) / 3
        twN += 1
        e5 := na(e5) ? c5 : e5 + 2.0 / 21.0 * (c5 - e5)
        array.push(bE, e5)
        bO_ := na
        k = array.size(bC) - 1
        mclose = mnt + 1
        if k >= 8 and mclose >= 630 and mclose <= 900 and tdDir != 0 and tdDir == trendDir and h2Pos == 0 and not h2Pend and h2N_ < h2Max
            tw = twSum / twN
            upT = c5 > tw and e5 > array.get(bE, k - 3)
            dnT = c5 < tw and e5 < array.get(bE, k - 3)
            hh = array.max(array.slice(bH, 0, k - 2))
            ll = array.min(array.slice(bL, 0, k - 2))
            rh = array.max(array.slice(bH, k - 8, k - 2))
            rl = array.min(array.slice(bL, k - 8, k - 2))
            c1 = array.get(bC, k - 1)
            c2 = array.get(bC, k - 2)
            h1 = array.get(bH, k - 1)
            l1 = array.get(bL, k - 1)
            sg = 0
            float st2 = na
            if tdDir > 0 and upT and rh >= hh and c1 < c2 and c5 > h1 and c5 > o5
                sg := 1
                st2 := array.min(array.slice(bL, k - 3, k + 1)) - tick
            else if tdDir < 0 and dnT and rl <= ll and c1 > c2 and c5 < l1 and c5 < o5
                sg := -1
                st2 := array.max(array.slice(bH, k - 3, k + 1)) + tick
            if sg != 0
                rr = math.abs(c5 - st2)
                if rr >= 6 and rr <= 0.25 * adr10
                    h2Pend := true
                    h2PSide := sg
                    h2PStp := st2

// ---------- unexpected spike marker (no trade; our trend trades did better when spikes happened: hold to plan) ----------
var string lastSpike = "none today"
if dChg
    lastSpike := "none today"
rg1 = high - low
med30 = ta.median(rg1, 30)[1]
isSpike = inRTH and mnt >= 575 and not na(adr10) and rg1 >= spikeK * med30 and rg1 >= spikeA * adr10 and math.abs(close - open) >= 0.5 * rg1 and not nearEvent(mnt, 5)
if showSpike and isSpike
    lastSpike := hhmm() + (close > open ? " up " : " down ") + fmt(rg1) + " pts"
    label.new(bar_index, close > open ? high : low, "⚡", color=color.new(color.black, 100), textcolor=color.yellow, style=close > open ? label.style_label_down : label.style_label_up, size=size.small, tooltip="Unexpected spike (no scheduled release): " + fmt(rg1) + " pts in 1 minute. Not a trade signal. Tested 2022-2026: our trades held through spikes did better (PF 2.2 vs 1.4), so stick to the plan, no early exits.")

// ---------- panel ----------
openList() =>
    s = ""
    s := s + (nwPos != 0 ? "NEWS " + str.tostring(nwQ) + " " : "")
    s := s + (v4Pos != 0 ? "V4+ " + str.tostring(v4Q) + (v4AtBE ? " (BE) " : " ") : "")
    s := s + (d2Pos != 0 ? "D2 " + str.tostring(d2Q) + " " : "")
    s := s + (tdPos != 0 ? "TDP " + str.tostring(tdQ) + " " : "")
    s := s + (pnPos != 0 ? "PIN " + str.tostring(pnQ) + " " : "")
    s := s + (h2Pos != 0 ? "H2 " + str.tostring(h2Q) + " " : "")
    s == "" ? "flat" : s + "MNQ"
var table pn = table.new(position.top_right, 2, 10, bgcolor=color.new(#131722, 10), border_color=color.new(color.gray, 80), border_width=1, frame_color=color.new(color.gray, 60), frame_width=1)
if showPanel and barstate.islast
    tc = color.new(color.white, 10)
    dim = color.new(color.gray, 0)
    table.cell(pn, 0, 0, "PLAYBOOK", text_color=color.yellow, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 0, grp == G_ALL ? "all strategies" : grp == G_1 ? "Chart 1: NEWS · V4+ · D2" : "Chart 2: TDP · H2 · PIN", text_color=color.yellow, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 0, 1, "Context", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 1, "trend " + (trendDir > 0 ? "UP" : "DOWN") + " · bias " + (not biasSet ? "9:45" : bias == 0 ? "none" : bias > 0 ? "LONG" : "SHORT") + " · ADR " + str.tostring(math.round(nz(adr10))), text_color=tc, text_size=size.small, text_halign=text.align_left)
    left = dayCap - usedNow()
    table.cell(pn, 0, 2, "Budget", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 2, usd(usedNow()) + " in use · " + usd(math.max(0, left)) + " left of " + usd(dayCap), text_color=left < 200 ? color.orange : tc, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 0, 3, "Open (all charts)", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 3, openList(), text_color=tc, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 0, 4, "Today P&L", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 4, usd(dayPnl), text_color=dayPnl >= 0 ? color.lime : color.red, text_size=size.small, text_halign=text.align_left)
    setups = grp != G_2 ? ((news830 ? "NEWS day · " : "") + (v4Done ? "V4+ done" : bias != 0 and bias == trendDir ? "V4+ watching retest" : "V4+ off today") + " · D2 at 10:30") : ((tdS != 0 and not tdDone and mnt < 720 ? "TDP armed " + (tdS > 0 ? "LONG" : "SHORT") : "TDP " + (tdDone ? "done" : "not armed")) + " · PIN " + (pinSide > 0 ? "LONG setup" : pinSide < 0 ? "SHORT setup" : "none") + " · H2 " + (tdDir != 0 ? "trend day" : "off"))
    table.cell(pn, 0, 5, "Setups", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 5, setups, text_color=tc, text_size=size.small, text_halign=text.align_left)
    tev = todayEv()
    table.cell(pn, 0, 6, "News", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 6, (tev == "" ? "none today" : "today " + tev) + " · next " + nextEv, text_color=tev == "" ? tc : color.orange, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 0, 7, "Spike", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 7, lastSpike, text_color=tc, text_size=size.small, text_halign=text.align_left)
    prof = acct - evStart + dayPnl
    best = math.max(bestDay, dayPnl)
    need = math.max(pfTgt, best / pfCons)
    table.cell(pn, 0, 8, "Eval", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 8, usd(prof) + " of " + usd(need) + " needed" + (need > pfTgt ? " (best day " + usd(best) + ", 50% rule)" : "") + (prof >= need ? " · TARGET MET" : " · " + usd(need - prof) + " to go"), text_color=prof >= need ? color.lime : tc, text_size=size.small, text_halign=text.align_left)
    room = acct + dayPnl - mllLine
    table.cell(pn, 0, 9, "Max-loss line", text_color=dim, text_size=size.small, text_halign=text.align_left)
    table.cell(pn, 1, 9, usd(mllLine) + " · room " + usd(room) + " · sizing uses 65% of " + usd(acct - mllLine), text_color=room < 800 ? color.red : tc, text_size=size.small, text_halign=text.align_left)

// ---------- results table (optional) ----------
var table tb = table.new(position.bottom_right, 3, 7, bgcolor=color.new(#131722, 10), border_color=color.new(color.gray, 80), border_width=1)
if showStats and barstate.islast
    names = array.from("NEWS", "V4+", "D2", "TDP", "Pinball", "H2")
    table.cell(tb, 0, 0, "Loaded bars", text_color=color.yellow, text_size=size.small)
    table.cell(tb, 1, 0, "trades / wins", text_color=color.yellow, text_size=size.small)
    table.cell(tb, 2, 0, "pts (1 MNQ $)", text_color=color.yellow, text_size=size.small)
    for k = 0 to 5
        pv = array.get(sPts, k)
        table.cell(tb, 0, k + 1, array.get(names, k), text_color=color.white, text_size=size.small)
        table.cell(tb, 1, k + 1, str.tostring(array.get(sN, k)) + " / " + str.tostring(array.get(sW, k)), text_color=color.white, text_size=size.small)
        table.cell(tb, 2, k + 1, fmt(pv) + " (" + usd(pv * 2) + ")", text_color=pv >= 0 ? color.lime : color.red, text_size=size.small)

// ---------- last trades (optional) ----------
var table lt = table.new(position.bottom_left, 4, 9, bgcolor=color.new(#131722, 10), border_color=color.new(color.gray, 80), border_width=1)
if showLog and barstate.islast
    table.cell(lt, 0, 0, "Last trades", text_color=color.yellow, text_size=size.small)
    table.cell(lt, 1, 0, "strategy / entry", text_color=color.yellow, text_size=size.small)
    table.cell(lt, 2, 0, "exit", text_color=color.yellow, text_size=size.small)
    table.cell(lt, 3, 0, "pts (1 MNQ $)", text_color=color.yellow, text_size=size.small)
    nL = array.size(lgP)
    if nL == 0
        table.cell(lt, 0, 1, "none on loaded bars", text_color=color.white, text_size=size.small)
    for i = 0 to 7
        if i < nL
            j = nL - 1 - i
            pv = array.get(lgP, j)
            table.cell(lt, 0, i + 1, array.get(lgD, j), text_color=color.white, text_size=size.small)
            table.cell(lt, 1, i + 1, array.get(lgS, j), text_color=color.white, text_size=size.small)
            table.cell(lt, 2, i + 1, array.get(lgX, j), text_color=color.white, text_size=size.small)
            table.cell(lt, 3, i + 1, fmt(pv) + " (" + usd(pv * 2) + ")", text_color=pv >= 0 ? color.lime : color.red, text_size=size.small)
```
