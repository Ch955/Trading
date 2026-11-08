#!/usr/bin/env python3
"""Paper-trading bot for NSE intraday (Zerodha costs). No real orders are ever placed.

  python3 run.py backtest          # last ~60 trading days, writes reports/backtest.md
  python3 run.py paper-day         # today's paper trade (run after 15:35 IST)
  python3 run.py paper-day --date 2026-11-06
  python3 run.py summary           # print the running paper-trading summary
"""
import argparse
import datetime as dt
import json
import os
import sys

from bot import data, engine

ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(ROOT, "state", "paper_ledger.json")
REPORTS = os.path.join(ROOT, "reports")


def load_cfg():
    with open(os.path.join(ROOT, "config.json")) as f:
        cfg = json.load(f)
    if cfg.get("mode") != "paper":
        sys.exit("config.json mode must be 'paper'. Live trading is not implemented in this script.")
    return cfg


def load_ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            return json.load(f)
    return {"trades": [], "days": {}}


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def get_market(range_):
    syms, src = data.universe()
    print("universe: %s (%d symbols)" % (src, len(syms)))
    bars, failed = data.fetch_all(syms, range_)
    try:
        index_bars = data.fetch_bars("^NSEI", range_)
    except Exception as e:
        print("  Nifty 50 index unavailable (%s); index filter off" % e)
        index_bars = {}
    return bars, index_bars, src, failed


def trade_line(t):
    return ("%s %s: bought %d @ %.2f (%s), stop %.2f, target %.2f -> sold @ %.2f (%s, %s). "
            "Gross %s, charges %s, net %s"
            % (t["date"], t["symbol"], t["qty"], t["entry"], t["entry_time"], t["stop"], t["target"],
               t["exit"], t["exit_time"], t["reason"], engine.fmt_inr(t["gross"]),
               engine.fmt_inr(t["charges"]), engine.fmt_inr(t["net"])))


def stats_md(st, cfg):
    return "\n".join([
        "| | |", "|---|---|",
        "| Starting capital | %s |" % engine.fmt_inr(cfg["capital"]),
        "| Trades | %d |" % st["trades"],
        "| Win rate | %.1f%% |" % st["win_rate"],
        "| Gross P&L | %s |" % engine.fmt_inr(st["gross"]),
        "| Charges paid | %s |" % engine.fmt_inr(st["charges"]),
        "| **Net P&L** | **%s** |" % engine.fmt_inr(st["net"]),
        "| Max drawdown | %s |" % engine.fmt_inr(st["max_drawdown"]),
        "| Ending equity | %s |" % engine.fmt_inr(st["end_equity"]),
        "| Exits | %s |" % ", ".join("%s %d" % kv for kv in st["by_reason"].items()),
    ])


def cmd_backtest(_args):
    cfg = load_cfg()
    bars, index_bars, src, failed = get_market("60d")
    days = sorted(index_bars) or sorted({d for v in bars.values() for d in v})
    trades, log = [], []
    for day in days:
        why = engine.blocked(trades, day, cfg)
        if why:
            log.append("%s: no trade (%s)" % (day, why))
            continue
        t, notes = engine.pick_trade(day, bars, index_bars, cfg)
        if t:
            trades.append(t)
            log.append(trade_line(t))
        else:
            log.append("%s: no trade (%s)" % (day, "; ".join(notes)))
    st = engine.stats(trades, cfg)
    months = sorted({t["date"][:7] for t in trades})
    md = ["# Backtest: opening-range breakout, Nifty 100, Zerodha intraday costs", "",
          "Generated %s IST. Data: Yahoo Finance 5-minute bars, %d trading days (%s to %s). "
          "Universe: %s, %d symbols skipped." % (
              dt.datetime.now(data.IST).strftime("%Y-%m-%d %H:%M"), len(days),
              days[0] if days else "-", days[-1] if days else "-", src, len(failed)), "",
          "Rules: 1 trade a day max, risk %s per trade including charges, capital %s with %dx MIS, "
          "monthly stop at %s loss. Entry at the next bar's open plus %.2f%% slippage." % (
              engine.fmt_inr(cfg["risk_per_trade"]), engine.fmt_inr(cfg["capital"]),
              cfg["mis_leverage"], engine.fmt_inr(-cfg["monthly_loss_limit"]), cfg["slippage_pct"]),
          "", stats_md(st, cfg), "", "## By month", "", "| Month | Trades | Net |", "|---|---|---|"]
    for m in months:
        mt = [t for t in trades if t["date"].startswith(m)]
        md.append("| %s | %d | %s |" % (m, len(mt), engine.fmt_inr(engine.month_pnl(trades, m))))
    md += ["", "## Every day", ""] + ["- " + x for x in log]
    md += ["", "Past results on 60 days of data do not predict future results."]
    write(os.path.join(REPORTS, "backtest.md"), "\n".join(md) + "\n")
    save_json(os.path.join(REPORTS, "backtest_trades.json"), trades)
    print("\n".join(md[:24]))


def cmd_paper_day(args):
    cfg = load_cfg()
    day = args.date or dt.datetime.now(data.IST).strftime("%Y-%m-%d")
    led = load_ledger()
    if day in led["days"]:
        print("%s already recorded: %s" % (day, led["days"][day]))
        return
    why = engine.blocked(led["trades"], day, cfg)
    if why:
        status, t = "no trade (%s)" % why, None
    else:
        bars, index_bars, _src, _failed = get_market("5d")
        if day not in index_bars and not any(day in v for v in bars.values()):
            print("%s: no market data (holiday or weekend). Nothing recorded." % day)
            return
        t, notes = engine.pick_trade(day, bars, index_bars, cfg)
        status = trade_line(t) if t else "no trade (%s)" % "; ".join(notes)
    if t:
        led["trades"].append(t)
    led["days"][day] = status
    save_json(LEDGER, led)

    st = engine.stats(led["trades"], cfg)
    month = day[:7]
    report = "\n".join([
        "# Paper trading report, %s" % day, "",
        "**Today:** %s" % status, "",
        "**This month (%s):** net %s of the %s loss limit" % (
            month, engine.fmt_inr(engine.month_pnl(led["trades"], month)),
            engine.fmt_inr(-cfg["monthly_loss_limit"])), "",
        "## Since paper trading started", "", stats_md(st, cfg), "",
        "Paper trading only: no real order was placed.",
    ]) + "\n"
    write(os.path.join(REPORTS, "daily", day + ".md"), report)
    write(os.path.join(REPORTS, "summary.md"), report)
    print(report)


def cmd_summary(_args):
    cfg = load_cfg()
    led = load_ledger()
    print(stats_md(engine.stats(led["trades"], cfg), cfg))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("backtest").set_defaults(fn=cmd_backtest)
    pd = sub.add_parser("paper-day")
    pd.add_argument("--date", help="YYYY-MM-DD (default: today in IST)")
    pd.set_defaults(fn=cmd_paper_day)
    sub.add_parser("summary").set_defaults(fn=cmd_summary)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
