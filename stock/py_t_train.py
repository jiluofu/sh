import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
import joblib

# 配置路径
real_dir = "real"
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# === ✅ 读取命令行参数（可选日期）===
if len(sys.argv) > 1:
    target_date = sys.argv[1].replace("-", "").replace("/", "")
else:
    target_date = None

# === 读取命令行参数（是否下载全部）
download_all = "-all" in sys.argv

# ✅ 可选股票代码列表（为空处理全部，不为空只处理指定）
stock_codes = []  # 例子：['601398', '601988']
stock_codes = ['601398', '601988']

if download_all:
    print("🌐 检测到 -all 参数，开始训练所有股票模型...")
    stock_codes = []

# 遍历每个股票目录
for code in os.listdir(real_dir):
    code_path = os.path.join(real_dir, code)
    if not os.path.isdir(code_path):
        continue

    # ✅ 如果 stock_codes 非空，只处理指定代码
    if stock_codes and code not in stock_codes:
        continue

    csv_files = [f for f in os.listdir(code_path) if f.endswith(".csv")]
    if not csv_files:
        continue

    # === ✅ 选择文件：优先找指定日期，否则用最新日期 ===
    file_path = None
    if target_date and f"{target_date}.csv" in csv_files:
        latest_file = f"{target_date}.csv"
        file_path = os.path.join(code_path, latest_file)
    else:
        latest_file = sorted(csv_files)[-1]
        file_path = os.path.join(code_path, latest_file)    

    try:
        df = pd.read_csv(file_path)
        df["成交时间"] = pd.to_datetime(df["成交时间"], format="%H:%M:%S")
        df["分钟"] = df["成交时间"].dt.floor("min")
        minute_data = df.groupby("分钟").agg(
            均价=("成交价格", "mean"),
            总成交量=("成交量", "sum")
        ).reset_index()

        if len(minute_data) < 60:
            print(f"⚠️ {code} 数据不足，跳过训练")
            continue

        # === 构造 XGBoost 训练数据（单条）
        main_price = df.groupby("成交价格")["成交量"].sum().idxmax()
        low_price = minute_data["均价"].min()
        high_price = minute_data["均价"].max()
        std = minute_data["均价"].std()
        volume_sum = minute_data["总成交量"].sum()
        volume_mean = minute_data["总成交量"].mean()

        xgb_features = pd.DataFrame([{
            "main_price": main_price,
            "low_price": low_price,
            "high_price": high_price,
            "std": std,
            "volume_sum": volume_sum,
            "volume_mean": volume_mean
        }])
        xgb_label = [round(low_price - np.random.uniform(0.01, 0.03), 2)]

        # === 训练 XGBoost 模型 ===
        xgb_model = GradientBoostingRegressor()
        xgb_model.fit(xgb_features, xgb_label)
        joblib.dump(xgb_model, os.path.join(model_dir, f"{code}_xgb_model.pkl"))
        print(f"✅ {code} - XGBoost 模型已保存")

        # === 构造 LSTM 样本（滑窗）
        lstm_sequences = []
        lstm_targets = []
        prices = minute_data["均价"].values

        for i in range(len(prices) - 45):
            input_seq = prices[i:i+30]
            future_window = prices[i+30:i+45]
            target = np.min(future_window)
            lstm_sequences.append(input_seq)
            lstm_targets.append(target)

        if len(lstm_sequences) < 10:
            print(f"⚠️ {code} LSTM 样本不足，跳过 LSTM")
            continue

        # === 训练 LSTM 模型 ===
        X_lstm = np.array(lstm_sequences).reshape(-1, 30, 1)
        y_lstm = np.array(lstm_targets)

        lstm_model = Sequential()
        lstm_model.add(LSTM(32, input_shape=(30, 1)))
        lstm_model.add(Dense(1))
        lstm_model.compile(loss='mse', optimizer=Adam(0.001))
        lstm_model.fit(X_lstm, y_lstm, epochs=50, batch_size=16,
                       validation_split=0.1, callbacks=[EarlyStopping(patience=5)], verbose=0)

        lstm_model.save(os.path.join(model_dir, f"{code}_lstm_model.h5"))
        print(f"✅ {code} - LSTM 模型已保存")

    except Exception as e:
        print(f"❌ {code} 训练失败: {e}")