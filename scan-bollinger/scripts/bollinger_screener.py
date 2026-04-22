"""
布林通道開布林選股程式
條件：
1. 日線布林帶寬收縮至近 60 日低點
2. 10MA > 20MA 連續 ≥ 10 個交易日
3. 20MA 方向上彎
4. 日線收盤站上日布林上軌
5. 成交量 ≥ 5 日均量 × 1.5
6. 日布林上下軌喇叭張口
7. 週線收盤同步站上週布林上軌
額外資訊：
- 近 20 日股價站上 10MA 天數
- 10MA 在 20MA 之上天數
- 10MA / 20MA 斜率
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 台股交易時段（09:00 ~ 13:30）
MARKET_OPEN_HOUR, MARKET_OPEN_MIN = 9, 0
MARKET_CLOSE_HOUR, MARKET_CLOSE_MIN = 13, 30
TOTAL_TRADING_MINUTES = (MARKET_CLOSE_HOUR - MARKET_OPEN_HOUR) * 60 + (MARKET_CLOSE_MIN - MARKET_OPEN_MIN)


def is_tw_market_open():
    """判斷現在是否為台股盤中時段"""
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MIN, second=0)
    market_close = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MIN, second=0)
    return market_open <= now <= market_close


def get_intraday_volume_ratio():
    """回傳盤中已交易時間佔比（0.0 ~ 1.0）"""
    now = datetime.now()
    market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MIN, second=0)
    elapsed = (now - market_open).total_seconds() / 60.0
    elapsed = max(1, min(elapsed, TOTAL_TRADING_MINUTES))
    return elapsed / TOTAL_TRADING_MINUTES


# ============================================================
# 台股熱門股票清單（可自行增減）
# ============================================================
TW_STOCKS = [
    "2330.TW",  # 台積電
    "2317.TW",  # 鴻海
    "2454.TW",  # 聯發科
    "2308.TW",  # 台達電
    "2881.TW",  # 富邦金
    "2882.TW",  # 國泰金
    "2891.TW",  # 中信金
    "2303.TW",  # 聯電
    "3711.TW",  # 日月光投控
    "2412.TW",  # 中華電
    "2886.TW",  # 兆豐金
    "1301.TW",  # 台塑
    "1303.TW",  # 南亞
    "2002.TW",  # 中鋼
    "2884.TW",  # 玉山金
    "3008.TW",  # 大立光
    "2357.TW",  # 華碩
    "2382.TW",  # 廣達
    "2395.TW",  # 研華
    "3034.TW",  # 聯詠
    "2327.TW",  # 國巨
    "3037.TW",  # 欣興
    "6505.TW",  # 台塑化
    "2301.TW",  # 光寶科
    "2345.TW",  # 智邦
    "4904.TW",  # 遠傳
    "2207.TW",  # 和泰車
    "5871.TW",  # 中租-KY
    "2379.TW",  # 瑞昱
    "3661.TW",  # 世芯-KY
    "2603.TW",  # 長榮
    "2609.TW",  # 陽明
    "2615.TW",  # 萬海
    "3443.TW",  # 創意
    "2049.TW",  # 上銀
    "8069.TW",  # 元太
    "6669.TW",  # 緯穎
    "3529.TW",  # 力旺
    "5274.TW",  # 信驊
    "6446.TW",  # 藥華藥
]


def fetch_data(symbol, period="1y"):
    """下載股票日線資料"""
    df = yf.download(symbol, period=period, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def calc_daily_indicators(df):
    """計算日線指標：布林通道、均線、成交量均線"""
    close = df["Close"]
    volume = df["Volume"]

    # 均線
    df["MA10"] = close.rolling(10).mean()
    df["MA20"] = close.rolling(20).mean()

    # 布林通道 (20, 2)
    df["BB_Mid"] = df["MA20"]
    df["BB_Std"] = close.rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * df["BB_Std"]
    df["BB_Lower"] = df["BB_Mid"] - 2 * df["BB_Std"]
    df["BandWidth"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

    # 成交量均線
    df["Vol_MA5"] = volume.rolling(5).mean()

    return df


def calc_weekly_bollinger(df):
    """從日線資料計算週布林通道，回傳最新一週的上軌值"""
    weekly = df.resample("W-FRI").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }).dropna()

    if len(weekly) < 20:
        return None, None

    weekly["W_MA20"] = weekly["Close"].rolling(20).mean()
    weekly["W_Std"] = weekly["Close"].rolling(20).std()
    weekly["W_Upper"] = weekly["W_MA20"] + 2 * weekly["W_Std"]
    weekly["W_Lower"] = weekly["W_MA20"] - 2 * weekly["W_Std"]

    return weekly


def calc_slope(series, n=5):
    """
    計算均線斜率（最近 n 日的線性回歸斜率）
    回傳每日變動量及年化角度
    """
    recent = series.dropna().tail(n).values
    if len(recent) < n:
        return np.nan, np.nan

    x = np.arange(n)
    slope = np.polyfit(x, recent, 1)[0]  # 每日變動量
    pct_slope = slope / recent[0] * 100   # 百分比斜率 (%/日)
    return round(slope, 2), round(pct_slope, 4)


def count_price_above_ma10(df, lookback=20):
    """近 N 日股價站上 10MA 的天數"""
    recent = df.tail(lookback)
    return int((recent["Close"] > recent["MA10"]).sum())


def count_ma10_above_ma20(df):
    """10MA 在 20MA 之上的連續天數（從最新日往回數）"""
    ma10 = df["MA10"].dropna()
    ma20 = df["MA20"].dropna()
    idx = ma10.index.intersection(ma20.index)
    if len(idx) == 0:
        return 0

    above = (ma10.loc[idx] > ma20.loc[idx])
    count = 0
    for val in reversed(above.values):
        if val:
            count += 1
        else:
            break
    return count


def check_bollinger_squeeze(df, lookback=60):
    """帶寬是否處於近 N 日低點附近（最低 20%）"""
    bw = df["BandWidth"].dropna().tail(lookback)
    if len(bw) < lookback:
        return False, np.nan

    current_bw = bw.iloc[-1]
    min_bw = bw.min()
    rank_pct = (bw < current_bw).sum() / len(bw)
    return rank_pct <= 0.20, round(rank_pct * 100, 1)


def check_band_expansion(df):
    """上軌往上 + 下軌往下（喇叭張口）"""
    if len(df) < 3:
        return False
    upper_rising = df["BB_Upper"].iloc[-1] > df["BB_Upper"].iloc[-2]
    lower_falling = df["BB_Lower"].iloc[-1] < df["BB_Lower"].iloc[-2]
    return upper_rising and lower_falling


def screen_single_stock(symbol, intraday=False):
    """對單一股票執行完整篩選"""
    df = fetch_data(symbol, period="2y")
    if df is None or len(df) < 120:
        return None

    # 盤中模式：推估全日量
    if intraday:
        time_ratio = get_intraday_volume_ratio()
        df.iloc[-1, df.columns.get_loc("Volume")] = df.iloc[-1]["Volume"] / time_ratio

    df = calc_daily_indicators(df)
    weekly = calc_weekly_bollinger(df)

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # ------ 漲幅 ------
    change_pct = round((latest["Close"] - prev["Close"]) / prev["Close"] * 100, 2)

    # ------ 基本資料 ------
    result = {
        "代碼": symbol.replace(".TW", ""),
        "收盤價": round(latest["Close"], 2),
        "漲幅(%)": change_pct,
        "日期": df.index[-1].strftime("%Y-%m-%d"),
    }

    # ------ 條件 1：布林帶寬收縮 ------
    is_squeezed, bw_rank = check_bollinger_squeeze(df, 60)
    # 注意：我們檢查的是突破「前一日」是否處於收縮狀態
    # 如果今天已經突破，帶寬可能已擴張，所以也看前幾日
    prev_squeezed, _ = check_bollinger_squeeze(
        df.iloc[:-1], 60) if len(df) > 61 else (False, None)
    squeeze_ok = is_squeezed or prev_squeezed

    # ------ 條件 2：10MA > 20MA 連續天數 ------
    ma10_above_ma20_days = count_ma10_above_ma20(df)
    ma_cross_ok = ma10_above_ma20_days >= 10

    # ------ 條件 3：20MA 上彎 ------
    ma20_slope, ma20_slope_pct = calc_slope(df["MA20"], n=5)
    ma20_up = ma20_slope > 0

    # ------ 條件 4：收盤站上日布林上軌 ------
    close_above_upper = latest["Close"] > latest["BB_Upper"]

    # ------ 條件 5：成交量 ≥ 1.5 倍 5 日均量 ------
    vol_ok = latest["Volume"] >= latest["Vol_MA5"] * 1.5
    vol_ratio = round(latest["Volume"] / latest["Vol_MA5"], 2) if latest["Vol_MA5"] > 0 else 0

    # ------ 條件 6：喇叭張口 ------
    band_expand = check_band_expansion(df)

    # ------ 條件 7：週線站上週布林上軌 ------
    weekly_ok = False
    if weekly is not None and len(weekly) >= 20:
        w_latest = weekly.iloc[-1]
        if not np.isnan(w_latest["W_Upper"]):
            weekly_ok = w_latest["Close"] > w_latest["W_Upper"]

    # ------ 額外資訊 ------
    price_above_ma10_days = count_price_above_ma10(df, 20)
    ma10_slope, ma10_slope_pct = calc_slope(df["MA10"], n=5)

    # ------ 彙整 ------
    conditions = [
        squeeze_ok,       # 1. 帶寬收縮
        ma_cross_ok,      # 2. 10MA > 20MA ≥ 10天
        ma20_up,          # 3. 20MA 上彎
        close_above_upper,# 4. 站上日布林上軌
        vol_ok,           # 5. 量能放大
        band_expand,      # 6. 喇叭張口
        weekly_ok,        # 7. 週線站上週布林上軌
    ]
    matched_nums = ",".join(str(i + 1) for i, ok in enumerate(conditions) if ok)

    result.update({
        "站上日布林上軌": "✅" if close_above_upper else "❌",
        "站上週布林上軌": "✅" if weekly_ok else "❌",
        "帶寬收縮": "✅" if squeeze_ok else "❌",
        "10>20MA天數": ma10_above_ma20_days,
        "20MA上彎": "✅" if ma20_up else "❌",
        "量比(倍)": vol_ratio,
        "量能放大": "✅" if vol_ok else "❌",
        "喇叭張口": "✅" if band_expand else "❌",
        "近20日站上10MA": f"{price_above_ma10_days}天",
        "10MA斜率(/日)": ma10_slope,
        "10MA斜率(%/日)": ma10_slope_pct,
        "20MA斜率(/日)": ma20_slope,
        "20MA斜率(%/日)": ma20_slope_pct,
        "符合條件數": sum(conditions),
        "符合項目": matched_nums if matched_nums else "-",
        "全部符合": "★" if all(conditions) else "",
    })

    return result


def format_display(df):
    """回傳一份顯示用副本：漲幅/10>20MA天數 超過門檻時附加 ✅"""
    out = df.copy()
    if "漲幅(%)" in out.columns:
        out["漲幅(%)"] = out["漲幅(%)"].apply(
            lambda v: f"{v:>6.2f} ✅" if pd.notna(v) and v > 5 else f"{v:>6.2f}  "
        )
    if "10>20MA天數" in out.columns:
        out["10>20MA天數"] = out["10>20MA天數"].apply(
            lambda v: f"{int(v):>3d} ✅" if pd.notna(v) and v >= 10 else f"{int(v):>3d}  "
        )
    return out


def run_screener(stock_list=None):
    """執行選股掃描"""
    if stock_list is None:
        stock_list = TW_STOCKS

    # 自動偵測盤中模式
    intraday = is_tw_market_open()

    print("=" * 80)
    print("  布林通道開布林選股系統（日線 + 週線共振）")
    print(f"  掃描時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if intraday:
        pct = round(get_intraday_volume_ratio() * 100)
        print(f"  ⏰ 盤中模式：已交易 {pct}%，成交量為推估全日量")
    print(f"  掃描檔數：{len(stock_list)}")
    print("=" * 80)
    print()

    results = []
    for i, symbol in enumerate(stock_list, 1):
        name = symbol.replace(".TW", "")
        print(f"\r  掃描中... [{i}/{len(stock_list)}] {name}    ", end="", flush=True)
        try:
            result = screen_single_stock(symbol, intraday=intraday)
            if result:
                results.append(result)
        except Exception as e:
            print(f"\n  ⚠ {name} 發生錯誤: {e}")

    print("\r" + " " * 60)

    if not results:
        print("  沒有取得任何股票資料。")
        return

    df = pd.DataFrame(results)
    df = df.sort_values("符合條件數", ascending=False)

    # ------ 輸出完整結果 ------
    print("\n" + "=" * 80)
    print("  【完整掃描結果】依符合條件數排序")
    print("=" * 80)

    display_cols = [
        "代碼", "收盤價", "漲幅(%)", "量比(倍)",
        "站上日布林上軌", "站上週布林上軌",
        "帶寬收縮", "10>20MA天數", "20MA上彎",
        "喇叭張口", "10MA斜率(%/日)", "20MA斜率(%/日)",
        "符合條件數", "全部符合",
    ]
    print(format_display(df)[display_cols].to_string(index=False))

    # ------ 均線詳細資訊 ------
    print("\n" + "=" * 80)
    print("  【均線與斜率詳細資訊】")
    print("=" * 80)

    ma_cols = [
        "代碼", "收盤價", "漲幅(%)", "量比(倍)",
        "近20日站上10MA", "10>20MA天數",
        "10MA斜率(/日)", "10MA斜率(%/日)",
        "20MA斜率(/日)", "20MA斜率(%/日)",
    ]
    print(format_display(df)[ma_cols].to_string(index=False))

    # ------ 漲跌幅 / 量能專屬排行榜 ------
    rank_cols = ["代碼", "收盤價", "漲幅(%)", "量比(倍)",
                 "10>20MA天數", "10MA斜率(%/日)", "20MA斜率(%/日)",
                 "符合條件數"]

    print("\n" + "=" * 80)
    print("  【今日漲幅排行 TOP 10】")
    print("=" * 80)
    top_gainers = df.sort_values("漲幅(%)", ascending=False).head(10)
    print(format_display(top_gainers)[rank_cols].to_string(index=False))

    print("\n" + "=" * 80)
    print("  【今日跌幅排行 TOP 5】")
    print("=" * 80)
    top_losers = df.sort_values("漲幅(%)", ascending=True).head(5)
    print(format_display(top_losers)[rank_cols].to_string(index=False))

    print("\n" + "=" * 80)
    print("  【量能放大排行 TOP 10】（量比 = 當日量 / 5日均量）")
    print("=" * 80)
    top_volume = df.sort_values("量比(倍)", ascending=False).head(10)
    print(format_display(top_volume)[rank_cols].to_string(index=False))

    vol_expand = df[df["量比(倍)"] >= 1.5].sort_values("量比(倍)", ascending=False)
    if not vol_expand.empty:
        print("\n  ★ 量能放大（量比 ≥ 1.5 倍）共 {} 檔：".format(len(vol_expand)))
        print(format_display(vol_expand)[rank_cols].to_string(index=False))
    else:
        print("\n  ⚠ 今日無量比 ≥ 1.5 倍之個股。")

    # ------ 精選股 ------
    selected = df[df["符合條件數"] >= 5]
    if not selected.empty:
        print("\n" + "=" * 80)
        print("  【精選強勢股】符合 5 個條件以上")
        print("=" * 80)
        print(format_display(selected)[display_cols + ["近20日站上10MA",
              "量能放大"]].to_string(index=False))

        # ------ 條件檢核矩陣（精選股一目瞭然） ------
        print("\n" + "=" * 80)
        print("  【強勢股條件檢核】符合=✅　不符合=❌")
        print("=" * 80)

        cond_labels = [
            ("1.帶寬收縮", "帶寬收縮"),
            ("2.10>20MA≥10", "10>20MA≥10"),
            ("3.20MA上彎", "20MA上彎"),
            ("4.站上日布林", "站上日布林上軌"),
            ("5.量能放大", "量能放大"),
            ("6.喇叭張口", "喇叭張口"),
            ("7.站上週布林", "站上週布林上軌"),
        ]

        matrix_rows = []
        for _, row in selected.iterrows():
            r = {"代碼": row["代碼"]}
            cond_vals = [
                row["帶寬收縮"] == "✅",
                row["10>20MA天數"] >= 10,
                row["20MA上彎"] == "✅",
                row["站上日布林上軌"] == "✅",
                row["量能放大"] == "✅",
                row["喇叭張口"] == "✅",
                row["站上週布林上軌"] == "✅",
            ]
            for (label, _), ok in zip(cond_labels, cond_vals):
                r[label] = "✅" if ok else "❌"
            r["達成"] = f"{sum(cond_vals)}/7"
            matrix_rows.append(r)

        matrix_df = pd.DataFrame(matrix_rows)
        print(matrix_df.to_string(index=False))

        # 逐檔缺項說明
        print("\n  【各強勢股缺少的條件】")
        for _, row in selected.iterrows():
            missing = []
            if row["帶寬收縮"] != "✅": missing.append("①帶寬收縮")
            if row["10>20MA天數"] < 10: missing.append(f"②10>20MA僅{row['10>20MA天數']}天")
            if row["20MA上彎"] != "✅": missing.append("③20MA上彎")
            if row["站上日布林上軌"] != "✅": missing.append("④站上日布林上軌")
            if row["量能放大"] != "✅": missing.append(f"⑤量能放大(量比{row['量比(倍)']}x)")
            if row["喇叭張口"] != "✅": missing.append("⑥喇叭張口")
            if row["站上週布林上軌"] != "✅": missing.append("⑦站上週布林上軌")
            missing_str = "、".join(missing) if missing else "全部符合！"
            print(f"  {row['代碼']}  缺 {7 - row['符合條件數']} 項：{missing_str}")

    full_match = df[df["全部符合"] == "★"]
    if not full_match.empty:
        print("\n" + "=" * 80)
        print("  ★★★【全條件符合】日週共振開布林強勢股 ★★★")
        print("=" * 80)
        print(full_match.to_string(index=False))
    else:
        print("\n  目前沒有全部 7 個條件都符合的個股。")

    print("\n" + "=" * 80)
    print("  篩選條件說明：")
    print("  1. 帶寬收縮：布林帶寬處於近 60 日最低 20%")
    print("  2. 10>20MA天數：10MA 在 20MA 之上的連續天數 ≥ 10")
    print("  3. 20MA上彎：20MA 近 5 日斜率為正")
    print("  4. 站上日布林上軌：收盤價 > 日布林上軌")
    print("  5. 量能放大：成交量 ≥ 5日均量 × 1.5")
    print("  6. 喇叭張口：上軌上升 + 下軌下降")
    print("  7. 站上週布林上軌：週收盤價 > 週布林上軌")
    if intraday:
        print("  ─────────────────────────────────────")
        print("  ⏰ 盤中模式注意事項：")
        print("     • 成交量已按交易時間佔比推估全日量")
        print("     • 收盤價為盤中即時價，非最終收盤價")
        print("     • 結果為預估，收盤後可能改變")
    print("=" * 80)

    # 儲存 CSV
    output_file = f"bollinger_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\n  結果已儲存至：{output_file}")

    return df


if __name__ == "__main__":
    run_screener()
