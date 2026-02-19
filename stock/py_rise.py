import numpy as np
import pandas as pd
import os
import akshare as ak
from datetime import datetime, timedelta
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import utils.utils as st

# 记录程序开始时间
start_time = time.time()

# 配置目标日期和交易日数量
TARGET_DATE = "20250324"
TARGET_DATE = st.get_end_date()
TRADING_DAYS_AHEAD = 3  # 可配置的交易日数量
data_dir = "data"
output_csv = "predicted_rise_results.csv"

print(f"\n📅 目标日期: {TARGET_DATE}, 预测未来 {TRADING_DAYS_AHEAD} 个交易日后的上涨概率")

# ======================== 统一列名 ========================
def standardize_column_names(df):
    rename_map = {
        "收盘": "close", "收盘价": "close", "成交量": "volume", "换手率": "turnover",
        "日期": "date", "时间": "date", "代码": "code", "股票代码": "code"
    }
    df.rename(columns=rename_map, inplace=True)
    return df

# ======================== 获取所有A股主板股票列表 ========================
def get_main_board_stocks():
    print("📥 正在从 AkShare 获取所有 A 股股票代码...")
    try:
        stock_list = ak.stock_info_a_code_name()
        print(f"✅ 成功获取 {len(stock_list)} 只股票代码")
    except Exception as e:
        print(f"❌ 无法从 AkShare 获取股票列表: {e}")
        return []

    # 过滤符合要求的主板股票代码
    main_board_stocks = stock_list[stock_list["code"].str.startswith(st.STOCK_LIST_WHITE_PRE)]["code"].tolist()
    print(f"✅ 筛选出 {len(main_board_stocks)} 只主板股票代码")
    return main_board_stocks

# ======================== 读取股票数据 ========================
def get_stock_data(stock_code):
    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ 数据文件不存在：{file_path}")
        return None

    df = pd.read_csv(file_path)
    df = standardize_column_names(df)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 计算 MACD ========================
def calculate_macd(df):
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_diff"] = df["macd"] - df["signal"]
    return df

# ======================== 计算筹码集中度 ========================
def calculate_chip_distribution(df):
    df["vol_ma20"] = df["volume"].rolling(window=20).mean()
    df["chip_concentration"] = df["close"].rolling(window=20).std() / df["close"].rolling(window=20).mean()
    return df

# ======================== 生成特征和标签 ========================
def generate_features(df):
    df = calculate_macd(df)
    df = calculate_chip_distribution(df)

    # 过滤数据，确保 full_df 范围为起始日期到目标日期
    df = df[df.index <= pd.to_datetime(TARGET_DATE)].copy()

    # 计算未来 n 个交易日的收盘价变化率
    df["price_change_3d"] = df["close"].pct_change(periods=TRADING_DAYS_AHEAD).shift(-TRADING_DAYS_AHEAD)
    df["label"] = (df["price_change_3d"] > 0).astype(int)

    features = ["macd", "signal", "macd_diff", "volume", "vol_ma20", "chip_concentration"]
    # 再次创建深拷贝，确保链式赋值警告完全消除
    df = df[features + ["label", "price_change_3d", "close"]].copy()

    # 处理无穷值为 NaN
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # 填充缺失值
    df.ffill(inplace=True)  # 前值填充
    df.fillna(0, inplace=True)  # 将剩余 NaN 填充为 0

    # 确保数据类型一致
    df = df.astype(np.float32)
    
    return df[features], df["label"], df

# ======================== 训练模型 ========================
def train_model(X, y):
    if len(X) < 2:
        print("⚠️ 样本数量不足，跳过训练")
        return None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# ======================== 获取未来交易日日期 ========================
def get_next_trading_date(df, start_date, n=3):
    trading_dates = df.index
    start_idx = trading_dates.get_loc(pd.to_datetime(start_date))   
    try:
        next_date = trading_dates[start_idx + n]
        return next_date
    except IndexError:
        print(f"⚠️ 无法获取 {start_date} 之后的第 {n} 个交易日")
        return None

# ======================== 读取股票名称和行业名称 ========================
stock_info_df = pd.read_csv("data/main_board_stocks.csv", dtype={"股票代码": str})

# ======================== 预测上涨概率 ========================
def predict_rise_probability(df, model, target_date):
    print(f"🔍 检查目标日期 {target_date} 是否在数据集中...")
    X, _, _ = generate_features(df)
    
    if target_date not in X.index:
        print(f"❌ 目标日期 {target_date} 不在数据集中")
        return None, None

    latest_data = X.loc[[target_date]]
    try:
        predicted_prob = model.predict_proba(latest_data)[:, 1][0]
        print(f"✅ 预测成功：上涨概率 {predicted_prob:.4f}")
        return predicted_prob, latest_data
    except Exception as e:
        print(f"❌ 预测失败：{e}")
        return None, None

# ======================== 生成CSV ========================
results = []
main_board_stocks = get_main_board_stocks()

for stock_code in main_board_stocks:
    print(f"\n🚀 正在处理股票代码：{stock_code}")

    df = get_stock_data(stock_code)
    if df is None or pd.to_datetime(TARGET_DATE) not in df.index:
        print(f"⚠️ 数据缺失或无目标日期数据，跳过：{stock_code}")
        continue

    print(f"📊 生成特征和标签...")
    X, y, full_df = generate_features(df)
    if X.empty:
        print(f"⚠️ 无有效特征，跳过股票代码：{stock_code}")
        continue

    print(f"🛠️ 训练模型中...")
    model = train_model(X, y)
    if model is None:
        print(f"⚠️ 模型训练失败，跳过股票代码：{stock_code}")
        continue

    print(f"🔮 预测上涨概率中...")
    predicted_prob, latest_data = predict_rise_probability(full_df, model, TARGET_DATE)
    if predicted_prob is None:
        print(f"⚠️ 预测失败，跳过股票代码：{stock_code}")
        continue

    close_price = df.loc[TARGET_DATE, "close"]
    future_date = get_next_trading_date(df, TARGET_DATE, n=TRADING_DAYS_AHEAD)

    # 未来收盘价和实际上涨初始化为空值
    future_close_price = ""
    actual_label = ""

    # 判断未来日期是否存在并获取未来收盘价
    if future_date is not None and future_date in df.index:
        try:
            future_close_price = df.loc[future_date, "close"]
            actual_label = "上涨" if (future_close_price - close_price) > 0 else "下跌"
        except KeyError:
            print(f"⚠️ 无法获取未来价格：{stock_code}")
    else:
        print(f"⚠️ 无法获取未来交易日或未来收盘价：{stock_code}")

    print(f"✅ 预测完成：{stock_code}，上涨概率：{predicted_prob:.4f}")

    stock_name = stock_info_df.loc[stock_info_df["股票代码"] == stock_code, "股票名称"].values[0]
    industry_name = stock_info_df.loc[stock_info_df["股票代码"] == stock_code, "行业名称"].values[0]

    # 只保留上涨概率大于 0.5 的记录
    if predicted_prob > 0.5:
        result = {
            "股票代码": stock_code,
            "股票名称": stock_name,
            "行业名称": industry_name,
            "预测日期": TARGET_DATE,
            "收盘价": close_price,
            "未来日期": future_date.strftime("%Y-%m-%d") if future_date else "",
            "未来收盘价": future_close_price,
            "预测上涨概率": predicted_prob,
            "实际上涨": actual_label
        }
        results.append(result)

# 生成最终结果的 DataFrame
result_df = pd.DataFrame(results)

# 只保留上涨概率大于 0.5 的股票
result_df = result_df[result_df["预测上涨概率"] > 0.5]

# 按照上涨概率降序排列
result_df = result_df.sort_values(by="预测上涨概率", ascending=False)

# 保存预测结果到 CSV
result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"\n✅ 预测结果已保存到 {output_csv}，只保留上涨概率大于 0.5 的记录")

st.print_elapsed_time(start_time)