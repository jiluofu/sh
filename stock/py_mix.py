import os
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input

# ============ 初始化 TensorFlow ============
def setup_tensorflow():
    print("\n🧠 正在检测 TensorFlow 设备...")
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✅ 检测到 {len(gpus)} 个 GPU，已开启 memory growth")
        except Exception as e:
            print(f"⚠️ 设置 GPU 内存失败：{e}")
    else:
        print("⚠️ 未检测到 GPU，使用 CPU 模式")

# ============ 构建 LSTM 模型 ============
def build_lstm_model(lookback):
    model = Sequential()
    model.add(Input(shape=(lookback, 1)))
    model.add(LSTM(64))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")
    return model

# ============ 筹码集中度判断 ============
def get_chip_status(df, end_date, window=20):
    if len(df) < window:
        return "数据不足"
    sub_df = df[df.index <= pd.to_datetime(end_date)].tail(window)
    std = sub_df["close"].std()
    mean = sub_df["close"].mean()
    ratio = std / mean
    if ratio < 0.03:
        return "筹码高度集中 🎯"
    elif ratio < 0.06:
        return "筹码中度集中 ✅"
    else:
        return "筹码分散 ⚠️"

# ============ 构造 XGBoost 输入 ============
def create_xgboost_features(df, lookback, days_ahead):
    X, y = [], []
    for i in range(len(df) - lookback - days_ahead):
        window = df["close"].iloc[i : i + lookback].values
        X.append(window)
        y.append(df["close"].iloc[i + lookback + days_ahead - 1])
    return np.array(X), np.array(y)

def create_latest_xgboost_input(df, lookback):
    if len(df) < lookback:
        return None
    latest_window = df["close"].iloc[-lookback:].values.reshape(1, -1)
    return latest_window

def train_predict_xgboost(df_train, last_price, lookback, days_ahead):
    X_xgb, y_xgb = create_xgboost_features(df_train, lookback, days_ahead)
    if len(X_xgb) == 0:
        return None, None, None
    model_xgb = xgb.XGBRegressor()
    model_xgb.fit(X_xgb, y_xgb)

    latest_input = create_latest_xgboost_input(df_train, lookback)
    if latest_input is None:
        return None, None, None

    pred = model_xgb.predict(latest_input)[0]
    pct_change = round((pred - last_price) / last_price * 100, 2)
    prob = 1.0 if pred > last_price else 0.0
    return pred, pct_change, prob

# ============ 主预测函数 ============
def run_full_prediction(stock_code, end_date, days_ahead, lookback=30, data_dir="data"):
    setup_tensorflow()

    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 文件不存在: {file_path}")
    
    df = pd.read_csv(file_path)
    df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    if end_date not in df.index:
        raise ValueError(f"❌ 截止日期 {end_date} 不在数据中")

    df_train = df[df.index <= pd.to_datetime(end_date)].copy()
    df_future = df[df.index > pd.to_datetime(end_date)]
    last_price = df_train.iloc[-1]["close"]
    chip_status = get_chip_status(df, end_date)

    # === XGBoost 预测 ===
    xgb_pred, xgb_change, xgb_prob = train_predict_xgboost(df_train, last_price, lookback, days_ahead)

    # === LSTM 预测 ===
    scaler = MinMaxScaler()
    scaled_close = scaler.fit_transform(df_train[["close"]])
    X_lstm, y_lstm = [], []
    for i in range(len(scaled_close) - lookback - days_ahead):
        X_lstm.append(scaled_close[i:i+lookback])
        y_lstm.append(scaled_close[i+lookback+days_ahead-1])
    X_lstm, y_lstm = np.array(X_lstm), np.array(y_lstm)

    model_lstm = build_lstm_model(lookback)
    model_lstm.fit(X_lstm, y_lstm, epochs=20, batch_size=8, verbose=0)

    last_seq = scaled_close[-lookback:].reshape(1, lookback, 1)
    lstm_pred_scaled = model_lstm.predict(last_seq)[0, 0]
    lstm_pred = scaler.inverse_transform([[lstm_pred_scaled]])[0, 0]
    lstm_change = round((lstm_pred - last_price) / last_price * 100, 2)
    lstm_prob = 1.0 if lstm_pred > last_price else 0.0

    # 获取真实未来价格
    future_date = df_future.index[days_ahead - 1] if len(df_future) >= days_ahead else None
    future_price = df_future.loc[future_date, "close"] if future_date else None

    result_df = pd.DataFrame([
        {
            "模型": "XGBoost",
            "截止日价格": round(last_price, 2),
            "预测未来价格": round(xgb_pred, 2),
            "预测涨幅(%)": xgb_change,
            "预测上涨概率": xgb_prob,
            "实际未来价格": round(future_price, 2) if future_price else "",
            "未来日期": future_date.strftime("%Y-%m-%d") if future_date else "",
            "筹码状态": chip_status
        },
        {
            "模型": "LSTM",
            "截止日价格": round(last_price, 2),
            "预测未来价格": round(lstm_pred, 2),
            "预测涨幅(%)": lstm_change,
            "预测上涨概率": lstm_prob,
            "实际未来价格": round(future_price, 2) if future_price else "",
            "未来日期": future_date.strftime("%Y-%m-%d") if future_date else "",
            "筹码状态": chip_status
        }
    ])

    return result_df

# 示例调用（可删除换成你的入口）
if __name__ == "__main__":
    df_result = run_full_prediction(
        stock_code="300059",
        end_date="2025-03-24",
        days_ahead=3,
        lookback=90,
        data_dir="data"
    )
    print("\n📊 预测结果：")
    print(df_result.to_string(index=False))
    df_result.to_csv("prediction_result.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 结果已保存为 prediction_result.csv")