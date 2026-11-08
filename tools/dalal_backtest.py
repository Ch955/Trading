#!/usr/bin/env python3
"""Backtest the dalal-street-skills ORB rule with ITS OWN code, on the same data as our bot.

    python3 tools/dalal_backtest.py /path/to/dalal-street-skills-clone

Backtest only: this reads public Yahoo 5-minute bars through the clone's own
nse-timemachine/timemachine.py (fetch_chart / parse_bars / split_sessions /
full_sessions), runs its history_replay (orb, 15-minute opening range, stop
or_mid, exit at the 15:10 bar) and prices every trade with its Econ class
(Zerodha MIS charges). It never places orders and never talks to a broker.

On top of the per-stock replay sits a portfolio layer with our bot's rules:
  * at most 1 trade a day: the earliest trigger across the universe, ties
    alphabetical; a stock whose qty comes out < 1 is skipped for the next one
    (as bot/engine.py does);
  * qty = largest whole number with loss at the stop incl. charges <= Rs 25
    and qty x entry <= capital x MIS leverage (Rs 2,400 x 5 = Rs 12,000);
  * no more trades in a month once that month's net P&L reaches -Rs 500.

The clone is imported by path and never modified.
"""

import argparse
import datetime
import importlib.util
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from bot.data import NIFTY50_FALLBACK  # noqa: E402

CAPITAL = 2400.0
LEVERAGE = 5
RISK = 25.0
MONTHLY_LIMIT = 500.0
START, END = "2026-08-12", "2026-11-06"     # the window of reports/backtest.md
CFG = {"broker": "zerodha"}                 # timemachine's Zerodha profile (also its default)


def load_tm(clone):
    path = os.path.join(clone, "nse-timemachine", "timemachine.py")
    spec = importlib.util.spec_from_file_location("dalal_timemachine", path)
    tm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tm)
    return tm


def clone_commit(clone):
    try:
        return subprocess.check_output(["git", "-C", clone, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def fetch_sessions(tm, symbols, start, end, log):
    """{sym: [(date, [72 bars])]} of full sessions in [start, end], via timemachine's own functions."""
    before = (datetime.date.fromisoformat(end) + datetime.timedelta(days=1)).isoformat()
    now = tm.utc_now()
    out, errors = {}, {}
    for sym in symbols:
        try:
            text = tm.fetch_chart(sym + ".NS")
            meta, bars, dropped = tm.parse_bars(tm.chart_result(text, sym), now)
            full, short = tm.full_sessions(tm.split_sessions(bars), before)
            out[sym] = [(d, D) for d, D in full if d >= start]
            log("  %-11s %d full sessions (%d short left out)" % (sym, len(out[sym]), len(short)))
        except Exception as e:  # keep going; report it
            errors[sym] = str(e)
            log("  %-11s ERROR %s" % (sym, e))
        time.sleep(0.3)
    return out, errors


def size(tm, entry, stop, target):
    """Largest qty with risk_cash (loss at stop incl. charges, from Econ) <= RISK and value <= margin."""
    per = entry - stop
    qty = min(int(CAPITAL * LEVERAGE // entry), int(RISK // per) if per > 0 else 0)
    while qty > 0:
        ec = tm.Econ(entry, stop, target, qty, "buy", "MIS", "NSE", CFG)
        if ec.risk_cash <= RISK + 1e-9:
            return qty, ec
        qty -= 1
    return 0, None


def run(tm, sessions, target_r, last):
    rule = {"or_minutes": 15, "stop_rule": "or_mid", "target_r": target_r}
    cost = {"qty": 1, "product": "MIS", "exchange": "NSE", "cfg": CFG}
    closes = {}
    by_day = {}
    for sym, sess in sessions.items():
        for d, D in sess:
            closes[(sym, d)] = D[last]["c"]
        res = tm.history_replay(sess, rule, last, side="buy", cost=cost)
        for t in res["trades"]:
            by_day.setdefault(t["date"], []).append(dict(t, symbol=sym))
    days = sorted({d for sess in sessions.values() for d, _ in sess})
    trades, log = [], []
    for day in days:
        month = day[:7]
        mnet = sum(t["net"] for t in trades if t["date"].startswith(month))
        if mnet <= -MONTHLY_LIMIT:
            log.append((day, "monthly loss limit reached"))
            continue
        cands = sorted(by_day.get(day, []), key=lambda t: (t["time"], t["symbol"]))
        if not cands:
            log.append((day, "no trigger"))
            continue
        for c in cands:
            qty, ec = size(tm, c["entry"], c["stop"], c["target"])
            if qty < 1:
                continue
            exit_px = {"target": c["target"], "stop": c["stop"]}.get(c["outcome"], closes[(c["symbol"], day)])
            gross = (exit_px - c["entry"]) * qty
            fees = ec.fees(exit_px)
            trades.append(dict(c, qty=qty, exit=exit_px, gross=round(gross, 2), charges=fees,
                               net=round(ec.net(exit_px), 2), risk_cash=round(ec.risk_cash, 2)))
            log.append((day, "trade"))
            break
        else:
            log.append((day, "%d triggers, none sizable (qty < 1)" % len(cands)))
    return trades, log, len(days)


def stats(trades):
    eq, peak, mdd = CAPITAL, CAPITAL, 0.0
    for t in trades:
        eq += t["net"]
        peak = max(peak, eq)
        mdd = max(mdd, peak - eq)
    months = {}
    for t in trades:
        m = months.setdefault(t["date"][:7], [0, 0.0])
        m[0] += 1
        m[1] += t["net"]
    return {
        "trades": len(trades),
        "win_rate": 100.0 * sum(1 for t in trades if t["net"] > 0) / len(trades) if trades else 0.0,
        "gross": sum(t["gross"] for t in trades), "charges": sum(t["charges"] for t in trades),
        "net": sum(t["net"] for t in trades), "mdd": mdd, "equity": eq, "months": months,
        "exits": {k: sum(1 for t in trades if t["outcome"] == k) for k in ("stop", "target", "close")},
    }


def rs(x):
    return ("-Rs %s" if x < 0 else "Rs %s") % format(abs(x), ",.2f")


# Our bot's numbers, copied from reports/backtest.md (generated by run.py backtest, same window).
OURS = {"trades": 45, "win_rate": 28.9, "gross": -277.03, "charges": 137.74, "net": -414.77,
        "mdd": 474.52, "equity": 1985.23,
        "exits": "stop 25, target 6, time 14",
        "months": {"2026-08": (8, -167.42), "2026-09": (15, -160.12), "2026-10": (17, -134.68),
                   "2026-11": (5, 47.45)}}


def report(results, commit, n_days, errors, sessions, tm_path):
    s2, s1 = results[2.0][0], results[1.0][0]
    L = []
    L.append("# Backtest: dalal-street-skills ORB rule vs our bot, same data")
    L.append("")
    L.append("Generated %s IST by `tools/dalal_backtest.py`. Backtest only, no orders, no broker."
             % (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M"))
    L.append("")
    L.append("- Third-party code: https://github.com/Adityaraj0421/dalal-street-skills (MIT), "
             "commit `%s`, file `nse-timemachine/timemachine.py`, run unmodified." % commit)
    L.append("- Its functions used: `fetch_chart`, `parse_bars`, `split_sessions`, `full_sessions` "
             "(data), `history_replay` (the trade rule), `Econ` / `trade_charges` (Zerodha MIS charges).")
    L.append("- Rule: `orb`, 15-minute opening range, `stop_rule` `or_mid`, `last` = the 15:10 bar "
             "(slot 71), long only. Run twice: `target_r` 2.0 and 1.0.")
    L.append("- Data: Yahoo Finance 5-minute bars (range=60d), full sessions %s to %s (%d trading days), "
             "the 49 symbols of `NIFTY50_FALLBACK` in `bot/data.py`; %d symbols failed to load%s."
             % (START, END, n_days, len(errors), (": " + ", ".join(sorted(errors))) if errors else ""))
    L.append("- Portfolio layer (ours): 1 trade a day max, earliest trigger across stocks (ties "
             "alphabetical); qty = largest whole number with loss at the stop incl. charges <= Rs 25 "
             "(Econ's `risk_cash`) and qty x entry <= Rs 12,000 (Rs 2,400 x 5 MIS); a stock with qty < 1 "
             "is skipped for the next trigger; no more trades in a month once its net reaches -Rs 500. "
             "Start equity Rs 2,400.")
    L.append("")
    L.append("## Side by side")
    L.append("")
    L.append("| | Our bot (reports/backtest.md) | dalal, target 2.0R | dalal, target 1.0R |")
    L.append("|---|---|---|---|")
    rows = [("Trades", lambda s: str(s["trades"])),
            ("Win rate", lambda s: "%.1f%%" % s["win_rate"]),
            ("Gross P&L", lambda s: rs(s["gross"])),
            ("Charges", lambda s: rs(s["charges"])),
            ("**Net P&L**", lambda s: "**%s**" % rs(s["net"])),
            ("Max drawdown", lambda s: rs(s["mdd"])),
            ("Ending equity", lambda s: rs(s["equity"]))]
    for name, f in rows:
        L.append("| %s | %s | %s | %s |" % (name, f(OURS), f(s2), f(s1)))
    ex = lambda s: "stop %d, target %d, time %d" % (s["exits"]["stop"], s["exits"]["target"], s["exits"]["close"])
    L.append("| Exits | %s | %s | %s |" % (OURS["exits"], ex(s2), ex(s1)))
    L.append("")
    L.append("## By month (trades / net)")
    L.append("")
    L.append("| Month | Our bot | dalal 2.0R | dalal 1.0R |")
    L.append("|---|---|---|---|")
    months = sorted(set(OURS["months"]) | set(s2["months"]) | set(s1["months"]))
    cell = lambda m, d: "%d / %s" % (d[m][0], rs(d[m][1])) if m in d else "0 / Rs 0.00"
    for m in months:
        L.append("| %s | %s | %s | %s |" % (m, cell(m, OURS["months"]), cell(m, s2["months"]), cell(m, s1["months"])))
    L.append("")
    L.append("## Why the numbers differ")
    L.append("")
    L.append("- **Entry price.** dalal's `history_replay` enters at the signal bar's own close (rounded up "
             "to the 0.05 tick). Our bot enters at the next bar's open plus 0.05%% slippage. dalal's fills "
             "are therefore slightly more optimistic.")
    L.append("- **Filters.** dalal's rule has none of our filters: no 0.3%%-2.0%% opening-range width band, "
             "no 10:55 last-entry cut-off (it accepts a trigger up to the 15:10 bar), no Nifty index filter, "
             "no Rs 50 minimum price, no Rs 100 daily loss limit (irrelevant at 1 trade/day).")
    L.append("- **Tie-break.** Ours ranks same-time signals by relative volume; here ties are alphabetical.")
    L.append("- **Charges.** dalal's Zerodha profile uses an NSE transaction charge of 0.00307%% vs our "
             "0.00297%%; the rest (0.03%% brokerage capped at Rs 20, 0.025%% STT sell, 0.003%% stamp buy, "
             "SEBI Rs 10/crore, 18%% GST) is the same.")
    L.append("- **Exit fills.** dalal books a stop or target at exactly that price (stop first if a bar "
             "touches both, like ours); otherwise the 15:10 bar's close.")
    for tr in (2.0, 1.0):
        trades, log = results[tr][1], results[tr][2]
        L.append("")
        L.append("## Every trade, target %.1fR" % tr)
        L.append("")
        tlist = {t["date"]: t for t in trades}
        for day, what in log:
            t = tlist.get(day) if what == "trade" else None
            if t:
                L.append("- %s %s: bought %d @ %.2f (signal close, %s), stop %.2f, target %.2f -> %s @ %.2f. "
                         "Gross %s, charges %s, net %s"
                         % (day, t["symbol"], t["qty"], t["entry"], t["time"], t["stop"], t["target"],
                            t["outcome"], t["exit"], rs(t["gross"]), rs(t["charges"]), rs(t["net"])))
            else:
                L.append("- %s: no trade (%s)" % (day, what))
    L.append("")
    L.append("Past results on 60 days of data do not predict future results.")
    L.append("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("clone", help="path to a clone of Adityaraj0421/dalal-street-skills")
    ap.add_argument("--out", default=os.path.join(ROOT, "reports", "dalal_backtest.md"))
    a = ap.parse_args(argv)
    tm = load_tm(a.clone)
    last = tm.SESSION_BARS - 1
    assert tm.clock24(tm.OPEN_MIN + 5 * last) == "15:10", "slot %d is not the 15:10 bar" % last
    commit = clone_commit(a.clone)
    print("dalal-street-skills commit %s; fetching %d symbols" % (commit, len(NIFTY50_FALLBACK)))
    sessions, errors = fetch_sessions(tm, NIFTY50_FALLBACK, START, END, print)
    results = {}
    for tr in (2.0, 1.0):
        trades, log, n_days = run(tm, sessions, tr, last)
        results[tr] = (stats(trades), trades, log)
        s = results[tr][0]
        print("target %.1fR: %d trades, win %.1f%%, net %s, equity %s"
              % (tr, s["trades"], s["win_rate"], rs(s["net"]), rs(s["equity"])))
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(report(results, commit, n_days, errors, sessions, a.clone))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
