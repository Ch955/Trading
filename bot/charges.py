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


def per_share_estimate(price, c):
    """Rough charges per share for a round trip near `price` (percentage part only)."""
    return round_trip(1000, price, price, dict(c, brokerage_cap=1e12)) / 1000
