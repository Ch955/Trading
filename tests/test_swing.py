import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import charges, data, swing  # noqa: E402


def series(closes, start="2024-01-01", spread=1.0):
    d0 = dt.date.fromisoformat(start)
    out = []
    prev = closes[0]
    for i, c in enumerate(closes):
        o = prev
        out.append({"d": (d0 + dt.timedelta(days=i)).isoformat(), "o": o, "h": max(o, c) + spread,
                    "l": min(o, c) - spread, "c": c, "v": 1000})
        prev = c
    return out


class Charges(unittest.TestCase):
    def test_cnc_small_trade_dominated_by_dp(self):
        # 10 shares at Rs 200 -> Rs 2,000 each way: STT Rs 4, stamp Rs 0.30, DP Rs 15.34
        total = charges.round_trip_cnc(10, 200, 200)
        self.assertAlmostEqual(total, 4 + 0.30 + 15.34 + 0.12 + 0.004 + 0.02, delta=0.05)


class Indicators(unittest.TestCase):
    def test_sma_rsi_atr(self):
        closes = [10, 11, 12, 13, 14]
        self.assertEqual(swing.sma(closes, 5, 4), 12)
        self.assertIsNone(swing.sma(closes, 5, 3))
        self.assertEqual(swing.rsi(closes, 2, 4), 100.0)
        self.assertAlmostEqual(swing.rsi([10, 11, 10], 2, 2), 50.0)
        bars = series([100] * 20, spread=1.0)
        self.assertAlmostEqual(swing.atr(bars, 14, 19), 2.0)

    def test_no_lookahead_in_channel(self):
        bars = series(list(range(100, 130)))
        ind = swing.indicators(bars)
        self.assertEqual(ind[25]["hh20"], max(b["h"] for b in bars[5:25]))  # excludes day 25 itself


class Backtest(unittest.TestCase):
    def test_breakout_enters_next_open_and_stops_out(self):
        closes = [100 + 0.1 * i for i in range(260)] + [140, 141, 90]   # uptrend, breakout, crash
        daily = {"AAA": series(closes)}
        trades, _ = swing.backtest(daily, "breakout", capital=100000, slippage_pct=0)
        self.assertTrue(trades)
        t = trades[-1]
        self.assertEqual(t["reason"], "stop")
        self.assertLess(t["net"], 0)
        by_date = {b["d"]: b for b in daily["AAA"]}
        days = [b["d"] for b in daily["AAA"]]
        for tr in trades:
            # fills at that day's open, and the day before it was a signal day
            self.assertAlmostEqual(tr["entry"], by_date[tr["entry_date"]]["o"], places=2)
            i = days.index(tr["entry_date"])
            ind = swing.indicators(daily["AAA"])[i - 1]
            self.assertTrue(swing.entry_signal("breakout", daily["AAA"][i - 1], ind)[0])

    def test_skips_stock_priced_above_capital(self):
        closes = [3000 + i for i in range(270)]
        trades, _ = swing.backtest({"BIG": series(closes)}, "breakout", capital=2400)
        self.assertEqual(trades, [])

    def test_monthly_limit_blocks_new_entries(self):
        # rising trend with a breakout and a crash early in a month, then more breakouts
        closes = [100 + 0.1 * i for i in range(260)] + [140, 141, 90] + [91 + i for i in range(10)]
        daily = {"AAA": series(closes, start="2024-01-01")}
        free, _ = swing.backtest(daily, "breakout", capital=100000, slippage_pct=0, monthly_loss_limit=10**9)
        capped, _ = swing.backtest(daily, "breakout", capital=100000, slippage_pct=0, monthly_loss_limit=1)
        loss_month = next(t["exit_date"][:7] for t in capped if t["net"] < 0)
        after = [t for t in capped if t["entry_date"][:7] == loss_month
                 and t["entry_date"] > next(x["exit_date"] for x in capped if x["net"] < 0)]
        self.assertEqual(after, [])
        self.assertGreaterEqual(len(free), len(capped))


class DailyParse(unittest.TestCase):
    def test_parse_daily(self):
        payload = {"chart": {"result": [{"timestamp": [1793936700, 1794023100],
                   "indicators": {"quote": [{"open": [1, 2], "high": [2, 3], "low": [0.5, 1.5],
                                             "close": [1.5, None], "volume": [10, 10]}]}}]}}
        bars = data.parse_daily(payload)
        self.assertEqual([b["d"] for b in bars], ["2026-11-06"])


if __name__ == "__main__":
    unittest.main()
