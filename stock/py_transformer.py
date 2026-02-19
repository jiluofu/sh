import numpy as np
import pandas as pd
import os
import akshare as ak
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import gc
import time

import utils.utils as st

start_time = time.time()

# ======================== GPU 限制 ========================
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("✅ GPU 受控使用")
    except RuntimeError as e:
        print(f"❌ GPU 配置失败: {e}")

# ======================== 配置 ========================
START_DATE = "20180101"
END_DATE = "20250319"  
END_DATE = st.get_end_date()
N_DAYS = 3  
N_DAYS = st.get_prediction_days()
LOOKBACK_DAYS = 90  
use_gold_list = True  
data_dir = "data"  

# ======================== 获取 A 股交易日历 ========================
china_trading_days = ak.tool_trade_date_hist_sina()
china_trading_days["trade_date"] = pd.to_datetime(china_trading_days["trade_date"].astype(str)).dt.strftime("%Y%m%d") 
future_dates = china_trading_days[china_trading_days["trade_date"] > END_DATE]["trade_date"].tolist()
future_dates = future_dates[:N_DAYS]  

print(f"\n📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1]}")  

# ======================== 选择股票代码 ========================
STOCK_CODES = st.get_gold_stocks() if use_gold_list else st.get_main_board_stocks()
print(f"\n📊 选择 {len(STOCK_CODES)} 只股票进行分析")

# ======================== 读取股票数据并计算技术指标 ========================
def get_stock_data(stock_code):
    print(f"\n📥 获取 {stock_code} 的数据...")
    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ 本地数据 {file_path} 不存在，跳过 {stock_code}。")
        return None
    
    df = pd.read_csv(file_path)
    if df.empty:
        print(f"❌ 无法获取 {stock_code} 的数据，跳过。")
        return None

    df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    # 计算技术指标
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["rsi"] = df["close"].diff().apply(lambda x: x if x > 0 else 0).rolling(14).mean() / df["close"].diff().abs().rolling(14).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    
    df.dropna(inplace=True)  
    return df

# ======================== 构建 Transformer 模型 ========================
def build_transformer_model(lookback_days, num_features):
    inputs = Input(shape=(lookback_days, num_features))
    
    x = MultiHeadAttention(num_heads=4, key_dim=64)(inputs, inputs)
    x = LayerNormalization(epsilon=1e-6)(x)
    x = Dense(64, activation="relu")(x)
    x = Dropout(0.2)(x)
    
    outputs = Dense(1)(x)
    
    model = Model(inputs, outputs)
    model.compile(optimizer="adam", loss="mse")
    return model

# ======================== 预测股价 ========================
def forecast(stock_code, df, n_days, lookback_days):
    print(f"\n🚀 训练 Transformer 预测 {stock_code} 的未来 {n_days} 天价格...")
    
    features = ["close", "macd", "rsi", "ma20", "volume"]
    df_features = df[features]

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df_features)

    X, y = [], []
    for i in range(len(scaled_data) - lookback_days):
        X.append(scaled_data[i : i + lookback_days])
        y.append(scaled_data[i + lookback_days, 0])  

    X, y = np.array(X), np.array(y)
    if len(X) < n_days:
        print("❌ 训练数据不足，跳过")
        return None

    tf.keras.backend.clear_session()
    gc.collect()

    model = build_transformer_model(lookback_days, len(features))
    model.fit(X[:-n_days], y[:-n_days], epochs=50, batch_size=16, verbose=0)

    last_price = df.iloc[-1]["close"]  
    future_prices = []
    last_window = X[-1]

    for _ in range(n_days):
        next_price_scaled = model.predict(last_window.reshape(1, lookback_days, len(features)), verbose=0)[0, 0]
        next_price = float(next_price_scaled * (scaler.data_max_[0] - scaler.data_min_[0]) + scaler.data_min_[0])

        future_prices.append(round(next_price, 3))
        last_window = np.roll(last_window, -1, axis=0)
        last_window[-1, 0] = next_price_scaled  

    last_predicted_price = future_prices[-1]
    price_change_percent = round(((last_predicted_price - last_price) / last_price) * 100, 2)

    return pd.DataFrame({
        "股票代码": [stock_code],
        "截止日价格": [last_price],
        "预测最后一天价格": [last_predicted_price],
        "预测涨幅 (%)": [price_change_percent]
    })

all_results = [forecast(stock_code, get_stock_data(stock_code), N_DAYS, LOOKBACK_DAYS) for stock_code in STOCK_CODES if get_stock_data(stock_code) is not None]
final_result_df = pd.concat(all_results, ignore_index=True)
final_result_df.to_csv("transformer_forecast.csv", index=False, encoding="utf-8-sig")

print("\n✅ 预测完成，结果已保存！")
print(f"\n📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1]}")  
st.print_elapsed_time(start_time)