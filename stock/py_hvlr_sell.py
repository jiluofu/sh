import os
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta

# ======================== 配置项 ========================
data_dir = 'data'
FILTER_AFTER_DATE = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # 只筛选该日期（含）之后的数据
FILTER_AFTER_DATE = '2025-03-17'
ENABLE_MA_ALIGNMENT = True  # 是否启用均线多头排列筛选
USE_FIXED_SELL_DAY = True   # ✅ 是否使用固定持仓周期卖出
HOLD_DAYS = 10              # 固定持仓的交易日数

# ======================== 涨停计算 ========================
def get_limit_up_price(prev_close, code):
    if code.startswith(('30', '68', '300')):
        return round(prev_close * 1.2, 2)
    else:
        return round(prev_close * 1.1, 2)

# ======================== 买入点判断函数 ========================
def match_conditions(df, code):
    hit_dates = []

    if ENABLE_MA_ALIGNMENT:
        df["ma5"] = df["收盘"].rolling(window=5).mean()
        df["ma10"] = df["收盘"].rolling(window=10).mean()
        df["ma20"] = df["收盘"].rolling(window=20).mean()
        df["ma30"] = df["收盘"].rolling(window=30).mean()

    for i in range(1, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]

        if today["日期"] < pd.to_datetime(FILTER_AFTER_DATE):
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
            hit_dates.append(str(today['日期']))

    return hit_dates

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
    stock_codes = stock_list["code"].tolist()

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

        hit_dates = match_conditions(df, code)
        if hit_dates:
            for d in hit_dates:
                buy_row = df[df['日期'] == pd.to_datetime(d)]
                if buy_row.empty:
                    continue
                buy_price = buy_row.iloc[0]['收盘']

                sell_date, sell_price = find_sell_date(df, d)

                if sell_date and sell_price:
                    gain_pct = round((sell_price - buy_price) / buy_price * 100, 2)
                    gain_pct_str = f"{gain_pct:.2f}%"
                else:
                    gain_pct_str = "—"
                    sell_price = None

                results.append([code, d, sell_date, buy_price, sell_price, gain_pct_str])
                print(f"✅ 命中: {code} - {d}，建议卖出: {sell_date if sell_date else '未触发'}，涨幅: {gain_pct_str}")

    if results:
        result_df = pd.DataFrame(results, columns=["股票代码", "命中日期", "建议卖出日期", "买入价", "卖出价", "涨幅 (%)"])
        result_df.to_csv("matched_buy_signals.csv", index=False, encoding="utf-8-sig")
        print(f"\n📄 筛选完成，共 {len(results)} 条命中，已保存 matched_buy_signals.csv")
    else:
        print("❌ 没有命中任何记录")

if __name__ == "__main__":
    main()