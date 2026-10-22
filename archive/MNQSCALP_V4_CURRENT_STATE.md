# MNQSCALP — V4.0 Current State (supersedes handoff where they differ)

**Updated:** 2026-10-20 (rebuilt by Claude from the full ChatGPT share thread, Oct 17 → Oct 20 18:00)
**Read with:** `MNQSCALP_PROJECT_HANDOFF.md` (history, V2→V3.7.8, risk rules) and `claude/MNQSCALP_CHATGPT_TRANSCRIPT_FULL.md` (searchable full transcript; use project_search).
**Status:** MNQSCALP V4.0 in moomoo Engine, BACKTEST ONLY. Coordinated fix of entry locks + stop lifecycle was promised by ChatGPT at 12:21 but never delivered. That is the next deliverable.

## 1. Working rules from Jey (repeated in the thread)
- Clear, short, numbered steps. Big coordinated changes, no more tiny diagnostic cards.
- After every backtest: analyze BOTH Run Log CSV and Futures History CSV together, report only performance, failures, exact fix, next action.
- Never ask again for cards/code already captured here.
- Two disconnected canvas sections are INTENTIONAL and RESERVED for later. Never delete, reconnect, or treat them as active. The old `BUY 2 MNQ` card and `STOP PRICE VERIFICATION` are also disconnected but kept.
- Jey answers in English; sometimes writes in French ("speak english" was requested once when assistant drifted).

## 2. What changed after the handoff (chronological, Oct 20)
1. **Indicator `MNQSCALPV4`** = copy of MNQSCALPV3 with typo fixed (`NOT(ISLASTBAR)`) + V4 block appended (section 5). Compiled ("Indicator applied").
2. **Strategy `MNQSCALP V4.0 — Momentum Scalper`** = duplicate of V3.7.8. Entry condition card switched to indicator MNQSCALPV4, current bar (select=1), >0.5.
   - BUG STILL PRESENT: the condition reads `variable_name="LONG_ENTRY"`, NOT `V4_LONG_ENTRY`. So fast momentum entries (FAST_BULL_EVENT/SB_EVENT) are still not used. This is why the first V4 backtest = V3.7.8 exactly.
3. `REENTRY DIAGNOSTIC` replaced with V4 Re-entry Eligibility (sets `self.REENTRY_READY`, plus `self.V4_UNLOCK_CANDIDATE`). Unlocks nothing.
4. `TWO-CONTRACT STOP TEST` moved onto main monitoring path, code replaced by **V4 STRUCTURAL STOP MANAGER** (uses `self.v4_planned_stop`, cap 25 pts). Then moved to run FIRST after START.
5. Indicator output added: `V4_SWING_LOW:REF(LOW_LEVEL,1),NODRAW;`
6. New Coded Condition **LONG RISK CHECK** (after VWAP): reads V4_SWING_LOW, stop = swing_low - 2, passes if 0 < entry - stop <= 25; stores `self.v4_planned_stop`. Note fix: `params={}` (dict, not 0).
7. Built-in `BUY 2 MNQ` disconnected and replaced by Coded Operation **V4 ENTRY ORDER MANAGER** (place_limit at ask, stores order ID, status tracking).
8. Proposed but NOT applied: Step 20 addition to NEW SESSION RESET (clear `v4_entry_order_id` when terminal). Jey's 12:18 paste of NEW SESSION RESET does not contain it.

## 3. Backtest results Oct 20 (Sep 14 – Oct 16 2026, MNQ Dec 2026, 5m, $50k sim)
| Run | Trades | Net | Notes |
|---|---:|---:|---|
| V4.0 first (indicator swap only) | 24 | +$323.48 | Identical to V3.7.8; 58.3% win; fees $227.52; Oct 13 9:30 rally missed (first Oct 13 BUY 04:05 ET) |
| Stop manager on main path (100 pt) | 24 | +$323.48 | 24/24 stops submitted; 10 stop fills, 14 cancels; one stop slipped 12.75 pts (30,830 → 30,817.25) |
| + LONG RISK CHECK 25 pt (verification only) | 0 orders | n/a | Only 2 setups qualified: Sep 16 07:10 (24.5 pts, $98), Oct 7 01:30 (21.25 pts, $85) |
| + structural stop live | 2 | −$132.96 | Sep 16: 29,391 → stop 29,366.50 filled 29,363 (3.5 pt slip, −$121.48 net). Oct 7: −$11.48 |
| Stop manager moved first | 2 | −$132.96 | Stop still submitted 5 min after BUY fill |
| + V4 ENTRY ORDER MANAGER | 1 | −$121.48 | Oct 7 blocked: `v4_entry_order_id` never cleared |
| + unlock candidate code | 1 | −$121.48 | `V4 REENTRY UNLOCK CANDIDATE` never printed |

## 4. Known blockers (priority)
1. **5-minute protection gap.** Engine evaluates once per 5m bar; stop is placed on the next evaluation after the BUY fills. Reordering cards did not help. No Order-Filled/event card exists; BUY card has no bracket/attached SL option (types: Lmt, Mkt, Stop Mkt...). Live-trading blocker.
2. **Entry locks:** `TEST_ENTRY_USED` (reset only at session) and `v4_entry_order_id` (never cleared) both block re-entry. Must be released together, only when flat + entry order terminal + stop terminal + TP1/runner orders terminal + cooldown passed + trades < 5.
3. **Per-trade flags never reset:** `initial_stop_attempted`, `initial_stop_id`, `initial_stop_last_status`, `tp1_stop_mod_attempted`, `qty_mod_attempted` reset only in NEW SESSION RESET.
4. **Wrong indicator output** (`LONG_ENTRY` vs `V4_LONG_ENTRY`).
5. **25-pt cap too selective** (2 trades in 5 weeks). Stop-market slippage means planned $100 is not a max loss.
6. If fill exceeds cap, stop manager places NO stop (unprotected). Needs emergency flatten.
7. V4 ENTRY ORDER MANAGER status checks only run when entry conditions pass (not every evaluation).
8. TP1 stop modify: no verification after `modify_order`.

## 5. MNQSCALPV4 indicator additions (appended at bottom of V3 source)
```
{ V4 - CONFIRMED ENTRY CANDIDATES }
V4_CORE_LONG:=LI_SIG;
V4_CORE_SHORT:=SI_SIG;
V4_FAST_LONG:=FAST_BULL_EVENT OR SB_EVENT;
V4_FAST_SHORT:=FAST_BEAR_EVENT OR SL_EVENT;
V4_LONG_RAW:=(V4_CORE_LONG OR V4_FAST_LONG) AND ENTRY_OK;
V4_SHORT_RAW:=(V4_CORE_SHORT OR V4_FAST_SHORT) AND ENTRY_OK;
V4_LONG_ENTRY:IF(V4_LONG_RAW,1,0),NODRAW;
V4_SHORT_ENTRY:IF(V4_SHORT_RAW,1,0),NODRAW;
V4_MOMENTUM_LONG:IF(V4_FAST_LONG AND ENTRY_OK,1,0),NODRAW;
V4_MOMENTUM_SHORT:IF(V4_FAST_SHORT AND ENTRY_OK,1,0),NODRAW;
V4_SWING_LOW:REF(LOW_LEVEL,1),NODRAW;
```
Full MNQSCALPV3 source (Jey's paste, 2026-10-20 08:23) is in `claude/MNQSCALPV3_SOURCE_2026-10-20.md`.

## 6. Active V4.0 flow (confirmed from Jey's 12:18–12:21 paste + 3 screenshots)
```
START (Trigger_Symbol1, globals)
  -> V4 STRUCTURAL STOP MANAGER   (card named "TWO-CONTRACT STOP TEST")
  -> POSITION FILL MONITOR + TRADE COUNTER
  -> REENTRY DIAGNOSTIC (V4 Re-entry Eligibility + unlock candidate)
  -> TRADE DURATION MONITOR (Combined Trade Timer)
  -> NEW SESSION RESET
  -> timeout / session-exit management (TP1 timeout, 3h exit, cancel orders, 16:45 flatten)
  -> Holding Qty = 0 ?
       -> MAX 5 TRADES (TRADES_TODAY < 5)
       -> TEST_ENTRY_USED = 0
       -> MNQSCALPV4 LONG_ENTRY > 0.5  (select=1, current bar)   <-- should be V4_LONG_ENTRY
       -> VWAP LONG CONFIRMATION (select=2 bar close > builtin VWAP)
       -> LONG RISK CHECK (25 pt structural)
       -> V4 ENTRY ORDER MANAGER (place_limit BUY 2 at ask)
       -> SET TEST_ENTRY_USED = 1
  TP1 branch: Holding Qty>0 / P&L ratio -> close 50% -> TP1_EXIT_ATTEMPTED=1 -> STOP QUANTITY MODIFIER (TP1 Stop Coordination: modify initial_stop_id to qty 1 @ entry)
  Runner branch: Holding Qty=1 -> LONG RUNNER SAFETY -> LONG_TRAIL_SUBMITTED=0 -> ...
  Read-only: "V3.6 - Breakeven validation" (Holding Qty>0 -> Coded Operation -> P/L ratio < -0.0333%) places no orders.
```
Exact order of the session-exit sub-branch must be read from the canvas before editing.

## 7. moomoo Engine platform knowledge (verified in this project)
**Card types used:** Start (Trigger Symbol, Global Variables via Properties), Condition cards (Indicator: My Language / Python indicator; Account → Positions: Holding Qty, Cost, Position Profit or Loss Ratio, Position Amount of P/L, Unrealized P/L, Available QTY), Coded Condition (Python, must `return True/False`), Coded Operation (Python), Place Order (Lmt, Mkt, Stop Mkt…, Buy/Sell; quantity/trigger can be Manual, Condition Variable, Global Variable, Advanced Calculation), Cancel Order (`Cancel One` exposes symbol/side/remark; `Cancel All`; no order-ID selector), Value Assignment (Other menu; sets a global variable), Global Variable.
- Validation: a condition card cannot be the final card of a path (red error); disconnected cards give an orange warning only.
- Canvas search (Cmd+F) not confirmed to work; zoom ~125% to read cards.
- Per-card persistent state: `self.<attr>` with `hasattr` init. Globals declared in Start: `self.X = show_variable(0, GlobalType.INT)`.
- Python print output appears in the Run Log CSV (columns: date, time, ?, card, message).
- Futures History CSV columns include Side, Order Qty, Status, Order Time, Order Type, Trigger price, Filled, Fill Qty, Fill Price, Fill Time "(CT)", Commission, Exchange Fees, Total. Times in **Central Time**.
- Fees in sim: $2.37 per contract per side.

**Python API (signatures confirmed via inspect in Run Log, Oct 18–19):**
| Function | Signature |
|---|---|
| `position_holding_qty` | `(symbol)` |
| `position_cost` | `(symbol, cost_price_model='AVG', currency='USD')` |
| `position_price` | `(symbol)` |
| `current_price` | `(symbol, price_type='ALL')` |
| `place_stop` | `(symbol, aux_price, qty, side='BUY', time_in_force='DAY')` → order ID |
| `place_trailing_stop` | `(symbol, trail_type, trail_value, qty, side='BUY', time_in_force='DAY')` → order ID |
| `place_limit` | `(symbol=, price=, qty=, side=OrderSide.BUY, time_in_force=TimeInForce.DAY, order_trade_session_type=TSType.ETH)` → order ID |
| `modify_order` | `(orderid, qty, price=None, aux_price=None, trail_type=None, trail_value=None, trail_spread=None)` |
| `cancel_order_by_orderid` | `(orderid)` |
| `order_status` | `(orderid)` → status; normalize with `str(x).strip().upper().split(".")[-1]`. Seen: WAITING_SUBMIT, SUBMITTING, SUBMITTED, FILLED_ALL, CANCELLED_ALL, FAILED |
| `order_filled_qty` | `(orderid)` |
| `request_orderid` | `(symbol, status=[], start='', end='', time_zone='MARKET_TIME_ZONE')` → list |
| `ask` / `lot_size` | `ask(symbol=, level=1)`, `lot_size(symbol=)` |
| `bar_close` | `(symbol=, bar_type=BarType.K_5M, select=2, session_type=THType.ALL)` |
| `get_MyLang_indicator` | `(indicator_name=, variable_name=, symbol=, params={}, bar_type=BarType.K_5M, select=1, session_type=THType.ALL)` |
| `get_Python_indicator` | `(indicator_name="VWAP", variable_name="VWAP", symbol=, params=[], bar_type=..., select=2, session_type=...)` |
| `declare_trig_symbol` | `(is_trade_symbol=True)` |
Symbol: `Contract("US.MNQ2612")` or `self.Trigger_Symbol1`. `select=1` = current (incomplete) bar, `select=2` = last completed bar.

## 8. Next deliverable (agreed, not yet done)
One coordinated update of existing cards, then one backtest:
1. Entry condition → `V4_LONG_ENTRY`.
2. Single per-trade state machine: release `TEST_ENTRY_USED` and `v4_entry_order_id` together when flat + all tracked orders terminal + cooldown + trades < 5; reset all per-trade stop/TP1 flags at the same moment.
3. Entry manager status tracking must run every evaluation (move status part to main path).
4. Stop manager: if fill exceeds cap, flatten instead of leaving unprotected; handle qty 1 partials.
5. Revisit 25 pt cap vs selectivity.
6. Decide strategy for the 5-minute protection gap (e.g. submit protective stop in the same evaluation as the entry, sized to intended qty, or use a limit entry that fills only at a known price; or move execution to OpenD/moomoo API, which Jey has running locally).

---
# Appendix A — Active card code, verbatim (Jey's paste 2026-10-20 12:18)
Order: Start globals, STRUCTURAL STOP MANAGER, POSITION FILL MONITOR, REENTRY DIAGNOSTIC, TRADE DURATION MONITOR, NEW SESSION RESET, entry condition MNQSCALPV4.

```python
def trigger_symbols(self):  # Define the trigger symbol
    self.Trigger_Symbol1 = declare_trig_symbol(is_trade_symbol=True)

def global_variables(self):  # Define the global variables
    self.LONG_TRAIL_SUBMITTED = show_variable(0, GlobalType.INT)
    self.TEST_ENTRY_USED = show_variable(0, GlobalType.INT)
    self.TP1_EXIT_ATTEMPTED = show_variable(0, GlobalType.INT)
    self.SESSION_EXIT_DONE = show_variable(0, GlobalType.INT)
    self.TIME_EXIT_DUE = show_variable(0, GlobalType.INT)
    self.TIME_EXIT_ATTEMPTED = show_variable(0, GlobalType.INT)
    self.TP1_TIMEOUT_DUE = show_variable(0, GlobalType.INT)
    self.TP1_TIMEOUT_ATTEMPTED = show_variable(0, GlobalType.INT)
    self.TRADES_TODAY = show_variable(0, GlobalType.INT)


# MNQSCALP V4.0 - STRUCTURAL STOP MANAGER
# BACKTEST ONLY
# Maximum intended risk: $100 for 2 MNQ
# Runs after POSITION FILL MONITOR

symbol = Contract("US.MNQ2612")
qty = position_holding_qty(symbol)

if not hasattr(self, "initial_stop_id"):
    self.initial_stop_id = None

if not hasattr(self, "initial_stop_attempted"):
    self.initial_stop_attempted = False

if not hasattr(self, "initial_stop_failed"):
    self.initial_stop_failed = False

if not hasattr(self, "initial_stop_last_status"):
    self.initial_stop_last_status = None

if qty == 2 and not self.initial_stop_attempted:

    entry = position_cost(symbol)
    planned_stop = getattr(self, "v4_planned_stop", None)

    # Block if the risk check did not supply a stop.
    if planned_stop is None:
        self.initial_stop_failed = True
        self.initial_stop_attempted = True
        print("STOP ERROR: NO PLANNED STOP")

    else:
        stop_price = planned_stop
        distance = entry - stop_price
        gross_risk = distance * 4.0

        print("=== V4 STRUCTURAL STOP ===")
        print("Actual entry:", entry)
        print("Structural stop:", stop_price)
        print("Distance:", distance)
        print("Gross risk:", gross_risk)

        if distance <= 0 or distance > 25:
            self.initial_stop_failed = True
            self.initial_stop_attempted = True
            print("STOP ERROR: FILL EXCEEDS RISK CAP")

        else:
            self.initial_stop_attempted = True

            try:
                stop_id = place_stop(
                    symbol=symbol,
                    aux_price=stop_price,
                    qty=2,
                    side="SELL",
                    time_in_force="DAY"
                )

                if stop_id is not None:
                    self.initial_stop_id = stop_id
                    print("STRUCTURAL STOP SUBMITTED:", repr(stop_id))
                else:
                    self.initial_stop_failed = True
                    print("STOP ERROR: NO ORDER ID")

            except Exception as e:
                self.initial_stop_failed = True
                print("STOP SUBMISSION ERROR:", str(e))

# Track every status change, not only the first one.
if self.initial_stop_id is not None:
    try:
        status = str(
            order_status(self.initial_stop_id)
        ).strip().upper().split(".")[-1]

        if status != self.initial_stop_last_status:
            print("STOP STATUS:", status)
            self.initial_stop_last_status = status

        if status in ("FAILED", "REJECTED"):
            self.initial_stop_failed = True

    except Exception as e:
        self.initial_stop_failed = True
        print("STOP STATUS LOOKUP ERROR:", str(e))



# MNQSCALP V3.7.8
# POSITION FILL MONITOR + TRADE COUNTER
# BACKTEST ONLY
# No orders placed, modified, or canceled

symbol = Contract("US.MNQ2612")
qty = position_holding_qty(symbol)

# Initialize monitoring state.
if not hasattr(self, "entry_probe_last_qty"):
    self.entry_probe_last_qty = qty
    self.entry_probe_initialized = True

    print("=== POSITION MONITOR INITIALIZED ===")
    print("Current quantity:", qty)
    print("Trades counted:", self.TRADES_TODAY)

else:
    previous = self.entry_probe_last_qty

    if previous != qty:

        print("=== POSITION CHANGE ===")
        print("Previous quantity:", previous)
        print("Current quantity:", qty)

        if qty != 0:
            print("Average position cost:", position_cost(symbol))

        # Count a NEW position, not an order submission.
        # Long or short direction is supported for counting.
        # A partial fill from 1 to 2 does not count twice.

        new_long = previous <= 0 and qty > 0
        new_short = previous >= 0 and qty < 0

        if new_long or new_short:

            self.TRADES_TODAY += 1

            print("=== NEW ENTRY DETECTED ===")
            print("Trades this session:", self.TRADES_TODAY)
            print("Entry direction:",
                  "LONG" if new_long else "SHORT")

        if previous != 0 and qty == 0:

            print("=== POSITION FLAT ===")
            print("Trades this session:", self.TRADES_TODAY)

        elif qty == 1:
            print("LONG RUNNER OR PARTIAL FILL")

        elif qty == -1:
            print("SHORT RUNNER OR PARTIAL FILL")

        elif qty == 2:
            print("LONG TWO CONTRACTS")

        elif qty == -2:
            print("SHORT TWO CONTRACTS")

        self.entry_probe_last_qty = qty

        print("=== END POSITION CHANGE ===")


# Diagnostic: report the most recently stored stop ID.
# This section does not modify any order.

stop_id = getattr(self, "be_order_id", None)

if stop_id is not None:

    try:
        status = str(order_status(stop_id))

        previous_status = getattr(
            self, "monitor_last_stop_status", None
        )

        if status != previous_status:
            print("STOP ID:", repr(stop_id))
            print("STOP STATUS:", status)

            self.monitor_last_stop_status = status

    except Exception as e:
        print("STOP STATUS CHECK ERROR:", str(e))

# MNQSCALP V4.0 - Re-entry Eligibility
# BACKTEST ONLY - DOES NOT PLACE OR MODIFY ORDERS

symbol = Contract("US.MNQ2612")
qty = position_holding_qty(symbol)

if not hasattr(self, "reentry_previous_qty"):
    self.reentry_previous_qty = qty
    self.reentry_flat_bars = 0

previous = self.reentry_previous_qty

if qty != 0:
    self.reentry_flat_bars = 0
elif previous != 0 and qty == 0:
    self.reentry_flat_bars = 0
    print("POSITION FLAT - COOLDOWN STARTED")
else:
    self.reentry_flat_bars += 1

self.reentry_previous_qty = qty

stop_id = getattr(self, "initial_stop_id", None)
stop_resolved = False
stop_status = "UNKNOWN"

if stop_id is not None:
    try:
        stop_status = str(order_status(stop_id))
        stop_status = stop_status.strip().upper().split(".")[-1]

        stop_resolved = stop_status in (
            "FILLED_ALL",
            "CANCELLED_ALL",
            "CANCELED_ALL"
        )

    except Exception as e:
        print("STOP CHECK ERROR:", str(e))

trades = getattr(self, "TRADES_TODAY", 0)

self.REENTRY_READY = (
    qty == 0
    and self.reentry_flat_bars >= 2
    and trades < 5
    and stop_resolved
)


# V4 - Re-entry unlock eligibility
# Does not authorize trading until all orders are verified.

entry_id = getattr(self, "v4_entry_order_id", None)
entry_resolved = False

if entry_id is not None:
    try:
        entry_status = str(
            order_status(entry_id)
        ).strip().upper().split(".")[-1]

        entry_resolved = entry_status in (
            "FILLED_ALL",
            "CANCELLED_ALL",
            "CANCELED_ALL"
        )
    except Exception as e:
        print("ENTRY STATUS CHECK ERROR:", str(e))

self.V4_UNLOCK_CANDIDATE = (
    self.REENTRY_READY
    and entry_resolved
    and getattr(self, "TEST_ENTRY_USED", 0) == 1
)

if self.V4_UNLOCK_CANDIDATE:
    print("=== V4 REENTRY UNLOCK CANDIDATE ===")
    print("Entry ID:", repr(entry_id))
    print("Entry resolved:", entry_resolved)
    print("Initial stop resolved:", stop_resolved)
    print("Trades this session:", trades)
    print("All orders verified: NO")


if not hasattr(self, "reentry_last_ready"):
    self.reentry_last_ready = None

if self.REENTRY_READY != self.reentry_last_ready:
    print("=== REENTRY STATUS ===")
    print("Position:", qty)
    print("Trades:", trades)
    print("Flat bars:", self.reentry_flat_bars)
    print("Stop:", stop_status)
    print("Candidate ready:", self.REENTRY_READY)
    print("All orders verified: NO")
    print("=== END REENTRY STATUS ===")

    self.reentry_last_ready = self.REENTRY_READY

# MNQSCALP V3.7.7 - Combined Trade Timer
# BACKTEST ONLY - NO ORDERS SUBMITTED
# Five-minute evaluation approximation

symbol = Contract("US.MNQ2612")
qty = position_holding_qty(symbol)

if not hasattr(self, "trade_elapsed_bars"):
    self.trade_elapsed_bars = 0
    self.trade_timer_active = False
    self.trade_time_limit_logged = False
    self.tp1_timeout_logged = False

if qty != 0:

    if not self.trade_timer_active:
        self.trade_timer_active = True
        self.trade_elapsed_bars = 0
        self.trade_time_limit_logged = False
        self.tp1_timeout_logged = False

        self.TIME_EXIT_DUE = 0
        self.TIME_EXIT_ATTEMPTED = 0
        self.TP1_TIMEOUT_DUE = 0
        self.TP1_TIMEOUT_ATTEMPTED = 0

        print("=== TRADE TIMER STARTED ===")
        print("Initial quantity:", qty)

    else:
        self.trade_elapsed_bars += 1

    elapsed = self.trade_elapsed_bars * 5

    # Approx. 20 minutes after initial entry
    # Only when both LONG contracts remain open.
    if (
        qty == 2
        and elapsed >= 15
        and not self.tp1_timeout_logged
    ):
        self.tp1_timeout_logged = True
        self.TP1_TIMEOUT_DUE = 1

        print("=== TP1 DEADLINE REACHED ===")
        print("Elapsed counter:", elapsed)
        print("Still holding:", qty)

    # Approx. 3 hours after initial entry
    if (
        elapsed >= 175
        and not self.trade_time_limit_logged
    ):
        self.trade_time_limit_logged = True
        self.TIME_EXIT_DUE = 1

        print("=== THREE HOUR EXIT REQUIRED ===")
        print("Elapsed counter:", elapsed)
        print("Current quantity:", qty)

else:

    if self.trade_timer_active:
        print("=== TRADE TIMER FINISHED ===")
        print(
            "Elapsed counter:",
            self.trade_elapsed_bars * 5
        )

    self.trade_timer_active = False
    self.trade_elapsed_bars = 0
    self.trade_time_limit_logged = False
    self.tp1_timeout_logged = False

    self.TIME_EXIT_DUE = 0
    self.TIME_EXIT_ATTEMPTED = 0
    self.TP1_TIMEOUT_DUE = 0
    self.TP1_TIMEOUT_ATTEMPTED = 0

# MNQSCALP V3.7.8
# NEW SESSION RESET
# BACKTEST ONLY - NO ORDER OPERATIONS

symbol = Contract("US.MNQ2612")

if getattr(self, "SESSION_EXIT_DONE", 0) == 1:

    qty = position_holding_qty(symbol)
    stop_id = getattr(self, "initial_stop_id", None)

    stop_resolved = stop_id is None

    if stop_id is not None:
        try:
            status = str(order_status(stop_id))
            status = status.strip().upper().split(".")[-1]

            stop_resolved = status in (
                "FILLED_ALL",
                "CANCELLED_ALL",
                "CANCELED_ALL"
            )

        except Exception as e:
            stop_resolved = False
            print("RESET BLOCKED - STOP STATUS:", str(e))

    if qty == 0 and stop_resolved:

        # Reset session trading controls.
        self.SESSION_EXIT_DONE = 0
        self.TEST_ENTRY_USED = 0
        self.TRADES_TODAY = 0

        # Reset exit-management flags.
        self.TP1_EXIT_ATTEMPTED = 0
        self.TIME_EXIT_DUE = 0
        self.TIME_EXIT_ATTEMPTED = 0
        self.TP1_TIMEOUT_DUE = 0
        self.TP1_TIMEOUT_ATTEMPTED = 0

        # Reset initial-stop diagnostics.
        self.initial_stop_attempted = False
        self.initial_stop_id = None

        # Reset per-trade stop modification flags.
        self.tp1_stop_mod_attempted = False
        self.qty_mod_attempted = False

        print("=== NEW SESSION INITIALIZED ===")
        print("Position flat:", qty == 0)
        print("Tracked initial stop resolved:", stop_resolved)
        print("TRADES_TODAY:", self.TRADES_TODAY)
        print("Trading flags reset")

    else:
        print("SESSION RESET WAITING")
        print("Position quantity:", qty)
        print("Tracked stop resolved:", stop_resolved)
_variable_1 = get_MyLang_indicator(indicator_name="MNQSCALPV4", variable_name="LONG_ENTRY", symbol=self.Trigger_Symbol1, params={}, bar_type=BarType.K_5M, select=1, session_type=THType.ALL)
if _variable_1 > 0.5:
    return True
else:
    return False
```

# Appendix B — Active card code, verbatim (Jey's paste 2026-10-20 12:19)
Order: VWAP LONG CONFIRMATION, STOP PRICE VERIFICATION (disconnected), old BUY 2 MNQ (disconnected), V4 ENTRY ORDER MANAGER, STOP QUANTITY MODIFIER (TP1 Stop Coordination). LONG RISK CHECK code is below.
```python
_bar_close = bar_close(symbol=self.Trigger_Symbol1, bar_type=BarType.K_5M, select=2, session_type=THType.ALL)
_variable_1 = get_Python_indicator(indicator_name="VWAP", variable_name="VWAP", symbol=self.Trigger_Symbol1, params=[], bar_type=BarType.K_5M, select=2, session_type=THType.ALL)
if _variable_1 < _bar_close:
    return True
else:
    return False


# V4.0 - Structural Stop Verification
# BACKTEST ONLY - NO ORDERS

symbol = Contract("US.MNQ2612")

planned_stop = getattr(self, "v4_planned_stop", None)
market = current_price(symbol)

print("=== STRUCTURAL STOP CHECK ===")
print("Market price:", market)
print("Planned stop:", planned_stop)

if planned_stop is not None:
    distance = market - planned_stop
    print("Stop distance:", distance)
    print("Estimated gross risk for 2 MNQ:", distance * 4)
else:
    print("ERROR: No planned stop found")

print("=== END STOP CHECK ===")



_ask = ask(symbol=self.Trigger_Symbol1, level=1)
_lot_size = lot_size(symbol=self.Trigger_Symbol1)
place_limit(symbol=self.Trigger_Symbol1, price=_ask, qty=2 * _lot_size, side=OrderSide.BUY, time_in_force=TimeInForce.DAY, order_trade_session_type=TSType.ETH)


# MNQSCALP V4.0 - ENTRY ORDER MANAGER
# BACKTEST ONLY

symbol = Contract("US.MNQ2612")

if not hasattr(self, "v4_entry_order_id"):
    self.v4_entry_order_id = None

if not hasattr(self, "v4_entry_pending"):
    self.v4_entry_pending = False

if not hasattr(self, "v4_entry_last_status"):
    self.v4_entry_last_status = None

# Check status of an existing entry order.
if self.v4_entry_order_id is not None:
    try:
        status = str(
            order_status(self.v4_entry_order_id)
        ).strip().upper().split(".")[-1]

        if status != self.v4_entry_last_status:
            print("V4 ENTRY ORDER STATUS:", status)
            self.v4_entry_last_status = status

        if status in (
            "FILLED_ALL",
            "CANCELLED_ALL",
            "CANCELED_ALL",
            "FAILED",
            "REJECTED"
        ):
            self.v4_entry_pending = False

    except Exception as e:
        # Unknown order state: keep entry locked.
        self.v4_entry_pending = True
        print("V4 ENTRY STATUS ERROR:", str(e))

# Submit a new entry only when this card is reached
# through the approved LONG entry conditions.
qty = position_holding_qty(symbol)

if (
    qty == 0
    and not self.v4_entry_pending
    and self.v4_entry_order_id is None
):
    try:
        entry_ask = ask(symbol=symbol, level=1)
        size = lot_size(symbol=symbol)

        order_id = place_limit(
            symbol=symbol,
            price=entry_ask,
            qty=2 * size,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            order_trade_session_type=TSType.ETH
        )

        if order_id is not None:
            self.v4_entry_order_id = order_id
            self.v4_entry_pending = True

            print("=== V4 ENTRY SUBMITTED ===")
            print("Order ID:", repr(order_id))
            print("Price:", entry_ask)
            print("Quantity:", 2 * size)
        else:
            print("V4 ENTRY ERROR: NO ORDER ID")

    except Exception as e:
        print("V4 ENTRY ERROR:", str(e))

# MNQSCALP V3.7.6.5 - TP1 Stop Coordination
# BACKTEST ONLY - ISOLATED EXPERIMENT

symbol = Contract("US.MNQ2612")
qty = position_holding_qty(symbol)

if not hasattr(self, "tp1_stop_mod_attempted"):
    self.tp1_stop_mod_attempted = False

stop_id = getattr(self, "initial_stop_id", None)
tp1_attempted = getattr(
    self, "TP1_EXIT_ATTEMPTED", 0
)

if (
    qty == 1
    and tp1_attempted == 1
    and stop_id is not None
    and not self.tp1_stop_mod_attempted
):

    print("=== TP1 STOP COORDINATION ===")
    print("Position after TP1:", qty)
    print("Stop ID:", repr(stop_id))

    try:
        status = str(
            order_status(stop_id)
        ).strip().upper().split(".")[-1]

        print("Stop status before:", status)

        working = status in (
            "WAITING_SUBMIT",
            "SUBMITTING",
            "SUBMITTED"
        )

        if working:

            entry = position_cost(symbol)
            stop_price = entry

            # One attempt only
            self.tp1_stop_mod_attempted = True

            result = modify_order(
                orderid=stop_id,
                qty=1,
                aux_price=stop_price
            )

            print("MODIFICATION REQUEST:", repr(result))
            print("Requested stop quantity: 1")
            print("Requested trigger:", stop_price)

        else:
            print("STOP NOT WORKING:", status)

    except Exception as e:
        self.tp1_stop_mod_attempted = True
        print("TP1 STOP MODIFICATION ERROR:", str(e))

    print("=== END TP1 COORDINATION ===")
```

## LONG RISK CHECK (Coded Condition)
```python
# MNQSCALP V4 - LONG RISK CHECK
# Max risk: $100 for 2 MNQ contracts
# 25 Nasdaq points maximum

symbol = Contract("US.MNQ2612")

swing_low = get_MyLang_indicator(
    indicator_name="MNQSCALPV4",
    variable_name="V4_SWING_LOW",
    symbol=symbol,
    params={},
    bar_type=BarType.K_5M,
    select=1,
    session_type=THType.ALL
)

entry = current_price(symbol)

# 2-point buffer below swing low
stop_price = swing_low - 2.0

distance = entry - stop_price

if swing_low > 0 and distance > 0 and distance <= 25:
    self.v4_planned_stop = stop_price
    return True
else:
    return False
```
