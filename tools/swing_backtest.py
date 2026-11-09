#!/usr/bin/env python3
"""Swing-trading backtest (delivery, Zerodha CNC charges) on ~5 years of daily candles.

  python3 tools/swing_backtest.py      # needs network; writes reports/swing_backtest.md
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from bot import data, swing  # noqa: E402

CAPITAL, MONTH_STOP = 2400, 500


def rs(x):
    return ("-Rs %s" if x < 0 else "Rs %s") % format(abs(x), ",.2f")


def main():
    syms = data.NIFTY50_FALLBACK
    daily, failed = data.fetch_all(syms, "5y", fetch=data.fetch_daily)
    try:
        bench = data.fetch_daily("NIFTYBEES.NS", "5y")
    except Exception as e:
        print("NIFTYBEES unavailable: %s" % e)
        bench = []
    # Start trading once a 200-day average exists for most stocks.
    lens = sorted(len(v) for v in daily.values())
    if not lens or lens[len(lens) // 2] < 260:
        sys.exit("not enough daily history downloaded; nothing written")
    all_days = sorted({b["d"] for v in daily.values() for b in v})
    start = all_days[200]

    res = {}
    for setup in ("breakout", "pullback"):
        trades, curve = swing.backtest(daily, setup, CAPITAL, monthly_loss_limit=MONTH_STOP, start_date=start)
        res[setup] = (trades, swing.summary(trades, curve, CAPITAL))
    bh = swing.buy_and_hold(bench, CAPITAL, start_date=start) if bench else None

    years = sorted({y for _, s in res.values() for y in s["by_year"]})
    md = ["# Swing-trading backtest: Nifty 50 stocks, delivery (CNC), Rs 2,400", "",
          "Generated %s IST. Daily candles from Yahoo Finance for %d stocks (%d skipped), trading from %s to %s "
          "(the first 200 days are only used to warm up the averages)." % (
              dt.datetime.now(data.IST).strftime("%Y-%m-%d %H:%M"), len(daily), len(failed), start, all_days[-1]),
          "",
          "Same rules for both setups: one stock at a time, buy with all available money (no leverage), "
          "orders fill at the next day's open with 0.1% slippage, Zerodha delivery charges including the "
          "Rs 15.34 DP charge on every sale, and no new buys for the rest of a month once that month loses "
          "Rs 500. Rules were fixed before running (see bot/swing.py); nothing was tuned on this data.", "",
          "| | Breakout (20-day high, uptrend) | Pullback (RSI-2 dip, uptrend) | Buy and hold NIFTYBEES |",
          "|---|---|---|---|"]
    b, p = res["breakout"][1], res["pullback"][1]
    bh_net = bh["net"] if bh else None
    rows = [("Trades", b["trades"], p["trades"], 1 if bh else "-"),
            ("Win rate", "%.1f%%" % b["win_rate"], "%.1f%%" % p["win_rate"], "-"),
            ("Average days held", b["avg_days"], p["avg_days"], "whole period" if bh else "-"),
            ("Gross P&L", rs(b["gross"]), rs(p["gross"]), "-"),
            ("Charges", rs(b["charges"]), rs(p["charges"]), rs(bh["charges"]) if bh else "-"),
            ("**Net P&L**", "**%s**" % rs(b["net"]), "**%s**" % rs(p["net"]),
             "**%s**" % rs(bh_net) if bh else "-"),
            ("Ending money (from Rs 2,400)", rs(b["end_equity"]), rs(p["end_equity"]),
             rs(CAPITAL + bh_net) if bh else "-"),
            ("Worst drop from peak", rs(b["max_drawdown"]), rs(p["max_drawdown"]), "-")]
    md += ["| %s | %s | %s | %s |" % r for r in rows]
    md += ["", "## Net by year", "", "| Year | Breakout | Pullback |", "|---|---|---|"]
    md += ["| %s | %s | %s |" % (y, rs(b["by_year"].get(y, 0)), rs(p["by_year"].get(y, 0))) for y in years]
    md += ["", "Caveats: the stock list is today's Nifty 50, so stocks that dropped out of the index over "
           "these years are missing (this flatters every result a little). Yahoo's daily data is unofficial. "
           "Past results do not predict future results."]
    for setup in ("breakout", "pullback"):
        md += ["", "## %s: every trade" % setup.capitalize(), ""]
        md += ["- %s -> %s %s: %d @ %.2f -> %.2f (%s, %d days). Net %s" % (
            t["entry_date"], t["exit_date"], t["symbol"], t["qty"], t["entry"], t["exit"], t["reason"],
            t["days"], rs(t["net"])) for t in res[setup][0]]
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    with open(os.path.join(ROOT, "reports", "swing_backtest.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(ROOT, "reports", "swing_trades.json"), "w") as f:
        json.dump({k: v[0] for k, v in res.items()}, f, indent=1)
    print("\n".join(md[:22 + len(years)]))


if __name__ == "__main__":
    main()
