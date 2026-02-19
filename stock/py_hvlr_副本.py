import os
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta

import utils.utils as st

# ======================== 配置项 ========================
data_dir = 'data'

FILTER_AFTER_DATE = '2025-01-01'
FILTER_AFTER_DATE = st.get_last_monday()
FILTER_BEFORE_DATE = '2025-05-31'
ENABLE_MA_ALIGNMENT = True
USE_FIXED_SELL_DAY = False
HOLD_DAYS = 10
ENABLE_NEXT_DAY_UP_CHECK = False

# ======================== 涨停计算 ========================
def get_limit_up_price(prev_close, code):
    if code.startswith(('30', '68', '300')):
        return round(prev_close * 1.2, 2)
    else:
        return round(prev_close * 1.1, 2)

# ======================== 筹码集中度估算 ========================
def estimate_chip_concentration(df, date, window=20):
    ref_date = pd.to_datetime(date)
    sub_df = df[df['日期'] <= ref_date].tail(window)
    if len(sub_df) < window:
        return "数据不足", None
    std = sub_df['收盘'].std()
    mean = sub_df['收盘'].mean()
    if mean == 0:
        return "异常", None
    concentration = round(100 * (1 - std / mean), 2)
    if concentration > 85:
        status = "高度集中"
    elif concentration > 75:
        status = "中度集中"
    else:
        status = "分散"
    return status, concentration

# ======================== 买入点判断函数 ========================
def match_conditions(df, code):
    hit_info = []

    if df is None or len(df) < 2:
        return hit_info

    if ENABLE_MA_ALIGNMENT:
        df["ma5"] = df["收盘"].rolling(window=5).mean()
        df["ma10"] = df["收盘"].rolling(window=10).mean()
        df["ma20"] = df["收盘"].rolling(window=20).mean()
        df["ma30"] = df["收盘"].rolling(window=30).mean()

    for i in range(1, len(df) - 1):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]
        tomorrow = df.iloc[i + 1]

        if not (pd.to_datetime(FILTER_AFTER_DATE) <= today["日期"] <= pd.to_datetime(FILTER_BEFORE_DATE)):
            continue
        if yesterday["成交量"] == 0:
            continue

        open_price = today['开盘']
        high_price = today['最高']
        close_price = today['收盘']
        volume_today = today['成交量']
        volume_yesterday = yesterday['成交量']
        close_yesterday = yesterday['收盘']

        is_bullish = close_price > open_price
        vol_ratio = volume_today / volume_yesterday
        upper_shadow = high_price > max(open_price, close_price)
        limit_up_price = get_limit_up_price(close_yesterday, code)
        is_limit_up = abs(close_price - limit_up_price) < 0.01
        close_higher = close_price > close_yesterday

        if ENABLE_MA_ALIGNMENT:
            if pd.isna(today['ma30']):
                continue
            if not (today['ma5'] > today['ma10'] > today['ma20'] > today['ma30']):
                continue

        if is_bullish and vol_ratio > 3 and upper_shadow and not is_limit_up and close_higher:
            if ENABLE_NEXT_DAY_UP_CHECK and tomorrow['收盘'] <= today['收盘']:
                continue
            next_day_gain = round((tomorrow['收盘'] - today['收盘']) / today['收盘'] * 100, 2)
            hit_info.append((today['日期'].strftime('%Y-%m-%d'), next_day_gain))

    return hit_info

# ======================== 卖出点判断函数 ========================
def find_sell_date(df, hit_date):
    hit_index = df[df['日期'] == pd.to_datetime(hit_date)].index
    if hit_index.empty:
        return None, None
    start = hit_index[0] + 1

    if USE_FIXED_SELL_DAY:
        sell_index = start + HOLD_DAYS - 1
        if sell_index < len(df):
            sell_row = df.iloc[sell_index]
            return str(sell_row['日期'].date()), sell_row['收盘']
        else:
            return None, None
    else:
        for i in range(start + 1, len(df)):
            today = df.iloc[i]
            yesterday = df.iloc[i - 1]
            if today['收盘'] < today['开盘'] and today['成交量'] > yesterday['成交量']:
                return str(today['日期'].date()), today['收盘']
        return None, None

# ======================== 主程序入口 ========================
def main():
    results = []

    stock_list = ak.stock_info_a_code_name()
    stock_codes = stock_list[~stock_list["code"].str.startswith("688")]["code"].tolist()

    for code in stock_codes:
        file_path = os.path.join(data_dir, f"{code}.csv")
        if not os.path.exists(file_path):
            continue

        try:
            df = pd.read_csv(file_path)
            df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']].copy()
            df.dropna(inplace=True)
            df['日期'] = pd.to_datetime(df['日期'])
            df.reset_index(drop=True, inplace=True)
        except Exception as e:
            print(f"⚠️ 读取 {code} 失败: {e}")
            continue

        hit_info_list = match_conditions(df, code)
        if hit_info_list:
            for d, next_day_gain in hit_info_list:
                buy_row = df[df['日期'] == pd.to_datetime(d)]
                if buy_row.empty:
                    continue

                buy_index = buy_row.index[0]
                if buy_index + 2 < len(df):
                    buy_price = df.iloc[buy_index + 2]['收盘']
                    sell_date, sell_price = find_sell_date(df, d)
                    if sell_date and sell_price:
                        gain_pct = round((sell_price - buy_price) / buy_price * 100, 2)
                        gain_pct_str = f"{gain_pct:.2f}%"
                    else:
                        gain_pct_str = "—"
                        sell_price = None
                else:
                    buy_price = None
                    sell_date = None
                    sell_price = None
                    gain_pct_str = "—"

                chip_status, chip_concentration = estimate_chip_concentration(df, d)

                results.append([
                    code, d, f"{next_day_gain:.2f}%", sell_date, buy_price,
                    sell_price, gain_pct_str, chip_status, chip_concentration
                ])

                print(
                    f"✅ 命中: {code} - {d}｜次日涨幅: {next_day_gain:.2f}%｜"
                    f"卖出: {sell_date if sell_date else '未触发'}｜涨幅: {gain_pct_str}｜"
                    f"筹码: {chip_status} ({chip_concentration if chip_concentration is not None else '—'}%)"
                )

    output_path = "matched_buy_signals.csv"
    if results:
        result_df = pd.DataFrame(results, columns=[
            "股票代码", "命中日期", "次日涨幅", "建议卖出日期", "买入价", "卖出价", "涨幅 (%)", "筹码状态", "集中度估算"
        ])
        result_df["次日涨幅值"] = result_df["次日涨幅"].str.replace('%', '').astype(float)

        result_df = result_df.sort_values(
            by=["命中日期", "股票代码", "次日涨幅值"],
            ascending=[False, True, False]
        )

        result_df.drop(columns=["次日涨幅值"], inplace=True)

        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

        valid_results = result_df[result_df['涨幅 (%)'] != '—'].copy()
        if not valid_results.empty:
            valid_results['涨幅数值'] = valid_results['涨幅 (%)'].str.replace('%', '').astype(float)
            avg_gain = round(valid_results['涨幅数值'].mean(), 2)
            with open(output_path, "a", encoding="utf-8-sig") as f:
                f.write(f"\n平均涨幅：{avg_gain:.2f}%")
            print(f"\n📄 筛选完成，共 {len(results)} 条命中，平均涨幅：{avg_gain:.2f}%")
        else:
            print("⚠️ 无法计算平均涨幅")
    else:
        print("❌ 没有命中任何记录")

if __name__ == "__main__":
    main()