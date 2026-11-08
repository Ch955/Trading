"""Pick at most one trade per day across the universe, size it, apply risk limits."""
from . import charges, strategy


def size(entry, stop, cfg):
    """Largest qty whose loss at the stop, including charges, stays within risk_per_trade
    and whose value stays within capital x MIS leverage."""
    c = cfg["charges"]
    max_qty_by_margin = int(cfg["capital"] * cfg["mis_leverage"] // entry)
    per_share = (entry - stop) + charges.per_share_estimate(entry, c)
    qty = min(max_qty_by_margin, int(cfg["risk_per_trade"] // per_share) if per_share > 0 else 0)
    while qty > 0:
        loss = qty * (entry - stop) + charges.round_trip(qty, entry, stop, c)
        if loss <= cfg["risk_per_trade"]:
            return qty, round(loss, 2)
        qty -= 1
    return 0, 0.0


def pick_trade(day, bars_by_symbol, index_bars, cfg):
    """Return (trade or None, list of notes). Deterministic for a given input."""
    s = cfg["strategy"]
    cands = []
    for sym, days in bars_by_symbol.items():
        bars = days.get(day)
        if not bars:
            continue
        sig = strategy.find_signal(bars, s, cfg["min_price"])
        if not sig:
            continue
        if cfg.get("use_index_filter") and not strategy.index_ok(index_bars, sig["signal_time"],
                                                               s["opening_range_bars"]):
            continue
        cands.append((sig["signal_time"], -sig["rvol"], sym, sig, bars))
    notes = ["%d stocks triggered a breakout" % len(cands)]
    cands.sort(key=lambda x: (x[0], x[1], x[2]))  # earliest, then highest relative volume
    for _, _, sym, sig, bars in cands:
        sim = strategy.simulate(bars, sig, s, cfg["slippage_pct"])
        if not sim:
            continue
        qty, max_loss = size(sim["entry"], sim["stop"], cfg)
        if qty < 1:
            notes.append("%s skipped: stop too wide for the risk budget" % sym)
            continue
        gross = qty * (sim["exit"] - sim["entry"])
        ch = charges.round_trip(qty, sim["entry"], sim["exit"], cfg["charges"])
        trade = dict(sim, date=day, symbol=sym, qty=qty, value=round(qty * sim["entry"], 2),
                     max_loss=max_loss, signal_time=sig["signal_time"], rvol=sig["rvol"],
                     gross=round(gross, 2), charges=ch, net=round(gross - ch, 2))
        return trade, notes
    return None, notes


def month_pnl(trades, month):
    return round(sum(t["net"] for t in trades if t["date"].startswith(month)), 2)


def blocked(trades, day, cfg):
    """Risk gates checked BEFORE a new day trades. Returns reason or None."""
    month = day[:7]
    if month_pnl(trades, month) <= -cfg["monthly_loss_limit"]:
        return "monthly loss limit of Rs %d reached for %s" % (cfg["monthly_loss_limit"], month)
    today = [t for t in trades if t["date"] == day]
    if len(today) >= cfg["max_trades_per_day"]:
        return "already traded today"
    if sum(t["net"] for t in today) <= -cfg["daily_loss_limit"]:
        return "daily loss limit reached"
    equity = cfg["capital"] + sum(t["net"] for t in trades)
    if equity < cfg["capital"] * 0.5:
        return "equity below half of starting capital; stopped for safety"
    return None


def equity(trades, cfg):
    return round(cfg["capital"] + sum(t["net"] for t in trades), 2)


def stats(trades, cfg):
    n = len(trades)
    wins = [t for t in trades if t["net"] > 0]
    peak, dd, eq = cfg["capital"], 0.0, cfg["capital"]
    for t in trades:
        eq += t["net"]
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    return {
        "trades": n,
        "win_rate": round(100 * len(wins) / n, 1) if n else 0.0,
        "gross": round(sum(t["gross"] for t in trades), 2),
        "charges": round(sum(t["charges"] for t in trades), 2),
        "net": round(sum(t["net"] for t in trades), 2),
        "max_drawdown": round(dd, 2),
        "end_equity": round(eq, 2),
        "by_reason": {r: sum(1 for t in trades if t["reason"] == r)
                      for r in sorted({t["reason"] for t in trades})},
    }


def fmt_inr(x):
    sign = "-" if x < 0 else ""
    return "%sRs %s" % (sign, format(abs(x), ",.2f"))
