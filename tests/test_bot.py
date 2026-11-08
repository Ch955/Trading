import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import charges, data, engine, strategy  # noqa: E402

with open(os.path.join(os.path.dirname(__file__), "..", "config.json")) as f:
    CFG = json.load(f)


def times():
    h, m, out = 9, 15, []
    while (h, m) <= (15, 25):
        out.append("%02d:%02d" % (h, m))
        m += 5
        if m == 60:
            h, m = h + 1, 0
    return out


def make_day(path):
    """path: list of (o, h, l, c) for the first bars; remaining bars flat at the last close."""
    ts = times()
    bars = []
    for i, t in enumerate(ts):
        if i < len(path):
            o, h, l, c = path[i]
        else:
            c = path[-1][3]
            o, h, l = c, c, c
        bars.append({"t": t, "o": o, "h": h, "l": l, "c": c, "v": 1000})
    return bars


OR = [(100, 101, 99.5, 100.5), (100.5, 101, 100, 100.8), (100.8, 101, 100.2, 100.6)]  # ORH 101, ORL 99.5


class Charges(unittest.TestCase):
    def test_round_trip_12k(self):
        # Rs 12,000 bought and sold flat: brokerage 7.2, STT 3, exch .71, stamp .36, GST ~1.43
        total = charges.round_trip(100, 120, 120, CFG["charges"])
        self.assertAlmostEqual(total, 12.73, delta=0.05)

    def test_brokerage_cap(self):
        total = charges.round_trip(1000, 1000, 1000, CFG["charges"])  # Rs 10 lakh each side
        self.assertLess(total, 20 * 2 * 1.18 + 1000 + 100)  # brokerage capped at Rs 20/order


class Strategy(unittest.TestCase):
    def test_target_hit(self):
        bars = make_day(OR + [(100.6, 101.5, 100.6, 101.4),   # 09:30 closes above 101 -> signal
                              (101.4, 101.6, 101.3, 101.5),   # entry at open 101.4
                              (101.5, 104.0, 101.4, 103.9)])  # target hit
        sig = strategy.find_signal(bars, CFG["strategy"])
        self.assertEqual(sig["signal_time"], "09:30")
        self.assertEqual(sig["stop"], 100.25)
        sim = strategy.simulate(bars, sig, CFG["strategy"], 0)
        self.assertEqual(sim["entry_time"], "09:35")
        self.assertEqual(sim["entry"], 101.4)
        self.assertEqual(sim["reason"], "target")
        self.assertAlmostEqual(sim["exit"], 101.4 + 2 * (101.4 - 100.25), places=2)

    def test_stop_wins_when_both_touched(self):
        bars = make_day(OR + [(100.6, 101.5, 100.6, 101.4), (101.4, 101.6, 101.3, 101.5),
                              (101.5, 110, 90, 101)])
        sig = strategy.find_signal(bars, CFG["strategy"])
        sim = strategy.simulate(bars, sig, CFG["strategy"], 0)
        self.assertEqual(sim["reason"], "stop")

    def test_gap_through_stop_fills_at_open(self):
        bars = make_day(OR + [(100.6, 101.5, 100.6, 101.4), (101.4, 101.6, 101.3, 101.5),
                              (99.0, 99.2, 98.5, 99.0)])
        sig = strategy.find_signal(bars, CFG["strategy"])
        sim = strategy.simulate(bars, sig, CFG["strategy"], 0)
        self.assertEqual((sim["reason"], sim["exit"]), ("stop", 99.0))

    def test_time_exit(self):
        bars = make_day(OR + [(100.6, 101.5, 100.6, 101.4), (101.4, 101.6, 101.3, 101.5)])
        sig = strategy.find_signal(bars, CFG["strategy"])
        sim = strategy.simulate(bars, sig, CFG["strategy"], 0)
        self.assertEqual((sim["reason"], sim["exit_time"]), ("time", "15:10"))

    def test_no_signal_after_cutoff(self):
        bars = make_day(OR)
        for b in bars:
            if b["t"] >= "11:00":
                b.update(h=105, c=104)
        self.assertIsNone(strategy.find_signal(bars, CFG["strategy"]))

    def test_range_too_wide(self):
        wide = [(100, 106, 99, 100), (100, 101, 100, 100), (100, 101, 100, 100)]
        self.assertIsNone(strategy.find_signal(make_day(wide + [(100, 107, 100, 107)]), CFG["strategy"]))


class Engine(unittest.TestCase):
    def test_size_respects_risk_and_margin(self):
        qty, loss = engine.size(101.4, 100.25, CFG)
        self.assertGreaterEqual(qty, 1)
        self.assertLessEqual(loss, CFG["risk_per_trade"])
        self.assertLessEqual(qty * 101.4, CFG["capital"] * CFG["mis_leverage"])

    def test_size_zero_when_stop_too_wide(self):
        self.assertEqual(engine.size(1000, 960, CFG)[0], 0)

    def test_monthly_kill_switch(self):
        trades = [{"date": "2026-11-03", "net": -260}, {"date": "2026-11-04", "net": -250}]
        self.assertIn("monthly", engine.blocked(trades, "2026-11-05", CFG))
        self.assertIsNone(engine.blocked(trades, "2026-12-01", CFG))

    def test_one_trade_per_day(self):
        self.assertIn("already", engine.blocked([{"date": "2026-11-05", "net": 5}], "2026-11-05", CFG))

    def test_pick_trade_end_to_end(self):
        win = make_day(OR + [(100.6, 101.5, 100.6, 101.4), (101.4, 101.6, 101.3, 101.5),
                             (101.5, 104.0, 101.4, 103.9)])
        flat = make_day(OR)
        t, _ = engine.pick_trade("2026-11-06", {"AAA": {"2026-11-06": win},
                                                "BBB": {"2026-11-06": flat}}, {}, CFG)
        self.assertEqual(t["symbol"], "AAA")
        self.assertEqual(t["reason"], "target")
        self.assertLessEqual(t["max_loss"], CFG["risk_per_trade"])
        self.assertAlmostEqual(t["net"], t["gross"] - t["charges"], places=2)

    def test_index_filter_uses_that_days_bars(self):
        day = "2026-11-06"
        win = make_day(OR + [(100.6, 101.5, 100.6, 101.4), (101.4, 101.6, 101.3, 101.5),
                             (101.5, 104.0, 101.4, 103.9)])
        index_up = make_day(OR + [(100.6, 101.5, 100.6, 101.4)])     # above its OR mid at 09:30
        index_down = make_day(OR + [(100.6, 100.6, 99.0, 99.2)])     # below its OR mid at 09:30
        stocks = {"AAA": {day: win}}
        t, _ = engine.pick_trade(day, stocks, {day: index_up, "2026-11-05": index_down}, CFG)
        self.assertEqual(t["symbol"], "AAA")
        t, _ = engine.pick_trade(day, stocks, {day: index_down, "2026-11-05": index_up}, CFG)
        self.assertIsNone(t)
        t, _ = engine.pick_trade(day, stocks, {}, CFG)  # no index data -> filter doesn't block
        self.assertEqual(t["symbol"], "AAA")


class Data(unittest.TestCase):
    def test_parse_chart_ist(self):
        # 2026-11-06 03:45 UTC = 09:15 IST
        payload = {"chart": {"result": [{"timestamp": [1793936700, 1793937000],
                   "indicators": {"quote": [{"open": [1, None], "high": [2, 2], "low": [0.5, 1],
                                             "close": [1.5, 1.5], "volume": [10, 10]}]}}]}}
        days = data.parse_chart(payload)
        self.assertEqual(list(days), ["2026-11-06"])
        self.assertEqual(days["2026-11-06"][0]["t"], "09:15")
        self.assertEqual(len(days["2026-11-06"]), 1)  # bar with None open dropped


if __name__ == "__main__":
    unittest.main()
