// MNQ Eval Lab engine. Shared by the web page and Node tests.
// Bars per day: {d: YYYYMMDD, b: [[hhmm, o, h, l, c], ...]} for 9:30-16:00 ET, 5-minute.
// Every sim returns Map(day -> [trade]) where trade = {side, eI, eP, xI, xP, q, pnl, why}.
(function (root) {
  const FLAT = 1555;

  function sizeQ(P, r, pv) { return Math.floor(Math.min(P.maxQty, P.risk / (r * pv + 2 * P.comm))); }
  function mkTrade(side, eI, eP, xI, xP, q, pv, comm, why) {
    return { side, eI, eP, xI, xP, q, pnl: (xP - eP) * side * q * pv - comm * q * 2, why, hold: (xI - eI) * BAR + BAR / 2 };
  }
  function orRange(b, orMin) {
    const n = Math.max(1, Math.round(orMin / BAR)); let hi = -Infinity, lo = Infinity;
    for (let i = 0; i < n; i++) { hi = Math.max(hi, b[i][2]); lo = Math.min(lo, b[i][3]); }
    return { n, hi, lo };
  }
  // walk an open position from bar i; returns trade when closed or null
  // MAXHOLD (minutes, 0 = off): exit at the close of the bar where held time reaches the limit
  let MAXHOLD = 0; let BAR = 5;
  function manage(pos, bar, i, T, S, pv, comm) {
    const [tm, o, h, l, c] = bar; const { side, stp, tgt } = pos;
    if (side > 0 ? l <= stp : h >= stp) return mkTrade(side, pos.eI, pos.eP, i, stp - side * S * T, pos.q, pv, comm, 'stop');
    if (tgt !== null && (side > 0 ? h >= tgt : l <= tgt)) return mkTrade(side, pos.eI, pos.eP, i, tgt, pos.q, pv, comm, 'target');
    if (tm >= FLAT) return mkTrade(side, pos.eI, pos.eP, i, c, pos.q, pv, comm, 'close');
    if (MAXHOLD && (i - pos.eI + 1) * BAR >= MAXHOLD) return mkTrade(side, pos.eI, pos.eP, i, c, pos.q, pv, comm, 'time');
    return null;
  }
  // entry bar: if the hold limit is one bar or less, exit at the entry bar close
  function entryBarHold(pos, bar, i, pv, comm) {
    if (MAXHOLD && MAXHOLD <= BAR) return mkTrade(pos.side, pos.eI, pos.eP, i, bar[4], pos.q, pv, comm, 'time');
    return null;
  }


  // ---------- Exit manager with TP1 partial, breakeven, runner target, trailing stop ----------
  // pos: {side,eI,eP,stp,q,r,tp1,q1,tgt,be,trailN,trailTrig}
  function manageX(pos, b, i, T, S, pv, comm) {
    const [tm, o, h, l, c] = b[i]; const sd = pos.side;
    if (pos.qRem === undefined) { pos.qRem = pos.q; pos.real = 0; pos.mfe = 0; pos.done1 = false; }
    const fin = (xP, why) => { pos.real += (xP - pos.eP) * sd * pos.qRem * pv; if (pos.qA) pos.real += (xP - pos.pA) * sd * pos.qA * pv; const pnl = pos.real - comm * (pos.q + (pos.qA || 0)) * 2;
      return { side: sd, eI: pos.eI, eP: pos.eP, xI: i, xP, q: pos.q, pnl, why: pos.done1 && why === 'stop' ? 'be/trail' : why, hold: (i - pos.eI) * BAR + BAR / 2, mfeR: pos.r > 0 ? pos.mfe / pos.r : 0, tp1: pos.done1 }; };
    if (sd > 0 ? l <= pos.stp : h >= pos.stp) return fin(pos.stp - sd * S * T, 'stop');
    pos.mfe = Math.max(pos.mfe, sd > 0 ? h - pos.eP : pos.eP - l);
    let newStop = null;
    if (!pos.done1 && pos.tp1 !== null && (sd > 0 ? h >= pos.tp1 : l <= pos.tp1)) {
      pos.done1 = true;
      if (pos.q1 > 0) { pos.real += (pos.tp1 - pos.eP) * sd * pos.q1 * pv; pos.qRem -= pos.q1; }
      if (pos.qRem <= 0) { pos.qRem = 0; return fin(pos.tp1, 'target'); }
      if (pos.be) newStop = pos.eP + sd * T;
    }
    if (pos.tgt !== null && (pos.tp1 === null || pos.done1) && (sd > 0 ? h >= pos.tgt : l <= pos.tgt)) return fin(pos.tgt, 'target');
    if (tm >= FLAT) return fin(c, 'close');
    if (MAXHOLD && (i - pos.eI + 1) * BAR >= MAXHOLD) return fin(c, 'time');
    const inProfit = (c - pos.eP) * sd > 0;
    if (pos.exitPB && i > pos.eI && (pos.exitPB === 1 || inProfit) && (sd > 0 ? c < b[i - 1][3] : c > b[i - 1][2])) return fin(c, 'pullback');
    if (pos.exhaust && i >= pos.eI + 2 && inProfit) {
      const bd = k => Math.abs(b[k][4] - b[k][1]);
      if (bd(i) < bd(i - 1) && bd(i - 1) < bd(i - 2)) return fin(c, 'exhaustion');
    }
    if (pos.trailN > 0 && (pos.done1 || pos.mfe >= pos.trailTrig * pos.r)) {
      let ex = sd > 0 ? Infinity : -Infinity;
      for (let k = Math.max(pos.eI, i - pos.trailN + 1); k <= i; k++) ex = sd > 0 ? Math.min(ex, b[k][3]) : Math.max(ex, b[k][2]);
      const ts = ex - sd * T; newStop = newStop === null ? ts : (sd > 0 ? Math.max(newStop, ts) : Math.min(newStop, ts));
    }
    // add to a winner: once, when the close is addR x risk in profit on a strong candle in the trade direction
    if (pos.addR > 0 && !pos.qA && i > pos.eI) {
      const rg = h - l, body = Math.abs(c - o);
      if ((c - pos.eP) * sd >= pos.addR * pos.r && rg > 0 && body >= 0.6 * rg && (c - o) * sd > 0) {
        const qa = Math.min(pos.maxQ - pos.q, Math.max(1, Math.round(pos.q * pos.addPct / 100)));
        if (qa > 0) { pos.qA = qa; pos.pA = c + sd * S * T; const pr = pos.eP + sd * T; newStop = newStop === null ? pr : (sd > 0 ? Math.max(newStop, pr) : Math.min(newStop, pr)); }
      }
    }
    if (newStop !== null) pos.stp = sd > 0 ? Math.max(pos.stp, newStop) : Math.min(pos.stp, newStop);
    return null;
  }
  function exitPlan(P, side, eP, stp, q, legacyTgtR, lv) {
    const r = Math.abs(eP - stp);
    const tp1R = +P.tp1R || 0, runR = P.runR === undefined ? legacyTgtR : +P.runR;
    const tp1 = tp1R > 0 ? eP + side * tp1R * r : null;
    const q1 = tp1R > 0 ? Math.floor(q * (+P.tp1Pct || 0) / 100) : 0;
    const tgtR = tp1R > 0 ? runR : legacyTgtR;
    let tgt = tgtR > 0 ? eP + side * tgtR * r : null;
    if (+P.tgtPts > 0) tgt = eP + side * +P.tgtPts;
    if (P.lvlTgt && lv) {
      const gap = +P.lvlGap || 2;
      const ahead = lv.filter(x => (x - eP) * side >= gap).sort((a, z) => (a - z) * side);
      const room = ahead.length ? Math.abs(ahead[0] - eP) : Infinity;
      if (+P.minRoomR > 0 && room < +P.minRoomR * r) return null;
      if (ahead.length) { const lt = ahead[0] - side * 0.25; if (tgt === null || (lt - tgt) * side < 0) tgt = lt; }
    }
    return { side, eP, stp, q, r, tp1, q1, tgt, be: !!P.beOn && tp1R > 0, trailN: +P.trailN || 0, trailTrig: P.trailTrig === undefined ? 1 : +P.trailTrig, exitPB: +P.exitPB || 0, exhaust: !!P.exhaust, addR: +P.addR || 0, addPct: P.addPct === undefined ? 100 : +P.addPct, maxQ: P.maxQty || 20 };
  }
  // support/resistance: 3-bar pivots of the prior 3 days, prior day high/low, plus today's pivots confirmed before bar i
  function piv(b, from, to, N) { N = N || 3; const o = []; for (let j = Math.max(N, from); j <= to - N; j++) {
      let ph = true, pl = true; for (let k = 1; k <= N; k++) { if (!(b[j][2] > b[j - k][2] && b[j][2] > b[j + k][2])) ph = false; if (!(b[j][3] < b[j - k][3] && b[j][3] < b[j + k][3])) pl = false; }
      if (ph) o.push(b[j][2]); if (pl) o.push(b[j][3]); } return o; }
  function levelsFor(days, d, b, i, N, back) {
    N = N || 3; back = back || 3; const key = '_lv' + N + '_' + back;
    if (!days[key]) { const M = new Map(); for (let k = 0; k < days.length; k++) { const L = []; for (let m = Math.max(0, k - back); m < k; m++) { const bb = days[m].b; L.push(...piv(bb, 0, bb.length - 1, N)); }
        if (k > 0) { const pb = days[k - 1].b; L.push(Math.max(...pb.map(x => x[2])), Math.min(...pb.map(x => x[3]))); } M.set(days[k].d, L); } days[key] = M; }
    return days[key].get(d).concat(piv(b, 0, i - 1, N));
  }


  // EMA of closes over all bars (continuous across days), cached per days array; avg candle range of the last n bars
  function emaArr(days, len) { const key = '_ema' + len; if (days[key]) return days[key]; const M = new Map(); let e = null; const k = 2 / (len + 1);
    for (const { d, b } of days) { const a = []; for (const x of b) { e = e === null ? x[4] : e + k * (x[4] - e); a.push(e); } M.set(d, a); } days[key] = M; return M; }
  function avgRange(b, j, n) { const f = Math.max(0, j - n); let s = 0; for (let k = f; k < j; k++) s += b[k][2] - b[k][3]; return j > f ? s / (j - f) : b[j][2] - b[j][3]; }
  // filters at bar j for a trade in direction side: trend = EMA21 rising/falling over 3 bars and last close on the right side; ext = stretch from EMA in candles
  function trendOK(em, b, j, side) { if (j < 4) return false; return (em[j - 1] - em[j - 4]) * side > 0 && (b[j - 1][4] - em[j - 1]) * side > 0; }
  function stretch(em, b, j, side) { return j < 1 ? 0 : (b[j - 1][4] - em[j - 1]) * side / avgRange(b, j, 12); }

  // ---------- Opening range breakout ----------
  function simORB(days, P, mk) {
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip;
    for (const { d, b } of days) {
      const res = []; out.set(d, res);
      if (b.length < 20 || b[0][0] !== 930) continue;
      const { n, hi, lo } = orRange(b, P.orMin);
      const used = new Set(), blocked = new Set(); let pos = null;
      for (let i = n; i < b.length; i++) {
        const [tm, o, h, l, c] = b[i];
        if (pos) { const t = manageX(pos, b, i, T, S, PV, C); if (t) { res.push(t); pos = null; if (!P.both) break; } continue; }
        if (tm > P.lastEntry || tm >= FLAT) continue;
        if (P.firstEntry && tm < P.firstEntry) continue;
        for (const [side, lvl] of [[1, hi + T], [-1, lo - T]]) {
          if (used.has(side)) continue;
          if ((side > 0 && h >= lvl) || (side < 0 && l <= lvl)) {
            if (P.trendF && !trendOK(emaArr(days, 21).get(d), b, i, side)) { if (P.trendF === 'skip') used.add(side); else blocked.add(side); continue; }
            if (P.maxExt && stretch(emaArr(days, 21).get(d), b, i, side) > P.maxExt) { blocked.add(side); continue; }
            const late = P.firstEntry || blocked.has(side);   // no order was resting: fill at the open if price is already past the level
            const eP = (late ? (side > 0 ? Math.max(o, lvl) : Math.min(o, lvl)) : lvl) + side * S * T;
            const stp = P.stopMode === 'pts' ? eP - side * P.stopPts : P.stopMode === 'opp' ? (side > 0 ? lo - T : hi + T) : Math.round(((hi + lo) / 2) / T) * T;
            if (P.maxStopPts && Math.abs(eP - stp) > P.maxStopPts) { used.add(side); continue; }
            const r = Math.abs(eP - stp); const q = sizeQ(P, r, PV);
            used.add(side); if (q < 1) continue;
            if ((side > 0 && l <= stp) || (side < 0 && h >= stp)) { res.push(mkTrade(side, i, eP, i, stp - side * S * T, q, PV, C, 'stop')); continue; }
            const plan = exitPlan(P, side, eP, stp, q, P.tgtR, P.lvlTgt ? levelsFor(days, d, b, i) : null); if (!plan) continue;
            pos = Object.assign(plan, { eI: i }); { const t0 = entryBarHold(pos, b[i], i, PV, C); if (t0) { res.push(t0); pos = null; } } break;
          }
        }
        if (!P.both && res.length) break;
      }
    }
    return out;
  }

  // ---------- A: Wade pullback entries inside the opening range breakout ----------
  // Bias = first 5m CLOSE beyond the opening range. Then wait for a pullback (a lower high for longs),
  // count H1/H2 (bar high above prior bar high while in pullback). Enter on a stop 1 tick beyond the
  // signal bar (next bar only). Stop 1 tick beyond the pullback extreme. Pullback must hold above
  // (OR high - depth x OR width) for longs. Opposite close beyond the other side flips the bias.
  function simPB(days, P, mk) {
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip;
    for (const { d, b } of days) {
      const res = []; out.set(d, res);
      if (b.length < 20 || b[0][0] !== 930) continue;
      const { n, hi, lo } = orRange(b, P.orMin); const w = hi - lo;
      let bias = 0, ext = 0, pb = false, cnt = 0, pbX = 0, pend = null, pos = null, trades = 0, dayPnl = 0;
      for (let i = n; i < b.length; i++) {
        const [tm, o, h, l, c] = b[i]; const ph = b[i - 1][2], pl = b[i - 1][3];
        if (pos) {
          const t = manage(pos, b[i], i, T, S, PV, C);
          if (t) { res.push(t); pos = null; trades++; dayPnl += t.pnl; pb = false; cnt = 0; ext = bias > 0 ? Math.max(ext, h) : Math.min(ext, l); }
          continue;
        }
        // try pending entry from previous bar's signal
        if (pend) {
          const p = pend; pend = null;
          if (tm <= P.lastEntry && (p.side > 0 ? h >= p.lvl : l <= p.lvl)) {
            const eP = p.lvl + p.side * S * T; let stp = p.stp;
            let r = Math.abs(eP - stp); if (r < P.minStop * T) { r = P.minStop * T; stp = eP - p.side * r; }
            const q = sizeQ(P, r, PV);
            if (q >= 1) {
              const tgt = P.tgtR > 0 ? eP + p.side * P.tgtR * r : null;
              if (p.side > 0 ? l <= stp : h >= stp) { const t = mkTrade(p.side, i, eP, i, stp - p.side * S * T, q, PV, C, 'stop'); res.push(t); trades++; dayPnl += t.pnl; pb = false; cnt = 0; continue; }
              if (tgt !== null && (p.side > 0 ? c >= tgt : c <= tgt)) { const t = mkTrade(p.side, i, eP, i, tgt, q, PV, C, 'target'); res.push(t); trades++; dayPnl += t.pnl; pb = false; cnt = 0; continue; }
              pos = { side: p.side, eI: i, eP, stp, tgt, q }; { const t0 = entryBarHold(pos, b[i], i, PV, C); if (t0) { res.push(t0); trades++; dayPnl += t0.pnl; pos = null; pb = false; cnt = 0; } } continue;
            }
          }
        }
        if (tm >= FLAT) continue;
        // bias from closes beyond the range
        if (c > hi && bias <= 0 && (bias === 0 || P.flip)) { bias = 1; ext = h; pb = false; cnt = 0; continue; }
        if (c < lo && bias >= 0 && (bias === 0 || P.flip)) { bias = -1; ext = l; pb = false; cnt = 0; continue; }
        if (!bias) continue;
        if (trades >= P.maxTrades || (P.dayStop && dayPnl <= -P.dayStop) || tm > P.lastEntry) continue;
        if (bias > 0) {
          if (h > ext) { ext = h; pb = false; cnt = 0; continue; }            // trend resumed without signal
          if (!pb) { if (h < ph) { pb = true; cnt = 0; pbX = l; } continue; }
          pbX = Math.min(pbX, l);
          if (pbX < hi - P.depth * w) { pb = false; cnt = 0; continue; }       // pullback too deep
          if (h > ph) { cnt++; if (cnt === P.need) pend = { side: 1, lvl: h + T, stp: pbX - T }; }
        } else {
          if (l < ext) { ext = l; pb = false; cnt = 0; continue; }
          if (!pb) { if (l > pl) { pb = true; cnt = 0; pbX = h; } continue; }
          pbX = Math.max(pbX, h);
          if (pbX > lo + P.depth * w) { pb = false; cnt = 0; continue; }
          if (l < pl) { cnt++; if (cnt === P.need) pend = { side: -1, lvl: l - T, stp: pbX + T }; }
        }
      }
      if (pos) { const bl = b[b.length - 1]; res.push(mkTrade(pos.side, pos.eI, pos.eP, b.length - 1, bl[4], pos.q, PV, C, 'close')); }
    }
    return out;
  }

  // ---------- ORB breakout + retest (Jey's rules) ----------
  // P.brk: '5m' | '15m'  breakout = candle CLOSE outside the 9:30 range
  // P.entry: 'limit' (limit at the range edge) | 'bounce' (stop beyond the retest candle after it holds)
  // P.stop: 'retest' | 'mid' | 'opp'
  // P.cancel: true = a 5m close back inside the range before entry cancels the day
  // P.tol: retest zone in ticks beyond the edge; P.maxW / P.minW: range width vs 20-day average (0 = off)
  function simRT(days, P, mk) {
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip; const hist = [];
    for (const { d, b } of days) {
      const res = []; out.set(d, res);
      if (b.length < 20 || b[0][0] !== 930) continue;
      const { n, hi, lo } = orRange(b, P.orMin); const w = hi - lo; const tol = (P.tol || 0) * T;
      const avg = hist.length ? hist.reduce((a, x) => a + x, 0) / hist.length : w;
      hist.push(w); if (hist.length > 20) hist.shift();
      if ((P.maxW && w > P.maxW * avg) || (P.minW && w < P.minW * avg)) continue;
      let dir = 0, brokeI = -1, inRetest = false, sig = null, rtLow = 0, rtHigh = 0, pos = null, done = false;
      for (let i = n; i < b.length && !done; i++) {
        const [tm, o, h, l, c] = b[i];
        if (pos) { const t = manage(pos, b[i], i, T, S, PV, C); if (t) { res.push(t); pos = null; done = true; } continue; }
        if (tm >= FLAT || tm > P.lastEntry) break;
        if (!dir) {
          const m = tm % 100; const span = P.brk === '15m' ? 15 : P.brk === '5m' ? 5 : BAR;
          if (((m + BAR) % span) !== 0) continue; // only bars that close a 5m / 15m candle
          let cHi = h, cLo = l; if (P.brk === '15m') { for (let k = 1; k < 15 / BAR; k++) { cHi = Math.max(cHi, b[i - k][2]); cLo = Math.min(cLo, b[i - k][3]); } }
          if (c > hi) { dir = 1; brokeI = i; } else if (c < lo) { dir = -1; brokeI = i; }
          continue;
        }
        // after the breakout: fake-out check (close back inside before entry)
        if (P.cancel && (dir > 0 ? c < hi : c > lo) && !(P.entry === 'limit' && (dir > 0 ? l <= hi + tol : h >= lo - tol))) { done = true; continue; }
        const edge = dir > 0 ? hi : lo;
        const stopFor = (ext) => P.stop === 'opp' ? (dir > 0 ? lo - T : hi + T)
          : P.stop === 'mid' ? Math.round(((hi + lo) / 2) / T) * T
          : (dir > 0 ? ext - T : ext + T);
        if (P.entry === 'limit') {
          const touch = dir > 0 ? l <= edge + tol : h >= edge - tol;
          if (!touch) continue;
          const eP = dir > 0 ? Math.min(o, edge + tol) : Math.max(o, edge - tol);
          let stp = P.stop === 'retest' ? (dir > 0 ? edge - Math.max(8 * T, 0.2 * w) : edge + Math.max(8 * T, 0.2 * w)) : stopFor(0);
          stp = Math.round(stp / T) * T;
          const r = Math.abs(eP - stp); if (r <= 0) { done = true; continue; }
          const q = sizeQ(P, r, PV); if (q < 1) { done = true; continue; }
          const tgt = P.tgtR > 0 ? eP + dir * P.tgtR * r : null;
          if (dir > 0 ? l <= stp : h >= stp) { res.push(mkTrade(dir, i, eP, i, stp - dir * S * T, q, PV, C, 'stop')); done = true; continue; }
          if (P.cancel && (dir > 0 ? c < hi - 0 && c <= stp : false)) { /* covered by stop */ }
          pos = { side: dir, eI: i, eP, stp, tgt, q }; { const t0 = entryBarHold(pos, b[i], i, PV, C); if (t0) { res.push(t0); pos = null; done = true; } } continue;
        }
        // bounce entry: retest = bar trading into the zone; signal = latest retest bar; enter on break of its high/low
        if (sig && (dir > 0 ? h >= sig.lvl : l <= sig.lvl)) {
          const eP = sig.lvl + dir * S * T; const ext = dir > 0 ? Math.min(rtLow, l) : Math.max(rtHigh, h);
          const stp = stopFor(dir > 0 ? rtLow : rtHigh);
          const r = Math.abs(eP - stp); const q = r > 0 ? sizeQ(P, r, PV) : 0;
          if (q < 1) { done = true; continue; }
          const tgt = P.tgtR > 0 ? eP + dir * P.tgtR * r : null;
          if (dir > 0 ? l <= stp : h >= stp) { res.push(mkTrade(dir, i, eP, i, stp - dir * S * T, q, PV, C, 'stop')); done = true; continue; }
          pos = { side: dir, eI: i, eP, stp, tgt, q }; { const t0 = entryBarHold(pos, b[i], i, PV, C); if (t0) { res.push(t0); pos = null; done = true; } } continue;
        }
        const touch = dir > 0 ? l <= edge + tol : h >= edge - tol;
        if (touch) {
          if (!inRetest) { inRetest = true; rtLow = l; rtHigh = h; } else { rtLow = Math.min(rtLow, l); rtHigh = Math.max(rtHigh, h); }
          sig = { lvl: dir > 0 ? h + T : l - T };
        }
      }
    }
    return out;
  }

  // ---------- Wade 2nd-entry scalper V2 (same logic as Pine "MNQ Wade 2E Scalper V2") ----------
  // Setups (each can be switched off):
  //  2E : 2nd entry with the trend (count from the swing extreme, H/L = 1-tick break of the prior bar)
  //  LH : lower-high / higher-low confirmation (1st entry allowed when the correction fails below/above the prior one)
  //  F2 : failed counter-trend 2nd entry (counter 2nd entry triggers, then price breaks back the other way)
  // Filters: key point (EMA 21 and/or auto trendline), correction trendline must be broken, no congestion,
  //          bullish/bearish signal bar. Exits: TP1 part, breakeven, runner, max hold, flatten. Daily limits.
  function simW2E(days, P, mk) {
    const D = Object.assign({ emaLen: 21, slopeBars: 3, keyTol: 8, keyMode: 'ema', sigFrac: 0.5, minBody: 0.3, allowFirst: false, swingN: 20,
      pivLen: 2, corrTL: false, useLH: false, useF2: false, fSwing: 6, fBars: 3, congBars: 8, congMult: 0, stopMode: 'signal', minStop: 12, maxStop: 100,
      risk: 200, maxQty: 20, tp1R: 1, tp1Pct: 50, runR: 2, beOn: true, maxHold: 30, maxTrades: 3, dayTarget: 600, dayLoss: 550, maxConsec: 2,
      sessStart: 930, sessEnd: 1530, flatT: 1555, comm: 2.37, slip: 1, volMin: 0, trendMode: 'ema', tgtMode: 'r', bufT: 4, exhaust: false }, P);
    P = D;
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip;
    const sm = hhmm => { const m = Math.floor(hhmm / 100) * 60 + hhmm % 100; return (m - 1080 + 1440) % 1440; }; // minutes since 18:00 ET
    const startS = sm(P.sessStart), endS = sm(P.sessEnd), flatS = sm(P.flatT);
    const k = 2 / (P.emaLen + 1); let ema = null, atr = null, atrS = null, prevClose = null; const emaHist = [];
    let pdh = null, pdl = null;
    const H = [], L = []; let gi = -1;
    const pivH = [], pivL = [];
    let hCnt = 0, pbDn = false, leg2Dn = false, pbLow = 0, pbStartDn = 0, lastPbLow = null;
    let lCnt = 0, pbUp = false, leg2Up = false, pbHigh = 0, pbStartUp = 0, lastPbHigh = null;
    let fsCnt = 0, fsPb = false, fsLeg2 = false, fsTrig = null;   // counter-trend shorts (inside an uptrend)
    let flCnt = 0, flPb = false, flLeg2 = false, flTrig = null;   // counter-trend longs (inside a downtrend)
    let started = false;
    const lineAt = (a, b, x) => a.p + (b.p - a.p) * (x - a.i) / (b.i - a.i);
    for (const { d, b } of days) {
      const res = []; out.set(d, res);
      let pend = null, pos = null, dayTrades = 0, dayPnl = 0, consec = 0;
      for (let i = 0; i < b.length; i++) {
        const [tm, o, h, l, c] = b[i]; gi++; const smin = sm(tm);
        if (i === 0 && d !== days[0].d) { /* prior day levels set at end of previous day */ }
        // 1) pending entry
        if (pend && !pos) {
          const p = pend; pend = null;
          if (p.side > 0 ? h >= p.lvl : l <= p.lvl) {
            const eP = (p.side > 0 ? Math.max(o, p.lvl) : Math.min(o, p.lvl)) + p.side * S * T;
            pos = { side: p.side, eI: i, eP, stp: p.stp, r: p.r, q: p.q, q1: p.q > 1 ? Math.max(1, Math.min(p.q - 1, Math.round(p.q * P.tp1Pct / 100))) : 0, tp1Done: false, pnl: 0, why: '', rem: p.q, setup: p.setup };
            pos.tp1 = p.tp1 !== undefined ? p.tp1 : eP + p.side * P.tp1R * p.r; pos.tgt = p.tgt !== undefined ? p.tgt : eP + p.side * P.runR * p.r; dayTrades++;
          }
        }
        // 2) manage
        if (pos) {
          const s = pos.side; let closed = false;
          const fill = (qty, px, why) => { pos.pnl += (px - pos.eP) * s * qty * PV - C * qty * 2; pos.rem -= qty; pos.why = why; };
          if (s > 0 ? l <= pos.stp : h >= pos.stp) { fill(pos.rem, pos.stp - s * S * T, pos.tp1Done ? 'breakeven' : 'stop'); closed = true; }
          else {
            if (!pos.tp1Done && pos.q1 > 0 && (s > 0 ? h >= pos.tp1 : l <= pos.tp1)) { fill(pos.q1, pos.tp1, 'tp1'); pos.tp1Done = true; if (P.beOn) pos.stp = s > 0 ? Math.max(pos.stp, pos.eP) : Math.min(pos.stp, pos.eP); }
            if (pos.rem > 0 && (s > 0 ? h >= pos.tgt : l <= pos.tgt)) { fill(pos.rem, pos.tgt, 'runner'); closed = true; }
            else if (P.exhaust && pos.tp1Done && pos.rem > 0 && atr && (h - l) >= 1.5 * atr && Math.abs(c - o) >= 0.6 * (h - l) && (s > 0 ? c < o : c > o)) { fill(pos.rem, c, 'exhaustion'); closed = true; }
            else if (pos.rem > 0 && (smin >= flatS || i === b.length - 1 || (P.maxHold && (i - pos.eI + 1) * BAR >= P.maxHold))) { fill(pos.rem, c, smin >= flatS || i === b.length - 1 ? 'close' : 'time'); closed = true; }
          }
          if (closed || pos.rem <= 0) {
            const t = { side: s, eI: pos.eI, eP: pos.eP, xI: i, xP: c, q: pos.q, pnl: pos.pnl, why: pos.why, hold: (i - pos.eI) * BAR + BAR / 2, tp1: pos.tp1Done, setup: pos.setup };
            res.push(t); dayPnl += t.pnl; consec = t.pnl < 0 ? consec + 1 : 0; pos = null;
          }
        }
        // 3) indicators
        ema = ema === null ? c : ema + k * (c - ema); emaHist.push(ema); if (emaHist.length > 60) emaHist.shift();
        const tr = prevClose === null ? h - l : Math.max(h - l, Math.abs(h - prevClose), Math.abs(l - prevClose));
        atr = atr === null ? tr : atr + (tr - atr) / 14; atrS = atrS === null ? tr : atrS + (tr - atrS) / 100; prevClose = c;
        const prevH = H.length ? H[H.length - 1] : h, prevL = L.length ? L[L.length - 1] : l;
        const win = P.swingN, fw = P.fSwing;
        let maxN = -Infinity, minN = Infinity, maxF = -Infinity, minF = Infinity;
        for (let q = Math.max(0, H.length - win); q < H.length; q++) { if (H[q] > maxN) maxN = H[q]; if (L[q] < minN) minN = L[q]; }
        for (let q = Math.max(0, H.length - fw); q < H.length; q++) { if (H[q] > maxF) maxF = H[q]; if (L[q] < minF) minF = L[q]; }
        const newHH = !started || h > maxN, newLL = !started || l < minN; started = true;
        // main counts
        if (newHH) { if (pbDn) lastPbLow = pbLow; hCnt = 0; pbDn = false; leg2Dn = false; pbLow = l; pbStartDn = gi; }
        else { pbLow = Math.min(pbLow, l); if (!pbDn && (h < prevH || l < prevL)) { pbDn = true; pbStartDn = gi; } if (pbDn && h > prevH) { hCnt++; leg2Dn = false; } if (pbDn && hCnt >= 1 && l < prevL) leg2Dn = true; }
        if (newLL) { if (pbUp) lastPbHigh = pbHigh; lCnt = 0; pbUp = false; leg2Up = false; pbHigh = h; pbStartUp = gi; }
        else { pbHigh = Math.max(pbHigh, h); if (!pbUp && (l > prevL || h > prevH)) { pbUp = true; pbStartUp = gi; } if (pbUp && l < prevL) { lCnt++; leg2Up = false; } if (pbUp && lCnt >= 1 && h > prevH) leg2Up = true; }
        // counter-trend counts on a short swing window (for failed 2nd entries)
        const nLLf = l < minF, nHHf = h > maxF;
        let fsFire = false, flFire = false;
        if (nLLf) { fsCnt = 0; fsPb = false; fsLeg2 = false; } else { if (!fsPb && (l > prevL || h > prevH)) fsPb = true; if (fsPb && l < prevL) { fsCnt++; if (fsCnt === 2) fsFire = true; fsLeg2 = false; } if (fsPb && fsCnt >= 1 && h > prevH) fsLeg2 = true; }
        if (nHHf) { flCnt = 0; flPb = false; flLeg2 = false; } else { if (!flPb && (h < prevH || l < prevL)) flPb = true; if (flPb && h > prevH) { flCnt++; if (flCnt === 2) flFire = true; flLeg2 = false; } if (flPb && flCnt >= 1 && l < prevL) flLeg2 = true; }
        if (fsFire) fsTrig = { gi, hi: Math.max(h, prevH) }; if (flFire) flTrig = { gi, lo: Math.min(l, prevL) };
        H.push(h); L.push(l); if (H.length > 400) { H.shift(); L.shift(); }
        // pivots (confirmed pivLen bars later)
        const pl = P.pivLen, n = H.length;
        if (n > 2 * pl) { const c0 = n - 1 - pl; let isH = true, isL = true;
          for (let q = 1; q <= pl; q++) { if (!(H[c0] > H[c0 - q] && H[c0] >= H[c0 + q])) isH = false; if (!(L[c0] < L[c0 - q] && L[c0] <= L[c0 + q])) isL = false; }
          if (isH) { pivH.push({ i: gi - pl, p: H[c0] }); if (pivH.length > 20) pivH.shift(); }
          if (isL) { pivL.push({ i: gi - pl, p: L[c0] }); if (pivL.length > 20) pivL.shift(); } }
        // 4) setups
        if (pos || emaHist.length <= P.slopeBars + 1) continue;
        const nextS = smin + BAR; if (nextS < startS || nextS > endS || smin >= flatS) continue;
        if (dayTrades >= P.maxTrades || (P.dayTarget && dayPnl >= P.dayTarget) || (P.dayLoss && dayPnl <= -P.dayLoss) || (P.maxConsec && consec >= P.maxConsec)) continue;
        const emaPrev = emaHist[emaHist.length - 1 - P.slopeBars]; const rg = h - l;
        let biasUp = c > ema && ema > emaPrev, biasDn = c < ema && ema < emaPrev;
        if (P.trendMode === 'swing') {
          const hU = pivH.length >= 2 && pivH[pivH.length - 1].p > pivH[pivH.length - 2].p, lU = pivL.length >= 2 && pivL[pivL.length - 1].p > pivL[pivL.length - 2].p;
          const hD = pivH.length >= 2 && pivH[pivH.length - 1].p < pivH[pivH.length - 2].p, lD = pivL.length >= 2 && pivL[pivL.length - 1].p < pivL[pivL.length - 2].p;
          biasUp = biasUp && hU && lU; biasDn = biasDn && hD && lD;
        }
        if (P.volMin > 0 && atrS && atr / atrS < P.volMin) continue;
        const bull = c > o && rg > 0 && (c - l) >= P.sigFrac * rg && Math.abs(c - o) >= P.minBody * rg;
        const bear = c < o && rg > 0 && (h - c) >= P.sigFrac * rg && Math.abs(c - o) >= P.minBody * rg;
        if (P.congMult > 0) { let a = -Infinity, z = Infinity; for (let q = Math.max(0, H.length - P.congBars); q < H.length; q++) { a = Math.max(a, H[q]); z = Math.min(z, L[q]); } if (a - z < P.congMult * atr) continue; }
        const tol = P.keyTol * T;
        // trendlines: rising line through the last two higher pivot lows (uptrend), falling through two lower pivot highs
        let tlUp = null, tlDn = null;
        if (pivL.length >= 2) { const a = pivL[pivL.length - 2], z = pivL[pivL.length - 1]; if (z.p > a.p) tlUp = lineAt(a, z, gi); }
        if (pivH.length >= 2) { const a = pivH[pivH.length - 2], z = pivH[pivH.length - 1]; if (z.p < a.p) tlDn = lineAt(a, z, gi); }
        const keyOK = (ext, side) => {
          const e = side > 0 ? ext <= ema + tol : ext >= ema - tol;
          const t = side > 0 ? (tlUp !== null && Math.abs(ext - tlUp) <= tol) : (tlDn !== null && Math.abs(ext - tlDn) <= tol);
          return P.keyMode === 'ema' ? e : P.keyMode === 'tl' ? t : P.keyMode === 'both' ? (e && t) : (e || t);
        };
        // correction trendline: line through the correction's last two lower highs (long) must be closed above
        const corrOK = (side, startI) => {
          if (!P.corrTL) return true;
          const pv = side > 0 ? pivH.filter(x => x.i >= startI) : pivL.filter(x => x.i >= startI);
          if (pv.length < 2) return true;
          const a = pv[pv.length - 2], z = pv[pv.length - 1];
          if (side > 0 ? z.p >= a.p : z.p <= a.p) return true;
          const v = lineAt(a, z, gi); return side > 0 ? c > v : c < v;
        };
        const cands = [];
        if (biasUp && bull && pbDn && !newHH && keyOK(pbLow, 1) && corrOK(1, pbStartDn)) {
          if (hCnt === 1 && leg2Dn) cands.push(['2E', 1]);
          else if (hCnt === 0 && P.allowFirst) cands.push(['1E', 1]);
          else if (hCnt === 0 && P.useLH && lastPbLow !== null && pbLow > lastPbLow) cands.push(['HL', 1]);
        }
        if (biasDn && bear && pbUp && !newLL && keyOK(pbHigh, -1) && corrOK(-1, pbStartUp)) {
          if (lCnt === 1 && leg2Up) cands.push(['2E', -1]);
          else if (lCnt === 0 && P.allowFirst) cands.push(['1E', -1]);
          else if (lCnt === 0 && P.useLH && lastPbHigh !== null && pbHigh < lastPbHigh) cands.push(['LH', -1]);
        }
        if (P.useF2 && biasUp && fsTrig && gi - fsTrig.gi <= P.fBars && gi > fsTrig.gi && c > fsTrig.hi) { cands.push(['F2', 1, fsTrig.hi]); fsTrig = null; }
        if (P.useF2 && biasDn && flTrig && gi - flTrig.gi <= P.fBars && gi > flTrig.gi && c < flTrig.lo) { cands.push(['F2', -1, flTrig.lo]); flTrig = null; }
        for (const cd of cands) {
          const side = cd[1];
          const lvl = side > 0 ? h + T : l - T;
          const ext = side > 0 ? pbLow : pbHigh;
          let sx;
          if (P.stopMode === 'pullback') sx = side > 0 ? Math.min(ext, l) - T : Math.max(ext, h) + T;
          else if (P.stopMode === 'swing') {
            const pv = side > 0 ? pivL.filter(x => x.p < lvl) : pivH.filter(x => x.p > lvl);
            const pvp = pv.length ? pv[pv.length - 1].p : ext;
            sx = side > 0 ? Math.min(ext, l, pvp) - P.bufT * T : Math.max(ext, h, pvp) + P.bufT * T;
          } else sx = side > 0 ? l - T : h + T;
          const r = Math.max(Math.abs(lvl + side * T - sx), P.minStop * T); if (r > P.maxStop * T) continue;
          const q = sizeQ(P, r, PV); if (q < 1) continue;
          const eEst = lvl + side * T; const pd = { side, lvl, stp: eEst - side * r, r, q, setup: cd[0] };
          if (P.tgtMode === 'levels') {
            const prevExt = side > 0 ? maxN : minN;                       // the swing extreme the pullback came from
            if (P.minRoomR && (!isFinite(prevExt) || (prevExt - eEst) * side < P.minRoomR * r)) continue;
            let t1 = prevExt; if (!isFinite(t1) || (t1 - eEst) * side < 0.5 * r) t1 = eEst + side * P.tp1R * r;
            const mm = eEst + side * Math.abs((side > 0 ? maxN : minN) - ext);   // measured move of the last leg
            const dayLvl = side > 0 ? pdh : pdl;
            let t2 = side > 0 ? Math.max(mm, dayLvl !== null && dayLvl > t1 ? dayLvl : -Infinity) : Math.min(mm, dayLvl !== null && dayLvl < t1 ? dayLvl : Infinity);
            if (!isFinite(t2) || (t2 - t1) * side <= 0) t2 = t1 + side * r;
            pd.tp1 = t1; pd.tgt = t2;
          }
          pend = pd; break;
        }
      }
      if (pos) { const bl = b[b.length - 1]; const s = pos.side; pos.pnl += (bl[4] - pos.eP) * s * pos.rem * PV - C * pos.rem * 2; res.push({ side: s, eI: pos.eI, eP: pos.eP, xI: b.length - 1, xP: bl[4], q: pos.q, pnl: pos.pnl, why: 'close', hold: (b.length - 1 - pos.eI) * BAR, setup: pos.setup }); }
      pdh = Math.max(...b.map(x => x[2])); pdl = Math.min(...b.map(x => x[3]));
    }
    return out;
  }

  // ---------- ORB retest V2 (Jey's corrected rules) ----------
  // - Range = 9:30 + orMin. While price is inside the range: no breakout trades.
  // - Breakout = a 5m (or 15m) candle CLOSES outside. Each new close-out re-arms that side (no day cancel).
  // - Entry: price comes back to retest the broken edge, then a HIGH-PROBABILITY signal bar (bullish close
  //   in top part, real body) -> buy stop 1 tick above it (shorts mirror).
  // - Big range (width >= bigPts points): also fade the edges inside the range (buy a bullish signal bar
  //   near the low, sell a bearish one near the high).
  // - Structure stop: beyond the lowest low of the pullback (the wick where liquidity sits) and beyond the
  //   key level (range edge for retests, range low/high for fades), plus a buffer; min/max size.
  // - No fixed trade count: every valid signal until lastEntry, daily loss / profit stops only.
  function simRT2(days, P, mk) {
    P = Object.assign({ orMin: 15, brk: '5m', bigPts: 0, fade: true, fadeZone: 0.2, stop: 'structure', bufT: 4, minStop: 16, maxStopPts: 0,
      sigFrac: 0.5, minBody: 0.3, tgtR: 2, risk: 300, maxQty: 20, lastEntry: 1300, maxTrades: 6, dayStop: 550, dayTarget: 600, comm: 2.37, slip: 1, tol: 0 }, P);
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip;
    for (const { d, b } of days) {
      const res = []; out.set(d, res);
      if (b.length < 20 || b[0][0] !== 930) continue;
      const { n, hi, lo } = orRange(b, P.orMin); const w = hi - lo, mid = (hi + lo) / 2, big = P.bigPts > 0 && w >= P.bigPts;
      const tol = (P.tol || 0) * T;
      let dir = 0, rtExt = null, sawRetest = false, pend = null, pos = null, dayPnl = 0, trades = 0, fadeLow = null, fadeHigh = null;
      for (let i = n; i < b.length; i++) {
        const [tm, o, h, l, c] = b[i];
        if (pend && !pos) {
          const p = pend; pend = null;
          if (tm <= P.lastEntry && (p.side > 0 ? h >= p.lvl : l <= p.lvl)) {
            const eP = (p.side > 0 ? Math.max(o, p.lvl) : Math.min(o, p.lvl)) + p.side * S * T;
            const r = Math.abs(eP - p.stp);
            if (p.side > 0 ? l <= p.stp : h >= p.stp) { const t = mkTrade(p.side, i, eP, i, p.stp - p.side * S * T, p.q, PV, C, 'stop'); t.setup = p.setup; res.push(t); dayPnl += t.pnl; trades++; }
            else { const plan = exitPlan(P, p.side, eP, p.stp, p.q, P.tgtR, P.lvlTgt ? levelsFor(days, d, b, i) : null); if (plan) { pos = Object.assign(plan, { eI: i, setup: p.setup }); trades++; } }
          }
        }
        if (pos) {
          const t = manageX(pos, b, i, T, S, PV, C);
          if (t) { t.setup = pos.setup; res.push(t); dayPnl += t.pnl; pos = null; sawRetest = false; rtExt = null; }
          continue;
        }
        if (tm >= FLAT || tm > P.lastEntry) continue;
        const done = trades >= P.maxTrades || (P.dayStop && dayPnl <= -P.dayStop) || (P.dayTarget && dayPnl >= P.dayTarget);
        if (done) continue;
        const m = tm % 100; const span = P.brk === '15m' ? 15 : 5; const closesSpan = ((m + BAR) % span) === 0;
        const rg = h - l;
        const bull = c > o && rg > 0 && (c - l) >= P.sigFrac * rg && Math.abs(c - o) >= P.minBody * rg;
        const bear = c < o && rg > 0 && (h - c) >= P.sigFrac * rg && Math.abs(c - o) >= P.minBody * rg;
        const inside = c <= hi && c >= lo;
        // breakout state: a close outside arms that side; a close back inside disarms (wait, don't cancel the day)
        if (closesSpan && c > hi) { if (dir !== 1) { dir = 1; sawRetest = false; rtExt = null; } }
        else if (closesSpan && c < lo) { if (dir !== -1) { dir = -1; sawRetest = false; rtExt = null; } }
        if (inside && dir !== 0) { dir = 0; sawRetest = false; rtExt = null; }
        const mkStop = (side, ext, key) => {
          let s;
          if (P.stop === 'pts') s = (side > 0 ? h + T : l - T) - side * P.stopPts;
          else if (P.stop === 'opp') s = side > 0 ? lo - T : hi + T;
          else if (P.stop === 'mid') s = side > 0 ? Math.min(mid, ext) - T : Math.max(mid, ext) + T;
          else if (P.stop === 'signal') s = side > 0 ? l - T : h + T;
          else s = side > 0 ? Math.min(ext, key) - P.bufT * T : Math.max(ext, key) + P.bufT * T; // structure
          return s;
        };
        const place = (side, ext, key, setup) => {
          if (P.trendF && !trendOK(emaArr(days, 21).get(d), b, i + 1 < b.length ? i + 1 : i, side)) return false;
          if (P.maxExt && stretch(emaArr(days, 21).get(d), b, i + 1 < b.length ? i + 1 : i, side) > P.maxExt) return false;
          if (P.minRoomPts) { const lv = levelsFor(days, d, b, i + 1 < b.length ? i + 1 : i, 1, 1).slice(-2); const pdx = side > 0 ? lv[0] : lv[1]; /* prior day high (long) / low (short) */
            const ent = side > 0 ? h : l; if (pdx !== undefined && (pdx - ent) * side > 0 && (pdx - ent) * side < P.minRoomPts) return false; }
          const lvl = side > 0 ? h + T : l - T; let stp = mkStop(side, ext, key);
          let r = Math.abs(lvl + side * S * T - stp); if (r < P.minStop * T) { r = P.minStop * T; stp = lvl + side * S * T - side * r; }
          if (P.maxStopPts && r > P.maxStopPts) return false;
          const q = sizeQ(P, r, PV); if (q < 1) return false;
          pend = { side, lvl, stp: Math.round(stp / T) * T, q, setup }; return true;
        };
        // 1) breakout retest (outside the range)
        if (dir !== 0) {
          const edge = dir > 0 ? hi : lo;
          const touch = dir > 0 ? l <= edge + tol + 0 * T : h >= edge - tol;
          if (touch) { sawRetest = true; rtExt = rtExt === null ? (dir > 0 ? l : h) : (dir > 0 ? Math.min(rtExt, l) : Math.max(rtExt, h)); }
          if (sawRetest && !inside && (dir > 0 ? bull : bear)) { if (place(dir, rtExt, edge, 'retest')) continue; }
          continue;
        }
        // 2) big range: fade the edges from inside
        if (big && P.fade && inside) {
          const zone = P.fadeZone * w;
          if (l <= lo + zone) fadeLow = fadeLow === null ? l : Math.min(fadeLow, l);
          if (h >= hi - zone) fadeHigh = fadeHigh === null ? h : Math.max(fadeHigh, h);
          if (fadeLow !== null && bull && c > lo && l <= lo + zone * 1.5) { if (place(1, fadeLow, lo, 'fade')) { fadeLow = null; continue; } }
          if (fadeHigh !== null && bear && c < hi && h >= hi - zone * 1.5) { if (place(-1, fadeHigh, hi, 'fade')) { fadeHigh = null; continue; } }
        }
      }
      if (pos) { const bl = b[b.length - 1]; const t = mkTrade(pos.side, pos.eI, pos.eP, b.length - 1, bl[4], pos.q, PV, C, 'close'); t.setup = pos.setup; res.push(t); }
    }
    return out;
  }


  // ---------- Key-level scalper (Jey, 2026-10-21) ----------
  // Levels: 3-bar swing highs/lows of the prior 3 days + today (confirmed), prior day high/low.
  // Setup: after sessStart, a 5m candle CLOSES through a level with momentum (strong body, bigger than average range),
  // in the trend direction (EMA rising/falling and price on the right side).
  // entry 'break': stop order 1 tick beyond the break candle (next bar only).
  // entry 'retest': wait for price to come back to the broken level and hold it, then a signal candle; stop order beyond it.
  // Stop: beyond the key level (or the retest wick) + buffer. Target: next level ahead; skip if room < minRoomR x risk.
  const REJ = { stop: 0, nolevel: 0, room: 0, ok: 0 };
  function simKL(days, P, mk) {
    REJ.stop = REJ.nolevel = REJ.room = REJ.ok = 0;
    P = Object.assign({ entry: 'retest', sessStart: 1000, lastEntry: 1500, emaLen: 21, slopeBars: 3, trend: true, momBody: 0.5, momRange: 1.0,
      pivN: 6, back: 3, bufPts: 2, stopMode: 'level', minStop: 3, maxStop: 40, needLevel: true, minRoomR: 1.5, lvlGap: 4, tgtR: 2, armBars: 12,
      sigFrac: 0.5, minBody: 0.3, risk: 300, maxQty: 20, maxTrades: 5, dayStop: 550, dayTarget: 600, comm: 2.37, slip: 1 }, P);
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip;
    const k = 2 / (P.emaLen + 1); let ema = null; const eh = []; const rh = [];
    for (const { d, b } of days) {
      const res = []; out.set(d, res);
      let pend = null, pos = null, trades = 0, dayPnl = 0; let armed = []; // {side, lvl, i, ext}
      for (let i = 0; i < b.length; i++) {
        const [tm, o, h, l, c] = b[i];
        ema = ema === null ? c : ema + k * (c - ema); eh.push(ema); rh.push(h - l);
        const avgR = rh.length > 20 ? rh.slice(-21, -1).reduce((a, z) => a + z, 0) / 20 : h - l;
        if (pend && !pos) {
          const p = pend; pend = null;
          if (p.side > 0 ? h >= p.lvl : l <= p.lvl) {
            const eP = (p.side > 0 ? Math.max(o, p.lvl) : Math.min(o, p.lvl)) + p.side * S * T;
            if (p.side > 0 ? l <= p.stp : h >= p.stp) { const t = mkTrade(p.side, i, eP, i, p.stp - p.side * S * T, p.q, PV, C, 'stop'); t.setup = p.setup; t.info = p.info; res.push(t); dayPnl += t.pnl; trades++; }
            else { pos = { side: p.side, eI: i, eP, stp: p.stp, q: p.q, r: Math.abs(eP - p.stp), tp1: null, q1: 0, tgt: p.tgt, be: false, trailN: 0, trailTrig: 1, exitPB: 0, exhaust: false, addR: 0, maxQ: P.maxQty, setup: p.setup, info: p.info }; trades++; }
          }
        }
        if (pos) {
          const t = manageX(pos, b, i, T, S, PV, C);
          if (t) { t.setup = pos.setup; t.info = pos.info; res.push(t); dayPnl += t.pnl; pos = null; }
          continue;
        }
        if (tm < P.sessStart || tm > P.lastEntry || tm >= FLAT || i < 1) continue;
        if (trades >= P.maxTrades || (P.dayStop && dayPnl <= -P.dayStop) || (P.dayTarget && dayPnl >= P.dayTarget)) continue;
        const n = eh.length - 1;
        const up = !P.trend || (eh[n] > eh[n - P.slopeBars] && c > eh[n]);
        const dn = !P.trend || (eh[n] < eh[n - P.slopeBars] && c < eh[n]);
        const lv = levelsFor(days, d, b, i, P.pivN, P.back);
        const pc = b[i - 1][4], rg = h - l, body = Math.abs(c - o);
        const mom = rg > 0 && body >= P.momBody * rg && rg >= P.momRange * avgR;
        // breaks of levels on this bar's close
        const brUp = lv.filter(x => pc <= x && c > x), brDn = lv.filter(x => pc >= x && c < x);
        const place = (side, lvlKey, ext, setup) => {
          const e = side > 0 ? h + T : l - T, eE = e + side * S * T;
          const buf = P.bufATR ? P.bufATR * avgR : P.bufPts, mxS = P.maxStopATR ? P.maxStopATR * avgR : P.maxStop;
          let stp = P.stopMode === 'bar' ? (side > 0 ? l - T : h + T) : (side > 0 ? Math.min(lvlKey, ext) - buf : Math.max(lvlKey, ext) + buf);
          let r = Math.abs(eE - stp); if (r < P.minStop) { r = P.minStop; stp = eE - side * r; } if (r > mxS) { REJ.stop++; return false; }
          const ahead = lv.filter(x => (x - eE) * side >= P.lvlGap).sort((a, z) => (a - z) * side);
          const room = ahead.length ? Math.abs(ahead[0] - eE) : null;
          if (room === null && P.needLevel) { REJ.nolevel++; return false; }
          if (room !== null && room < P.minRoomR * r) { REJ.room++; return false; }
          REJ.ok++;
          const tgt = room !== null ? ahead[0] - side * T : eE + side * P.tgtR * r;
          const q = sizeQ(P, r, PV); if (q < 1) return false;
          pend = { side, lvl: e, stp: Math.round(stp / T) * T, tgt, q, setup, info: { key: lvlKey, r, room, tm, mom: +(rg / avgR).toFixed(2), ext: +((c - eh[n]) * side).toFixed(1) } };
          return true;
        };
        if (P.entry === 'break') {
          if (mom && c > o && up && brUp.length) { place(1, Math.max(...brUp), l, 'break'); continue; }
          if (mom && c < o && dn && brDn.length) { place(-1, Math.min(...brDn), h, 'break'); continue; }
        } else {
          // arm on momentum breaks
          if (mom && c > o && brUp.length) armed.push({ side: 1, lvl: Math.max(...brUp), i, ext: null, seen: false });
          if (mom && c < o && brDn.length) armed.push({ side: -1, lvl: Math.min(...brDn), i, ext: null, seen: false });
          armed = armed.filter(a => i - a.i <= P.armBars && (a.side > 0 ? c >= a.lvl - P.bufPts : c <= a.lvl + P.bufPts));
          const sigU = rg > 0 && c > o && (c - l) >= P.sigFrac * rg && body >= P.minBody * rg;
          const sigD = rg > 0 && c < o && (h - c) >= P.sigFrac * rg && body >= P.minBody * rg;
          for (const a of armed) {
            if (a.i === i) continue;
            const touch = a.side > 0 ? l <= a.lvl + P.lvlGap / 2 : h >= a.lvl - P.lvlGap / 2;
            if (touch) { a.seen = true; a.ext = a.ext === null ? (a.side > 0 ? l : h) : (a.side > 0 ? Math.min(a.ext, l) : Math.max(a.ext, h)); }
            if (a.seen && (a.side > 0 ? (sigU && up && c > a.lvl) : (sigD && dn && c < a.lvl))) {
              if (place(a.side, a.lvl, a.ext, 'retest')) { armed = armed.filter(x => x !== a); break; }
            }
          }
        }
      }
      if (pos) { const bl = b[b.length - 1]; const t = mkTrade(pos.side, pos.eI, pos.eP, b.length - 1, bl[4], pos.q, PV, C, 'close'); t.setup = pos.setup; t.info = pos.info; res.push(t); }
    }
    return out;
  }


  // ---------- Failed breakout (Wade setup #3): poke through a key level, signal bar closes back, trade the failure ----------
  // levels: prior day high/low, today's opening range (first orMin) high/low, confirmed swing highs/lows (pivN) of today and prior `back` days.
  function simFB(days, P, mk) {
    P = Object.assign({ sessStart: 1000, lastEntry: 1500, pokeMin: 2, pokeMax: 60, within: 3, pivN: 6, back: 2, useOR: true, orMin: 15, usePD: true, useSw: true,
      sigFrac: 0.5, minBody: 0.3, stopMode: 'poke', bufPts: 2, minStop: 4, maxStop: 60, tgtMode: 'r', tgtR: 1.5, tp1R: 0, tp1Pct: 50, beOn: false,
      risk: 300, maxQty: 20, maxTrades: 4, dayStop: 0, dayTarget: 0, comm: 2.37, slip: 1, emaLen: 21 }, P);
    const out = new Map(), T = mk.tick, PV = mk.pv, C = P.comm, S = P.slip; const em = emaArr(days, P.emaLen);
    for (let k = 0; k < days.length; k++) {
      const { d, b } = days[k]; const res = []; out.set(d, res); if (b.length < 20 || b[0][0] !== 930) continue;
      const e = em.get(d); let pend = null, pos = null, trades = 0, dayPnl = 0; const used = new Set();
      const L = []; // [price, kind]
      if (P.usePD && k > 0) { const pb = days[k - 1].b; L.push([Math.max(...pb.map(x => x[2])), 'pdh'], [Math.min(...pb.map(x => x[3])), 'pdl']); }
      if (P.useSw) for (let m = Math.max(0, k - P.back); m < k; m++) { const bb = days[m].b; for (const v of piv(bb, 0, bb.length - 1, P.pivN)) L.push([v, 'sw']); }
      let orHi = null, orLo = null; const nOR = Math.max(1, Math.round(P.orMin / BAR));
      for (let i = 0; i < b.length; i++) {
        const [tm, o, h, l, c] = b[i];
        if (P.useOR && i === nOR - 1) { const r = orRange(b, P.orMin); orHi = r.hi; orLo = r.lo; L.push([orHi, 'orh'], [orLo, 'orl']); }
        if (P.useSw && i >= 2 * P.pivN) { const j = i - P.pivN; let ph = true, pl = true; for (let q = 1; q <= P.pivN; q++) { if (!(b[j][2] > b[j - q][2] && b[j][2] > b[j + q][2])) ph = false; if (!(b[j][3] < b[j - q][3] && b[j][3] < b[j + q][3])) pl = false; } if (ph) L.push([b[j][2], 'sw']); if (pl) L.push([b[j][3], 'sw']); }
        if (pend && !pos) { const p = pend; pend = null;
          if (p.side > 0 ? h >= p.lvl : l <= p.lvl) { const eP = (p.side > 0 ? Math.max(o, p.lvl) : Math.min(o, p.lvl)) + p.side * S * T;
            if (p.side > 0 ? l <= p.stp : h >= p.stp) { const t = mkTrade(p.side, i, eP, i, p.stp - p.side * S * T, p.q, PV, C, 'stop'); t.setup = p.setup; res.push(t); dayPnl += t.pnl; trades++; }
            else { const pl = exitPlan(P, p.side, eP, p.stp, p.q, P.tgtR); if (p.tgt !== undefined) pl.tgt = p.tgt; pos = Object.assign(pl, { eI: i, setup: p.setup }); trades++; } } }
        if (pos) { const t = manageX(pos, b, i, T, S, PV, C); if (t) { t.setup = pos.setup; res.push(t); dayPnl += t.pnl; pos = null; } continue; }
        if (tm < P.sessStart || tm > P.lastEntry || tm >= FLAT || i < 1) continue;
        if (trades >= P.maxTrades || (P.dayStop && dayPnl <= -P.dayStop) || (P.dayTarget && dayPnl >= P.dayTarget)) continue;
        const rg = h - l, body = Math.abs(c - o);
        const bull = rg > 0 && c > o && (c - l) >= P.sigFrac * rg && body >= P.minBody * rg;
        const bear = rg > 0 && c < o && (h - c) >= P.sigFrac * rg && body >= P.minBody * rg;
        // look for a level poked within the last `within` bars (incl. this one) and now closed back through
        for (const [lv, kind] of L) {
          const key = lv + ':' + kind; if (used.has(key)) continue;
          // failed break UP of resistance -> short
          if (bear && c < lv) { let pk = -Infinity; for (let q = Math.max(0, i - P.within + 1); q <= i; q++) pk = Math.max(pk, b[q][2]);
            const poke = pk - lv; if (poke >= P.pokeMin && poke <= P.pokeMax && b[i - 1][4] <= lv + P.pokeMax) {
              const lvl = l - T, eE = lvl - S * T; let stp = P.stopMode === 'bar' ? h + T : pk + P.bufPts; let r = stp - eE; if (r < P.minStop) { r = P.minStop; stp = eE + r; } if (r > P.maxStop) { used.add(key); continue; }
              const q = sizeQ(P, r, PV); if (q < 1) { used.add(key); continue; }
              const pd = { side: -1, lvl, stp: Math.round(stp / T) * T, q, setup: 'fail-' + kind }; if (P.tgtMode === 'ema') pd.tgt = e[i]; pend = pd; used.add(key); break; } }
          if (bull && c > lv) { let pk = Infinity; for (let q = Math.max(0, i - P.within + 1); q <= i; q++) pk = Math.min(pk, b[q][3]);
            const poke = lv - pk; if (poke >= P.pokeMin && poke <= P.pokeMax && b[i - 1][4] >= lv - P.pokeMax) {
              const lvl = h + T, eE = lvl + S * T; let stp = P.stopMode === 'bar' ? l - T : pk - P.bufPts; let r = eE - stp; if (r < P.minStop) { r = P.minStop; stp = eE - r; } if (r > P.maxStop) { used.add(key); continue; }
              const q = sizeQ(P, r, PV); if (q < 1) { used.add(key); continue; }
              const pd = { side: 1, lvl, stp: Math.round(stp / T) * T, q, setup: 'fail-' + kind }; if (P.tgtMode === 'ema') pd.tgt = e[i]; pend = pd; used.add(key); break; } }
        }
      }
      if (pos) { const bl = b[b.length - 1]; const t = mkTrade(pos.side, pos.eI, pos.eP, b.length - 1, bl[4], pos.q, PV, C, 'close'); t.setup = pos.setup; res.push(t); }
    }
    return out;
  }

  // ---------- Eval simulator ----------
  function evals(dayList, dt, F) {
    const out = []; const N = F.evDays;
    for (let k = 0; k + N <= dayList.length; k++) {
      let eq = 0, peak = 0, thr = -F.mll, best = 0, res = 0, used = 0;
      for (let j = 0; j < N; j++) {
        const tl = dt.get(dayList[k + j]) || []; let dp = 0;
        for (const t of tl) {
          const p = typeof t === 'number' ? t : t.pnl;
          if (F.dll && dp <= -F.dll) break;
          if (F.cap && dp >= F.cap) break;
          eq += p; dp += p;
          if (eq <= thr) { res = -1; break; }
          if (eq >= F.target && (!F.consist || Math.max(best, dp) <= F.consist / 100 * eq)) { res = 1; break; }
        }
        used = j + 1; if (res) break;
        best = Math.max(best, dp); peak = Math.max(peak, eq); thr = Math.min(peak - F.mll, 100);
      }
      out.push({ start: dayList[k], res, days: used, eq });
    }
    return out;
  }
  function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function pnlOf(t) { return typeof t === 'number' ? t : t.pnl; }
  function randomBaseline(dayList, dt, F, runs = 6) {
    const all = []; dayList.forEach(d => (dt.get(d) || []).forEach(t => all.push(pnlOf(t))));
    if (!all.length) return { p: 0, f: 0, o: 1 };
    const mean = all.reduce((a, b) => a + b, 0) / all.length; const pool = all.map(x => x - mean);
    let P = 0, Fa = 0, n = 0;
    for (let s = 1; s <= runs; s++) {
      const R = rng(s * 7919); const fake = new Map();
      dayList.forEach(d => { const c = (dt.get(d) || []).length; const a = []; for (let i = 0; i < c; i++) a.push(pool[Math.floor(R() * pool.length)]); fake.set(d, a); });
      evals(dayList, fake, F).forEach(e => { n++; if (e.res === 1) P++; else if (e.res === -1) Fa++; });
    }
    return { p: P / n, f: Fa / n, o: 1 - (P + Fa) / n };
  }
  function summarize(ev) {
    const n = ev.length || 1; const p = ev.filter(e => e.res === 1), f = ev.filter(e => e.res === -1);
    return { n: ev.length, p: p.length / n, f: f.length / n, o: 1 - (p.length + f.length) / n, pd: p.map(e => e.days).sort((a, b) => a - b) };
  }
  function parseBars(text) {
    const days = [];
    for (const line of text.split('\n')) {
      if (!line) continue; const parts = line.split('|'); const b = [];
      for (let i = 1; i < parts.length; i++) { const a = parts[i].split(','); b.push([+a[0], a[1] / 4, a[2] / 4, a[3] / 4, a[4] / 4]); }
      days.push({ d: +parts[0], b });
    }
    return days;
  }
  function setMaxHold(m) { MAXHOLD = +m || 0; }
  function setBar(m) { BAR = +m || 5; }
  const E = { simFB, emaArr, trendOK, stretch, avgRange, REJ, setMaxHold, setBar, simKL, simW2E, simRT2, simORB, simPB, simRT, evals, randomBaseline, summarize, parseBars, orRange, pnlOf };
  if (typeof module !== 'undefined' && module.exports) module.exports = E; else root.Engine = E;
})(typeof window !== 'undefined' ? window : globalThis);
