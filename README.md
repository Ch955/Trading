# Trading bot: NSE intraday, paper trading

A small, auditable bot that paper-trades one NSE intraday setup with Zerodha's real costs, so we
can find out whether it makes money **before** any real rupee is at risk.

**It never places a real order.** `config.json` must say `"mode": "paper"` or the script exits.

## The strategy (opening-range breakout, long only)

| Step | Rule |
|---|---|
| Universe | Nifty 100 stocks (list from NSE; falls back to Nifty 50) |
| Opening range | High and low of 09:15-09:30 (three 5-minute bars). Range must be 0.3%-2% of price |
| Market filter | Nifty 50 must be above its own opening-range midpoint |
| Signal | First 5-minute close above the range high, no later than the 10:55 bar |
| Entry | **Open of the next bar** + 0.05% slippage (never the signal bar's close) |
| Stop-loss | Midpoint of the opening range. If a bar gaps through it, we fill at that bar's open |
| Target | 2x the risk. If stop and target are touched in the same bar, we count the stop |
| Time exit | Flat at 15:10, before Zerodha's MIS auto square-off |
| Pick | At most **1 trade a day**: the earliest breakout, ties go to higher relative volume |

## Money rules

| Limit | Value |
|---|---|
| Capital | Rs 2,400, MIS leverage 5x (max position Rs 12,000) |
| Risk per trade | Rs 25, **including charges** |
| Daily loss limit | Rs 100 |
| Monthly loss limit | Rs 500, then no trades until next month |
| Safety stop | Equity below half of the starting capital stops everything |
| Not allowed | F&O, short selling, overnight positions |

Charges follow Zerodha's equity-intraday rates (brokerage 0.03% capped at Rs 20/order, STT 0.025% on
the sell, exchange fees, SEBI fee, stamp duty and 18% GST). Re-check them at zerodha.com/charges.

## Commands

```bash
python3 run.py backtest      # last ~60 trading days -> reports/backtest.md
python3 run.py paper-day     # today's paper trade (after 15:35 IST) -> state/ + reports/
python3 run.py summary       # running paper-trading totals
python3 -m unittest discover -s tests -v
```

Only the Python standard library is used. Data: Yahoo Finance 5-minute bars (unofficial, can lag)
and NSE's published Nifty 100 list. The cloud environment must allow `query1.finance.yahoo.com`
and `nsearchives.nseindia.com`.

## How it runs (your laptop and phone can be off)

A Claude cloud scheduled task runs on weekdays after the market closes. It runs
`paper-day`, commits `state/paper_ledger.json` and the report to this repo, and emails you the day's
result. Because each paper day only uses bars up to each decision point, running it once after the
close gives the same result as watching live.

## Going live (Phase 2, not built yet)

Only if paper trading shows a profit **after charges** over 3-4 weeks, and only when you say so.
That would use Zerodha's official Kite MCP connector (`https://mcp.kite.trade/mcp`), needs one Kite
login tap each morning, places a stop-loss order immediately after every entry, and keeps all the
limits above.

Not financial advice. Most intraday traders lose money. Past results do not predict future ones.
