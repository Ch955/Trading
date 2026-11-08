"""Market data: NSE 5-minute bars from Yahoo Finance, Nifty 100 list from NSE archives.

Bars are dicts: {"t": "HH:MM" (IST bar start), "o", "h", "l", "c", "v"}.
`fetch_bars` returns {"YYYY-MM-DD": [bars...]} for each trading day in range.
"""
import csv
import datetime as dt
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
UA = {"User-Agent": "Mozilla/5.0 (paper-trading-bot)"}

NIFTY100_URL = "https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv"

# Fallback if the NSE list can't be fetched. Symbols that no longer exist are skipped.
NIFTY50_FALLBACK = """ADANIENT ADANIPORTS APOLLOHOSP ASIANPAINT AXISBANK BAJAJ-AUTO BAJFINANCE
BAJAJFINSV BEL BHARTIARTL CIPLA COALINDIA DRREDDY EICHERMOT ETERNAL GRASIM HCLTECH HDFCBANK
HDFCLIFE HEROMOTOCO HINDALCO HINDUNILVR ICICIBANK INDUSINDBK INFY ITC JIOFIN JSWSTEEL KOTAKBANK
LT M&M MARUTI NESTLEIND NTPC ONGC POWERGRID RELIANCE SBILIFE SBIN SHRIRAMFIN SUNPHARMA
TATACONSUM TATASTEEL TCS TECHM TITAN TRENT ULTRACEMCO WIPRO""".split()


def _get(url, tries=4):
    """GET with retries. Yahoo answers HTTP 429 when rate-limited: back off much longer
    then, and alternate between its query1 and query2 hosts."""
    for i in range(tries):
        u = url.replace("://query1.", "://query2.") if (i % 2 and "://query1." in url) else url
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if i == tries - 1 or e.code == 404:
                raise
            time.sleep(15 * (i + 1) if e.code == 429 else 2 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def universe():
    try:
        text = _get(NIFTY100_URL).decode("utf-8", "replace")
        syms = [row["Symbol"].strip() for row in csv.DictReader(io.StringIO(text)) if row.get("Symbol")]
        if len(syms) >= 80:
            return syms, "nifty100"
    except Exception:
        pass
    return list(NIFTY50_FALLBACK), "nifty50-fallback"


def parse_chart(payload):
    res = payload["chart"]["result"][0]
    ts = res.get("timestamp") or []
    q = res["indicators"]["quote"][0]
    days = {}
    for i, t in enumerate(ts):
        o, h, l, c, v = (q[k][i] for k in ("open", "high", "low", "close", "volume"))
        if None in (o, h, l, c):
            continue
        d = dt.datetime.fromtimestamp(t, IST)
        hm = d.strftime("%H:%M")
        if not ("09:15" <= hm <= "15:25"):
            continue
        days.setdefault(d.strftime("%Y-%m-%d"), []).append(
            {"t": hm, "o": o, "h": h, "l": l, "c": c, "v": v or 0})
    for bars in days.values():
        bars.sort(key=lambda b: b["t"])
    return days


def fetch_bars(yahoo_symbol, range_="5d", interval="5m"):
    sym = urllib.parse.quote(yahoo_symbol)
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=%s&range=%s"
           % (sym, interval, range_))
    return parse_chart(json.loads(_get(url)))


class DataError(Exception):
    pass


def fetch_all(symbols, range_="5d", pause=0.6, log=print):
    """Download every symbol; raise DataError if more than a quarter of them fail, so a
    rate-limited run stops loudly instead of producing an empty or skewed report."""
    out, failed = {}, []
    for s in symbols:
        try:
            out[s] = fetch_bars(s + ".NS", range_)
        except Exception as e:
            failed.append(s)
            log("  skip %s: %s" % (s, str(e)[:80]))
        time.sleep(pause)
    if len(failed) > len(symbols) // 4:
        raise DataError("%d of %d symbols failed to download (e.g. Yahoo rate limit, HTTP 429); "
                        "nothing written. Try again later." % (len(failed), len(symbols)))
    return out, failed
