import numpy as np
import pandas as pd
import os
import akshare as ak
from datetime import datetime

# 配置开始和结束日期
START_DATE = "20240101"
END_DATE = "20250226"
TARGET_DATE = "20250304"

# 获取 A 股交易日历
china_trading_days = ak.tool_trade_date_hist_sina()
china_trading_days = pd.to_datetime(china_trading_days["trade_date"].astype(str))

# 将 TARGET_DATE 转换为 datetime 格式
target_date_dt = pd.to_datetime(TARGET_DATE)

# 确保 TARGET_DATE 是交易日，如果不是，则寻找最近的未来交易日
if target_date_dt not in china_trading_days:
    next_trading_date = china_trading_days[china_trading_days > target_date_dt].min()
    TARGET_DATE = next_trading_date.strftime("%Y%m%d")


print(f"调整后的目标交易日: {TARGET_DATE}")

data_dir = "data"
use_akshare = False  # True 使用在线数据, False 使用本地 CSV

# **计算从 END_DATE 到 TARGET_DATE 之间的交易日数**
end_date_dt = datetime.strptime(END_DATE, "%Y%m%d")
target_date_dt = datetime.strptime(TARGET_DATE, "%Y%m%d")

# 生成交易日范围
valid_trading_days = china_trading_days[(china_trading_days > end_date_dt) & (china_trading_days <= target_date_dt)]
NUM_DAYS = len(valid_trading_days)

if NUM_DAYS <= 0:
    raise ValueError(f"❌ TARGET_DATE {TARGET_DATE} 不能早于或等于 END_DATE {END_DATE}，请检查输入数据！")

if NUM_DAYS <= 0:
    print("❌ TARGET_DATE 不能早于或等于 END_DATE")
    exit()

print(f"📅 数据截止日期: {END_DATE}")
print(f"📅 计算得到的 NUM_DAYS: {NUM_DAYS}")
print(f"📅 预测目标日期: {TARGET_DATE}")

# **获取 A 股主板深市和沪市所有股票代码（去掉创业板）**
def get_main_board_stocks():
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]["code"].tolist()
    return main_board_stocks

# **处理单个股票数据**
def process_stock_data(stock_code, df, num_simulations=10000, num_days=NUM_DAYS):
    if df.empty:
        print(f"❌ 未能获取 {stock_code} 的数据")
        return None
    
    df = df.copy()
    df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    else:
        print(f"❌ 数据 {stock_code} 中没有找到 '日期' 或 'date' 列，请检查数据格式！")
        return None
    
    if "close" in df.columns:
        df = df[["close"]]
    else:
        print(f"❌ 数据 {stock_code} 中没有找到 '收盘' 或 'close' 列，请检查数据格式！")
        return None

    df["收益率"] = df["close"].pct_change()
    df.dropna(inplace=True)

    mu = df["收益率"].mean()
    sigma = df["收益率"].std()

    print(END_DATE)
    S0 = df.loc[END_DATE, "close"] if END_DATE in df.index else None  # 使用 END_DATE 当天的收盘价作为起始价
    # END_DATE_DT = pd.to_datetime(END_DATE)  # 转换成 datetime 类型
    # S0 = df.loc[END_DATE_DT, "close"] if END_DATE_DT in df.index else None
    print(S0)
    print(df.iloc[-1, 0])
    if S0 == None:
        return None

    np.random.seed(42)
    Z = np.random.standard_normal((num_simulations, num_days))
    price_paths = np.zeros((num_simulations, num_days))
    price_paths[:, 0] = S0

    for t in range(1, num_days):
        price_paths[:, t] = price_paths[:, t - 1] * np.exp((mu - 0.5 * sigma ** 2) * (1 / 252) + sigma * np.sqrt(1 / 252) * Z[:, t])

    future_prices = price_paths[:, -1]
    price_mean = round(np.mean(future_prices), 3)

    if END_DATE in df.index:
        end_date_price = df.loc[END_DATE, "close"]
    else:
        return None

    increase_percent = round(((price_mean - end_date_price) / end_date_price) * 100, 2) if end_date_price else None

    # **恢复 print 语句**
    print(f"{stock_code} 未来 {num_days} 个交易日股价预测：")
    print(f" - 预测均值: {price_mean}")
    print(f" - END_DATE ({END_DATE}) 收盘价: {end_date_price}")
    print(f" - 预测比 END_DATE 变化百分比: {increase_percent}%")

    return [stock_code, price_mean, end_date_price, increase_percent]

# **分析股票状态**
def analyze_stock_phase(stock_code, df, predicted_price, increase_percent):
    if increase_percent <= 0:
        return None

    df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume", "换手率": "turnover"}, inplace=True)

    df["ma60"] = df["close"].rolling(window=60).mean()
    df["vol_ma20"] = df["volume"].rolling(window=20).mean()
    df["turnover_ma20"] = df["turnover"].rolling(window=20).mean()

    last_60 = df.iloc[-60:]
    low_volatility = last_60["close"].std() / last_60["close"].mean() < 0.05
    moderate_volume = (last_60["volume"] > last_60["vol_ma20"] * 0.8).sum() > 30
    stable_turnover = (last_60["turnover"] < last_60["turnover_ma20"] * 1.2).sum() > 30

    completed_accumulation = low_volatility and moderate_volume and stable_turnover

    last_5 = df.iloc[-5:]
    breakout = (last_5["close"] > last_5["ma60"]).sum() > 3
    high_volume = (last_5["volume"] > last_5["vol_ma20"] * 1.5).sum() > 2
    strong_turnover = (last_5["turnover"] > last_5["turnover_ma20"] * 1.5).sum() > 3

    entering_rally = breakout and high_volume and strong_turnover

    if completed_accumulation and entering_rally:
        return [stock_code, predicted_price, increase_percent, "完成建仓，进入拉升"]
    elif completed_accumulation:
        return [stock_code, predicted_price, increase_percent, "完成建仓"]
    elif entering_rally:
        return [stock_code, predicted_price, increase_percent, "进入拉升"]
    else:
        return None

# **运行预测**
# stock_codes = get_main_board_stocks()
stock_codes = ["002979"]
results, results_build = [], []

for stock_code in stock_codes:
    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        continue

    df = pd.read_csv(file_path)
    result = process_stock_data(stock_code, df)
    if result:
        results.append(result)
        result_build = analyze_stock_phase(stock_code, df, result[1], result[3])
        if result_build:
            results_build.append(result_build)

# **保存预测结果**
results_df = pd.DataFrame(results, columns=["股票代码", "预测价格", "END_DATE 收盘价", "预测比 END_DATE 变化%"])
results_df.sort_values(by="预测比 END_DATE 变化%", ascending=False, inplace=True)
results_df.to_csv("predicted_prices.csv", index=False, encoding="utf-8-sig")

# **筛选涨幅 > 1% 的股票**
filtered_stocks = results_df[results_df["预测比 END_DATE 变化%"] > 1]
with open("filtered_stocks.txt", "w", encoding="utf-8") as f:
    f.write(",".join([f"'{stock}'" for stock in filtered_stocks["股票代码"].tolist()]))

# **保存符合条件的股票**
results_build_df = pd.DataFrame(results_build, columns=["股票代码", "预测价格", "预测比 END_DATE 变化%", "状态"])
status_order = {"完成建仓，进入拉升": 1, "进入拉升": 2}
results_build_df = results_build_df[results_build_df["状态"].isin(status_order.keys())]
results_build_df["排序顺序"] = results_build_df["状态"].map(status_order)
results_build_df.sort_values(by=["排序顺序", "股票代码"], ascending=[True, True], inplace=True)
results_build_df.drop(columns=["排序顺序"], inplace=True)
results_build_df.to_csv("rally_stocks.csv", index=False, encoding="utf-8-sig")

print("✅ 预测完成，结果已保存！")

print(f"📅 数据截止日期: {END_DATE}")
print(f"📅 计算得到的 NUM_DAYS: {NUM_DAYS}")
print(f"📅 预测目标日期: {TARGET_DATE}")