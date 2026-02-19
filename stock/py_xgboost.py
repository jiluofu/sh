import numpy as np
import pandas as pd
import os
import akshare as ak
import xgboost as xgb
import time
from datetime import datetime

import utils.utils as st

# 记录程序开始时间
start_time = time.time()

# ======================== 配置 ========================
START_DATE = "20180101"
END_DATE = "20250319"
END_DATE = st.get_end_date()  
N_DAYS = st.get_prediction_days()
LOOKBACK_DAYS = 90  
use_akshare = False  
use_gold_list = True  # **🔹 新增：是否从 gold.txt 读取股票代码**
data_dir = "data" 

# ======================== 1. 获取 A 股交易日历 ========================
china_trading_days = ak.tool_trade_date_hist_sina()
china_trading_days["trade_date"] = pd.to_datetime(china_trading_days["trade_date"].astype(str)).dt.strftime("%Y%m%d") 

# 获取未来 N 个交易日的日期
future_dates = china_trading_days[china_trading_days["trade_date"] > END_DATE]["trade_date"].tolist()
future_dates = future_dates[:N_DAYS]  # 确保长度一致

print(f"\n📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1]}")  # 只显示预测的最后一天

# ======================== 选择股票代码 ========================
STOCK_CODES = st.get_gold_stocks() if use_gold_list else st.get_main_board_stocks()
print(f"\n📊 选择 {len(STOCK_CODES)} 只股票进行分析")

# ======================== 读取股票数据 ========================
def get_stock_data(stock_code):
    """获取股票数据"""
    print(f"\n📥 获取 {stock_code} 的数据...")
    if use_akshare:
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

    df = df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume", "换手率": "turnover"})[["date", "close", "volume", "turnover"]]
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 计算 MACD 状态 ========================
def detect_accumulation_phase(stock_code, df):
    """ 判断主力是否建仓完成，准备拉升 """
    print(f"\n🔍 计算 {stock_code} 的 MACD...")
    if df is None or len(df) < 120:
        return "数据不足"

    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    last_macd = df["macd"].iloc[-2]
    last_signal = df["signal"].iloc[-2]
    current_macd = df["macd"].iloc[-1]
    current_signal = df["signal"].iloc[-1]
    
    macd_crossover = last_macd < last_signal and current_macd > current_signal

    if macd_crossover and current_macd > 0:
        return "完成建仓，准备拉升 🚀"
    elif macd_crossover:
        return "进入拉升初期 📈"
    else:
        return "无明显建仓信号"

# ======================== 预测股价 ========================
def forecast(stock_code, df, n_days, lookback_days):
    """ 使用 XGBoost 训练模型并预测未来 n 天股价 """
    print(f"\n🚀 训练 XGBoost 预测 {stock_code} 的未来 {n_days} 天价格...")
    X, y = [], []
    for i in range(len(df) - lookback_days):
        X.append(df["close"].values[i : i + lookback_days])
        y.append(df["close"].values[i + lookback_days])

    if len(X) < n_days:
        print("❌ 训练数据不足，跳过")
        return None

    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, objective="reg:squarederror")
    try:
        model.fit(X[:-n_days], y[:-n_days])
    except ValueError as e:
        print(f"⚠️ 训练失败: {e}，跳过 {stock_code}")
        return None

    future_prices = []
    last_window = df["close"].values[-lookback_days:].tolist()

    for _ in range(n_days):
        next_price = model.predict([last_window])[0]
        future_prices.append(round(next_price, 3))
        last_window.pop(0)
        last_window.append(next_price)

    last_price = df.iloc[-1]["close"]
    last_predicted_price = future_prices[-1]
    price_change_percent = round(((last_predicted_price - last_price) / last_price) * 100, 2)

    print(f"📊 {stock_code} 预测涨幅: {price_change_percent}%")

    return pd.DataFrame({
        "股票代码": [stock_code],
        "截止日价格": [last_price],
        "预测最后一天价格": [last_predicted_price],
        "预测涨幅 (%)": [price_change_percent]
    })

# ======================== 运行预测 ========================
all_results = []

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    accumulation_status = detect_accumulation_phase(stock_code, df)
    result_df = forecast(stock_code, df, N_DAYS, LOOKBACK_DAYS)
    if result_df is not None:
        result_df["主力状态"] = accumulation_status
        all_results.append(result_df)

# ======================== 保存预测结果 ========================
if all_results:
    final_result_df = pd.concat(all_results, ignore_index=True)
    final_result_df.to_csv("xgboost_forecast.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 预测完成，结果已保存！")
else:
    print("\n⚠️ 没有可用的预测结果，请检查数据源。")
print(f"\n📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1]}")  # 只显示预测的最后一天

st.print_elapsed_time(start_time)