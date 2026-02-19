import os
import numpy as np
import pandas as pd
import akshare as ak
from datetime import datetime
import time

# ======================== 配置 ========================
USE_LOCAL_DATA = True  # 是否优先读取本地数据
USE_REALTIME_DATA = False  # 是否使用 stock_zh_a_spot_em() 获取实时数据
START_DATE = "20240101"
END_DATE = datetime.today().strftime("%Y%m%d")
DATA_DIR = "data"

# ======================== 获取 A 股主板股票列表 ========================
def get_main_board_stocks():
    """获取 A 股主板股票列表"""
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[
        stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))
    ]["code"].tolist()
    return main_board_stocks

STOCK_CODES = get_main_board_stocks()
print(f"✅ 选定 {len(STOCK_CODES)} 只主板股票进行分析")

# ======================== 获取最新市场数据（批量获取） ========================
def get_latest_market_data():
    """获取所有 A 股最新市场数据，包括总市值 & 量比"""
    try:
        df = ak.stock_zh_a_spot_em()

        if df is None or df.empty:
            print("⚠️ `stock_zh_a_spot_em()` 获取的数据为空，可能是 AKShare 数据源问题！")
            return None

        # 重新匹配列名，防止字段变化导致 KeyError
        df = df.rename(columns={
            "代码": "stock_code",
            "名称": "name",
            "最新价": "latest_price",
            "涨跌幅": "change",
            "涨跌额": "price_change",
            "成交量": "volume",
            "成交额": "turnover_amount",
            "振幅": "amplitude",
            "最高": "high",
            "最低": "low",
            "今开": "open",
            "昨收": "previous_close",
            "量比": "volume_ratio",
            "换手率": "turnover",
            "市盈率(动态)": "pe_ratio",
            "市净率": "pb_ratio",
            "总市值": "total_market_cap",
            "流通市值": "circulating_market_cap",
            "涨速": "price_speed",
            "5分钟涨跌": "five_min_change",
            "60日涨跌幅": "sixty_day_change",
            "年初至今涨跌幅": "ytd_change"
        })

        # 处理总市值数据（转换单位：元 → 亿）
        df["total_market_cap"] = pd.to_numeric(df["total_market_cap"], errors='coerce') / 1e8
        df["circulating_market_cap"] = pd.to_numeric(df["circulating_market_cap"], errors='coerce') / 1e8

        return df.set_index("stock_code")

    except Exception as e:
        print(f"❌ 获取最新市场数据失败: {e}")
        return None

latest_market_data = get_latest_market_data()
if latest_market_data is None:
    print("⚠️ 无法获取最新市场数据，仅使用历史数据进行筛选。")

# ======================== 计算 MACD 指标（仅日线） ========================
def calculate_macd(df):
    """
    计算 MACD 指标并判断日线 0 轴上方金叉
    :param df: 股票数据
    :return: 是否发生金叉, MACD 状态描述
    """
    if df is None or len(df) < 26:
        return False, "数据不足"

    df["ema12"] = df["latest_price"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["latest_price"].ewm(span=26, adjust=False).mean()
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
    if latest_market_data is not None:
        try:
            market_info = latest_market_data.loc[stock_code]
            volume_ratio = market_info["volume_ratio"]
            total_market_cap = market_info["total_market_cap"]
            latest_price = market_info["latest_price"]
            change = market_info["change"]
            turnover = market_info["turnover"]
        except KeyError:
            print(f"⚠️ {stock_code} 无最新市场数据，跳过。")
            continue
    else:
        continue

    # 过滤不符合条件的股票
    if change < 3 or change > 7:
        continue
    if volume_ratio < 2 or volume_ratio > 5:
        continue
    if turnover < 5 or turnover > 10:
        continue
    if total_market_cap >= 150:
        continue
    print(1)
    # **MACD 筛选**
    df = pd.DataFrame({"latest_price": [latest_price]})
    macd_crossover, macd_status = calculate_macd(df)
    print(macd_crossover, macd_status)

    # 必须 **日线 MACD 0 轴上方金叉**
    if not macd_crossover:
        continue

    all_results.append({
        "股票代码": stock_code,
        "股票名称": market_info["name"],
        "最新价": latest_price,
        "涨幅(%)": change,
        "市值(亿)": total_market_cap,
        "流通市值(亿)": market_info["circulating_market_cap"],
        "量比": volume_ratio,
        "自由换手率(%)": turnover,
        "MACD（日线）": macd_status
    })

    golden_stocks.append(stock_code)

# ======================== 保存结果 ========================
final_result_df = pd.DataFrame(all_results)
if not final_result_df.empty:
    final_result_df.to_csv("EOB_Buying_Method.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 结果已保存到 EOB_Buying_Method.csv")

if golden_stocks:
    with open("EOB_Golden_Stocks.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(golden_stocks))
    print(f"\n✅ 符合 MACD 金叉条件的股票已保存到 EOB_Golden_Stocks.txt！")

print("\n🎯 筛选完成！")