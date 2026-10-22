"""MNQSCALP Python replica of the TradingView Pine strategy (V9.6 logic).
Bar-by-bar port with a TradingView-style broker emulator:
- orders placed at bar close, active from next bar
- intrabar path O-H-L-C if high is closer to open than low, else O-L-H-C
- stop orders: fill at level (or open if gapped) + slippage ticks adverse
- limit orders: fill at level (or open if gapped favorably), no slippage
- market (close_all) at next bar open + slippage
- commission per contract per fill
"""
import json, math, datetime as dt
from zoneinfo import ZoneInfo
import numpy as np

NY = ZoneInfo("America/New_York")
NAN = float("nan")

DEFAULTS = dict(
    contracts=2, maxRiskUSD=150.0, minRiskTicks=8, tp1R=1.0, runnerR=3.0, useKeyTgt=True,
    lowVolMode=True, lowVolRatio=0.8, maxHoldMin=180, beOffTicks=4, trailRunner=True,
    skipLondon=True, maxTrades=4, dailyLossUSD=600.0, dayProfitUSD=300.0, sizeDown=True,
    allowLong=True, allowShort=True, useSE=True, useLHHL=True, useHL=True, hlMode="Structure",
    lhMode="Loose", useBP=True, useDT=True, useDB=False, useF2=False,
    emaLen=21, useVwapF=True, sigBeyond=True, sigFrac=0.5, minBodyFr=0.4, dtTol=0.25,
    pivLen=2, trendBars=20, chopBars=10, chopMax=6, maxPushes=3, emaTol=0.3, roomR=1.0,
    wickMult=2.0, wLook=20, wF2Bars=3, wNeedSlope=True,
    tick=0.25, pv=2.0, commission=2.37, slipTicks=1, tfMin=5,
    noNew=((1630, 1800), (0, 400)), londonWin=(400, 930), flatWin=(1640, 1800),
    blockHours=(),
    tp1Frac=0.5, propMaxLoss=0.0, propBuf=0.0,
    htfMin=0, htfMode='slope', minAtrRatio=0.0, maxAtrRatio=99.0, dowBlock=(),
    seCountMin=1, seCountMax=2, seTrend='full', seTol=None, lhWin=15, bpWin=10, lhMinUps=1,
)


def load_yahoo(path):
    d = json.load(open(path))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    rows = []
    for i, t in enumerate(d["timestamp"]):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, c):
            continue
        rows.append((t, o, h, l, c, v or 0))
    return rows


def ema_series(x, n):
    a = 2.0 / (n + 1)
    out = np.full(len(x), NAN)
    s = NAN
    for i, v in enumerate(x):
        if i < n - 1:
            continue
        if math.isnan(s):
            s = float(np.mean(x[i - n + 1:i + 1]))
        else:
            s = a * v + (1 - a) * s
        out[i] = s
    return out


def rma(x, n):
    out = np.full(len(x), NAN)
    s = NAN
    for i, v in enumerate(x):
        if i < n - 1:
            continue
        if math.isnan(s):
            s = float(np.mean(x[i - n + 1:i + 1]))
        else:
            s = (s * (n - 1) + v) / n
        out[i] = s
    return out


def run(rows, **kw):
    P = dict(DEFAULTS); P.update(kw)
    tick, pv = P["tick"], P["pv"]
    n = len(rows)
    T = np.array([r[0] for r in rows]); O = np.array([r[1] for r in rows]); H = np.array([r[2] for r in rows])
    L = np.array([r[3] for r in rows]); C = np.array([r[4] for r in rows]); V = np.array([r[5] for r in rows], float)
    # times (NY)
    tcl = [dt.datetime.fromtimestamp(t + P["tfMin"] * 60, NY) for t in T]
    topen6 = [dt.datetime.fromtimestamp(t + 6 * 3600, NY) for t in T]
    tB = np.array([d.hour * 100 + d.minute for d in tcl])
    hourC = np.array([d.hour for d in tcl])
    sessDay = [d.date() for d in topen6]
    # core series
    ema = ema_series(C, P["emaLen"])
    tr = np.maximum(H - L, np.maximum(np.abs(H - np.r_[NAN, C[:-1]]), np.abs(L - np.r_[NAN, C[:-1]])))
    tr[0] = H[0] - L[0]
    atr = rma(tr, 14)
    atrL = np.full(n, NAN)
    for i in range(n):
        if i >= 99 + 13:
            atrL[i] = np.mean(atr[i - 99:i + 1])
    rng = H - L
    # HTF trend from completed higher-timeframe bars (no lookahead)
    htfUpA = np.zeros(n, bool); htfDnA = np.zeros(n, bool)
    if P["htfMin"]:
        k = P["htfMin"] * 60
        buckets = {}
        order = []
        for i0 in range(n):
            b = (T[i0] // k) * k
            if b not in buckets:
                buckets[b] = [i0, i0]; order.append(b)
            buckets[b][1] = i0
        hc = np.array([C[buckets[b][1]] for b in order])
        he = ema_series(hc, P["emaLen"])
        idx = {b: j for j, b in enumerate(order)}
        for i0 in range(n):
            j = idx[(T[i0] // k) * k] - 1   # last completed HTF bar
            if j >= 3 and not math.isnan(he[j]) and not math.isnan(he[j - 3]):
                if P["htfMode"] == 'slope':
                    htfUpA[i0] = he[j] > he[j - 3]; htfDnA[i0] = he[j] < he[j - 3]
                else:
                    htfUpA[i0] = hc[j] > he[j]; htfDnA[i0] = hc[j] < he[j]

    pivLen = P["pivLen"]; emaTol = P["emaTol"]
    # state
    sh1 = sh2 = sl1 = sl2 = NAN; upP = dnP = 0
    hCount = 0; hArm = False; pbLow = NAN
    lCount = 0; lArm = False; pbHigh = NAN
    wickRes = wickSup = NAN
    upsSinceDn = 0; dnsSinceUp = 0
    lastBrokeUp = lastBrokeDn = None; bpLvlUp = bpLvlDn = NAN
    sh1_hist = [NAN] * n; sl1_hist = [NAN] * n
    sHigh = sLow = pdh = pdl = NAN
    vw_pv = vw_v = 0.0
    # Wade F2 counters
    wPbL = NAN; wB = 0; wBArm = False; wPbH = NAN; wS = 0; wSArm = False
    wB_prev = 0; wS_prev = 0; lastF2s = None; lastF2l = None
    # account
    net = 0.0; sessStartNet = 0.0; subTrades = 0
    eqPeak = 0.0
    propBreach = None
    pos = None          # dict: side, legs [{qty,lim,stop,name}], entry, entryBar, stop0, tgt, lowVol, q, id
    pend = None         # dict: side, ePx, sPx, tp1, tgt, qty, q1, id, bar
    pend_close = None   # pending market close reason
    trades = []         # closed legs: dict
    daily = {}

    def fill_exit(leg_qty, px, reason, i):
        nonlocal net
        sign = 1 if pos["side"] == 1 else -1
        pnl = (px - pos["entry"]) * sign * leg_qty * pv - P["commission"] * leg_qty * 2
        net += pnl
        trades.append(dict(id=pos["id"], side=pos["side"], qty=leg_qty, entry=pos["entry"], exit=px, pnl=pnl,
                           reason=reason, etime=pos["etime"], ebar=pos["entryBar"], xbar=i, sess=pos["sess"]))
        daily[pos["sess"]] = daily.get(pos["sess"], 0.0) + pnl

    for i in range(n):
        o, h, l, c = O[i], H[i], L[i], C[i]
        newSess = i == 0 or sessDay[i] != sessDay[i - 1]
        # ---------------- broker emulator for bar i (orders from previous close) ----------------
        if pend_close is not None and pos is not None:
            sign = pos["side"]
            px = o - sign * P["slipTicks"] * tick
            for leg in list(pos["legs"]):
                fill_exit(leg["qty"], px, pend_close, i)
            pos = None
        pend_close = None
        path = [o, h, l, c] if abs(h - o) < abs(l - o) else [o, l, h, c]
        opened_this_bar = False
        # walk segments
        cur = o
        segs = [(path[k], path[k + 1]) for k in range(3)]
        # gap handling at open for pending entry
        def try_entry(a, b, at_open=False):
            nonlocal pos, pend, opened_this_bar
            if pend is None or pos is not None:
                return None
            e = pend["ePx"]
            if pend["side"] == 1:
                hit = (at_open and a >= e) or (not at_open and a < e <= b)
                fpx = (a if at_open else e) + P["slipTicks"] * tick
            else:
                hit = (at_open and a <= e) or (not at_open and a > e >= b)
                fpx = (a if at_open else e) - P["slipTicks"] * tick
            if not hit:
                return None
            legs = [dict(qty=pend["q1"], lim=pend["tp1"], stop=pend["sPx"], name="TP1")]
            if pend["qty"] - pend["q1"] > 0:
                legs.append(dict(qty=pend["qty"] - pend["q1"], lim=pend["tgt"], stop=pend["sPx"], name="RUN"))
            pos = dict(side=pend["side"], legs=legs, entry=fpx, entryBar=i, stop0=pend["sPx"], tgt=pend["tgt"],
                       lowVol=pend["lowVol"], q=pend["qty"], id=pend["id"], etime=T[i], sess=sessDay[i])
            pend = None
            opened_this_bar = True
            return e

        def try_exits(a, b, at_open=False):
            # returns True if something filled; processes in price order along a->b
            nonlocal pos
            if pos is None:
                return
            side = pos["side"]
            events = []
            for leg in pos["legs"]:
                for kind, lvl in (("lim", leg["lim"]), ("stop", leg["stop"])):
                    if lvl is None or (isinstance(lvl, float) and math.isnan(lvl)):
                        continue
                    if at_open:
                        if kind == "lim" and ((side == 1 and a >= lvl) or (side == -1 and a <= lvl)):
                            events.append((0, leg, kind, a))
                        if kind == "stop" and ((side == 1 and a <= lvl) or (side == -1 and a >= lvl)):
                            events.append((0, leg, kind, a - side * P["slipTicks"] * tick))
                    else:
                        lo, hi = min(a, b), max(a, b)
                        if lo <= lvl <= hi and lvl != a:
                            fpx = lvl if kind == "lim" else lvl - side * P["slipTicks"] * tick
                            events.append((abs(lvl - a), leg, kind, fpx))
            events.sort(key=lambda e: e[0])
            done = set()
            for _, leg, kind, fpx in events:
                if id(leg) in done or pos is None:
                    continue
                if leg not in pos["legs"]:
                    continue
                reason = ("TP1" if leg["name"] == "TP1" else "RUN TGT") if kind == "lim" else leg.get("slname", "SL")
                fill_exit(leg["qty"], fpx, reason, i)
                pos["legs"].remove(leg)
                done.add(id(leg))
                if not pos["legs"]:
                    pos = None
                    return

        # open
        try_exits(o, o, at_open=True)
        try_entry(o, o, at_open=True)
        if pos is not None and opened_this_bar:
            try_exits(o, o, at_open=True)
        for a, b in segs:
            if pos is not None:
                try_exits(a, b)
            if pos is None and pend is not None:
                e = try_entry(a, b)
                if e is not None:
                    try_exits(e, b)
        inPos_now = pos is not None

        # ---------------- indicators at bar close ----------------
        ph = NAN; pl = NAN
        if i >= 2 * pivLen:
            c_ = i - pivLen
            if all(H[c_] > H[c_ - k] for k in range(1, pivLen + 1)) and all(H[c_] > H[c_ + k] for k in range(1, pivLen + 1)):
                ph = H[c_]
            if all(L[c_] < L[c_ - k] for k in range(1, pivLen + 1)) and all(L[c_] < L[c_ + k] for k in range(1, pivLen + 1)):
                pl = L[c_]
        prev_sh1, prev_sl1 = sh1, sl1
        if not math.isnan(ph):
            sh2 = sh1; sh1 = ph
            upP = upP + 1 if (not math.isnan(sh2) and sh1 > sh2) else 0
        if not math.isnan(pl):
            sl2 = sl1; sl1 = pl
            dnP = dnP + 1 if (not math.isnan(sl2) and sl1 < sl2) else 0
        sh1_hist[i] = sh1; sl1_hist[i] = sl1
        upStruct = sh1 > sh2 and sl1 > sl2
        dnStruct = sh1 < sh2 and sl1 < sl2
        tb = P["trendBars"]
        aboveCnt = int(np.sum(C[max(0, i - tb + 1):i + 1] > ema[max(0, i - tb + 1):i + 1]))
        cb = P["chopBars"]
        lo_ = max(0, i - cb + 1)
        chopCnt = int(np.sum((L[lo_:i + 1] <= ema[lo_:i + 1]) & (H[lo_:i + 1] >= ema[lo_:i + 1])))
        chop = chopCnt >= P["chopMax"]
        emaUp = i >= 3 and ema[i] > ema[i - 3]
        emaDn = i >= 3 and ema[i] < ema[i - 3]
        longTrend = emaUp and aboveCnt >= round(tb * 0.5) and not chop
        shortTrend = emaDn and aboveCnt <= round(tb * 0.5) and not chop
        a_ = atr[i]
        if i == 0 or math.isnan(a_) or math.isnan(ema[i]):
            # session bookkeeping still needed
            pass
        insideBar = i > 0 and h <= H[i - 1] and l >= L[i - 1]
        r = rng[i]
        bullSig = i > 0 and (not P["sigBeyond"] or c > C[i - 1]) and c > o and r > 0 and (c - l) >= r * P["sigFrac"] and r >= a_ * 0.4 and not insideBar
        bearSig = i > 0 and (not P["sigBeyond"] or c < C[i - 1]) and c < o and r > 0 and (h - c) >= r * P["sigFrac"] and r >= a_ * 0.4 and not insideBar
        body = abs(c - o)
        upW = h - max(o, c); dnW = min(o, c) - l
        if r >= a_ and upW >= P["wickMult"] * body and upW >= r * 0.5:
            wickRes = h
        if r >= a_ and dnW >= P["wickMult"] * body and dnW >= r * 0.5:
            wickSup = l
        if not math.isnan(wickRes) and c > wickRes:
            wickRes = NAN
        if not math.isnan(wickSup) and c < wickSup:
            wickSup = NAN
        # legs
        hh20 = np.max(H[max(0, i - 19):i + 1]); ll20 = np.min(L[max(0, i - 19):i + 1])
        if h >= hh20:
            hCount = 0; hArm = False; pbLow = l
        else:
            pbLow = min(l if math.isnan(pbLow) else pbLow, l)
            if i > 0 and h < H[i - 1]:
                hArm = True
            if i > 0 and h > H[i - 1] and hArm:
                hCount += 1; hArm = False
        if l <= ll20:
            lCount = 0; lArm = False; pbHigh = h
        else:
            pbHigh = max(h if math.isnan(pbHigh) else pbHigh, h)
            if i > 0 and l > L[i - 1]:
                lArm = True
            if i > 0 and l < L[i - 1] and lArm:
                lCount += 1; lArm = False
        ema_i = ema[i]
        seT = P["seTol"] if P["seTol"] is not None else emaTol
        lt = longTrend if P["seTrend"] == 'full' else (emaUp and c > ema_i)
        st = shortTrend if P["seTrend"] == 'full' else (emaDn and c < ema_i)
        seLong = P["useSE"] and lt and not (upP >= P["maxPushes"]) and P["seCountMin"] <= hCount <= P["seCountMax"] and hArm and pbLow <= ema_i + seT * a_ and c > ema_i - seT * a_ and bullSig
        seShort = P["useSE"] and st and not (dnP >= P["maxPushes"]) and P["seCountMin"] <= lCount <= P["seCountMax"] and lArm and pbHigh >= ema_i - seT * a_ and c < ema_i + seT * a_ and bearSig
        # breaks (crossover close vs sh1[1])
        s1p = sh1_hist[i - 1] if i >= 1 else NAN; s1pp = sh1_hist[i - 2] if i >= 2 else NAN
        l1p = sl1_hist[i - 1] if i >= 1 else NAN; l1pp = sl1_hist[i - 2] if i >= 2 else NAN
        brokeUp = i >= 2 and c > s1p and C[i - 1] <= s1pp
        brokeDn = i >= 2 and c < l1p and C[i - 1] >= l1pp
        if brokeUp:
            lastBrokeUp = i; bpLvlUp = s1p
        if brokeDn:
            lastBrokeDn = i; bpLvlDn = l1p
        # cntSince
        if brokeDn:
            upsSinceDn = 0
        else:
            upsSinceDn += 1 if (i > 0 and h > H[i - 1]) else 0
        if brokeUp:
            dnsSinceUp = 0
        else:
            dnsSinceUp += 1 if (i > 0 and l < L[i - 1]) else 0
        bsUp = (i - lastBrokeUp) if lastBrokeUp is not None else None
        bsDn = (i - lastBrokeDn) if lastBrokeDn is not None else None
        hlModeOk = P["hlMode"] == "Loose" or (upStruct if P["hlMode"] == "Structure" else l >= bpLvlUp - emaTol * a_)
        lhModeOk = P["lhMode"] == "Loose" or (dnStruct if P["lhMode"] == "Structure" else h <= bpLvlDn + emaTol * a_)
        lhShort = P["useLHHL"] and lhModeOk and bsDn is not None and 2 <= bsDn <= P["lhWin"] and upsSinceDn >= P["lhMinUps"] and h < ema_i + emaTol * a_ and c < ema_i and h < sh1 and bearSig and not upStruct
        hlLong = P["useLHHL"] and P["useHL"] and hlModeOk and bsUp is not None and 2 <= bsUp <= 15 and dnsSinceUp >= 1 and l > ema_i - emaTol * a_ and c > ema_i and l > sl1 and bullSig and not dnStruct
        bpLong = P["useBP"] and bsUp is not None and 2 <= bsUp <= P["bpWin"] and dnsSinceUp >= 1 and l <= bpLvlUp + emaTol * a_ and c > bpLvlUp and c > ema_i and bullSig
        bpShort = P["useBP"] and bsDn is not None and 2 <= bsDn <= P["bpWin"] and upsSinceDn >= 1 and h >= bpLvlDn - emaTol * a_ and c < bpLvlDn and c < ema_i and bearSig
        dbLong = P["useDB"] and not math.isnan(sl2) and abs(sl1 - sl2) <= P["dtTol"] * a_ and l <= sl1 + 0.3 * a_ and c > sl1 and bullSig
        dtShort = P["useDT"] and not math.isnan(sh2) and abs(sh1 - sh2) <= P["dtTol"] * a_ and h >= sh1 - 0.3 * a_ and c < sh1 and bearSig
        # Wade F2 (failed 2nd entry against trend)
        wl = P["wLook"]
        whh = np.max(H[max(0, i - wl + 1):i + 1]); wll = np.min(L[max(0, i - wl + 1):i + 1])
        wB_prev, wS_prev = wB, wS
        if h >= whh:
            wPbL = l; wB = 0; wBArm = False
        else:
            if math.isnan(wPbL) or l < wPbL:
                wPbL = l; wB = 0; wBArm = False
            else:
                if l >= L[i - 1]:
                    wBArm = True
                if l < L[i - 1] and wBArm:
                    wB += 1; wBArm = False
        if l <= wll:
            wPbH = h; wS = 0; wSArm = False
        else:
            if math.isnan(wPbH) or h > wPbH:
                wPbH = h; wS = 0; wSArm = False
            else:
                if h <= H[i - 1]:
                    wSArm = True
                if h > H[i - 1] and wSArm:
                    wS += 1; wSArm = False
        if wB == 2 and wB_prev == 1:
            lastF2s = i
        if wS == 2 and wS_prev == 1:
            lastF2l = i
        upTL = False; dnTL = False  # trendline bias simplified: structure only
        wBiasUp = c > ema_i and upStruct and (not P["wNeedSlope"] or emaUp)
        wBiasDn = c < ema_i and dnStruct and (not P["wNeedSlope"] or emaDn)
        f2Long = P["useF2"] and wBiasUp and lastF2s is not None and i - lastF2s <= P["wF2Bars"] and bullSig
        f2Short = P["useF2"] and wBiasDn and lastF2l is not None and i - lastF2l <= P["wF2Bars"] and bearSig
        # VWAP (session anchored at 18:00 ET)
        if newSess:
            vw_pv = 0.0; vw_v = 0.0
        hlc3 = (h + l + c) / 3
        vw_pv += hlc3 * V[i]; vw_v += V[i]
        vwap = vw_pv / vw_v if vw_v > 0 else hlc3
        vLong = (not P["useVwapF"]) or c > vwap
        vShort = (not P["useVwapF"]) or c < vwap
        bodyOk = P["minBodyFr"] <= 0 or body >= P["minBodyFr"] * r
        htfOkL = (not P["htfMin"]) or not htfDnA[i]
        htfOkS = (not P["htfMin"]) or not htfUpA[i]
        volOkR = (not math.isnan(atrL[i])) and P["minAtrRatio"] <= a_ / atrL[i] <= P["maxAtrRatio"]
        dowOk = dt.datetime.fromtimestamp(T[i], NY).weekday() not in P["dowBlock"]
        longSetup = volOkR and dowOk and htfOkL and P["allowLong"] and bodyOk and vLong and (seLong or dbLong or hlLong or bpLong or f2Long)
        shortSetup = volOkR and dowOk and htfOkS and P["allowShort"] and bodyOk and vShort and (seShort or dtShort or lhShort or bpShort or f2Short)
        longName = "F2ES" if f2Long else "H2" if seLong else "DB" if dbLong else "HL" if hlLong else "BP L"
        shortName = "F2EL" if f2Short else "L2" if seShort else "DT" if dtShort else "LH" if lhShort else "BP S"
        # session levels + account
        if newSess:
            pdh, pdl = sHigh, sLow
            sHigh, sLow = h, l
            sessStartNet = net
            subTrades = 0
        else:
            sHigh = max(h if math.isnan(sHigh) else sHigh, h)
            sLow = min(l if math.isnan(sLow) else sLow, l)
        t_ = tB[i]
        flat = P["flatWin"][0] <= t_ < P["flatWin"][1]
        noNew = any(a <= t_ < b for a, b in P["noNew"]) or (P["skipLondon"] and P["londonWin"][0] <= t_ < P["londonWin"][1]) or (hourC[i] in P["blockHours"])
        openP = 0.0
        if pos is not None:
            openP = sum((c - pos["entry"]) * pos["side"] * lg["qty"] * pv for lg in pos["legs"])
        sessPnl = net + openP - sessStartNet
        if newSess:
            eqPeak = max(eqPeak, net)
        eqNow = net + openP
        if P["propMaxLoss"] > 0 and eqNow <= eqPeak - P["propMaxLoss"] and propBreach is None:
            propBreach = sessDay[i]
        propHalt = P["propMaxLoss"] > 0 and (eqNow <= eqPeak - P["propMaxLoss"] + P["propBuf"] or propBreach is not None)
        lossHit = propHalt or sessPnl <= -P["dailyLossUSD"] or (P["dayProfitUSD"] > 0 and sessPnl >= P["dayProfitUSD"])
        # opened / pend cancel
        if opened_this_bar and pos is not None:
            subTrades += 1
        if pend is not None and pos is None:
            pend = None  # one-bar validity
        if math.isnan(a_) or math.isnan(ema_i) or math.isnan(atrL[i]):
            continue
        lowVol = P["lowVolMode"] and a_ / atrL[i] < P["lowVolRatio"]
        canTrade = pos is None and pend is None and not noNew and not lossHit and subTrades < P["maxTrades"]
        mr = P["maxRiskUSD"]
        def nearest(px, vals, above):
            best = NAN
            for v in vals:
                if math.isnan(v):
                    continue
                if above and v > px and (math.isnan(best) or v < best):
                    best = v
                if not above and v < px and (math.isnan(best) or v > best):
                    best = v
            return best
        placed = False
        if canTrade and longSetup:
            ePx = h + tick; sPx = l - tick
            risk = max(ePx - sPx, P["minRiskTicks"] * tick); sPx = ePx - risk
            keyUp = nearest(ePx, [sh1, sHigh, pdh, wickRes], True)
            roomOk = math.isnan(keyUp) or keyUp - ePx >= P["roomR"] * risk
            qty = min(P["contracts"], int(math.floor(mr / (risk * pv)))) if P["sizeDown"] else (P["contracts"] if risk * pv * P["contracts"] <= mr else 0)
            if roomOk and qty >= 1:
                tp1 = ePx + P["tp1R"] * risk; tmax = ePx + P["runnerR"] * risk
                kb = nearest(tp1, [sh1, sHigh, pdh, wickRes], True)
                tgt = min(kb - tick, tmax) if (P["useKeyTgt"] and not math.isnan(kb)) else tmax
                q1 = qty if (lowVol or qty == 1) else max(1, int(round(qty * P["tp1Frac"])))
                pend = dict(side=1, ePx=ePx, sPx=sPx, tp1=tp1, tgt=tgt, qty=qty, q1=q1, id=longName, lowVol=lowVol, bar=i)
                placed = True
        if canTrade and not placed and shortSetup:
            ePx = l - tick; sPx = h + tick
            risk = max(sPx - ePx, P["minRiskTicks"] * tick); sPx = ePx + risk
            keyDn = nearest(ePx, [sl1, sLow, pdl, wickSup], False)
            roomOk = math.isnan(keyDn) or ePx - keyDn >= P["roomR"] * risk
            qty = min(P["contracts"], int(math.floor(mr / (risk * pv)))) if P["sizeDown"] else (P["contracts"] if risk * pv * P["contracts"] <= mr else 0)
            if roomOk and qty >= 1:
                tp1 = ePx - P["tp1R"] * risk; tmax = ePx - P["runnerR"] * risk
                kb = nearest(tp1, [sl1, sLow, pdl, wickSup], False)
                tgt = max(kb + tick, tmax) if (P["useKeyTgt"] and not math.isnan(kb)) else tmax
                q1 = qty if (lowVol or qty == 1) else max(1, int(round(qty * P["tp1Frac"])))
                pend = dict(side=-1, ePx=ePx, sPx=sPx, tp1=tp1, tgt=tgt, qty=qty, q1=q1, id=shortName, lowVol=lowVol, bar=i)
        # management
        if pos is not None:
            tp1Done = (not pos["lowVol"]) and pos["q"] > 1 and sum(lg["qty"] for lg in pos["legs"]) < pos["q"]
            side = pos["side"]
            be = pos["entry"] + side * P["beOffTicks"] * tick
            if side == 1:
                trail = max(be, (sl1 - tick) if not math.isnan(sl1) else be)
            else:
                trail = min(be, (sh1 + tick) if not math.isnan(sh1) else be)
            runStop = trail if P["trailRunner"] else be
            if tp1Done:
                for lg in pos["legs"]:
                    lg["stop"] = runStop
                    lg["slname"] = "BE+" if runStop == be else "TRAIL"
            barsIn = i - pos["entryBar"]
            if barsIn * P["tfMin"] >= P["maxHoldMin"]:
                pend_close = "Max hold"
            if flat:
                pend_close = "Session flat"
    run.propBreach = propBreach
    return trades, daily, net


def summary(trades, net, label=""):
    n = len(trades)
    wins = sum(1 for t in trades if t["pnl"] > 0)
    gp = sum(t["pnl"] for t in trades if t["pnl"] > 0); gl = -sum(t["pnl"] for t in trades if t["pnl"] <= 0)
    eq = 0; peak = 0; dd = 0
    for t in trades:
        eq += t["pnl"]; peak = max(peak, eq); dd = max(dd, peak - eq)
    pf = gp / gl if gl > 0 else float("inf")
    return f"{label} net {net:+.0f}  legs {n}  win {100*wins/max(n,1):.1f}%  PF {pf:.2f}  DD {dd:.0f}"
