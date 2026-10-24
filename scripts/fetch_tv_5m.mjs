// Fetch recent MNQ1! 5m bars from TradingView (guest, delayed) in headless Chromium -> mnq5_tv.json. Run: NODE_PATH=/opt/npm-tools/node_modules node scripts/fetch_tv_5m.mjs
// Verified 2026-10-24: matches Databento MNQ.v.0 RTH 5m exactly (1326 bars, 0 diff).
import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--headless=new'] });
const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
await p.goto('https://www.tradingview.com/chart/?symbol=CME_MINI%3AMNQ1%21&interval=5', { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.waitForTimeout(15000);
const r = await p.evaluate(async () => {
  const w = window.TradingViewApi && window.TradingViewApi._activeChartWidgetWV && window.TradingViewApi._activeChartWidgetWV.value();
  if (!w) return { err: 'no api' };
  const ms = w._chartWidget.model().mainSeries();
  for (let k = 0; k < 6; k++) { try { ms.requestMoreData(2000); } catch (e) {} await new Promise(r => setTimeout(r, 3000)); }
  const bb = ms.bars(); const out = [];
  for (let i = bb.firstIndex(); i <= bb.lastIndex(); i++) { const v = bb.valueAt(i); if (v) out.push(v.slice(0, 5)); }
  return { sym: ms.symbol(), n: out.length, bars: out };
});
await p.screenshot({ path: 'tv.png' });
const fs = await import('fs'); fs.writeFileSync('mnq5_tv.json', JSON.stringify(r));
console.log(r.err || `${r.sym} ${r.n} bars ${new Date(r.bars[0][0]*1000).toISOString()} .. ${new Date(r.bars[r.n-1][0]*1000).toISOString()}`);
await b.close();
