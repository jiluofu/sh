import numpy as np
import pandas as pd
import os
import akshare as ak
import time
from datetime import datetime

# ======================== 计时函数 ========================
def print_elapsed_time(start_time):
    """打印代码运行时间，并自动调整时间单位"""
    elapsed_time = time.time() - start_time
    if elapsed_time > 3600:
        print(f"\n⏱️ 总运行时间: {elapsed_time / 3600:.2f} 小时")
    elif elapsed_time > 60:
        print(f"\n⏱️ 总运行时间: {elapsed_time / 60:.2f} 分钟")
    else:
        print(f"\n⏱️ 总运行时间: {elapsed_time:.2f} 秒")

# 记录程序开始时间
start_time = time.time()

# ======================== 配置 ========================
STOCK_CODES = ["600519", "000001"]  # 预测多个股票
START_DATE = "20180101"  # 历史数据起始日期
END_DATE = "20250217"  # 历史数据截止日期（最后一个训练数据点）
N_DAYS = 5  # 预测未来 N 个交易日的价格
LOOKBACK_DAYS = 365  # 过去多少天的数据作为输入窗口
use_akshare = False  # True: 使用 akshare 下载数据, False: 读取 data 目录下的 CSV 文件
data_dir = "data"  # 本地数据目录

# ======================== 1. 获取 A 股交易日历 ========================
china_trading_days = ak.tool_trade_date_hist_sina()
china_trading_days["trade_date"] = pd.to_datetime(china_trading_days["trade_date"].astype(str)).dt.strftime("%Y%m%d")

# 获取未来 N 个交易日的日期
future_dates = china_trading_days[china_trading_days["trade_date"] > END_DATE]["trade_date"].tolist()
future_dates = future_dates[:N_DAYS]  # 确保长度一致

print(f"📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1]}")  # 只显示预测的最后一天

# **股票代码列表（主板股票，不包含创业板）**
def get_main_board_stocks():
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]["code"].tolist()
    return main_board_stocks

# ======================== 2. 读取股票数据 ========================
def get_stock_data(stock_code):
    if use_akshare:
        print(f"📥 正在从 akshare 获取 {stock_code} 的数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=START_DATE, end_date=END_DATE, adjust="qfq")
    else:
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ 本地数据 {file_path} 不存在，跳过 {stock_code}。")
            return None
        print(f"📂 读取本地数据 {file_path}")
        df = pd.read_csv(file_path)

    if df.empty:
        print(f"❌ 无法获取 {stock_code} 的数据，跳过。")
        return None

    df = df.rename(columns={"日期": "date", "收盘": "close"})[["date", "close"]]
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 3. 检测主力建仓状态 ========================
def detect_accumulation_phase(stock_code, df):
    """ 判断主力是否建仓完成，准备拉升 """
    if df is None or len(df) < 120:
        return "数据不足"

    df["ma60"] = df["close"].rolling(window=60).mean()
    df["vol_ma20"] = df["close"].rolling(window=20).mean()

    last_60 = df.iloc[-60:]
    volatility = last_60["close"].std() / last_60["close"].mean()
    volume_increase = (last_60["close"] > last_60["vol_ma20"] * 1.5).sum() > 5
    turnover_stable = (last_60["close"].std() / last_60["close"].mean()) < 0.05

    if volatility < 0.05 and turnover_stable and volume_increase:
        return "完成建仓，准备拉升 🚀"
    elif volatility < 0.05 and turnover_stable:
        return "主力建仓完成 ✅"
    elif volume_increase:
        return "进入拉升初期 📈"
    else:
        return "无明显建仓信号"

# ======================== 4. 预测函数（蒙特卡洛模拟） ========================
def forecast(stock_code, df, n_days, future_dates, accumulation_status):
    """ 使用蒙特卡洛模拟预测未来 n 天股价 """
    if len(df) < LOOKBACK_DAYS:
        return None

    # 计算对数收益率
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df.dropna(inplace=True)

    # 计算均值和标准差
    mu = df["log_return"].mean()
    sigma = df["log_return"].std()

    # 取最后一天收盘价
    last_price = df["close"].iloc[-1]

    # 进行模拟
    num_simulations = 1000
    simulated_paths = np.zeros((n_days, num_simulations))

    for i in range(num_simulations):
        prices = [last_price]
        for _ in range(n_days):
            shock = np.random.normal(loc=mu, scale=sigma)
            price = prices[-1] * np.exp(shock)
            prices.append(price)
        simulated_paths[:, i] = prices[1:]

    # 计算均值和置信区间
    future_prices = pd.DataFrame(simulated_paths).mean(axis=1)
    last_predicted_price = round(float(f"{future_prices.iloc[-1]:.3f}"), 3)
    last_predicted_date = future_dates[-1] if future_dates else None
    price_change_percent = round(((last_predicted_price - last_price) / last_price) * 100, 2)

    # 打印预测结果
    print(f"{stock_code} - 截止日价格: {last_price}, 预测最后一天价格: {last_predicted_price}, 预测涨幅: {price_change_percent}%")

    return pd.DataFrame({
        "股票代码": [stock_code],
        "截止日价格": [last_price],
        "预测最后一天价格": [last_predicted_price],
        "预测涨幅 (%)": [price_change_percent],
        "主力状态": [accumulation_status]
    })

# ======================== 5. 运行预测 ========================
all_results = []

STOCK_CODES = get_main_board_stocks()

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    accumulation_status = detect_accumulation_phase(stock_code, df)
    result_df = forecast(stock_code, df, N_DAYS, future_dates, accumulation_status)
    if result_df is not None:
        all_results.append(result_df)

# ======================== 6. 保存预测结果 ========================
if all_results:
    final_result_df = pd.concat(all_results, ignore_index=True)

    # 定义主力状态的排序优先级
    status_order = {
        "完成建仓，准备拉升 🚀": 1,
        "进入拉升初期 📈": 2,
        "主力建仓完成 ✅": 3,
        "无明显建仓信号": 4,
        "数据不足": 5
    }

    final_result_df["状态排序"] = final_result_df["主力状态"].map(status_order)
    final_result_df = final_result_df.sort_values(by=["状态排序", "预测涨幅 (%)"], ascending=[True, False])
    final_result_df.drop(columns=["状态排序"], inplace=True)

    final_result_df.to_csv("monte_carlo_forecast.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 预测完成，结果已保存（按主力状态 & 预测涨幅降序）")
else:
    print("\n⚠️ 没有可用的预测结果，请检查数据源。")

print_elapsed_time(start_time)