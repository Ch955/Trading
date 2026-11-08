"""The dalal-street-skills opening-range-breakout rule, copied for a side-by-side backtest.

Source: https://github.com/Adityaraj0421/dalal-street-skills
        commit 6fcc8d46032dd551ad89c51745fd95a32db5edfa, nse-timemachine/timemachine.py
License: MIT (c) the dalal-street-skills authors.

Copied as written: the 0.05 tick rounding, opening_range, rule_stop, the Zerodha MIS
charges (statutory CHARGES + Zerodha brokerage 0.03% capped at Rs 20), Econ and
history_replay. Only changes: the Zerodha profile is fixed instead of read from a
broker table, IndiaError is replaced by ValueError, and history_replay also returns the
exit price so a caller can size the trade in rupees.
"""
import math
import statistics

TICK = 0.05


def _q(x, tick):
    return round(x / tick, 6)


def tick_down(x, tick=TICK):
    return round(math.floor(_q(x, tick)) * tick, 2) + 0.0


def tick_up(x, tick=TICK):
    return round(math.ceil(_q(x, tick)) * tick, 2) + 0.0


# Statutory rates as read by dalal-street-skills on 2026-10-26, plus Zerodha's MIS brokerage.
CHARGES = {
    "stt_pct_mis_sell": 0.025,
    "txn_pct_nse": 0.00307,
    "sebi_per_crore": 10.0,
    "stamp_pct_mis_buy": 0.003,
    "gst_pct": 18.0,
    "brokerage_pct_mis": 0.03, "brokerage_min_mis": 0.0, "brokerage_cap_mis": 20.0,
}


def trade_charges(buy_value, sell_value, product="MIS", exchange="NSE", cfg=None):
    c = CHARGES
    if str(product).upper() != "MIS":
        raise ValueError("this copy only covers MIS (intraday)")

    def brokerage(v):
        if v <= 0:
            return 0.0
        b = max(c["brokerage_min_mis"], v * c["brokerage_pct_mis"] / 100.0)
        cap = c["brokerage_cap_mis"]
        return min(b, cap) if cap else b

    brk = brokerage(buy_value) + brokerage(sell_value)
    stt = sell_value * c["stt_pct_mis_sell"] / 100.0
    stamp = buy_value * c["stamp_pct_mis_buy"] / 100.0
    txn = (buy_value + sell_value) * c["txn_pct_nse"] / 100.0
    sebi = (buy_value + sell_value) * c["sebi_per_crore"] / 1e7
    gst = (brk + txn + sebi) * c["gst_pct"] / 100.0
    parts = {"brokerage": brk, "stt": stt, "exchange_txn": txn, "sebi": sebi,
             "stamp_duty": stamp, "gst": gst}
    parts = {k: round(v, 2) + 0.0 for k, v in parts.items()}
    parts["total"] = round(sum(parts.values()), 2) + 0.0
    return parts


class Econ(object):
    """What a trade is worth in rupees and in R. 1R = the max loss at the stop,
    charges included. Prices are per share; qty is whole shares."""

    def __init__(self, entry, stop, target, qty, side="buy", product="MIS", exchange="NSE", cfg=None):
        self.entry, self.stop, self.target, self.qty = entry, stop, target, int(qty)
        self.long = side == "buy"
        self.product, self.exchange, self.cfg = product, exchange, cfg
        self.charges_at_stop = self.fees(stop)
        self.charges_at_target = self.fees(target)
        self.risk_gross = abs(entry - stop) * self.qty
        self.risk_cash = self.risk_gross + self.charges_at_stop
        self.net_at_target = self.net(target)
        self.r_target = round(self.net_at_target / self.risk_cash, 4)
        self.gross_r = round(abs(target - entry) / abs(entry - stop), 4)

    def fees(self, exit_price):
        e, x = self.entry * self.qty, exit_price * self.qty
        buy, sell = (e, x) if self.long else (x, e)
        return trade_charges(buy, sell, self.product, self.exchange, self.cfg)["total"]

    def net(self, exit_price):
        gross = ((exit_price - self.entry) if self.long else (self.entry - exit_price)) * self.qty
        return gross - self.fees(exit_price)

    def r_at(self, exit_price):
        return self.net(exit_price) / self.risk_cash


def tick_away(x, long):
    return tick_down(x) if long else tick_up(x)


def opening_range(D, n):
    rows = [D[i] for i in range(n)]
    return max(b["h"] for b in rows), min(b["l"] for b in rows)


def rule_stop(rule, oh, ol, entry, long):
    r = rule["stop_rule"]
    if r == "or_mid":
        return tick_away((oh + ol) / 2, long)
    if r in ("or_low", "or_high"):
        return tick_away(ol if long else oh, long)
    frac = rule["stop_pct"] / 100.0
    return tick_away(entry * (1 - frac) if long else entry * (1 + frac), long)


def history_replay(sessions, rule, last, side="buy", cost=None):
    """The rule on every past full session: entry = the first bar after the opening
    range to close beyond it (up to the exit bar), then stop first, then target,
    bar by bar, else the close at the exit bar. R includes charges."""
    long = side == "buy"
    cost = cost or {"qty": 1, "product": "MIS", "exchange": "NSE", "cfg": None}
    n = rule["or_minutes"] // 5
    trades = []
    for d, D in sessions:
        oh, ol = opening_range(D, n)
        kk = next((i for i in range(n, last + 1) if (D[i]["c"] > oh if long else D[i]["c"] < ol)), None)
        if kk is None:
            continue
        e = tick_up(D[kk]["c"]) if long else tick_down(D[kk]["c"])
        s = rule_stop(rule, oh, ol, e, long)
        risk = (e - s) if long else (s - e)
        if risk <= 0:
            continue
        raw_t = e + rule["target_r"] * risk if long else e - rule["target_r"] * risk
        t = tick_down(raw_t) if long else tick_up(raw_t)
        if (t <= e) if long else (t >= e):
            continue
        ec = Econ(e, s, t, cost["qty"], side, cost["product"], cost["exchange"], cost["cfg"])
        oc = None
        for b in D[kk + 1:last + 1]:
            if (b["l"] <= s) if long else (b["h"] >= s):
                oc = "stop"
                break
            if (b["h"] >= t) if long else (b["l"] <= t):
                oc = "target"
                break
        cl = D[last]["c"]
        R = ec.r_target if oc == "target" else -1.0 if oc == "stop" else ec.r_at(cl)
        exit_px = t if oc == "target" else s if oc == "stop" else cl
        trades.append({"date": d, "signal_idx": kk, "time": D[kk + 1]["t"] if kk + 1 < len(D) else D[kk]["t"],
                       "entry": e, "stop": s, "target": t, "exit": exit_px,
                       "outcome": oc or "close", "R": round(R, 2)})
    return {
        "sessions": len(sessions), "triggered": len(trades),
        "avg_R": round(statistics.mean(x["R"] for x in trades), 3) if trades else None,
        "rule": rule, "trades": trades,
    }
