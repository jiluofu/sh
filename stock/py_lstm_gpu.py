import numpy as np
import pandas as pd
import os
import akshare as ak
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import gc
import time
import psutil
import tracemalloc

import utils.utils as st

# ======================== 限制 TensorFlow 线程数 ========================
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["TF_NUM_INTRAOP_THREADS"] = "2"
os.environ["TF_NUM_INTEROP_THREADS"] = "2"
tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(2)

# ======================== 内存监控函数 ========================
def print_memory_usage():
    process = psutil.Process(os.getpid())
    print(f"📊 当前内存使用: {process.memory_info().rss / 1024 ** 2:.2f} MB")

def start_memory_tracking():
    tracemalloc.start()

def print_memory_snapshot():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 10 内存占用 ]")
    for stat in top_stats[:10]:
        print(stat)

# ======================== 全局预测函数绑定 ========================
safe_model = None  # 用于绑定当前模型

@tf.function(reduce_retracing=True)
def safe_predict(x):
    return safe_model(x, training=False)

# ======================== 配置 ========================
start_time = time.time()
try:
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("✅ GPU 受控使用")
    else:
        print("⚠️ 未检测到 GPU, 使用 CPU 运行")
except Exception as e:
    print(f"❌ GPU 初始化失败: {e}, 继续使用 CPU")

START_DATE = "20180101"
END_DATE = st.get_end_date()
N_DAYS = st.get_prediction_days()
LOOKBACK_DAYS = 90
use_gold_list = True
data_dir = "data"

china_trading_days = ak.tool_trade_date_hist_sina()
china_trading_days["trade_date"] = pd.to_datetime(china_trading_days["trade_date"].astype(str)).dt.strftime("%Y%m%d")
future_dates = china_trading_days[china_trading_days["trade_date"] > END_DATE]["trade_date"].tolist()[:N_DAYS]

print(f"📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1] if future_dates else '未知'}")

STOCK_CODES = st.get_gold_stocks() if use_gold_list else st.get_main_board_stocks()
print(f"\n📊 选择 {len(STOCK_CODES)} 只股票进行分析")

# ======================== 读取数据 ========================
def get_stock_data(stock_code):
    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    if df.empty:
        return None
    df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 构建模型 ========================
def build_lstm_model(lookback_days):
    inputs = Input(shape=(lookback_days, 1))
    x = LSTM(64, return_sequences=True)(inputs)
    x = Dropout(0.2)(x)
    x = LSTM(64)(x)
    outputs = Dense(1)(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer="adam", loss="mse")
    return model

# ======================== 预测函数 ========================
def forecast(stock_code, df, n_days, lookback_days):
    global safe_model  # 用于给 safe_predict 提供模型

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df["close"].values.reshape(-1, 1))

    X, y = [], []
    for i in range(len(scaled_data) - lookback_days):
        X.append(scaled_data[i : i + lookback_days])
        y.append(scaled_data[i + lookback_days])
    X, y = np.array(X), np.array(y)

    if len(X) < n_days:
        print(f"⚠️ {stock_code} 数据不足，跳过")
        return None

    tf.keras.backend.clear_session()
    gc.collect()

    model = build_lstm_model(lookback_days)
    print(f"🚀 {stock_code} LSTM 训练开始...")
    history = model.fit(X[:-n_days], y[:-n_days], epochs=20, batch_size=8, verbose=0)
    del history.history
    gc.collect()
    print(f"✅ {stock_code} LSTM 训练完成！")

    safe_model = model  # 设置为当前模型供 safe_predict 使用

    future_prices = []
    last_window = X[-1]

    for _ in range(n_days):
        input_tensor = tf.convert_to_tensor(last_window.reshape(1, lookback_days, 1), dtype=tf.float32)
        next_price_scaled = safe_predict(input_tensor)[0, 0].numpy()
        next_price = scaler.inverse_transform([[next_price_scaled]])[0, 0]
        future_prices.append(float(f"{next_price:.3f}"))
        last_window = np.roll(last_window, -1)
        last_window[-1] = next_price_scaled

    last_price = df.iloc[-1]["close"]
    last_predicted_price = future_prices[-1]
    price_change_percent = round(((last_predicted_price - last_price) / last_price) * 100, 2)

    print(f"📊 {stock_code} - 预测涨幅: {price_change_percent}%")

    return pd.DataFrame({
        "股票代码": [stock_code],
        "截止日价格": [last_price],
        "预测最后一天价格": [last_predicted_price],
        "预测涨幅 (%)": [price_change_percent]
    })

# ======================== 主程序运行 ========================
all_results = []
start_memory_tracking()

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue

    result_df = forecast(stock_code, df, N_DAYS, LOOKBACK_DAYS)
    if result_df is not None:
        all_results.append(result_df)
    time.sleep(0.1)

if all_results:
    pd.concat(all_results, ignore_index=True).to_csv("lstm_forecast.csv", index=False)
    print("✅ 预测完成，结果已保存")

st.print_elapsed_time(start_time)