# TradingView setup: Playbook v6 on two charts (Oct 25, 2026)

## Why two charts, one engine
- **One engine on every chart:** each chart runs the same script, which calculates all six strategies (NEWS, V4+, D2, TDP, Pinball, H2) and the shared $1,100 budget.
- **Display only:** the "Show on this chart" setting decides which strategies draw markers and send alerts on that chart.
- **Consistent numbers:** contract sizes and "budget left" are the same on both charts. The panel's "Open (all charts)" line lists every open trade, so you always know what is already at risk.
- **Keep strategies on:** leave all six switched on in the Strategies group on both charts. Switching one off removes it from the budget on that chart, and the two charts would then disagree.

## Charts
| Chart | Setting | Shows | When to watch |
|---|---|---|---|
| Chart 1: Open & News | "Chart 1: Open & News" | NEWS, V4+, D2, 8:29 price line | 8:25-13:00 ET |
| Chart 2: Trend & Swing | "Chart 2: Trend & Swing" | TDP (armed tag + dashed limit line), H2, Pinball | 10:30-15:55 ET |

## Both charts
- **Symbol and timeframe:** MNQ1!, 1 minute.
- **Extended hours ON:** needed for NEWS and the 8:29 price.
- **Script:** MNQ Playbook v6, plus the EMA it draws.
- **News markers on both:** release lines, ⚡ spikes, and the news row in the panel.

## Reading the chart
- **Entry tag:** for example "V4+ ▲ 4" means V4+, long, 4 MNQ.
  - A faded tag means 0 contracts: the budget is full, so skip that signal.
  - Hover the tag for the reason, entry, stop, target, size, risk and budget left.
- **Zones:**
  - Green box from entry to target, red box from entry to stop.
  - They grow while the trade is open and stop at the exit.
  - D2 and Pinball have no target, so they show only the red stop zone.
- **Exit tag:** "✓ +137" or "✗ -99" in points. Hover it for the reason and the dollar result.
- **Breakeven:** "BE" when V4+ moves its stop to breakeven.
- **TDP:** "TDP armed" at 10:30 on trend days, then a dashed line where the limit order waits until 12:00.
- **News:**
  - A red dotted vertical line with the event name at release time.
  - A yellow dotted "8:29 price" line on CPI, PPI and NFP days.
  - ⚡ marks an unexpected spike. It's information only: hold to plan.
- **Panel (top right):** context, budget in use and left, open trades on all charts, today's P&L, setups for this chart, news today and the next event, and the last spike.
- **Calendar:** the Economic calendar input lists dates through Dec 2026, checked against the BLS schedule. Add new dates in the same format.

## Alerts (one set per chart)
- **How:** on each chart, Alerts > Create > Condition: MNQ Playbook v6 > "Any alert() function call" > Once per bar.
- **What fires:** Chart 1 alerts only for NEWS, V4+ and D2. Chart 2 alerts only for TDP, H2 and Pinball.

## Status Oct 25 2026, 19:50 (set up through the Claude browser)
- **Script:** MNQ Playbook v6 is saved (version 10), compiled with no errors, and on the MNQ1! 1m chart (extended hours on). Layout "MNQ 1m".
- **Check against Python:** Oct 20 D2 -148 (Python -148.2), Oct 22 V4+ +136.9 (+137.2), Oct 22 Pinball +194.8 (+194.5). TDP Oct 22 +259 has no Python match only because our 1m data ends Oct 20.
- **TradingView Basic plan limits:** 1 saved layout and 0 indicator alerts. So:
  - Show on this chart = "All strategies" on the one layout.
  - The Chart 1 / Chart 2 split works only with more layouts (Essential plan: 5 layouts, 20 alerts).
  - No alerts on Basic.
- **Chart settings changed:** inputs and labels removed from the status line and price scale, last trades table on, results table off.
