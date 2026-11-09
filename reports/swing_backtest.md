# Swing-trading backtest: Nifty 50 stocks, delivery (CNC), Rs 2,400

Generated 2026-11-09 07:16 IST. Daily candles from Yahoo Finance for 49 stocks (0 skipped), trading from 2022-08-26 to 2026-11-08 (the first 200 days are only used to warm up the averages).

Same rules for both setups: one stock at a time, buy with all available money (no leverage), orders fill at the next day's open with 0.1% slippage, Zerodha delivery charges including the Rs 15.34 DP charge on every sale, and no new buys for the rest of a month once that month loses Rs 500. Rules were fixed before running (see bot/swing.py); nothing was tuned on this data.

| | Breakout (20-day high, uptrend) | Pullback (RSI-2 dip, uptrend) | Buy and hold NIFTYBEES |
|---|---|---|---|
| Trades | 56 | 117 | 1 |
| Win rate | 32.1% | 23.1% | - |
| Average days held | 16.2 | 3.6 | whole period |
| Gross P&L | Rs 1,025.63 | -Rs 187.72 | - |
| Charges | Rs 1,210.09 | Rs 2,030.43 | Rs 21.63 |
| **Net P&L** | **-Rs 184.46** | **-Rs 2,218.15** | **Rs 1,074.72** |
| Ending money (from Rs 2,400) | Rs 2,215.54 | Rs 181.85 | Rs 3,474.72 |
| Worst drop from peak | Rs 2,533.11 | Rs 2,301.43 | - |

## Net by year

| Year | Breakout | Pullback |
|---|---|---|
| 2022 | Rs 102.31 | -Rs 639.50 |
| 2023 | Rs 1,430.55 | -Rs 724.75 |
| 2024 | -Rs 625.44 | -Rs 766.61 |
| 2025 | Rs 533.62 | -Rs 87.29 |
| 2026 | -Rs 1,625.50 | Rs 0.00 |

Caveats: the stock list is today's Nifty 50, so stocks that dropped out of the index over these years are missing (this flatters every result a little). Yahoo's daily data is unofficial. Past results do not predict future results.

## Breakout: every trade

- 2022-08-29 -> 2022-09-22 BEL: 23 @ 100.70 -> 108.49 (exit rule, 17 days). Net Rs 158.51
- 2022-09-30 -> 2022-11-16 SUNPHARMA: 2 @ 934.88 -> 1006.09 (time, 30 days). Net Rs 122.77
- 2022-11-17 -> 2022-12-08 KOTAKBANK: 6 @ 393.15 -> 379.40 (exit rule, 15 days). Net -Rs 103.02
- 2022-12-09 -> 2022-12-22 AXISBANK: 2 @ 944.94 -> 916.71 (stop, 10 days). Net -Rs 75.95
- 2022-12-28 -> 2023-01-06 JSWSTEEL: 3 @ 761.76 -> 729.67 (stop, 8 days). Net -Rs 116.60
- 2023-01-10 -> 2023-02-22 M&M: 1 @ 1311.81 -> 1345.55 (time, 30 days). Net Rs 15.45
- 2023-03-03 -> 2023-03-20 COALINDIA: 10 @ 224.12 -> 215.60 (stop, 11 days). Net -Rs 105.47
- 2023-03-28 -> 2023-04-25 SUNPHARMA: 2 @ 987.99 -> 979.02 (exit rule, 16 days). Net -Rs 37.65
- 2023-04-26 -> 2023-06-08 ITC: 5 @ 397.12 -> 428.74 (time, 30 days). Net Rs 138.20
- 2023-06-09 -> 2023-07-24 JSWSTEEL: 3 @ 752.25 -> 788.21 (time, 30 days). Net Rs 87.41
- 2023-07-26 -> 2023-09-07 NTPC: 12 @ 201.70 -> 232.77 (time, 30 days). Net Rs 351.68
- 2023-09-08 -> 2023-10-25 COALINDIA: 10 @ 274.87 -> 305.79 (time, 30 days). Net Rs 287.41
- 2023-11-01 -> 2023-12-15 TRENT: 1 @ 2165.86 -> 2997.00 (time, 30 days). Net Rs 810.12
- 2023-12-18 -> 2024-01-03 TCS: 1 @ 3861.96 -> 3723.40 (stop, 12 days). Net -Rs 162.35
- 2024-01-04 -> 2024-01-08 ITC: 8 @ 462.66 -> 447.17 (stop, 3 days). Net -Rs 147.37
- 2024-01-09 -> 2024-02-13 SHRIRAMFIN: 8 @ 441.76 -> 452.95 (exit rule, 23 days). Net Rs 66.18
- 2024-02-14 -> 2024-03-20 CIPLA: 2 @ 1456.25 -> 1434.36 (exit rule, 24 days). Net -Rs 65.55
- 2024-03-26 -> 2024-05-13 HINDALCO: 6 @ 546.20 -> 624.47 (time, 30 days). Net Rs 446.56
- 2024-05-15 -> 2024-06-28 M&M: 1 @ 2283.58 -> 2852.14 (time, 30 days). Net Rs 547.55
- 2024-07-01 -> 2024-07-22 RELIANCE: 2 @ 1564.09 -> 1505.22 (stop, 15 days). Net -Rs 139.92
- 2024-07-23 -> 2024-09-04 TATACONSUM: 3 @ 1201.28 -> 1194.85 (time, 30 days). Net -Rs 42.63
- 2024-09-05 -> 2024-09-25 ASIANPAINT: 1 @ 3243.24 -> 3248.75 (exit rule, 14 days). Net -Rs 17.05
- 2024-09-26 -> 2024-09-30 POWERGRID: 12 @ 364.41 -> 350.30 (stop, 3 days). Net -Rs 194.27
- 2024-10-01 -> 2024-10-17 JSWSTEEL: 4 @ 1030.03 -> 980.33 (stop, 12 days). Net -Rs 223.08
- 2024-10-18 -> 2024-10-23 SBIN: 4 @ 811.91 -> 780.66 (stop, 4 days). Net -Rs 147.45
- 2024-10-30 -> 2024-11-18 SBIN: 4 @ 828.83 -> 810.19 (exit rule, 12 days). Net -Rs 97.20
- 2024-11-25 -> 2024-12-04 POWERGRID: 10 @ 342.19 -> 323.43 (stop, 8 days). Net -Rs 210.35
- 2024-12-05 -> 2024-12-19 BEL: 11 @ 314.31 -> 294.70 (exit rule, 10 days). Net -Rs 238.51
- 2024-12-27 -> 2025-01-10 SUNPHARMA: 1 @ 1847.35 -> 1786.06 (stop, 11 days). Net -Rs 80.67
- 2025-01-13 -> 2025-01-14 HCLTECH: 1 @ 1996.89 -> 1899.42 (stop, 2 days). Net -Rs 117.15
- 2025-01-21 -> 2025-01-27 BHARTIARTL: 1 @ 1655.65 -> 1593.12 (stop, 5 days). Net -Rs 81.50
- 2025-01-29 -> 2025-03-12 BAJFINANCE: 3 @ 766.49 -> 833.28 (time, 30 days). Net Rs 179.70
- 2025-03-18 -> 2025-04-08 ICICIBANK: 2 @ 1270.27 -> 1298.55 (exit rule, 14 days). Net Rs 35.51
- 2025-04-16 -> 2025-05-12 HDFCBANK: 3 @ 942.84 -> 957.84 (exit rule, 16 days). Net Rs 23.32
- 2025-05-13 -> 2025-06-24 BEL: 9 @ 324.02 -> 425.97 (time, 30 days). Net Rs 894.77
- 2025-06-25 -> 2025-07-14 GRASIM: 1 @ 2794.69 -> 2771.23 (exit rule, 13 days). Net -Rs 45.00
- 2025-07-15 -> 2025-07-17 ETERNAL: 15 @ 272.17 -> 260.67 (stop, 3 days). Net -Rs 196.82
- 2025-07-23 -> 2025-09-05 ETERNAL: 13 @ 298.30 -> 327.22 (time, 30 days). Net Rs 351.66
- 2025-09-08 -> 2025-09-29 M&M: 1 @ 3564.86 -> 3415.58 (exit rule, 15 days). Net -Rs 172.40
- 2025-10-06 -> 2025-11-19 HINDALCO: 5 @ 782.83 -> 796.35 (time, 30 days). Net Rs 43.48
- 2025-11-20 -> 2025-12-03 TITAN: 1 @ 3953.95 -> 3819.07 (stop, 10 days). Net -Rs 158.88
- 2025-12-04 -> 2025-12-09 DRREDDY: 3 @ 1281.88 -> 1242.34 (stop, 4 days). Net -Rs 142.40
- 2025-12-12 -> 2026-01-07 KOTAKBANK: 8 @ 436.78 -> 422.09 (stop, 18 days). Net -Rs 140.47
- 2026-01-08 -> 2026-01-08 JIOFIN: 12 @ 303.60 -> 293.94 (stop, 1 days). Net -Rs 139.23
- 2026-01-13 -> 2026-01-16 ASIANPAINT: 1 @ 2902.90 -> 2785.11 (stop, 4 days). Net -Rs 139.47
- 2026-01-19 -> 2026-02-04 TECHM: 2 @ 1691.69 -> 1622.45 (stop, 12 days). Net -Rs 161.20
- 2026-02-05 -> 2026-03-02 ADANIPORTS: 2 @ 1569.57 -> 1460.41 (stop, 18 days). Net -Rs 240.42
- 2026-03-06 -> 2026-04-10 COALINDIA: 6 @ 451.60 -> 428.74 (stop, 23 days). Net -Rs 158.38
- 2026-04-13 -> 2026-05-12 HINDALCO: 2 @ 979.03 -> 1026.17 (exit rule, 19 days). Net Rs 74.50
- 2026-05-14 -> 2026-05-18 TATASTEEL: 13 @ 222.52 -> 210.79 (stop, 3 days). Net -Rs 174.15
- 2026-05-19 -> 2026-05-26 SUNPHARMA: 1 @ 1902.40 -> 1818.64 (stop, 6 days). Net -Rs 103.25
- 2026-05-29 -> 2026-06-05 HINDALCO: 2 @ 1177.18 -> 1112.36 (stop, 6 days). Net -Rs 150.07
- 2026-06-15 -> 2026-07-06 AXISBANK: 1 @ 1373.37 -> 1354.34 (exit rule, 14 days). Net -Rs 37.41
- 2026-07-07 -> 2026-08-18 INDUSINDBK: 2 @ 1010.71 -> 1005.99 (time, 30 days). Net -Rs 29.26
- 2026-08-21 -> 2026-08-31 ETERNAL: 7 @ 330.33 -> 315.78 (stop, 7 days). Net -Rs 122.24
- 2026-09-10 -> 2026-10-08 ADANIPORTS: 1 @ 1781.68 -> 1696.45 (stop, 19 days). Net -Rs 104.45

## Pullback: every trade

- 2022-08-29 -> 2022-09-01 CIPLA: 2 @ 1001.00 -> 1024.97 (exit rule, 2 days). Net Rs 28.11
- 2022-09-05 -> 2022-09-06 CIPLA: 2 @ 1013.51 -> 1023.98 (exit rule, 1 days). Net Rs 1.06
- 2022-09-07 -> 2022-09-08 ADANIPORTS: 2 @ 847.85 -> 879.72 (exit rule, 1 days). Net Rs 44.56
- 2022-09-09 -> 2022-09-14 NTPC: 14 @ 167.82 -> 164.84 (exit rule, 3 days). Net -Rs 62.28
- 2022-09-15 -> 2022-09-23 BEL: 20 @ 114.76 -> 106.50 (stop, 7 days). Net -Rs 185.63
- 2022-09-26 -> 2022-09-28 AXISBANK: 2 @ 759.76 -> 707.07 (stop, 3 days). Net -Rs 124.00
- 2022-09-29 -> 2022-10-06 ADANIPORTS: 2 @ 839.84 -> 832.07 (exit rule, 4 days). Net -Rs 34.60
- 2022-10-07 -> 2022-10-17 DRREDDY: 2 @ 878.88 -> 860.14 (exit rule, 6 days). Net -Rs 56.69
- 2022-10-18 -> 2022-10-19 M&M: 1 @ 1237.39 -> 1258.69 (exit rule, 1 days). Net Rs 3.18
- 2022-10-20 -> 2022-10-25 GRASIM: 1 @ 1678.46 -> 1688.09 (exit rule, 3 days). Net -Rs 9.45
- 2022-10-27 -> 2022-10-31 KOTAKBANK: 5 @ 377.12 -> 379.42 (exit rule, 2 days). Net -Rs 8.03
- 2022-11-01 -> 2022-11-02 DRREDDY: 2 @ 887.94 -> 908.10 (exit rule, 1 days). Net Rs 21.00
- 2022-11-03 -> 2022-11-09 AXISBANK: 2 @ 858.76 -> 874.17 (exit rule, 3 days). Net Rs 11.64
- 2022-11-10 -> 2022-11-24 BAJAJFINSV: 1 @ 1746.74 -> 1637.36 (time, 10 days). Net -Rs 128.49
- 2022-11-25 -> 2022-11-29 BAJAJFINSV: 1 @ 1635.63 -> 1647.35 (exit rule, 2 days). Net -Rs 7.27
- 2022-11-30 -> 2022-12-01 ADANIPORTS: 2 @ 879.78 -> 883.87 (exit rule, 1 days). Net -Rs 11.09
- 2022-12-02 -> 2022-12-05 BEL: 17 @ 104.65 -> 106.24 (exit rule, 1 days). Net Rs 7.68
- 2022-12-06 -> 2022-12-09 HCLTECH: 1 @ 1122.72 -> 1067.31 (stop, 4 days). Net -Rs 73.19
- 2022-12-12 -> 2022-12-26 KOTAKBANK: 4 @ 373.37 -> 364.03 (time, 10 days). Net -Rs 56.01
- 2022-12-27 -> 2023-01-06 CIPLA: 1 @ 1095.14 -> 1087.26 (exit rule, 8 days). Net -Rs 25.65
- 2023-01-09 -> 2023-01-10 AXISBANK: 1 @ 947.75 -> 963.04 (exit rule, 1 days). Net -Rs 2.17
- 2023-01-11 -> 2023-01-16 GRASIM: 1 @ 1646.60 -> 1651.27 (exit rule, 3 days). Net -Rs 14.34
- 2023-01-17 -> 2023-01-20 AXISBANK: 1 @ 915.86 -> 930.32 (exit rule, 3 days). Net -Rs 2.94
- 2023-01-23 -> 2023-01-24 BHARTIARTL: 2 @ 768.67 -> 772.23 (exit rule, 1 days). Net -Rs 11.65
- 2023-01-25 -> 2023-01-27 BEL: 16 @ 100.30 -> 94.51 (stop, 2 days). Net -Rs 111.52
- 2023-01-30 -> 2023-02-06 AXISBANK: 1 @ 852.75 -> 870.98 (exit rule, 5 days). Net Rs 0.97
- 2023-02-07 -> 2023-02-08 DRREDDY: 1 @ 877.01 -> 889.11 (exit rule, 1 days). Net -Rs 5.20
- 2023-02-09 -> 2023-02-15 AXISBANK: 1 @ 877.03 -> 871.13 (exit rule, 4 days). Net -Rs 23.19
- 2023-02-16 -> 2023-03-02 INDUSINDBK: 1 @ 1156.51 -> 1098.85 (exit rule, 10 days). Net -Rs 75.51
- 2023-03-03 -> 2023-03-06 HDFCBANK: 1 @ 798.80 -> 809.19 (exit rule, 1 days). Net -Rs 6.74
- 2023-03-09 -> 2023-03-15 SUNPHARMA: 1 @ 958.46 -> 951.05 (exit rule, 4 days). Net -Rs 24.87
- 2023-03-16 -> 2023-03-20 HCLTECH: 1 @ 1085.03 -> 1103.89 (exit rule, 2 days). Net Rs 1.09
- 2023-03-21 -> 2023-03-31 NTPC: 8 @ 177.03 -> 174.63 (exit rule, 7 days). Net -Rs 37.68
- 2023-04-05 -> 2023-04-06 SUNPHARMA: 1 @ 985.98 -> 996.15 (exit rule, 1 days). Net -Rs 7.37
- 2023-04-10 -> 2023-04-17 AXISBANK: 1 @ 855.65 -> 881.12 (exit rule, 4 days). Net Rs 8.19
- 2023-04-18 -> 2023-04-19 DRREDDY: 1 @ 973.25 -> 976.50 (exit rule, 1 days). Net -Rs 14.26
- 2023-04-20 -> 2023-04-25 ICICIBANK: 1 @ 893.14 -> 905.39 (exit rule, 3 days). Net -Rs 5.09
- 2023-04-26 -> 2023-05-02 BEL: 13 @ 100.90 -> 103.90 (exit rule, 3 days). Net Rs 20.64
- 2023-05-03 -> 2023-05-09 SHRIRAMFIN: 5 @ 264.87 -> 271.47 (exit rule, 4 days). Net Rs 14.65
- 2023-05-10 -> 2023-05-15 ETERNAL: 23 @ 61.06 -> 62.04 (exit rule, 3 days). Net Rs 3.98
- 2023-05-16 -> 2023-05-19 HDFCLIFE: 2 @ 562.76 -> 564.34 (exit rule, 3 days). Net -Rs 14.70
- 2023-05-22 -> 2023-05-23 BEL: 12 @ 108.66 -> 110.84 (exit rule, 1 days). Net Rs 7.90
- 2023-05-24 -> 2023-05-26 AXISBANK: 1 @ 912.06 -> 917.08 (exit rule, 2 days). Net -Rs 12.35
- 2023-05-29 -> 2023-05-30 NTPC: 7 @ 175.12 -> 176.82 (exit rule, 1 days). Net -Rs 6.19
- 2023-05-31 -> 2023-06-01 ETERNAL: 20 @ 67.37 -> 68.63 (exit rule, 1 days). Net Rs 6.92
- 2023-06-02 -> 2023-06-08 COALINDIA: 6 @ 228.73 -> 231.17 (exit rule, 4 days). Net -Rs 3.77
- 2023-06-09 -> 2023-06-13 BAJFINANCE: 1 @ 701.98 -> 709.29 (exit rule, 2 days). Net -Rs 9.60
- 2023-06-14 -> 2023-06-23 SBIN: 2 @ 577.58 -> 555.30 (stop, 8 days). Net -Rs 62.41
- 2023-06-26 -> 2023-06-30 BAJFINANCE: 1 @ 699.70 -> 709.29 (exit rule, 3 days). Net -Rs 7.32
- 2023-07-03 -> 2023-07-04 HDFCLIFE: 2 @ 651.65 -> 653.75 (exit rule, 1 days). Net -Rs 14.05
- 2023-07-05 -> 2023-07-07 AXISBANK: 1 @ 969.97 -> 975.27 (exit rule, 2 days). Net -Rs 12.20
- 2023-07-10 -> 2023-07-17 BAJFINANCE: 1 @ 763.00 -> 751.25 (exit rule, 5 days). Net -Rs 28.78
- 2023-07-18 -> 2023-07-27 HDFCLIFE: 1 @ 667.67 -> 657.94 (exit rule, 7 days). Net -Rs 26.55
- 2023-07-28 -> 2023-08-09 BAJFINANCE: 1 @ 732.63 -> 719.28 (exit rule, 8 days). Net -Rs 30.31
- 2023-08-10 -> 2023-08-22 BHARTIARTL: 1 @ 882.88 -> 870.13 (exit rule, 7 days). Net -Rs 30.04
- 2023-08-24 -> 2023-08-30 ADANIPORTS: 1 @ 834.83 -> 827.17 (exit rule, 4 days). Net -Rs 24.85
- 2023-08-31 -> 2023-09-04 BEL: 8 @ 134.68 -> 139.36 (exit rule, 2 days). Net Rs 19.63
- 2023-09-05 -> 2023-09-06 HDFCLIFE: 1 @ 644.64 -> 642.86 (exit rule, 1 days). Net -Rs 18.56
- 2023-09-07 -> 2023-09-11 AXISBANK: 1 @ 966.02 -> 980.82 (exit rule, 2 days). Net -Rs 2.70
- 2023-09-13 -> 2023-09-14 COALINDIA: 4 @ 271.77 -> 281.02 (exit rule, 1 days). Net Rs 19.19
- 2023-09-15 -> 2023-09-20 HDFCLIFE: 1 @ 641.84 -> 658.69 (exit rule, 2 days). Net Rs 0.06
- 2023-09-21 -> 2023-09-28 ADANIPORTS: 1 @ 821.97 -> 832.42 (exit rule, 5 days). Net -Rs 6.73
- 2023-09-29 -> 2023-10-04 BAJFINANCE: 1 @ 774.67 -> 801.70 (exit rule, 2 days). Net Rs 9.93
- 2023-10-05 -> 2023-10-06 BHARTIARTL: 1 @ 925.98 -> 928.27 (exit rule, 1 days). Net -Rs 15.10
- 2023-10-09 -> 2023-10-10 NESTLEIND: 1 @ 1141.74 -> 1146.85 (exit rule, 1 days). Net -Rs 12.78
- 2023-10-13 -> 2023-10-26 SBIN: 1 @ 578.33 -> 547.79 (stop, 9 days). Net -Rs 47.13
- 2023-10-27 -> 2023-11-07 BAJFINANCE: 1 @ 751.75 -> 763.24 (exit rule, 7 days). Net -Rs 5.53
- 2023-11-08 -> 2023-11-15 SHRIRAMFIN: 2 @ 397.84 -> 396.65 (exit rule, 4 days). Net -Rs 19.48
- 2023-11-16 -> 2023-11-17 BAJFINANCE: 1 @ 695.15 -> 713.34 (exit rule, 1 days). Net Rs 1.28
- 2023-11-20 -> 2023-11-24 AXISBANK: 1 @ 981.98 -> 1001.00 (exit rule, 4 days). Net Rs 1.48
- 2023-11-28 -> 2023-11-29 BAJFINANCE: 1 @ 704.20 -> 712.69 (exit rule, 1 days). Net -Rs 8.44
- 2023-12-01 -> 2023-12-04 ADANIPORTS: 1 @ 840.04 -> 864.13 (exit rule, 1 days). Net Rs 6.87
- 2023-12-05 -> 2023-12-08 HDFCLIFE: 1 @ 679.68 -> 679.77 (exit rule, 3 days). Net -Rs 16.76
- 2023-12-11 -> 2023-12-15 BAJFINANCE: 1 @ 733.23 -> 752.13 (exit rule, 4 days). Net Rs 1.91
- 2023-12-18 -> 2023-12-28 HDFCLIFE: 1 @ 674.47 -> 646.35 (exit rule, 7 days). Net -Rs 44.93
- 2024-01-02 -> 2024-01-08 JSWSTEEL: 1 @ 884.73 -> 824.77 (stop, 5 days). Net -Rs 77.22
- 2024-01-09 -> 2024-01-11 BEL: 5 @ 185.08 -> 186.81 (exit rule, 2 days). Net -Rs 8.77
- 2024-01-12 -> 2024-01-18 BAJFINANCE: 1 @ 769.17 -> 722.92 (stop, 5 days). Net -Rs 63.25
- 2024-01-19 -> 2024-01-30 BAJFINANCE: 1 @ 736.74 -> 698.15 (exit rule, 5 days). Net -Rs 55.52
- 2024-02-01 -> 2024-02-09 BEL: 4 @ 187.89 -> 185.31 (exit rule, 6 days). Net -Rs 27.29
- 2024-02-12 -> 2024-02-15 SHRIRAMFIN: 1 @ 467.47 -> 486.95 (exit rule, 3 days). Net Rs 3.09
- 2024-02-20 -> 2024-02-21 ONGC: 2 @ 275.07 -> 275.72 (exit rule, 1 days). Net -Rs 15.27
- 2024-02-22 -> 2024-02-27 COALINDIA: 1 @ 438.44 -> 441.86 (exit rule, 3 days). Net -Rs 12.90
- 2024-02-28 -> 2024-03-04 COALINDIA: 1 @ 440.74 -> 451.40 (exit rule, 3 days). Net -Rs 5.67
- 2024-03-06 -> 2024-03-11 SHRIRAMFIN: 1 @ 489.29 -> 488.71 (exit rule, 2 days). Net -Rs 17.01
- 2024-03-12 -> 2024-03-13 COALINDIA: 1 @ 454.35 -> 414.53 (stop, 2 days). Net -Rs 56.13
- 2024-03-14 -> 2024-03-22 BEL: 3 @ 189.19 -> 196.30 (exit rule, 6 days). Net Rs 4.72
- 2024-03-27 -> 2024-04-02 WIPRO: 2 @ 240.09 -> 240.73 (exit rule, 3 days). Net -Rs 15.12
- 2024-04-04 -> 2024-04-05 ETERNAL: 3 @ 180.68 -> 188.06 (exit rule, 1 days). Net Rs 5.57
- 2024-04-08 -> 2024-04-12 ONGC: 2 @ 267.82 -> 271.63 (exit rule, 3 days). Net -Rs 8.92
- 2024-04-15 -> 2024-04-25 NTPC: 1 @ 355.86 -> 350.65 (exit rule, 7 days). Net -Rs 21.34
- 2024-04-26 -> 2024-04-29 ETERNAL: 3 @ 189.19 -> 189.21 (exit rule, 1 days). Net -Rs 16.54
- 2024-05-02 -> 2024-05-15 BEL: 2 @ 234.93 -> 231.57 (exit rule, 9 days). Net -Rs 23.11
- 2024-05-22 -> 2024-06-04 ETERNAL: 3 @ 190.19 -> 162.71 (stop, 10 days). Net -Rs 98.97
- 2024-06-05 -> 2024-06-06 ETERNAL: 2 @ 175.17 -> 184.81 (exit rule, 1 days). Net Rs 3.14
- 2024-06-12 -> 2024-06-13 COALINDIA: 1 @ 481.48 -> 493.41 (exit rule, 1 days). Net -Rs 4.49
- 2024-06-18 -> 2024-06-19 COALINDIA: 1 @ 492.49 -> 488.91 (exit rule, 1 days). Net -Rs 20.01
- 2024-06-20 -> 2024-06-21 TATASTEEL: 2 @ 181.78 -> 179.22 (exit rule, 1 days). Net -Rs 21.26
- 2024-06-24 -> 2024-06-25 ETERNAL: 2 @ 194.09 -> 201.55 (exit rule, 1 days). Net -Rs 1.31
- 2024-06-26 -> 2024-07-03 TATASTEEL: 2 @ 175.86 -> 174.37 (exit rule, 5 days). Net -Rs 19.10
- 2024-07-05 -> 2024-07-08 ETERNAL: 2 @ 207.21 -> 208.04 (exit rule, 1 days). Net -Rs 14.59
- 2024-07-09 -> 2024-07-19 TATASTEEL: 2 @ 173.77 -> 163.74 (stop, 8 days). Net -Rs 36.15
- 2024-07-22 -> 2024-07-29 BEL: 1 @ 306.31 -> 312.49 (exit rule, 5 days). Net -Rs 9.85
- 2024-07-31 -> 2024-08-08 JIOFIN: 1 @ 329.68 -> 329.67 (exit rule, 6 days). Net -Rs 16.08
- 2024-08-12 -> 2024-08-13 JIOFIN: 1 @ 325.32 -> 329.17 (exit rule, 1 days). Net -Rs 12.22
- 2024-08-14 -> 2024-08-19 BEL: 1 @ 296.45 -> 304.50 (exit rule, 2 days). Net -Rs 7.96
- 2024-08-22 -> 2024-08-27 ONGC: 1 @ 328.88 -> 329.07 (exit rule, 3 days). Net -Rs 15.88
- 2024-08-28 -> 2024-09-06 ETERNAL: 1 @ 257.26 -> 254.75 (exit rule, 7 days). Net -Rs 18.42
- 2024-09-09 -> 2024-09-12 BEL: 1 @ 282.28 -> 290.61 (exit rule, 3 days). Net -Rs 7.65
- 2024-09-18 -> 2024-09-24 BEL: 1 @ 285.18 -> 286.01 (exit rule, 4 days). Net -Rs 15.15
- 2024-09-30 -> 2024-10-07 ETERNAL: 1 @ 278.18 -> 278.27 (exit rule, 4 days). Net -Rs 15.87
- 2024-10-08 -> 2024-10-22 TATASTEEL: 1 @ 163.16 -> 154.75 (exit rule, 10 days). Net -Rs 24.11
- 2025-03-27 -> 2025-04-03 TATASTEEL: 1 @ 154.95 -> 152.85 (exit rule, 4 days). Net -Rs 17.79
- 2025-05-28 -> 2025-05-30 TATASTEEL: 1 @ 162.56 -> 162.95 (exit rule, 2 days). Net -Rs 15.32
- 2025-06-03 -> 2025-06-17 TATASTEEL: 1 @ 159.20 -> 153.66 (time, 10 days). Net -Rs 21.23
- 2025-06-19 -> 2025-06-24 TATASTEEL: 1 @ 152.15 -> 153.65 (exit rule, 3 days). Net -Rs 14.19
- 2025-07-07 -> 2025-07-15 TATASTEEL: 1 @ 163.16 -> 160.10 (exit rule, 6 days). Net -Rs 18.76
