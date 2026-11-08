#!/usr/bin/env python3
"""Backtest the dalal-street-skills ORB rule (bot/dalal_port.py) on the same data and money
rules as our bot, and write reports/dalal_backtest.md next to our own result.

  python3 tools/dalal_compare.py            # downloads ~60 days of 5m bars (needs network)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from bot import data, dalal_port as dp  # noqa: E402

CAPITAL, LEVERAGE, RISK, MONTH_STOP = 2400, 5, 25, 500
EXIT_BAR = "15:05"  # its close at 15:10 is the exit, matching our bot's flat time
SESSION_BARS = 75   # 09:15 .. 15:25


SLOTS = ["%02d:%02d" % divmod(9 * 60 + 15 + 5 * i, 60) for i in range(SESSION_BARS)]
MAX_MISSING = 5


def full_sessions(days):
    """Sessions as lists indexed by bar slot (what history_replay expects). Yahoo often drops
    a bar or two; a missing slot becomes a flat bar at the previous close so later bars keep
    their slot. Days missing the 09:15 bar or more than MAX_MISSING bars up to the exit are
    skipped."""
    exit_idx = SLOTS.index(EXIT_BAR)
    out = []
    for d in sorted(days):
        by_t = {b["t"]: b for b in days[d]}
        if "09:15" not in by_t:
            continue
        if sum(1 for t in SLOTS[:exit_idx + 1] if t not in by_t) > MAX_MISSING:
            continue
        bars, prev = [], None
        for t in SLOTS:
            b = by_t.get(t)
            if b is None:
                c = prev["c"]
                b = {"t": t, "o": c, "h": c, "l": c, "c": c, "v": 0, "filled": True}
            bars.append(b)
            prev = b
        out.append((d, bars))
    return out


def size(entry, stop, target):
    """Largest qty with loss at the stop incl. charges <= RISK and value <= CAPITAL x LEVERAGE."""
    qty = int(CAPITAL * LEVERAGE // entry)
    while qty > 0:
        ec = dp.Econ(entry, stop, target, qty)
        if ec.risk_cash <= RISK:
            return qty, ec
        qty -= 1
    return 0, None


def run(sessions_by_symbol, target_r):
    rule = {"setup": "orb", "or_minutes": 15, "stop_rule": "or_mid", "target_r": target_r}
    by_day = {}
    for sym, sessions in sessions_by_symbol.items():
        if not sessions:
            continue
        last = [b["t"] for b in sessions[0][1]].index(EXIT_BAR)
        for t in dp.history_replay(sessions, rule, last)["trades"]:
            by_day.setdefault(t["date"], []).append((t["signal_idx"], sym, t))
    trades = []
    for day in sorted(by_day):
        month = day[:7]
        if sum(x["net"] for x in trades if x["date"].startswith(month)) <= -MONTH_STOP:
            continue
        for _, sym, t in sorted(by_day[day], key=lambda x: (x[0], x[1])):  # earliest, then A-Z
            qty, ec = size(t["entry"], t["stop"], t["target"])
            if not qty:
                continue
            net = ec.net(t["exit"])
            gross = (t["exit"] - t["entry"]) * qty
            trades.append(dict(t, symbol=sym, qty=qty, gross=round(gross, 2),
                               charges=round(gross - net, 2), net=round(net, 2)))
            break
    return trades


def stats(trades):
    eq = peak = CAPITAL
    dd = 0.0
    for t in trades:
        eq += t["net"]
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    n = len(trades)
    return {"trades": n,
            "win_rate": round(100.0 * sum(1 for t in trades if t["net"] > 0) / n, 1) if n else 0.0,
            "gross": round(sum(t["gross"] for t in trades), 2),
            "charges": round(sum(t["charges"] for t in trades), 2),
            "net": round(sum(t["net"] for t in trades), 2),
            "max_drawdown": round(dd, 2), "end_equity": round(eq, 2),
            "exits": {k: sum(1 for t in trades if t["outcome"] == k) for k in ("target", "stop", "close")}}


def ours():
    path = os.path.join(ROOT, "reports", "backtest_trades.json")
    with open(path) as f:
        t = json.load(f)
    s = {"trades": len(t), "win_rate": round(100.0 * sum(1 for x in t if x["net"] > 0) / len(t), 1),
         "gross": round(sum(x["gross"] for x in t), 2), "charges": round(sum(x["charges"] for x in t), 2),
         "net": round(sum(x["net"] for x in t), 2)}
    eq = peak = CAPITAL
    dd = 0.0
    for x in t:
        eq += x["net"]
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    s.update(max_drawdown=round(dd, 2), end_equity=round(eq, 2),
             exits={"target": sum(1 for x in t if x["reason"] == "target"),
                    "stop": sum(1 for x in t if x["reason"] == "stop"),
                    "close": sum(1 for x in t if x["reason"] in ("time", "eod"))})
    months = {}
    for x in t:
        months[x["date"][:7]] = round(months.get(x["date"][:7], 0) + x["net"], 2)
    return s, months


def rs(x):
    return ("-Rs %s" if x < 0 else "Rs %s") % format(abs(x), ",.2f")


def main():
    syms = data.NIFTY50_FALLBACK
    raw, failed = data.fetch_all(syms, "60d")
    sessions = {s: full_sessions(days) for s, days in raw.items()}
    dates = sorted({d for v in sessions.values() for d, _ in v})
    if not dates:
        sys.exit("no usable sessions in the downloaded data; nothing written")
    filled = sum(1 for v in sessions.values() for _, D in v for b in D if b.get("filled"))
    results = {r: run(sessions, r) for r in (2.0, 1.0)}
    st = {r: stats(results[r]) for r in results}
    our, our_months = ours()

    cols = [("Our bot (2R, next-bar entry, Nifty filter)", our), ("dalal-street-skills rule, 2R", st[2.0]),
            ("dalal-street-skills rule, 1R", st[1.0])]
    rows = [("Trades", "trades", str), ("Win rate", "win_rate", lambda v: "%.1f%%" % v),
            ("Gross P&L", "gross", rs), ("Charges", "charges", rs), ("**Net P&L**", "net", lambda v: "**%s**" % rs(v)),
            ("Max drawdown", "max_drawdown", rs), ("Ending equity (from Rs 2,400)", "end_equity", rs),
            ("Exits: target / stop / close", "exits", lambda e: "%d / %d / %d" % (e["target"], e["stop"], e["close"]))]
    md = ["# Our bot vs the dalal-street-skills rule, same data", "",
          "Same 49 Nifty 50 stocks, same Yahoo 5-minute bars, %d complete sessions (%s to %s), %d symbols "
          "skipped. Same money rules for all: Rs 2,400 capital, 5x MIS, max 1 trade a day (earliest breakout), "
          "Rs 25 max loss per trade incl. charges, monthly stop at a Rs 500 loss."
          % (len(dates), dates[0] if dates else "-", dates[-1] if dates else "-", len(failed)), "",
          "Data gaps: Yahoo was missing %d five-minute bars across all stocks and days; each was filled "
          "with a flat bar at the previous close for the dalal rule (days missing more than %d bars "
          "before 15:10 were dropped)." % (filled, MAX_MISSING), "",
          "The dalal-street-skills rule is its own code (bot/dalal_port.py, copied from commit 6fcc8d4, MIT): "
          "15-minute opening range, stop at the range midpoint, exit at 15:10. Differences from our bot: it "
          "enters at the **signal bar's close** (ours waits for the next bar's open plus 0.05% slippage, so its "
          "fills are slightly more optimistic), it has no Nifty 50 market filter, and it counts a stop before "
          "a target inside the same bar, like ours.", "",
          "| | " + " | ".join(c[0] for c in cols) + " |", "|---|" + "---|" * len(cols)]
    for label, key, f in rows:
        md.append("| %s | %s |" % (label, " | ".join(f(c[1][key]) for c in cols)))
    months = sorted(set(our_months) | {t["date"][:7] for r in results.values() for t in r})
    md += ["", "## Net by month", "", "| Month | Our bot | dalal 2R | dalal 1R |", "|---|---|---|---|"]
    for m in months:
        md.append("| %s | %s | %s | %s |" % (m, rs(our_months.get(m, 0)),
                  rs(round(sum(t["net"] for t in results[2.0] if t["date"].startswith(m)), 2)),
                  rs(round(sum(t["net"] for t in results[1.0] if t["date"].startswith(m)), 2))))
    for r in (2.0, 1.0):
        md += ["", "## dalal-street-skills rule %gR: every trade" % r, ""]
        md += ["- %s %s: %d @ %.2f (%s), stop %.2f, target %.2f -> %.2f (%s). Net %s" % (
            t["date"], t["symbol"], t["qty"], t["entry"], t["time"], t["stop"], t["target"], t["exit"],
            t["outcome"], rs(t["net"])) for t in results[r]]
    md += ["", "Past results on 60 days of data do not predict future results."]
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    with open(os.path.join(ROOT, "reports", "dalal_backtest.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[:16 + len(rows)]))


if __name__ == "__main__":
    main()
