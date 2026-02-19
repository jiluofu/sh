import numpy as np
import pandas as pd
import os
import akshare as ak
from datetime import datetime
import time  # 计时模块

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
START_DATE = "20180101"
END_DATE = "20250228"
use_akshare = False  # True: 使用 akshare 下载数据, False: 读取本地CSV
data_dir = "data"

print(f"📅 数据截止日期: {END_DATE}")

# **获取 A 股主板股票列表（不包含创业板）**
def get_main_board_stocks():
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]["code"].tolist()
    return main_board_stocks

# ======================== 读取股票数据 ========================
def get_stock_data(stock_code):
    """获取股票数据"""
    if use_akshare:
        print(f"📥 正在从 akshare 获取 {stock_code} 的数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=START_DATE, end_date=END_DATE, adjust="qfq")
    else:
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ 本地数据 {file_path} 不存在，跳过 {stock_code}。")
            return None
        df = pd.read_csv(file_path)

    if df.empty:
        print(f"❌ 无法获取 {stock_code} 的数据，跳过。")
        return None

    df = df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume", "换手率": "turnover"})[["date", "close", "volume", "turnover"]]
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 3. 检测主力建仓状态 ========================
def detect_accumulation_phase(stock_code, df):
    """ 判断主力是否建仓完成，准备拉升 """
    if df is None or len(df) < 120:
        return "数据不足"

    df["ma60"] = df["close"].rolling(window=60).mean()
    df["ma120"] = df["close"].rolling(window=120).mean()
    df["vol_ma20"] = df["volume"].rolling(window=20).mean()

    last_60 = df.iloc[-60:]
    volatility = last_60["close"].std() / last_60["close"].mean()
    volume_increase = (last_60["volume"] > last_60["vol_ma20"] * 1.5).sum() > 5
    turnover_stable = (last_60["turnover"] < 10).sum() > 50
    recent_turnover_spike = (last_60["turnover"].iloc[-5:] > 10).sum() >= 3
    golden_cross = (df["ma60"].iloc[-10:] > df["ma120"].iloc[-10:]).all()

    # 计算 MACD
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # 仅判断最近一次金叉
    last_macd = df["macd"].iloc[-2]
    last_signal = df["signal"].iloc[-2]
    current_macd = df["macd"].iloc[-1]
    current_signal = df["signal"].iloc[-1]

    macd_bullish = last_macd < last_signal and current_macd > current_signal

    # 判定主力建仓状态
    if volatility < 0.05 and turnover_stable and volume_increase and recent_turnover_spike and golden_cross and macd_bullish:
        return "完成建仓，准备拉升 🚀"
    elif volatility < 0.05 and turnover_stable:
        return "主力建仓完成 ✅"
    elif recent_turnover_spike and golden_cross and macd_bullish:
        return "进入拉升初期 📈"
    else:
        return "无明显建仓信号"

# ======================== 4. 运行建仓检测 ========================
all_results = []

STOCK_CODES = get_main_board_stocks()

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    accumulation_status = detect_accumulation_phase(stock_code, df)
    print(f"{stock_code} - {accumulation_status}")

    result_df = pd.DataFrame({
        "股票代码": [stock_code],
        "主力状态": [accumulation_status]
    })
    all_results.append(result_df)

# ======================== 5. 生成 CSV 文件 ========================
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

    # 排序
    final_result_df["状态排序"] = final_result_df["主力状态"].map(status_order)
    final_result_df = final_result_df.sort_values(by=["状态排序", "股票代码"], ascending=[True, True])
    final_result_df.drop(columns=["状态排序"], inplace=True)

    # 保存文件
    final_result_df.to_csv("accumulation_status.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 结果已保存到 accumulation_status.csv")

else:
    print("\n⚠️ 没有可用的结果，请检查数据源。")

print_elapsed_time(start_time)