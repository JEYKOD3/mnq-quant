# MNQSCALP V4.1 - ENTRY ORDER MANAGER - PER TRADE RESET
# BACKTEST ONLY

symbol = Contract("US.MNQ2612")
qty = position_holding_qty(symbol)

if not hasattr(self, "v4_entry_order_id"):
    self.v4_entry_order_id = None

if not hasattr(self, "v4_entry_last_status"):
    self.v4_entry_last_status = None

entry_ready = True

# 1. Previous entry order must be finished
if self.v4_entry_order_id is not None:
    try:
        status = str(
            order_status(self.v4_entry_order_id)
        ).strip().upper().split(".")[-1]

        if status != self.v4_entry_last_status:
            print("V4 ENTRY ORDER STATUS:", status)
            self.v4_entry_last_status = status

        if status not in (
            "FILLED_ALL",
            "CANCELLED_ALL",
            "CANCELED_ALL",
            "FAILED",
            "REJECTED"
        ):
            entry_ready = False

    except Exception as e:
        entry_ready = False
        print("V4 ENTRY STATUS ERROR:", str(e))

# 2. Previous protective stop must be finished
stop_id = getattr(self, "initial_stop_id", None)

if entry_ready and stop_id is not None:
    try:
        status = str(
            order_status(stop_id)
        ).strip().upper().split(".")[-1]

        if status not in (
            "FILLED_ALL",
            "CANCELLED_ALL",
            "CANCELED_ALL",
            "FAILED",
            "REJECTED"
        ):
            entry_ready = False

            if qty == 0:
                print("V4 ORPHAN STOP STILL WORKING:", repr(stop_id), status)

    except Exception as e:
        entry_ready = False
        print("V4 STOP CHECK ERROR:", str(e))

# 3. Cooldown: 2 flat bars after a closed trade
if entry_ready and self.v4_entry_order_id is not None:
    if getattr(self, "reentry_flat_bars", 0) < 2:
        entry_ready = False

# 4. Reset per-trade state, then submit new entry
if entry_ready and qty == 0:

    if self.v4_entry_order_id is not None:
        self.initial_stop_id = None
        self.initial_stop_attempted = False
        self.initial_stop_failed = False
        self.initial_stop_last_status = None
        self.tp1_stop_mod_attempted = False
        self.qty_mod_attempted = False
        self.TP1_EXIT_ATTEMPTED = 0
        print("V4 PER-TRADE STATE RESET")

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
            self.v4_entry_last_status = None

            print("=== V4 ENTRY SUBMITTED ===")
            print("Order ID:", repr(order_id))
            print("Price:", entry_ask)
            print("Planned stop:", getattr(self, "v4_planned_stop", None))
            print("Trades this session:", getattr(self, "TRADES_TODAY", 0))
        else:
            print("V4 ENTRY ERROR: NO ORDER ID")

    except Exception as e:
        print("V4 ENTRY ERROR:", str(e))
