# Our bot vs the dalal-street-skills rule, same data

Same 49 Nifty 50 stocks, same Yahoo 5-minute bars, 60 complete sessions (2026-08-12 to 2026-11-06), 0 symbols skipped. Same money rules for all: Rs 2,400 capital, 5x MIS, max 1 trade a day (earliest breakout), Rs 25 max loss per trade incl. charges, monthly stop at a Rs 500 loss.

Data gaps: Yahoo was missing 5716 five-minute bars across all stocks and days; each was filled with a flat bar at the previous close for the dalal rule (days missing more than 5 bars before 15:10 were dropped).

The dalal-street-skills rule is its own code (bot/dalal_port.py, copied from commit 6fcc8d4, MIT): 15-minute opening range, stop at the range midpoint, exit at 15:10. Differences from our bot: it enters at the **signal bar's close** (ours waits for the next bar's open plus 0.05% slippage, so its fills are slightly more optimistic), it has no Nifty 50 market filter, and it counts a stop before a target inside the same bar, like ours.

| | Our bot (2R, next-bar entry, Nifty filter) | dalal-street-skills rule, 2R | dalal-street-skills rule, 1R |
|---|---|---|---|
| Trades | 45 | 60 | 60 |
| Win rate | 28.9% | 25.0% | 35.0% |
| Gross P&L | -Rs 277.03 | -Rs 325.95 | -Rs 319.50 |
| Charges | Rs 137.74 | Rs 232.82 | Rs 232.84 |
| **Net P&L** | **-Rs 414.77** | **-Rs 558.77** | **-Rs 552.34** |
| Max drawdown | Rs 474.52 | Rs 591.90 | Rs 568.27 |
| Ending equity (from Rs 2,400) | Rs 1,985.23 | Rs 1,841.23 | Rs 1,847.66 |
| Exits: target / stop / close | 6 / 25 / 14 | 10 / 40 / 10 | 20 / 36 / 4 |

## Net by month

| Month | Our bot | dalal 2R | dalal 1R |
|---|---|---|---|
| 2026-08 | -Rs 167.42 | -Rs 53.75 | -Rs 77.84 |
| 2026-09 | -Rs 160.12 | -Rs 363.95 | -Rs 326.68 |
| 2026-10 | -Rs 134.68 | -Rs 154.74 | -Rs 142.31 |
| 2026-11 | Rs 47.45 | Rs 13.67 | -Rs 5.51 |

## dalal-street-skills rule 2R: every trade

- 2026-08-12 SBIN: 2 @ 1082.00 (09:35), stop 1074.10, target 1097.80 -> 1074.10 (stop). Net -Rs 18.08
- 2026-08-13 BAJFINANCE: 6 @ 1090.50 (09:35), stop 1087.55, target 1096.40 -> 1087.55 (stop). Net -Rs 24.64
- 2026-08-14 ADANIPORTS: 2 @ 1670.60 (09:35), stop 1663.75, target 1684.30 -> 1684.30 (target). Net Rs 23.83
- 2026-08-17 BAJAJFINSV: 2 @ 2011.60 (09:35), stop 2004.35, target 2026.10 -> 2026.10 (target). Net Rs 24.71
- 2026-08-18 ADANIENT: 2 @ 3022.70 (09:40), stop 3015.05, target 3038.00 -> 3020.30 (close). Net -Rs 11.22
- 2026-08-19 INDUSINDBK: 8 @ 1012.00 (09:45), stop 1010.15, target 1015.70 -> 1010.15 (stop). Net -Rs 23.40
- 2026-08-20 ETERNAL: 7 @ 326.65 (09:35), stop 323.70, target 332.55 -> 328.20 (close). Net Rs 8.42
- 2026-08-21 BEL: 13 @ 411.90 (09:35), stop 410.50, target 414.70 -> 414.70 (target). Net Rs 30.69
- 2026-08-24 ADANIENT: 2 @ 3015.85 (09:35), stop 3006.75, target 3034.05 -> 3006.75 (stop). Net -Rs 24.59
- 2026-08-25 BEL: 10 @ 409.30 (09:35), stop 407.35, target 413.20 -> 407.35 (stop). Net -Rs 23.84
- 2026-08-26 KOTAKBANK: 6 @ 407.40 (09:35), stop 403.85, target 414.50 -> 414.50 (target). Net Rs 39.99
- 2026-08-27 ASIANPAINT: 3 @ 2642.35 (09:35), stop 2638.55, target 2649.95 -> 2638.55 (stop). Net -Rs 19.83
- 2026-08-28 HCLTECH: 1 @ 1318.50 (09:35), stop 1306.75, target 1342.00 -> 1306.75 (stop). Net -Rs 13.15
- 2026-08-31 COALINDIA: 8 @ 404.50 (09:35), stop 402.10, target 409.30 -> 402.10 (stop). Net -Rs 22.64
- 2026-09-01 ADANIPORTS: 1 @ 1648.70 (09:35), stop 1637.45, target 1671.20 -> 1637.45 (stop). Net -Rs 13.00
- 2026-09-02 ICICIBANK: 3 @ 1434.85 (09:35), stop 1429.50, target 1445.55 -> 1429.50 (stop). Net -Rs 20.61
- 2026-09-03 AXISBANK: 3 @ 1274.45 (09:35), stop 1267.50, target 1288.35 -> 1267.50 (stop). Net -Rs 24.90
- 2026-09-04 BEL: 11 @ 411.40 (09:35), stop 409.60, target 415.00 -> 409.60 (stop). Net -Rs 24.61
- 2026-09-07 BEL: 16 @ 407.90 (09:40), stop 406.85, target 410.00 -> 406.85 (stop). Net -Rs 23.73
- 2026-09-08 HEROMOTOCO: 1 @ 5324.00 (09:35), stop 5304.75, target 5362.50 -> 5304.75 (stop). Net -Rs 24.90
- 2026-09-09 NTPC: 7 @ 336.00 (09:35), stop 333.05, target 341.90 -> 333.05 (stop). Net -Rs 23.13
- 2026-09-10 HCLTECH: 3 @ 1229.70 (09:35), stop 1224.50, target 1240.10 -> 1224.50 (stop). Net -Rs 19.52
- 2026-09-11 BHARTIARTL: 2 @ 1846.45 (09:35), stop 1838.30, target 1862.75 -> 1838.30 (stop). Net -Rs 20.22
- 2026-09-15 RELIANCE: 3 @ 1258.60 (09:40), stop 1253.25, target 1269.30 -> 1253.25 (stop). Net -Rs 20.05
- 2026-09-16 HCLTECH: 2 @ 1274.35 (09:35), stop 1265.05, target 1292.95 -> 1265.05 (stop). Net -Rs 21.30
- 2026-09-17 AXISBANK: 2 @ 1251.20 (09:35), stop 1240.40, target 1272.80 -> 1240.40 (stop). Net -Rs 24.24
- 2026-09-18 DRREDDY: 3 @ 1194.85 (09:35), stop 1189.00, target 1206.55 -> 1206.55 (target). Net Rs 31.27
- 2026-09-21 ASIANPAINT: 2 @ 2462.35 (09:35), stop 2453.55, target 2479.95 -> 2453.55 (stop). Net -Rs 22.83
- 2026-09-22 DRREDDY: 2 @ 1215.45 (09:35), stop 1204.80, target 1236.75 -> 1204.80 (stop). Net -Rs 23.86
- 2026-09-23 INDUSINDBK: 3 @ 965.25 (09:35), stop 958.55, target 978.65 -> 959.90 (close). Net -Rs 19.12
- 2026-09-24 ICICIBANK: 2 @ 1347.10 (09:35), stop 1336.45, target 1368.40 -> 1336.45 (stop). Net -Rs 24.15
- 2026-09-25 ASIANPAINT: 1 @ 2416.00 (09:35), stop 2406.05, target 2435.90 -> 2435.90 (target). Net Rs 17.32
- 2026-09-28 NESTLEIND: 6 @ 1350.20 (09:45), stop 1347.50, target 1355.60 -> 1347.50 (stop). Net -Rs 24.81
- 2026-09-29 GRASIM: 2 @ 3149.65 (09:45), stop 3142.65, target 3163.65 -> 3142.65 (stop). Net -Rs 20.69
- 2026-09-30 TECHM: 1 @ 1549.00 (09:35), stop 1533.75, target 1579.50 -> 1533.75 (stop). Net -Rs 16.87
- 2026-10-01 ADANIENT: 1 @ 2898.00 (09:40), stop 2878.55, target 2936.90 -> 2878.55 (stop). Net -Rs 22.52
- 2026-10-05 ETERNAL: 6 @ 314.30 (09:35), stop 310.70, target 321.50 -> 321.50 (target). Net Rs 41.17
- 2026-10-06 AXISBANK: 3 @ 1242.10 (09:35), stop 1236.20, target 1253.90 -> 1236.20 (stop). Net -Rs 21.65
- 2026-10-07 BAJFINANCE: 2 @ 973.25 (09:35), stop 964.35, target 991.05 -> 964.35 (stop). Net -Rs 19.85
- 2026-10-08 DRREDDY: 3 @ 1200.00 (09:35), stop 1194.45, target 1211.10 -> 1194.45 (stop). Net -Rs 20.48
- 2026-10-09 ADANIPORTS: 1 @ 1736.70 (09:35), stop 1717.25, target 1775.60 -> 1754.50 (close). Net Rs 15.94
- 2026-10-12 JSWSTEEL: 4 @ 1180.60 (09:35), stop 1176.10, target 1189.60 -> 1176.10 (stop). Net -Rs 23.01
- 2026-10-13 ASIANPAINT: 1 @ 2344.85 (09:35), stop 2332.05, target 2370.45 -> 2358.70 (close). Net Rs 11.36
- 2026-10-14 INDUSINDBK: 4 @ 878.70 (09:35), stop 874.05, target 888.00 -> 874.05 (stop). Net -Rs 22.33
- 2026-10-15 CIPLA: 2 @ 1328.35 (09:35), stop 1318.25, target 1348.55 -> 1322.60 (close). Net -Rs 14.32
- 2026-10-16 INFY: 1 @ 1149.85 (09:35), stop 1134.95, target 1179.65 -> 1165.00 (close). Net Rs 13.93
- 2026-10-19 SBIN: 2 @ 979.00 (09:35), stop 969.30, target 998.40 -> 969.30 (stop). Net -Rs 21.46
- 2026-10-21 ASIANPAINT: 2 @ 2348.65 (09:35), stop 2338.90, target 2368.15 -> 2338.90 (stop). Net -Rs 24.48
- 2026-10-22 BAJFINANCE: 2 @ 921.00 (09:35), stop 912.45, target 938.10 -> 938.10 (target). Net Rs 32.22
- 2026-10-23 ONGC: 28 @ 225.75 (10:05), stop 225.10, target 227.05 -> 225.10 (stop). Net -Rs 24.91
- 2026-10-26 TATASTEEL: 24 @ 167.35 (09:35), stop 166.50, target 169.05 -> 166.50 (stop). Net -Rs 24.66
- 2026-10-27 BEL: 5 @ 372.55 (09:35), stop 368.15, target 381.35 -> 368.15 (stop). Net -Rs 23.96
- 2026-10-28 BEL: 10 @ 365.40 (09:35), stop 363.45, target 369.30 -> 364.30 (close). Net -Rs 14.88
- 2026-10-29 ADANIENT: 1 @ 2505.70 (09:35), stop 2490.00, target 2537.10 -> 2537.10 (target). Net Rs 28.72
- 2026-10-30 BAJAJFINSV: 3 @ 1666.95 (09:35), stop 1662.20, target 1676.45 -> 1662.20 (stop). Net -Rs 19.57
- 2026-11-02 COALINDIA: 10 @ 399.00 (09:35), stop 396.95, target 403.10 -> 403.10 (target). Net Rs 36.72
- 2026-11-03 BAJAJFINSV: 1 @ 1714.35 (09:35), stop 1701.75, target 1739.55 -> 1701.75 (stop). Net -Rs 14.40
- 2026-11-04 ADANIPORTS: 1 @ 1904.00 (09:35), stop 1881.20, target 1949.60 -> 1903.70 (close). Net -Rs 2.33
- 2026-11-05 TATACONSUM: 4 @ 1074.00 (09:35), stop 1069.90, target 1082.20 -> 1069.90 (stop). Net -Rs 20.95
- 2026-11-06 CIPLA: 2 @ 1397.20 (09:35), stop 1387.75, target 1416.10 -> 1406.00 (close). Net Rs 14.63

## dalal-street-skills rule 1R: every trade

- 2026-08-12 SBIN: 2 @ 1082.00 (09:35), stop 1074.10, target 1089.90 -> 1074.10 (stop). Net -Rs 18.08
- 2026-08-13 BAJFINANCE: 6 @ 1090.50 (09:35), stop 1087.55, target 1093.45 -> 1087.55 (stop). Net -Rs 24.64
- 2026-08-14 ADANIPORTS: 2 @ 1670.60 (09:35), stop 1663.75, target 1677.45 -> 1677.45 (target). Net Rs 10.13
- 2026-08-17 BAJAJFINSV: 2 @ 2011.60 (09:35), stop 2004.35, target 2018.85 -> 2018.85 (target). Net Rs 10.21
- 2026-08-18 ADANIENT: 2 @ 3022.70 (09:40), stop 3015.05, target 3030.35 -> 3030.35 (target). Net Rs 8.87
- 2026-08-19 INDUSINDBK: 8 @ 1012.00 (09:45), stop 1010.15, target 1013.85 -> 1010.15 (stop). Net -Rs 23.40
- 2026-08-20 ETERNAL: 7 @ 326.65 (09:35), stop 323.70, target 329.60 -> 328.20 (close). Net Rs 8.42
- 2026-08-21 BEL: 13 @ 411.90 (09:35), stop 410.50, target 413.30 -> 413.30 (target). Net Rs 12.50
- 2026-08-24 ADANIENT: 2 @ 3015.85 (09:35), stop 3006.75, target 3024.95 -> 3006.75 (stop). Net -Rs 24.59
- 2026-08-25 BEL: 10 @ 409.30 (09:35), stop 407.35, target 411.25 -> 407.35 (stop). Net -Rs 23.84
- 2026-08-26 KOTAKBANK: 6 @ 407.40 (09:35), stop 403.85, target 410.95 -> 410.95 (target). Net Rs 18.70
- 2026-08-27 ASIANPAINT: 3 @ 2642.35 (09:35), stop 2638.55, target 2646.15 -> 2638.55 (stop). Net -Rs 19.83
- 2026-08-28 HCLTECH: 1 @ 1318.50 (09:35), stop 1306.75, target 1330.25 -> 1330.25 (target). Net Rs 10.35
- 2026-08-31 COALINDIA: 8 @ 404.50 (09:35), stop 402.10, target 406.90 -> 402.10 (stop). Net -Rs 22.64
- 2026-09-01 ADANIPORTS: 1 @ 1648.70 (09:35), stop 1637.45, target 1659.95 -> 1637.45 (stop). Net -Rs 13.00
- 2026-09-02 ICICIBANK: 3 @ 1434.85 (09:35), stop 1429.50, target 1440.20 -> 1429.50 (stop). Net -Rs 20.61
- 2026-09-03 AXISBANK: 3 @ 1274.45 (09:35), stop 1267.50, target 1281.40 -> 1267.50 (stop). Net -Rs 24.90
- 2026-09-04 BEL: 11 @ 411.40 (09:35), stop 409.60, target 413.20 -> 409.60 (stop). Net -Rs 24.61
- 2026-09-07 BEL: 16 @ 407.90 (09:40), stop 406.85, target 408.95 -> 408.95 (target). Net Rs 9.85
- 2026-09-08 HEROMOTOCO: 1 @ 5324.00 (09:35), stop 5304.75, target 5343.25 -> 5304.75 (stop). Net -Rs 24.90
- 2026-09-09 NTPC: 7 @ 336.00 (09:35), stop 333.05, target 338.95 -> 333.05 (stop). Net -Rs 23.13
- 2026-09-10 HCLTECH: 3 @ 1229.70 (09:35), stop 1224.50, target 1234.90 -> 1234.90 (target). Net Rs 11.66
- 2026-09-11 BHARTIARTL: 2 @ 1846.45 (09:35), stop 1838.30, target 1854.60 -> 1838.30 (stop). Net -Rs 20.22
- 2026-09-15 RELIANCE: 3 @ 1258.60 (09:40), stop 1253.25, target 1263.95 -> 1253.25 (stop). Net -Rs 20.05
- 2026-09-16 HCLTECH: 2 @ 1274.35 (09:35), stop 1265.05, target 1283.65 -> 1265.05 (stop). Net -Rs 21.30
- 2026-09-17 AXISBANK: 2 @ 1251.20 (09:35), stop 1240.40, target 1262.00 -> 1240.40 (stop). Net -Rs 24.24
- 2026-09-18 DRREDDY: 3 @ 1194.85 (09:35), stop 1189.00, target 1200.70 -> 1200.70 (target). Net Rs 13.72
- 2026-09-21 ASIANPAINT: 2 @ 2462.35 (09:35), stop 2453.55, target 2471.15 -> 2453.55 (stop). Net -Rs 22.83
- 2026-09-22 DRREDDY: 2 @ 1215.45 (09:35), stop 1204.80, target 1226.10 -> 1204.80 (stop). Net -Rs 23.86
- 2026-09-23 INDUSINDBK: 3 @ 965.25 (09:35), stop 958.55, target 971.95 -> 959.90 (close). Net -Rs 19.12
- 2026-09-24 ICICIBANK: 2 @ 1347.10 (09:35), stop 1336.45, target 1357.75 -> 1336.45 (stop). Net -Rs 24.15
- 2026-09-25 ASIANPAINT: 1 @ 2416.00 (09:35), stop 2406.05, target 2425.95 -> 2425.95 (target). Net Rs 7.38
- 2026-09-28 NESTLEIND: 6 @ 1350.20 (09:45), stop 1347.50, target 1352.90 -> 1347.50 (stop). Net -Rs 24.81
- 2026-09-29 GRASIM: 2 @ 3149.65 (09:45), stop 3142.65, target 3156.65 -> 3142.65 (stop). Net -Rs 20.69
- 2026-09-30 TECHM: 1 @ 1549.00 (09:35), stop 1533.75, target 1564.25 -> 1533.75 (stop). Net -Rs 16.87
- 2026-10-01 ADANIENT: 1 @ 2898.00 (09:40), stop 2878.55, target 2917.45 -> 2878.55 (stop). Net -Rs 22.52
- 2026-10-05 ETERNAL: 6 @ 314.30 (09:35), stop 310.70, target 317.90 -> 317.90 (target). Net Rs 19.57
- 2026-10-06 AXISBANK: 3 @ 1242.10 (09:35), stop 1236.20, target 1248.00 -> 1236.20 (stop). Net -Rs 21.65
- 2026-10-07 BAJFINANCE: 2 @ 973.25 (09:35), stop 964.35, target 982.15 -> 964.35 (stop). Net -Rs 19.85
- 2026-10-08 DRREDDY: 3 @ 1200.00 (09:35), stop 1194.45, target 1205.55 -> 1194.45 (stop). Net -Rs 20.48
- 2026-10-09 ADANIPORTS: 1 @ 1736.70 (09:35), stop 1717.25, target 1756.15 -> 1756.15 (target). Net Rs 17.59
- 2026-10-12 JSWSTEEL: 4 @ 1180.60 (09:35), stop 1176.10, target 1185.10 -> 1185.10 (target). Net Rs 12.97
- 2026-10-13 ASIANPAINT: 1 @ 2344.85 (09:35), stop 2332.05, target 2357.65 -> 2357.65 (target). Net Rs 10.31
- 2026-10-14 INDUSINDBK: 4 @ 878.70 (09:35), stop 874.05, target 883.35 -> 874.05 (stop). Net -Rs 22.33
- 2026-10-15 CIPLA: 2 @ 1328.35 (09:35), stop 1318.25, target 1338.45 -> 1322.60 (close). Net -Rs 14.32
- 2026-10-16 INFY: 1 @ 1149.85 (09:35), stop 1134.95, target 1164.75 -> 1164.75 (target). Net Rs 13.68
- 2026-10-19 SBIN: 2 @ 979.00 (09:35), stop 969.30, target 988.70 -> 969.30 (stop). Net -Rs 21.46
- 2026-10-21 ASIANPAINT: 2 @ 2348.65 (09:35), stop 2338.90, target 2358.40 -> 2338.90 (stop). Net -Rs 24.48
- 2026-10-22 BAJFINANCE: 2 @ 921.00 (09:35), stop 912.45, target 929.55 -> 929.55 (target). Net Rs 15.14
- 2026-10-23 ONGC: 28 @ 225.75 (10:05), stop 225.10, target 226.40 -> 225.10 (stop). Net -Rs 24.91
- 2026-10-26 TATASTEEL: 24 @ 167.35 (09:35), stop 166.50, target 168.20 -> 166.50 (stop). Net -Rs 24.66
- 2026-10-27 BEL: 5 @ 372.55 (09:35), stop 368.15, target 376.95 -> 368.15 (stop). Net -Rs 23.96
- 2026-10-28 BEL: 10 @ 365.40 (09:35), stop 363.45, target 367.35 -> 367.35 (target). Net Rs 15.60
- 2026-10-29 ADANIENT: 1 @ 2505.70 (09:35), stop 2490.00, target 2521.40 -> 2521.40 (target). Net Rs 13.02
- 2026-10-30 BAJAJFINSV: 3 @ 1666.95 (09:35), stop 1662.20, target 1671.70 -> 1662.20 (stop). Net -Rs 19.57
- 2026-11-02 COALINDIA: 10 @ 399.00 (09:35), stop 396.95, target 401.05 -> 401.05 (target). Net Rs 16.24
- 2026-11-03 BAJAJFINSV: 1 @ 1714.35 (09:35), stop 1701.75, target 1726.95 -> 1701.75 (stop). Net -Rs 14.40
- 2026-11-04 ADANIPORTS: 1 @ 1904.00 (09:35), stop 1881.20, target 1926.80 -> 1903.70 (close). Net -Rs 2.33
- 2026-11-05 TATACONSUM: 4 @ 1074.00 (09:35), stop 1069.90, target 1078.10 -> 1069.90 (stop). Net -Rs 20.95
- 2026-11-06 CIPLA: 2 @ 1397.20 (09:35), stop 1387.75, target 1406.65 -> 1406.65 (target). Net Rs 15.93

Past results on 60 days of data do not predict future results.
