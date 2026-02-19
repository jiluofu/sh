import os
import numpy as np
import pandas as pd
import akshare as ak
from datetime import datetime

import utils.utils as st

# ======================== 配置 ========================
USE_LOCAL_DATA = True  # 是否优先读取本地数据
START_DATE = "20250319"
END_DATE = datetime.today().strftime("%Y%m%d")
DATA_DIR = "data"

STOCK_CODES = st.get_main_board_stocks()
print(f"✅ 选定 {len(STOCK_CODES)} 只主板股票进行分析")

# ======================== 批量获取最新市场数据（包含量比 & 总市值） ========================
def get_latest_market_data():
    """获取所有 A 股最新市场数据，包括总市值 & 量比"""
    try:
        df = ak.stock_zh_a_spot_em()[["代码", "量比", "总市值"]]
        df = df.rename(columns={"代码": "stock_code", "量比": "volume_ratio", "总市值": "total_market_cap"})
        df["total_market_cap"] = pd.to_numeric(df["total_market_cap"], errors='coerce') / 1e8  # 转换为亿单位
        return df.set_index("stock_code")
    except Exception as e:
        print(f"⚠️ 获取最新市场数据失败: {e}")
        return None

latest_market_data = get_latest_market_data()
if latest_market_data is None:
    raise Exception("❌ 无法获取最新市场数据，程序终止！")

# ======================== 读取股票数据 ========================
def get_stock_data(stock_code):
    """读取本地 CSV 或 AkShare 数据"""
    file_path = os.path.join(DATA_DIR, f"{stock_code}.csv")

    if USE_LOCAL_DATA and os.path.exists(file_path):
        # print(f"📂 读取本地数据: {file_path}")
        df = pd.read_csv(file_path)
    else:
        print(f"📥 从 AkShare 获取 {stock_code} 的数据...")
        try:
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=START_DATE, end_date=END_DATE, adjust="qfq")
        except Exception as e:
            print(f"⚠️ 获取 {stock_code} 失败: {e}")
            return None

    if df.empty:
        print(f"❌ {stock_code} 数据为空，跳过。")
        return None

    df = df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume", "换手率": "turnover", "涨跌幅": "change"})
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    # print(f"✅ {stock_code} 数据修正，列名: {df.columns.tolist()}")
    return df

# ======================== 计算 MACD 指标（仅日线） ========================
def calculate_macd(df):
    """
    计算 MACD 指标并判断日线 0 轴上方金叉
    :param df: 股票数据
    :return: 是否发生金叉, MACD 状态描述
    """
    if df is None or len(df) < 26:
        return False, "数据不足"

    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    if len(df) < 2:
        return False, "数据不足"

    last_macd, last_signal = df["macd"].iloc[-2], df["signal"].iloc[-2]
    current_macd, current_signal = df["macd"].iloc[-1], df["signal"].iloc[-1]

    # 判断 MACD 0 轴上方金叉
    macd_crossover = last_macd < last_signal and current_macd > current_signal and current_macd > 0

    return macd_crossover, "日线MACD金叉 ✅" if macd_crossover else "无明显信号"

# ======================== 选股逻辑 ========================
all_results = []
golden_stocks = []

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    latest_data = df.iloc[-1]  # 最新数据
    if latest_data["change"] < 3 or latest_data["change"] > 7:
        continue

    # **从 `latest_market_data` 获取量比 & 总市值**
    try:
        market_info = latest_market_data.loc[stock_code]
        volume_ratio = market_info["volume_ratio"]
        total_market_cap = market_info["total_market_cap"]  # 总市值 (单位: 亿)
    except KeyError:
        print(f"⚠️ {stock_code} 没有最新市场数据，跳过。")
        continue

    if volume_ratio < 1 or volume_ratio > 5:  # **量比 1 - 5**
        continue
    if latest_data["turnover"] < 3 or latest_data["turnover"] > 10:  # **换手率 3% - 10%**
        continue
    if total_market_cap >= 150:
        continue

    # **MACD 筛选**
    macd_crossover, macd_status = calculate_macd(df)

    # 必须 **日线 MACD 0 轴上方金叉**
    if not macd_crossover:
        continue

    all_results.append({
        "股票代码": stock_code,
        "涨幅": latest_data["change"],
        "市值(亿)": total_market_cap,
        "量比": volume_ratio,
        "自由换手率": latest_data["turnover"],
        "MACD（日线）": macd_status
    })

    golden_stocks.append(stock_code)

# ======================== 保存 CSV 结果 ========================
output_csv_path = "EOB_Buying_Method.csv"
final_result_df = pd.DataFrame(all_results)
if not final_result_df.empty:
    final_result_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 结果已保存到 {output_csv_path}")

# ======================== 生成 TXT 文件（每行存储股票代码，文件名 gold.txt） ========================
output_txt_path = "gold.txt"
if golden_stocks:
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(golden_stocks))  # **每行存储一个股票代码**
    print(f"\n✅ 符合 MACD 金叉条件的股票已保存到 {output_txt_path}！")

print("\n🎯 筛选完成！")