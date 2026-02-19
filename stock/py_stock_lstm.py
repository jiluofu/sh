import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as fm
import akshare as ak
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# **自动匹配系统内的中文字体**
def set_chinese_font():
    font_list = ["SimHei", "Arial Unicode MS", "Noto Sans CJK SC", "STHeiti"]
    for font in font_list:
        if font in [f.name for f in fm.fontManager.ttflist]:
            plt.rcParams["font.sans-serif"] = font
            plt.rcParams["axes.unicode_minus"] = False
            print(f"✅ 选择字体: {font}")
            return
    print("⚠️ 没有找到合适的中文字体，可能会乱码！")

# 获取 A 股主板深市和沪市所有股票代码（去掉创业板）
def get_main_board_stocks():
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]["code"].tolist()
    return main_board_stocks

set_chinese_font()

# 开关：是否从 AkShare 在线获取数据
use_akshare = True  # True 使用在线数据, False 使用本地 CSV
num_days = 5  # 用户可自定义预测天数

data_dir = "data"
# 股票代码数组
stock_codes = ["002580", "600519", "000001", "002594"]
stock_codes = get_main_board_stocks()

# 如果 stock_codes 为空，则遍历 data 目录下所有 CSV 文件
if not stock_codes:
    stock_codes = [f.split(".")[0] for f in os.listdir(data_dir) if f.endswith(".csv")]

# 存储结果的数据框
results = []

for stock_code in stock_codes:
    if use_akshare:
        print(f"🔄 正在从 AkShare 获取 {stock_code} 的数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date="20240101", end_date="20250225", adjust="qfq")
        if df.empty:
            print(f"❌ 未能获取 {stock_code} 的数据，请检查代码是否正确！")
            continue
        df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
    else:
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        if not os.path.exists(file_path):
            print(f"❌ 文件 {file_path} 不存在，请检查路径！")
            continue
        df = pd.read_csv(file_path)

    # 处理数据（确保列名正确）
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"])
        df.set_index("日期", inplace=True)
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    else:
        print(f"❌ 数据 {stock_code} 中没有找到 '日期' 或 'date' 列，请检查数据格式！")
        continue

    # 提取收盘价
    if "收盘" in df.columns:
        df = df[["收盘"]]
    elif "close" in df.columns:
        df = df[["close"]]
    else:
        print(f"❌ 数据 {stock_code} 中没有找到 '收盘' 或 'close' 列，请检查数据格式！")
        continue

    # 归一化数据
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_scaled = scaler.fit_transform(df)

    # 生成 LSTM 训练数据
    X, y = [], []
    lookback = 60
    for i in range(len(df_scaled) - lookback - num_days):
        X.append(df_scaled[i:i + lookback])
        y.append(df_scaled[i + lookback:i + lookback + num_days])
    X, y = np.array(X), np.array(y)

    # 构建 LSTM 模型
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
        LSTM(50, return_sequences=False),
        Dense(num_days)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')

    # 训练模型
    model.fit(X, y, epochs=20, batch_size=16, verbose=0)

    # 预测
    last_lookback = df_scaled[-lookback:].reshape(1, lookback, 1)
    predicted_scaled = model.predict(last_lookback)
    predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(-1, 1))
    price_mean = round(np.mean(predicted_prices), 3)

    # 获取昨日收盘价
    yesterday_price = df.iloc[-2, 0] if len(df) > 1 else None

    # 计算预测价格相对于昨日收盘价的涨幅
    increase_percent = round(((price_mean - yesterday_price) / yesterday_price) * 100, 2) if yesterday_price else None

    # 存储结果
    results.append([stock_code, price_mean, yesterday_price, increase_percent])

# 按照第四列（变化百分比）排序
results_df = pd.DataFrame(results, columns=["股票代码", "预测价格", "昨日收盘价", "预测比昨日收盘价变化%"])
results_df.sort_values(by="预测比昨日收盘价变化%", ascending=False, inplace=True)
results_df.to_csv("predicted_prices_lstm.csv", index=False, encoding='utf-8-sig')
print("✅ 预测结果已保存到 predicted_prices_lstm.csv，并按变化百分比排序")

# 提取前20个股票代码并保存到 txt 文件
top_20_stocks = results_df.head(20)["股票代码"].tolist()
with open("top_20_stocks_lstm.txt", "w", encoding="utf-8") as f:
    for stock in top_20_stocks:
        f.write(stock + "\n")

print("✅ 预测结果已保存到 predicted_prices_lstm.csv，并按预测比昨日收盘增长%排序")
print("✅ 前20个股票代码已保存到 top_20_stocks_lstm.txt")
