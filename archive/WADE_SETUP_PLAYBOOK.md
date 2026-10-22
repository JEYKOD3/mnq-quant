# Wade Setup Playbook (MNQ scalping)

Source: Thomas Wade videos. The images in this folder are frames from them.
- "The ONLY Price Action Setup Traders NEED To Know" (youtube.com/watch?v=GrRbOItgLgc), images 01-09
- "Learn To Day Trade With Price Action" (2gfaQ9I5Fbc), images 10-12
- "Learn Price Action Trading LIVE" (vZ0Ke1FFH88), images 13-14
- "Reading Price Chart As A Scalper Trader" (eb65JNY4JZs), images 15-16

Our rule: **we hunt setups.** No setup on the chart = no trade. Get in, take the scalp, get out, wait for the next one.

---

## 1. The one setup: second entry at a key entry point (images 01, 09)

First entries are not reliable because the market may still be correcting. The high-probability trade is the **second entry**, taken **with the trend**, at a **key entry point**.

**Key entry points:**
1. Trendline
2. EMA 21
3. Support / resistance key level (prior high/low, breakout level, opening range edge)

**Checklist before every trade (image 09). All 4 must be true:**
1. The correction (pullback) has played out: two legs.
2. To buy: the signal bar is bullish (green, closes near its high).
3. To sell: the signal bar is bearish (red, closes near its low).
4. The second entry forms at a key entry point.

## 2. How to count legs (images 02, 03, 04)

- A series of bullish bars (or one bullish bar) = a bullish leg. Same for bearish.
- In a downtrend, the market pulls back UP in two legs:
  - Leg I up, then a bar breaks lower = **1st entry short (1ES)**. Don't take it.
  - Leg II up, then a bar breaks lower = **2nd entry short (2ES)**. This is the safe place to sell, especially at the EMA or the trendline.
- In an uptrend it's the mirror: 1EL then **2EL** (2nd entry long) at the EMA / trendline (images 05, 06, 08).
- Restart the count after a new extreme (new low in a downtrend, new high in an uptrend).

## 3. Entry, stop, target (image 08)

- **Entry:** stop order 1 tick beyond the signal bar (above it for longs, below for shorts). If it doesn't trigger on the next bar, cancel.
- **Stop:** 1 tick beyond the signal bar or the pullback extreme (image 08 shows the stop under the 2EL low).
- **Goal (image 07):** "predict a small market move for a scalp". Take the quick move, don't marry the trade.

## 4. Trendline rule and context (images 10, 11, 13, 16)

- Draw the trendline of the current leg. While it holds, the move continues; trade 2nd entries in its direction.
- A **trendline break** after a new high/low warns the move is ending. Stop taking with-trend entries and wait for the next structure.
- **Overshoot** (image 13, 15): price pushes beyond the channel line then reverses. Often marks the end of the move.
- New high / new low labels mark where to restart the leg count.

## 5. Other setups seen live

- **Failed 2nd entry (F2ES / F2EL), image 12:** a 2nd entry against the trend that fails and reverses. Trade in the trend direction once it fails.
- **Breakout pullback (BP), image 14:** a level breaks, price comes back to test it, then continues. Enter on the 2nd entry at the retest. This is the same idea as our ORB retest.
- **Lower high (LH) / higher low (HL), images 14, 15:** after a trend break, the first pullback that fails to make a new extreme. Sell the LH / buy the HL with a strong signal bar.
- **Congestion / range (image 16):** many overlapping bars, new highs and lows that go nowhere. Avoid, or wait for a clean breakout pullback.
- **Not every 2nd entry is equal:** weak signal bar, no key point, or against the trendline = skip.

## 6. Risk management (for prop evals)

Per trade:
- Fixed dollar risk per trade. Lucid Flex 25K: $150 to $300. Size = risk / (stop distance x $2 per point per micro), max 20 micros.
- Skip the trade if the stop needed is too wide for your risk (fewer than 1 contract) or tighter than 8 ticks (noise).
- **TP1 + runner:** take half (or a third) at 1R, move the stop to breakeven, let the runner go to the next key level or 2R to 3R.
- **Time stop:** if the scalp hasn't worked in about 30 minutes, close it.

Per day:
- Max 3 to 4 trades. Stop after 2 losses in a row.
- Daily loss stop: about 2R (for example -$550 on Flex 25K, below the $600 daily limit).
- Daily profit stop: about half the eval target ($600 on 25K) to respect the 50% consistency rule.
- No trades in congestion, right before red-folder news, or after 15:30 ET.
- Remember the trailing max loss ($1,000 on 25K) moves up with your best end-of-day balance.

## 7. How to use this folder

1. Before testing, re-read sections 1 to 3 and look at images 01, 04, 06, 08.
2. Scroll a past MNQ 5-minute day (TradingView replay or the Eval Lab chart). Mark every place where all 4 checklist items are true.
3. Screenshot about 10 of your own marked setups with entry, stop, TP1 and runner. Send them to Claude: they become the exact rules of the setup hunter.
4. Only then backtest, and judge it with the Testing Guide (pass/fail vs random, every year, MNQ and MES).

Note: our 5-year tests so far found tight-stop scalps on MNQ lost money when entries were taken mechanically everywhere. The point of this playbook is to only trade the clean, checklist-passing setups, which is what we test next.
