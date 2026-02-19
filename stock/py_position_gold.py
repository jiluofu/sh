import numpy as np
import pandas as pd
import os
import akshare as ak
from datetime import datetime
import time  # 计时模块

import utils.utils as st



# 记录程序开始时间
start_time = time.time()

# ======================== 配置 ========================
START_DATE = "20180101"
END_DATE = "20250319"
use_akshare = False  # True: 使用 akshare 下载数据, False: 读取本地CSV
data_dir = "data"

# **筛选概念板块：优先筛选这些板块的股票**
# selected_concepts = ["人形机器人", "人工智能", "机器人概念", "智能制造"]
selected_concepts = []

# print(f"📅 数据截止日期: {END_DATE}")

# ======================== 获取符合概念板块的股票 ========================
def get_selected_stocks():
    """获取指定概念板块的股票列表"""
    all_stocks = set()
    for concept in selected_concepts:
        try:
            concept_df = ak.stock_board_concept_cons_em(symbol=concept)
            all_stocks.update(concept_df["代码"].tolist())  # 添加股票代码
        except Exception as e:
            print(f"⚠️ 获取概念 {concept} 失败: {e}")
    return list(all_stocks)

# **如果指定概念板块为空，则获取所有主板股票**
STOCK_CODES = get_selected_stocks()

if not STOCK_CODES:  
    print("⚠️ 没有符合筛选的概念股票，切换到获取主板股票...")
    STOCK_CODES = st.get_main_board_stocks()

print(f"✅ 选定 {len(STOCK_CODES)} 只股票进行分析")

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

# ======================== 计算筹码分布 ========================
def calculate_chip_distribution(df):
    """计算筹码集中度"""
    if df is None or len(df) < 60:
        return "数据不足"

    recent_prices = df["close"].iloc[-60:]  
    price_bins = np.linspace(recent_prices.min(), recent_prices.max(), num=20)  
    chip_distribution, _ = np.histogram(recent_prices, bins=price_bins, density=True)  

    main_chip_zone = chip_distribution.max()  

    if main_chip_zone > 0.5:
        return "筹码高度集中 🎯"
    elif main_chip_zone > 0.3:
        return "筹码震荡区 🔄"
    else:
        return "筹码分散 ⚠️"

# ======================== 检测 MACD 上方金叉（月线） ========================
def detect_macd(stock_code, df):
    """ 检测月线MACD上方金叉 """
    if df is None or len(df) < 180:
        return "数据不足", "数据不足"

    df_monthly = df.resample("ME").agg({"close": "last", "volume": "sum"})
    df_monthly["ema12"] = df_monthly["close"].ewm(span=12, adjust=False).mean()
    df_monthly["ema26"] = df_monthly["close"].ewm(span=26, adjust=False).mean()
    df_monthly["macd"] = df_monthly["ema12"] - df_monthly["ema26"]
    df_monthly["signal"] = df_monthly["macd"].ewm(span=9, adjust=False).mean()

    last_macd = df_monthly["macd"].iloc[-2]
    last_signal = df_monthly["signal"].iloc[-2]
    current_macd = df_monthly["macd"].iloc[-1]
    current_signal = df_monthly["signal"].iloc[-1]
    macd_crossover = last_macd < last_signal and current_macd > current_signal and current_macd > 0

    chip_status = calculate_chip_distribution(df)

    if macd_crossover:
        macd_status = "月线MACD上方金叉 ✅"
    else:
        macd_status = "无明显信号"

    return macd_status, chip_status

# ======================== 运行检测 ========================
all_results = []
golden_stocks = []  

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    macd_status, chip_status = detect_macd(stock_code, df)
    print(f"{stock_code} - {macd_status} | 筹码状态: {chip_status}")

    result_df = pd.DataFrame({
        "股票代码": [stock_code],
        "MACD 检测结果": [macd_status],
        "筹码状态": [chip_status]
    })
    all_results.append(result_df)

    if macd_status == "月线MACD上方金叉 ✅":
        golden_stocks.append(stock_code)

# ======================== 生成 CSV 文件 ========================
if all_results:
    final_result_df = pd.concat(all_results, ignore_index=True)

    status_order = {
        "月线MACD上方金叉 ✅": 1,
        "无明显信号": 2,
        "数据不足": 3
    }
    final_result_df["排序"] = final_result_df["MACD 检测结果"].map(status_order)
    final_result_df = final_result_df.sort_values(by=["排序", "股票代码"], ascending=[True, True])
    final_result_df.drop(columns=["排序"], inplace=True)

    final_result_df.to_csv("macd_ma20_chip_status.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 结果已保存！")

# ======================== 输出符合条件的股票到 gold.txt ========================
if golden_stocks:
    with open("gold.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(golden_stocks))
    print(f"\n✅ 符合 '月线MACD上方金叉 ✅' 的股票已保存到 gold.txt！")

st.print_elapsed_time(start_time)