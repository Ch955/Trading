"""Zerodha equity-intraday charges for one round trip (buy then sell)."""


def round_trip(qty, buy_price, sell_price, c):
    buy_val = qty * buy_price
    sell_val = qty * sell_price
    turnover = buy_val + sell_val

    brokerage = (min(c["brokerage_cap"], buy_val * c["brokerage_pct"] / 100)
                 + min(c["brokerage_cap"], sell_val * c["brokerage_pct"] / 100))
    stt = sell_val * c["stt_sell_pct"] / 100
    exchange = turnover * c["exchange_txn_pct"] / 100
    sebi = turnover * c["sebi_per_crore"] / 1e7
    stamp = buy_val * c["stamp_buy_pct"] / 100
    gst = (brokerage + exchange + sebi) * c["gst_pct"] / 100

    total = brokerage + stt + exchange + sebi + stamp + gst
    return round(total, 2)


CNC = {
    "_note": "Zerodha equity delivery (CNC), read 2026-11. Re-check zerodha.com/charges.",
    "brokerage": 0.0,
    "stt_pct": 0.1,             # buy and sell
    "exchange_txn_pct": 0.00307,
    "sebi_per_crore": 10,
    "stamp_buy_pct": 0.015,
    "gst_pct": 18,
    "dp_charge_per_sell": 15.34,  # per stock per day sold, GST included
}


def round_trip_cnc(qty, buy_price, sell_price, c=CNC):
    """Zerodha delivery charges for buying and later selling `qty` shares."""
    buy_val, sell_val = qty * buy_price, qty * sell_price
    turnover = buy_val + sell_val
    stt = turnover * c["stt_pct"] / 100
    exchange = turnover * c["exchange_txn_pct"] / 100
    sebi = turnover * c["sebi_per_crore"] / 1e7
    stamp = buy_val * c["stamp_buy_pct"] / 100
    gst = (c["brokerage"] + exchange + sebi) * c["gst_pct"] / 100
    return round(c["brokerage"] + stt + exchange + sebi + stamp + gst + c["dp_charge_per_sell"], 2)


def per_share_estimate(price, c):
    """Rough charges per share for a round trip near `price` (percentage part only)."""
    return round_trip(1000, price, price, dict(c, brokerage_cap=1e12)) / 1000
