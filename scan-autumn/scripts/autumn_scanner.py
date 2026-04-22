#!/usr/bin/env python3
"""
秋天股票掃描器 — 台股版（僅掃描有股票期貨的標的）

根據權證小哥「股票四季理論」，秋天股票特徵：
  股價經過一波大漲後進入高檔震盪，漲勢鈍化、量能萎縮、技術指標出現背離。
  代表風險大於機會，適合獲利了結或做空。

篩選條件：
  1. 股價高檔區：收盤價在近 120 日高點的 90% 以上
  2. 漲勢鈍化：近 10 日漲幅明顯小於前 10~20 日漲幅
  3. 量價背離：股價接近高點但成交量低於 20 日均量
  4. 黑 K 頻現：近 10 日黑 K（收盤 < 開盤）≥ 5 根
  5. KD 從高檔滑落：K 從 80 以上回落至 80 以下（由強轉弱）
  6. MACD 動能減弱：MACD 柱狀體由正開始縮小
  7. 均線多排鬆動：5MA < 10MA 或 10MA < 20MA（多頭排列瓦解）
  8. 連續黑 K：近 5 日出現連續 ≥ 3 根黑 K（持續性賣壓）
"""

import argparse
import yfinance as yf
import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime, timedelta
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 有股票期貨的台股標的（來源：期交所 2026/03/19 更新）
# 僅保留個股，排除 ETF（00 開頭）
# ============================================================
STOCK_FUTURES_LIST = [
    # 整理自期交所股票期貨標的清單，去重後
    "1101.TW", "1102.TW", "1210.TW", "1216.TW", "1301.TW", "1303.TW",
    "1312.TW", "1314.TW", "1319.TW", "1326.TW", "1402.TW", "1440.TW",
    "1476.TW", "1477.TW", "1503.TW", "1504.TW", "1513.TW", "1536.TW",
    "1560.TW", "1565.TW", "1590.TW", "1605.TW", "1608.TW", "1609.TW",
    "1717.TW", "1718.TW", "1722.TW", "1760.TW", "1795.TW", "1802.TW",
    "1904.TW", "1905.TW", "1907.TW", "1909.TW",
    "2002.TW", "2006.TW", "2014.TW", "2027.TW", "2049.TW", "2059.TW",
    "2105.TW", "2201.TW", "2207.TW", "2231.TW", "2301.TW", "2303.TW",
    "2308.TW", "2312.TW", "2313.TW", "2317.TW", "2323.TW", "2324.TW",
    "2327.TW", "2328.TW", "2329.TW", "2330.TW", "2331.TW", "2332.TW",
    "2337.TW", "2338.TW", "2340.TW", "2344.TW", "2345.TW", "2347.TW",
    "2352.TW", "2353.TW", "2354.TW", "2355.TW", "2356.TW", "2357.TW",
    "2360.TW", "2367.TW", "2368.TW", "2371.TW", "2376.TW", "2377.TW",
    "2379.TW", "2382.TW", "2383.TW", "2385.TW", "2388.TW", "2392.TW",
    "2393.TW", "2395.TW", "2401.TW", "2404.TW", "2408.TW", "2409.TW",
    "2412.TW", "2421.TW", "2439.TW", "2441.TW", "2449.TW", "2454.TW",
    "2455.TW", "2457.TW", "2458.TW", "2474.TW", "2481.TW", "2485.TW",
    "2486.TW", "2489.TW", "2492.TW", "2498.TW", "2515.TW", "2520.TW",
    "2542.TW", "2548.TW", "2603.TW", "2605.TW", "2606.TW", "2609.TW",
    "2610.TW", "2615.TW", "2618.TW", "2633.TW", "2634.TW",
    "2801.TW", "2834.TW", "2880.TW", "2881.TW", "2882.TW", "2883.TW",
    "2884.TW", "2885.TW", "2886.TW", "2887.TW", "2890.TW", "2891.TW",
    "2892.TW", "2912.TW", "2913.TW", "2915.TW",
    "3005.TW", "3006.TW", "3008.TW", "3017.TW", "3019.TW", "3034.TW",
    "3035.TW", "3036.TW", "3037.TW", "3042.TW", "3044.TW", "3045.TW",
    "3078.TW", "3081.TW", "3105.TW", "3152.TW", "3189.TW", "3211.TW",
    "3227.TW", "3231.TW", "3260.TW", "3264.TW", "3293.TW", "3324.TW",
    "3374.TW", "3376.TW", "3380.TW", "3406.TW", "3443.TW", "3481.TW",
    "3529.TW", "3532.TW", "3533.TW", "3552.TW", "3653.TW", "3661.TW",
    "3665.TW", "3673.TW", "3680.TW", "3691.TW", "3702.TW", "3706.TW",
    "3711.TW", "3714.TW",
    "4123.TW", "4128.TW", "4162.TW", "4736.TW", "4743.TW",
    "4904.TW", "4919.TW", "4938.TW", "4958.TW", "4977.TW",
    "5009.TW", "5269.TW", "5274.TW", "5347.TW", "5371.TW",
    "5388.TW", "5425.TW", "5457.TW", "5483.TW", "5534.TW",
    "5765.TW", "5871.TW", "5876.TW", "5880.TW", "5904.TW",
    "6005.TW", "6116.TW", "6121.TW", "6139.TW", "6147.TW",
    "6153.TW", "6173.TW", "6176.TW", "6182.TW", "6188.TW",
    "6213.TW", "6223.TW", "6239.TW", "6245.TW", "6257.TW",
    "6269.TW", "6271.TW", "6274.TW", "6278.TW", "6279.TW",
    "6282.TW", "6285.TW", "6290.TW", "6414.TW", "6443.TW",
    "6446.TW", "6472.TW", "6488.TW", "6505.TW", "6510.TW",
    "6526.TW", "6547.TW", "6669.TW", "6757.TW", "6770.TW",
    "8039.TW", "8044.TW", "8046.TW", "8069.TW", "8086.TW",
    "8112.TW", "8150.TW", "8163.TW", "8299.TW", "8358.TW",
    "8436.TW",
    "9904.TW", "9914.TW", "9938.TW", "9939.TW", "9945.TW", "9958.TW",
]


def fetch_data(symbol, period="1y"):
    """下載股票日線資料"""
    df = yf.download(symbol, period=period, auto_adjust=True, progress=False)
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def calc_kd(df, n=9):
    """計算 KD 指標（9 日）"""
    low_min = df["Low"].rolling(window=n).min()
    high_max = df["High"].rolling(window=n).max()
    rsv = (df["Close"] - low_min) / (high_max - low_min) * 100

    k = pd.Series(index=df.index, dtype=float)
    d = pd.Series(index=df.index, dtype=float)
    k.iloc[n - 1] = 50
    d.iloc[n - 1] = 50

    for i in range(n, len(df)):
        k.iloc[i] = 2 / 3 * k.iloc[i - 1] + 1 / 3 * rsv.iloc[i]
        d.iloc[i] = 2 / 3 * d.iloc[i - 1] + 1 / 3 * k.iloc[i]

    df["K"] = k
    df["D"] = d
    return df


def calc_macd(df, fast=12, slow=26, signal=9):
    """計算 MACD 指標"""
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["DIF"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["DIF"].ewm(span=signal, adjust=False).mean()
    df["OSC"] = (df["DIF"] - df["MACD_Signal"]) * 2  # 柱狀體
    return df


def calc_indicators(df):
    """計算所有技術指標"""
    close = df["Close"]
    volume = df["Volume"]

    # 均線
    df["MA5"] = close.rolling(5).mean()
    df["MA10"] = close.rolling(10).mean()
    df["MA20"] = close.rolling(20).mean()

    # 成交量均線
    df["Vol_MA20"] = volume.rolling(20).mean()

    # 近 120 日最高價
    df["High_120"] = close.rolling(120).max()

    # KD
    df = calc_kd(df)

    # MACD
    df = calc_macd(df)

    return df


def check_autumn(df):
    """
    檢查股票是否處於秋天階段
    回傳 (符合條件數, 條件明細 dict, 額外資訊 dict)
    """
    if len(df) < 120:
        return 0, {}, {}

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    conditions = {}
    info = {}

    # === 條件 1：股價高檔區 ===
    # 收盤價在近 120 日高點的 90% 以上
    high_120 = latest["High_120"]
    price_ratio = latest["Close"] / high_120 if high_120 > 0 else 0
    conditions["高檔區"] = price_ratio >= 0.90
    info["距高點(%)"] = round((1 - price_ratio) * 100, 1)

    # === 條件 2：漲勢鈍化 ===
    # 近 10 日漲幅 vs 前 10~20 日漲幅
    if len(df) >= 21:
        recent_10_return = (df["Close"].iloc[-1] / df["Close"].iloc[-11] - 1) * 100
        prev_10_return = (df["Close"].iloc[-11] / df["Close"].iloc[-21] - 1) * 100
        momentum_decay = recent_10_return < prev_10_return and prev_10_return > 0
        conditions["漲勢鈍化"] = momentum_decay
        info["近10日漲幅(%)"] = round(recent_10_return, 2)
        info["前10日漲幅(%)"] = round(prev_10_return, 2)
    else:
        conditions["漲勢鈍化"] = False
        info["近10日漲幅(%)"] = np.nan
        info["前10日漲幅(%)"] = np.nan

    # === 條件 3：量價背離 ===
    # 股價在高檔（距高點 5% 內）但成交量低於 20 日均量
    near_high = price_ratio >= 0.95
    vol_shrink = latest["Volume"] < latest["Vol_MA20"]
    conditions["量價背離"] = near_high and vol_shrink
    vol_ratio = round(latest["Volume"] / latest["Vol_MA20"], 2) if latest["Vol_MA20"] > 0 else 0
    info["量比"] = vol_ratio

    # === 條件 4：黑 K 頻現 ===
    # 近 10 日黑 K（收盤 < 開盤）≥ 5 根
    recent_10 = df.tail(10)
    black_k_count = int((recent_10["Close"] < recent_10["Open"]).sum())
    conditions["黑K頻現"] = black_k_count >= 5
    info["近10日黑K數"] = black_k_count

    # === 條件 5：KD 從高檔滑落 ===
    # 近 10 日 K 值曾 ≥ 80，但目前已回落至 80 以下（由強轉弱）
    k_val = latest["K"]
    d_val = latest["D"]
    if not np.isnan(k_val) and not np.isnan(d_val):
        recent_k = df["K"].tail(10)
        k_was_high = recent_k.max() >= 80
        k_now_falling = k_val < 80
        conditions["KD滑落"] = k_was_high and k_now_falling
        info["K值"] = round(k_val, 1)
        info["D值"] = round(d_val, 1)
        info["近10日K最高"] = round(recent_k.max(), 1)
    else:
        conditions["KD滑落"] = False
        info["K值"] = np.nan
        info["D值"] = np.nan
        info["近10日K最高"] = np.nan

    # === 條件 6：MACD 動能減弱 ===
    # OSC（柱狀體）> 0 但開始縮小（今天 < 昨天）
    osc_today = latest["OSC"]
    osc_yesterday = prev["OSC"]
    if not np.isnan(osc_today) and not np.isnan(osc_yesterday):
        macd_weakening = osc_today > 0 and osc_today < osc_yesterday
        conditions["MACD減弱"] = macd_weakening
        info["OSC"] = round(osc_today, 2)
        info["OSC前日"] = round(osc_yesterday, 2)
    else:
        conditions["MACD減弱"] = False
        info["OSC"] = np.nan
        info["OSC前日"] = np.nan

    # === 條件 7：均線多排鬆動 ===
    # 原本多頭排列（5MA > 10MA > 20MA）開始瓦解
    # 判斷：5MA < 10MA 或 10MA < 20MA（短均線開始下穿長均線）
    ma5 = latest["MA5"]
    ma10 = latest["MA10"]
    ma20 = latest["MA20"]
    if not any(np.isnan(v) for v in [ma5, ma10, ma20]):
        ma_breakdown = (ma5 < ma10) or (ma10 < ma20)
        conditions["均線鬆動"] = ma_breakdown
        info["5MA-10MA"] = round(ma5 - ma10, 2)
        info["10MA-20MA"] = round(ma10 - ma20, 2)
    else:
        conditions["均線鬆動"] = False
        info["5MA-10MA"] = np.nan
        info["10MA-20MA"] = np.nan

    # === 條件 8：連續黑 K ===
    # 近 5 日出現連續 ≥ 3 根黑 K（持續性賣壓）
    recent_5_black = (df["Close"].tail(5) < df["Open"].tail(5)).values
    max_consecutive = 0
    current_streak = 0
    for is_black in recent_5_black:
        if is_black:
            current_streak += 1
            max_consecutive = max(max_consecutive, current_streak)
        else:
            current_streak = 0
    conditions["連續黑K"] = max_consecutive >= 3
    info["近5日最長連黑"] = max_consecutive

    score = sum(conditions.values())
    return score, conditions, info


def scan_single_stock(symbol):
    """掃描單一股票"""
    try:
        df = fetch_data(symbol, period="1y")
        if df is None or len(df) < 120:
            return None

        df = calc_indicators(df)

        score, conditions, info = check_autumn(df)

        # 至少符合 3 個條件才列入
        if score >= 3:
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            change_pct = round((latest["Close"] - prev["Close"]) / prev["Close"] * 100, 2)

            result = {
                "代號": symbol.replace(".TW", ""),
                "收盤價": round(latest["Close"], 2),
                "漲跌(%)": change_pct,
                "分數": f"{score}/8",
                "分數值": score,
            }

            # 條件欄位
            for name, ok in conditions.items():
                result[name] = "✅" if ok else "❌"

            # 額外資訊
            result.update(info)

            return result

        return None

    except Exception as e:
        return None


def print_results(results):
    """輸出掃描結果"""
    if not results:
        print("\n  ❌ 沒有符合秋天股票條件的標的（至少 3/8 條件）")
        print("  提示：目前市場可能處於其他季節階段。\n")
        return

    results.sort(key=lambda x: x["分數值"], reverse=True)

    print(f"\n  🍂 找到 {len(results)} 檔秋天股票（有股票期貨標的）：\n")

    # === 主要表格 ===
    main_cols = ["代號", "收盤價", "漲跌(%)", "分數", "距高點(%)", "量比", "K值", "D值"]
    main_data = [{k: r.get(k, "-") for k in main_cols} for r in results]
    print(tabulate(main_data, headers="keys", tablefmt="rounded_grid",
                   numalign="right", stralign="center"))

    # === 條件明細 ===
    print("\n  📋 條件明細：\n")
    cond_cols = ["代號", "高檔區", "漲勢鈍化", "量價背離", "黑K頻現",
                 "KD滑落", "MACD減弱", "均線鬆動", "連續黑K", "分數"]
    cond_data = [{k: r.get(k, "-") for k in cond_cols} for r in results]
    print(tabulate(cond_data, headers="keys", tablefmt="rounded_grid",
                   stralign="center"))

    # === 動能詳細 ===
    print("\n  📊 動能詳細資訊：\n")
    detail_cols = ["代號", "近10日漲幅(%)", "前10日漲幅(%)", "近10日黑K數",
                   "K值", "近10日K最高", "OSC", "5MA-10MA", "10MA-20MA",
                   "近5日最長連黑"]
    detail_data = [{k: r.get(k, "-") for k in detail_cols} for r in results]
    print(tabulate(detail_data, headers="keys", tablefmt="rounded_grid",
                   numalign="right", stralign="center"))

    # === 高危險群（5 分以上） ===
    high_risk = [r for r in results if r["分數值"] >= 5]
    if high_risk:
        print("\n  ⚠️  高危險群（5 分以上，強烈秋天訊號）：\n")
        hr_cols = ["代號", "收盤價", "分數", "距高點(%)", "K值", "D值", "量比"]
        hr_data = [{k: r.get(k, "-") for k in hr_cols} for r in high_risk]
        print(tabulate(hr_data, headers="keys", tablefmt="rounded_grid",
                       numalign="right", stralign="center"))

    # === 說明 ===
    print("\n" + "=" * 70)
    print("  🍂 秋天股票判讀說明：")
    print("  ─────────────────────────────────────")
    print("  • 7-8/8 分：極度危險！強烈建議獲利了結")
    print("  • 5-6/8 分：秋意濃厚，應減碼或停止加碼")
    print("  • 3-4/8 分：初秋訊號，提高警覺、設好停損")
    print("  ─────────────────────────────────────")
    print("  • 高檔區：股價位於近半年高點 90% 以上")
    print("  • 漲勢鈍化：近 10 日漲幅 < 前 10 日漲幅（動能衰退）")
    print("  • 量價背離：股價在高檔但成交量萎縮")
    print("  • 黑 K 頻現：近 10 日黑 K ≥ 5 根（賣壓持續勝出）")
    print("  • KD 滑落：K 值曾達 80 以上，但已回落至 80 以下（由強轉弱）")
    print("  • MACD 減弱：柱狀體由正開始縮小（多方力道衰退）")
    print("  • 均線鬆動：5MA < 10MA 或 10MA < 20MA（多頭排列瓦解）")
    print("  • 連續黑 K：近 5 日出現連續 ≥ 3 根黑 K（持續性賣壓）")
    print("  ─────────────────────────────────────")
    print("  💡 有股票期貨標的，可考慮用「股票期貨做空」來獲利")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="秋天股票掃描器 — 台股（僅掃描有股票期貨標的）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  python3 autumn_scanner.py                  # 掃描所有有股票期貨的標的
  python3 autumn_scanner.py 2330 2454        # 掃描指定股票
  python3 autumn_scanner.py --min-score 5    # 只顯示 5 分以上的高危險群
        """)
    parser.add_argument("stocks", nargs="*",
                        help="股票代號（可多個），例如 2330 2454。不帶 .TW 會自動補上")
    parser.add_argument("--min-score", "-m", type=int, default=3,
                        help="最低分數門檻（預設 3，範圍 1-8）")

    args = parser.parse_args()
    min_score = max(1, min(8, args.min_score))

    # 標題
    print("=" * 70)
    print("  🍂 秋天股票掃描器 — 台股（股票期貨標的）")
    print(f"  掃描時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  最低分數門檻：{min_score}/8")
    print("=" * 70)

    # 股票清單
    if args.stocks:
        stock_list = [s if "." in s else f"{s}.TW" for s in args.stocks]
        print(f"\n  自訂掃描：{', '.join(stock_list)}")
    else:
        stock_list = STOCK_FUTURES_LIST
        print(f"\n  掃描範圍：有股票期貨的標的，共 {len(stock_list)} 檔")

    total = len(stock_list)
    results = []

    print(f"  正在掃描 {total} 檔股票...\n")

    for i, symbol in enumerate(stock_list, 1):
        name = symbol.replace(".TW", "")
        print(f"\r  [{i:3d}/{total}] 掃描 {name}...    ", end="", flush=True)

        result = scan_single_stock(symbol)
        if result and result["分數值"] >= min_score:
            results.append(result)

        # 避免 API 過度請求
        if i % 5 == 0:
            time.sleep(1)

    print(f"\r{' ' * 60}\r", end="")

    print_results(results)

    # 儲存 CSV
    if results:
        output_file = f"autumn_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        # 移除分數值欄位（僅用於排序）
        save_data = [{k: v for k, v in r.items() if k != "分數值"} for r in results]
        pd.DataFrame(save_data).to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n  結果已儲存至：{output_file}")

    # 用法提示
    print("\n  💡 用法提示：")
    print("     python3 autumn_scanner.py                  # 掃描全部股票期貨標的")
    print("     python3 autumn_scanner.py 2330 2454        # 指定股票")
    print("     python3 autumn_scanner.py --min-score 5    # 只看高危險群")
    print()


if __name__ == "__main__":
    main()
