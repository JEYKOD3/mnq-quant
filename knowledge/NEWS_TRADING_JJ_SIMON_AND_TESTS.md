# Trading the news: JJ Simon's rules and what our tests say (Oct 25, 2026)

## What JJ Simon says (my summary from his podcast and his own channel)
**Where he gets the news**
- US red-folder releases on Forex Factory, mainly at 8:30 ET: CPI, PPI, NFP (jobs report), and similar.
- He checks the calendar before the session.

**Expected news (scheduled, result close to the forecast)**
- The price just before the release (the 8:29 candle body) is the fair price. The spike is "unfair" because the news was already priced in.
- He trades the first reversion back toward the 8:29 price on a displacement or break of structure. He calls it his highest win-rate trade and sizes up.
- The edge fades with volume, so he takes the first reversion only.
- If the 9:30 open drops straight back to the 8:29 price, he ignores the open and keeps the 8:29 price as fair.

**Big surprise**
- The latest consolidation becomes the new fair price.
- He takes a continuation trade during the first candle.

**Unexpected news (tweets, speeches)**
- The fair price moves to the first consolidation after the jump.
- He takes a "drift" trade: no target, very wide stop, exit when a 1-minute candle closes against the trend structure.

**Caution rules**
- Don't be in a trade at the 9:45 or 10:00 releases.
- Be careful around the 9:30 open (widen the stop or move it to breakeven).
- Stop trading before scheduled speeches. On Aug 28 he quit before a 10:00 AM speech.

## What our MNQ tests say (2022-2026)
- **8:30 news reversion (CPI, PPI, NFP), 8:30-9:30, 5m bars:**
  - Toward the 8:29 price on a displacement or break of structure, 50/50 bracket.
  - PF about 1.5, positive every year, about 13 trades a year. Kept as module NEWS.
  - Other 8:30 releases lose, and so do tight 25-pt stops.
- **His drift trade after unexpected spikes** (spike = a 1m bar of at least 4x the recent bars and at least 6% ADR, outside scheduled times):
  - Loses in every version (PF 0.35-0.94).
  - Fading the spike back to the pre-spike price is break-even (PF 0.76-1.23).
  - Not traded.
- **"Stay out during news" does not suit our strategies, which follow trends:**
  - Trades open while a spike happened did better: PF 2.2 vs 1.4-1.5.
  - CPI and PPI days were better than normal days.
  - So news is shown on the chart for awareness, and existing trades are held to plan.
- **FOMC (14:00):** samples are small (20 trades). Trades still open at 14:00 did fine.

## How it shows on the chart
- **Scheduled events:** a dotted vertical line with the event name at release time, plus the next event in the panel.
- **News days:** a dotted line at the 8:29 price from 8:30 to 10:30. NEWS signals appear on Chart 1.
- **Unexpected spikes:** a small ⚡ with a tooltip, logged in the panel. It's a reminder to hold to plan, not a trade.
