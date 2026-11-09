"""Swing trading (delivery / CNC) backtest on daily candles, one position at a time.

Two setups, rules fixed in advance (not tuned on this data):

  breakout  Buy when today's close is above the highest high of the previous 20 days, the
            stock is in an uptrend (close > 200-day average and 50-day > 200-day average).
            Stop 2 x ATR(14) below entry. Exit when a close falls below the lowest low of the
            previous 10 days, or after 30 trading days.
  pullback  Buy a short dip inside an uptrend: close > 200-day average and RSI(2) < 10.
            Stop 3 x ATR(14) below entry. Exit when a close is back above the 5-day average,
            or after 10 trading days.

Mechanics, the same for both:
  * Signals use the day's close; orders fill at the NEXT day's open plus slippage.
  * A stop is checked against each day's low; a gap below it fills at that day's open.
  * Exit signals on a close fill at the next open.
  * One stock at a time. Qty = whatever the current equity can pay for (no leverage),
    keeping Rs 30 aside for charges. Stocks priced above that are skipped.
  * When several stocks signal on one day: breakout takes the one with the highest
    volume versus its 20-day average, pullback the lowest RSI(2). Ties go A-Z.
  * Monthly loss limit: no new entries for the rest of a month once that month's realised
    loss reaches the limit.
"""
from . import charges

SETUPS = {
    "breakout": {"stop_atr": 2.0, "max_hold": 30},
    "pullback": {"stop_atr": 3.0, "max_hold": 10},
}


def sma(xs, n, i):
    return sum(xs[i - n + 1:i + 1]) / n if i >= n - 1 else None


def atr(bars, n, i):
    if i < n:
        return None
    trs = [max(bars[j]["h"] - bars[j]["l"], abs(bars[j]["h"] - bars[j - 1]["c"]),
               abs(bars[j]["l"] - bars[j - 1]["c"])) for j in range(i - n + 1, i + 1)]
    return sum(trs) / n


def rsi(closes, n, i):
    """Wilder-style RSI over the last n changes, simple averages (fine for n=2)."""
    if i < n:
        return None
    ups = downs = 0.0
    for j in range(i - n + 1, i + 1):
        ch = closes[j] - closes[j - 1]
        ups += max(ch, 0)
        downs += max(-ch, 0)
    if downs == 0:
        return 100.0
    rs = ups / downs
    return 100 - 100 / (1 + rs)


def indicators(bars):
    """Per-day indicators, computed only from that day and earlier."""
    closes = [b["c"] for b in bars]
    vols = [b["v"] for b in bars]
    out = []
    for i, b in enumerate(bars):
        out.append({
            "sma5": sma(closes, 5, i), "sma50": sma(closes, 50, i), "sma200": sma(closes, 200, i),
            "atr14": atr(bars, 14, i), "rsi2": rsi(closes, 2, i),
            "hh20": max(x["h"] for x in bars[i - 20:i]) if i >= 20 else None,
            "ll10": min(x["l"] for x in bars[i - 10:i]) if i >= 10 else None,
            "vol20": sma(vols, 20, i - 1) if i >= 20 else None,
        })
    return out


def entry_signal(setup, b, ind):
    """(True, rank_key) when today's close is a buy signal. Lower rank_key wins."""
    if ind["sma200"] is None or ind["atr14"] is None:
        return False, None
    if setup == "breakout":
        if (ind["hh20"] is not None and ind["sma50"] is not None and b["c"] > ind["hh20"]
                and b["c"] > ind["sma200"] and ind["sma50"] > ind["sma200"]):
            rvol = b["v"] / ind["vol20"] if ind["vol20"] else 0.0
            return True, -rvol
        return False, None
    if setup == "pullback":
        if ind["rsi2"] is not None and b["c"] > ind["sma200"] and ind["rsi2"] < 10:
            return True, ind["rsi2"]
        return False, None
    raise ValueError(setup)


def exit_signal(setup, b, ind):
    if setup == "breakout":
        return ind["ll10"] is not None and b["c"] < ind["ll10"]
    return ind["sma5"] is not None and b["c"] > ind["sma5"]


def backtest(daily, setup, capital=2400, slippage_pct=0.1, monthly_loss_limit=500,
             reserve=30, start_date=None):
    """daily: {symbol: [daily bars]}. Returns (trades, equity_curve)."""
    cfg = SETUPS[setup]
    slip = slippage_pct / 100
    ind = {s: indicators(b) for s, b in daily.items()}
    idx = {s: {b["d"]: i for i, b in enumerate(bars)} for s, bars in daily.items()}
    days = sorted({b["d"] for bars in daily.values() for b in bars})
    if start_date:
        days = [d for d in days if d >= start_date]

    equity = float(capital)
    pos = None          # open position
    pending = None      # ("buy", sym) or ("sell", reason) to fill at next open
    trades, curve = [], []

    def month_loss(month):
        return sum(t["net"] for t in trades if t["exit_date"][:7] == month)

    for d in days:
        # 1) fill orders decided at yesterday's close, at today's open
        if pending and pending[0] == "sell" and pos:
            i = idx[pos["sym"]].get(d)
            if i is not None:
                px = daily[pos["sym"]][i]["o"] * (1 - slip)
                trades.append(_close(pos, d, px, pending[1]))
                equity += trades[-1]["net"]
                pos, pending = None, None
        if pending and pending[0] == "buy" and pos is None:
            sym = pending[1]
            i = idx[sym].get(d)
            if i is not None:
                px = daily[sym][i]["o"] * (1 + slip)
                qty = int((equity - reserve) // px)
                if qty >= 1:
                    a = ind[sym][i - 1]["atr14"]
                    pos = {"sym": sym, "entry_date": d, "entry": px, "qty": qty,
                           "stop": px - cfg["stop_atr"] * a, "held": 0}
            pending = None

        # 2) manage the open position during today's candle
        if pos:
            i = idx[pos["sym"]].get(d)
            if i is not None:
                b = daily[pos["sym"]][i]
                pos["held"] += 1
                if b["l"] <= pos["stop"]:
                    px = min(b["o"], pos["stop"]) * (1 - slip)
                    trades.append(_close(pos, d, px, "stop"))
                    equity += trades[-1]["net"]
                    pos = None
                elif exit_signal(setup, b, ind[pos["sym"]][i]):
                    pending = ("sell", "exit rule")
                elif pos["held"] >= cfg["max_hold"]:
                    pending = ("sell", "time")

        # 3) look for a new entry at today's close
        if pos is None and pending is None and month_loss(d[:7]) > -monthly_loss_limit:
            cands = []
            for s, bars in daily.items():
                i = idx[s].get(d)
                if i is None:
                    continue
                ok, key = entry_signal(setup, bars[i], ind[s][i])
                if ok and bars[i]["c"] * (1 + slip) <= equity - reserve:
                    cands.append((key, s))
            if cands:
                pending = ("buy", min(cands)[1])

        mark = equity
        if pos:
            i = idx[pos["sym"]].get(d)
            if i is not None:
                mark = equity + pos["qty"] * (daily[pos["sym"]][i]["c"] - pos["entry"])
        curve.append((d, round(mark, 2)))
    return trades, curve


def _close(pos, d, px, reason):
    gross = pos["qty"] * (px - pos["entry"])
    ch = charges.round_trip_cnc(pos["qty"], pos["entry"], px)
    return {"symbol": pos["sym"], "entry_date": pos["entry_date"], "exit_date": d,
            "qty": pos["qty"], "entry": round(pos["entry"], 2), "exit": round(px, 2),
            "days": pos["held"], "reason": reason, "gross": round(gross, 2),
            "charges": ch, "net": round(gross - ch, 2)}


def buy_and_hold(bars, capital=2400, slippage_pct=0.1, start_date=None):
    """Buy at the first open on/after start_date with all the money, sell at the last close."""
    bars = [b for b in bars if not start_date or b["d"] >= start_date]
    slip = slippage_pct / 100
    entry, exit_ = bars[0]["o"] * (1 + slip), bars[-1]["c"] * (1 - slip)
    qty = int((capital - 30) // entry)
    gross = qty * (exit_ - entry)
    ch = charges.round_trip_cnc(qty, entry, exit_) if qty else 0.0
    return {"first": bars[0]["d"], "last": bars[-1]["d"], "qty": qty, "entry": round(entry, 2),
            "exit": round(exit_, 2), "net": round(gross - ch, 2), "charges": ch}


def summary(trades, curve, capital=2400):
    n = len(trades)
    peak, dd = capital, 0.0
    for _, v in curve:
        peak = max(peak, v)
        dd = max(dd, peak - v)
    years = {}
    for t in trades:
        y = t["exit_date"][:4]
        years[y] = round(years.get(y, 0) + t["net"], 2)
    return {
        "trades": n,
        "win_rate": round(100.0 * sum(1 for t in trades if t["net"] > 0) / n, 1) if n else 0.0,
        "gross": round(sum(t["gross"] for t in trades), 2),
        "charges": round(sum(t["charges"] for t in trades), 2),
        "net": round(sum(t["net"] for t in trades), 2),
        "avg_days": round(sum(t["days"] for t in trades) / n, 1) if n else 0.0,
        "max_drawdown": round(dd, 2),
        "end_equity": round(capital + sum(t["net"] for t in trades), 2),
        "by_year": years,
    }
