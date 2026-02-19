import numpy as np
import pandas as pd
import os

# ✅ 配置
data_dir = "data"  # CSV 文件存放目录
LOOKBACK_DAYS = 60  # 识别周期

# **扫描 data 目录下所有 CSV 文件**
def scan_data_directory():
    if not os.path.exists(data_dir):
        print(f"❌ 目录 {data_dir} 不存在，请检查数据路径！")
        return []
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    stock_list = [f.split(".csv")[0] for f in csv_files]
    
    # ✅ 只保留沪深A股股票代码（沪市60xxxx，深市00xxxx和30xxxx）
    stock_list = [code for code in stock_list if code.startswith(("60", "00", "30"))]

    print(f"✅ 在 {data_dir}/ 目录中找到 {len(stock_list)} 只股票")
    return stock_list

# **从 data 目录读取 CSV**
def load_stock_data_from_csv(stock_code):
    file_path = os.path.join(data_dir, f"{stock_code}.csv")

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df["日期"] = pd.to_datetime(df["日期"])  # 确保日期格式正确
            df.set_index("日期", inplace=True)
            return df
        except Exception as e:
            print(f"❌ 读取 {file_path} 失败: {e}")
            return None
    else:
        print(f"⚠️ {file_path} 不存在，跳过该股票")
        return None

# **方法1：成交量放大 + 缩量调整**
def detect_volume_accumulation(df):
    df["vol_ma5"] = df["成交量"].rolling(5).mean()
    df["vol_ma20"] = df["成交量"].rolling(20).mean()
    df["volume_ratio"] = df["vol_ma5"] / df["vol_ma20"]
    return df["volume_ratio"].iloc[-1] > 1.5

# **方法2：价格振幅低**
def detect_low_volatility(df):
    df["振幅"] = (df["最高"] - df["最低"]) / df["收盘"]
    df["波动率_ma10"] = df["振幅"].rolling(10).mean()
    return df["波动率_ma10"].iloc[-1] < 0.02

# **方法3：主力资金流入**
def detect_fund_inflow(df):
    df["主力资金流"] = df["成交量"].rolling(5).sum()
    return df["主力资金流"].iloc[-1] > df["主力资金流"].rolling(20).mean().iloc[-1]

# **方法4：K 线形态**
def detect_kline_pattern(df):
    df["阴线放量"] = (df["收盘"] < df["收盘"].shift(1)) & (df["成交量"] > df["成交量"].rolling(5).mean())
    df["阳线缩量"] = (df["收盘"] > df["收盘"].shift(1)) & (df["成交量"] < df["成交量"].rolling(5).mean())
    return df["阴线放量"].sum() > 3 and df["阳线缩量"].sum() > 3

# **方法5：MACD 低位金叉**
def detect_macd_crossover(df):
    df["ema12"] = df["收盘"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["收盘"].ewm(span=26, adjust=False).mean()
    df["dif"] = df["ema12"] - df["ema26"]
    df["dea"] = df["dif"].ewm(span=9, adjust=False).mean()
    
    return (df["dif"].iloc[-1] > df["dea"].iloc[-1]) and (df["dif"].iloc[-2] < df["dea"].iloc[-2]) and (df["dif"].iloc[-1] < 0)

# **方法6：换手率稳定**
def detect_turnover_stability(df):
    return (df["换手率"].iloc[-1] > 0.03) & (df["换手率"].iloc[-1] < 0.07)

# **获取股票列表**
stock_list = scan_data_directory()
results = {method: set() for method in ["volume", "volatility", "fund", "kline", "macd", "turnover"]}

# **进行筛选**
for stock_code in stock_list:
    df = load_stock_data_from_csv(stock_code)
    if df is None or len(df) < LOOKBACK_DAYS:
        continue

    if detect_volume_accumulation(df):
        results["volume"].add(stock_code)
    if detect_low_volatility(df):
        results["volatility"].add(stock_code)
    if detect_fund_inflow(df):
        results["fund"].add(stock_code)
    if detect_kline_pattern(df):
        results["kline"].add(stock_code)
    if detect_macd_crossover(df):
        results["macd"].add(stock_code)
    if detect_turnover_stability(df):
        results["turnover"].add(stock_code)

# **统计股票在不同方法中的出现次数**
stock_occurrences = {}
for method, stocks in results.items():
    for stock in stocks:
        if stock is not None:  # 过滤掉填充的 None 值
            if stock not in stock_occurrences:
                stock_occurrences[stock] = set()
            stock_occurrences[stock].add(method)

# **找出重复出现的股票代码（出现次数 ≥ 3）**
filtered_repeated_stocks = {stock: methods for stock, methods in stock_occurrences.items() if len(methods) >= 3}

# **按出现次数排序**
sorted_repeated_stocks_df = pd.DataFrame(
    [(stock, len(methods), ", ".join(methods)) for stock, methods in sorted(filtered_repeated_stocks.items(), key=lambda x: len(x[1]), reverse=True)],
    columns=["股票代码", "出现的方法数量", "出现的方法"]
)

# **保存筛选后的结果**
sorted_repeated_stocks_df.to_csv("吸筹重复股票_出现次数大于等于3.csv", index=False, encoding="utf-8-sig")

# **显示筛选后的重复股票**
if not sorted_repeated_stocks_df.empty:
    print("\n✅ 发现出现次数 ≥ 3 的股票，已保存到 '吸筹重复股票_出现次数大于等于3.csv'")
    print(sorted_repeated_stocks_df)
else:
    print("\n⚠️ 没有找到出现次数 ≥ 3 的股票")