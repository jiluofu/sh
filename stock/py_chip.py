import numpy as np
import pandas as pd
import os
import akshare as ak
from datetime import datetime
import time

import utils.utils as st

# 记录程序开始时间
start_time = time.time()

# ======================== 配置 ========================
START_DATE = "20180101"
END_DATE = "20250319"
use_akshare = False  
data_dir = "data"

print(f"📅 数据截止日期: {END_DATE}")

# **读取股票数据**
def get_stock_data(stock_code):
    """获取股票数据"""
    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    if df.empty:
        return None
    df = df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume", "换手率": "turnover"})[["date", "close", "volume", "turnover"]]
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 识别低位筹码集中 & 突破信号 ========================
def detect_low_position_accumulation(stock_code, df):
    """ 识别筹码在低位集中，并出现突破 """
    if df is None or len(df) < 120:
        return None

    df["ma60"] = df["close"].rolling(window=60).mean()
    df["ma120"] = df["close"].rolling(window=120).mean()
    df["vol_ma20"] = df["volume"].rolling(window=20).mean()

    # 计算波动率（放宽到 7%）
    last_120 = df.iloc[-120:]
    volatility = last_120["close"].std() / last_120["close"].mean()

    # 计算低位筹码集中信号
    volume_low = (last_120["volume"].mean() < df["volume"].rolling(window=240).mean().iloc[-1] * 0.8)
    turnover_low = (last_120["turnover"].mean() < 7)

    # 计算突破信号（最近 60 天新高 + 成交量放大 1.3 倍）
    breakout = df["close"].iloc[-1] > last_120["close"].max()
    volume_surge = df["volume"].iloc[-3:].mean() > last_120["vol_ma20"].iloc[-1] * 1.3

    # 计算 MACD
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    recent_macd_crosses = ((df["macd"] > df["signal"]) & (df["macd"].shift(1) < df["signal"].shift(1))).iloc[-5:].sum() > 0

    # 逻辑判断（增加日志输出）
    if volume_low and turnover_low and volatility < 0.07 and breakout and volume_surge and recent_macd_crosses:
        print(f"✅ {stock_code} 满足低位筹码集中 & 突破买入信号 🚀")
        return "低位筹码集中，突破买入信号 🚀"
    elif volume_low and turnover_low and volatility < 0.07:
        print(f"✅ {stock_code} 满足低位筹码集中 ✅")
        return "低位筹码集中 ✅"
    elif breakout and volume_surge and recent_macd_crosses:
        print(f"✅ {stock_code} 进入突破初期 📈")
        return "突破初期 📈"
    else:
        print(f"❌ {stock_code} 未满足条件")
        return None

# ======================== 运行检测 ========================
all_results = []
STOCK_CODES = st.get_main_board_stocks()

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    accumulation_status = detect_low_position_accumulation(stock_code, df)
    
    # 只保存符合条件的股票
    if accumulation_status:
        result_df = pd.DataFrame({
            "股票代码": [stock_code],
            "状态": [accumulation_status]
        })
        all_results.append(result_df)

# ======================== 生成 CSV 文件 ========================
if all_results:
    final_result_df = pd.concat(all_results, ignore_index=True)

    # 定义状态排序
    status_order = {
        "低位筹码集中，突破买入信号 🚀": 1,
        "突破初期 📈": 2,
        "低位筹码集中 ✅": 3
    }

    # 排序
    final_result_df["状态排序"] = final_result_df["状态"].map(status_order)
    final_result_df = final_result_df.sort_values(by=["状态排序", "股票代码"], ascending=[True, True])
    final_result_df.drop(columns=["状态排序"], inplace=True)

    # 保存文件
    final_result_df.to_csv("low_position_breakout.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 结果已保存到 low_position_breakout.csv")

else:
    print("\n⚠️ 没有符合条件的股票，请调整筛选标准。")

st.print_elapsed_time(start_time)