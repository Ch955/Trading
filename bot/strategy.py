"""Opening-range breakout, long only, one day at a time, no look-ahead.

For one stock's bars on one day:
  * Opening range (OR) = first N bars (default 3 x 5m = 09:15-09:30).
  * Signal = first bar closing above the OR high, starting no later than last_entry_time.
  * Entry = OPEN of the next bar (+ slippage). We never assume we bought at the signal close.
  * Stop = OR midpoint. Target = entry + target_r x risk. Flat at exit_time regardless.
  * If stop and target are both touched inside one bar, we assume the stop hit (conservative).
"""


def opening_range(bars, n):
    if len(bars) < n + 2 or bars[0]["t"] != "09:15":
        return None
    first = bars[:n]
    return max(b["h"] for b in first), min(b["l"] for b in first), sum(b["v"] for b in first) / n


def find_signal(bars, s, min_price=0):
    orr = opening_range(bars, s["opening_range_bars"])
    if not orr:
        return None
    orh, orl, or_vol = orr
    mid = (orh + orl) / 2
    range_pct = (orh - orl) / mid * 100
    if not (s["min_range_pct"] <= range_pct <= s["max_range_pct"]) or mid < min_price:
        return None
    n = s["opening_range_bars"]
    for i in range(n, len(bars) - 1):
        b = bars[i]
        if b["t"] > s["last_entry_time"]:
            return None
        if b["c"] > orh:
            return {"signal_idx": i, "signal_time": b["t"], "orh": orh, "orl": orl,
                    "stop": round(mid, 2), "range_pct": round(range_pct, 2),
                    "rvol": round(b["v"] / or_vol, 2) if or_vol else 0.0}
    return None


def index_ok(index_bars, signal_time, n):
    """Market filter: Nifty 50 must be above its own OR midpoint at the signal bar."""
    if not index_bars:
        return True  # no index data -> don't block
    orr = opening_range(index_bars, n)
    if not orr:
        return True
    mid = (orr[0] + orr[1]) / 2
    upto = [b for b in index_bars if b["t"] <= signal_time]
    return bool(upto) and upto[-1]["c"] > mid


def simulate(bars, sig, s, slippage_pct):
    """Walk the bars after the signal. Returns entry/exit prices and reason."""
    slip = slippage_pct / 100
    e_idx = sig["signal_idx"] + 1
    entry = bars[e_idx]["o"] * (1 + slip)
    stop = sig["stop"]
    risk = entry - stop
    if risk <= 0:
        return None
    target = entry + s["target_r"] * risk
    for b in bars[e_idx:]:
        if b["t"] >= s["exit_time"]:
            return _res(bars[e_idx]["t"], entry, stop, target, b["t"], b["o"] * (1 - slip), "time")
        if b["l"] <= stop:
            px = min(b["o"], stop)  # gap through stop fills worse
            return _res(bars[e_idx]["t"], entry, stop, target, b["t"], px * (1 - slip), "stop")
        if b["h"] >= target:
            return _res(bars[e_idx]["t"], entry, stop, target, b["t"], target * (1 - slip), "target")
    last = bars[-1]
    return _res(bars[e_idx]["t"], entry, stop, target, last["t"], last["c"] * (1 - slip), "eod")


def _res(et, entry, stop, target, xt, exit_px, why):
    return {"entry_time": et, "entry": round(entry, 2), "stop": round(stop, 2),
            "target": round(target, 2), "exit_time": xt, "exit": round(exit_px, 2), "reason": why}
