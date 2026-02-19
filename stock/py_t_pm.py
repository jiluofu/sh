import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import joblib
from tensorflow.keras.models import load_model

# === ✅ 字体设置（macOS 中文支持）===
matplotlib.rcParams['font.family'] = 'Source Han Sans SC'
matplotlib.rcParams['axes.unicode_minus'] = False

# === 读取命令行参数（是否下载全部）
download_all = "-all" in sys.argv

# === ✅ 读取命令行参数（可选日期）===
if len(sys.argv) > 1:
    target_date = sys.argv[1].replace("-", "").replace("/", "")
else:
    target_date = None

# === ✅ 模型路径 ===
model_dir = "models"

# === ✅ 股票代码筛选列表（为空处理全部，不为空只处理指定）
stock_codes = []  # 例如：['601398', '601988']
stock_codes = ['601398', '601988']

if download_all:
    print("🌐 检测到 -all 参数，开始对所有股票预测...")
    stock_codes = []

# === ✅ 数据目录 ===
real_dir = "real"

# === 遍历每只股票子目录 ===
for code in os.listdir(real_dir):
    code_path = os.path.join(real_dir, code)
    if not os.path.isdir(code_path):
        continue

    # ✅ 如果 stock_codes 非空，只处理指定股票
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
        # === 1. 读取数据 ===
        df = pd.read_csv(file_path)
        df["成交时间"] = pd.to_datetime(df["成交时间"], format="%H:%M:%S")
        df["分钟"] = df["成交时间"].dt.floor("min")

        minute_data = df.groupby("分钟").agg(
            均价=("成交价格", "mean"),
            总成交量=("成交量", "sum"),
            买盘成交量=("成交量", lambda s: s[df.loc[s.index, "性质"] == "买盘"].sum()),
            卖盘成交量=("成交量", lambda s: s[df.loc[s.index, "性质"] == "卖盘"].sum())
        ).reset_index()

        # === 2. 主力成交密集价 ===
        volume_by_price = df.groupby("成交价格")["成交量"].sum()
        main_price = volume_by_price.idxmax()

        # === 3. 策略价位1-6 ===
        suggest_low1 = round(main_price - 0.03, 2)
        suggest_low2 = round(minute_data["均价"].min() - 0.01, 2)

        price_range = minute_data["均价"].max() - minute_data["均价"].min()
        price_range_pct = price_range / main_price if main_price else 0
        suggest_low3 = round(main_price * (1 - price_range_pct * 0.8), 2)
        suggest_low4 = round(main_price * (1 - price_range_pct * 1.2), 2)

        price_std = minute_data["均价"].std()
        suggest_low5 = round(main_price - price_std * 1.5, 2)
        suggest_low6 = round(main_price - price_std * 2.0, 2)

        # === 4. XGBoost 特征构造 ===
        xgb_model_path = f"{model_dir}/{code}_xgb_model.pkl"
        xgb_price1 = xgb_price2 = "N/A"
        try:
            xgb_model = joblib.load(xgb_model_path)
            xgb_features = pd.DataFrame([{
                "main_price": main_price,
                "low_price": minute_data["均价"].min(),
                "high_price": minute_data["均价"].max(),
                "std": price_std,
                "volume_sum": minute_data["总成交量"].sum(),
                "volume_mean": minute_data["总成交量"].mean(),
            }])
            xgb_pred = xgb_model.predict(xgb_features)[0]
            xgb_price1 = round(xgb_pred - 0.01, 2)
            xgb_price2 = round(xgb_pred - 0.02, 2)
        except Exception as e:
            print(f"⚠️ XGBoost预测失败（{code}）：{e}")

        # === 5. LSTM 预测 ===
        lstm_model_path = f"{model_dir}/{code}_lstm_model.h5"
        lstm_price1 = lstm_price2 = "N/A"
        try:
            lstm_model = load_model(lstm_model_path, compile=False)
            seq = minute_data["均价"].values[-30:]
            if len(seq) < 30:
                raise ValueError("LSTM 输入不足30步")
            lstm_input = np.array(seq).reshape(1, -1, 1)
            lstm_pred = lstm_model.predict(lstm_input)
            lstm_low = np.min(lstm_pred)
            lstm_price1 = round(lstm_low - 0.01, 2)
            lstm_price2 = round(lstm_low - 0.02, 2)
        except Exception as e:
            print(f"⚠️ LSTM预测失败（{code}）：{e}")

        # === 6. 输出策略结果 ===
        print(f"\n📈 股票代码：{code} - 日期：{latest_file.replace('.csv', '')}")
        print("📊 做T低吸策略建议（含6种传统+2种AI预测）")
        print(f"🔽 策略1（主力价 - 0.03）            = ¥{suggest_low1}  【稳健挂】")
        print(f"🔽 策略2（最低均价 - 0.01）          = ¥{suggest_low2}  【激进挂】")
        print(f"🔽 策略3（动态波幅 × 0.8）          = ¥{suggest_low3}  【半稳健挂】")
        print(f"🔽 策略4（动态波幅 × 1.2）          = ¥{suggest_low4}  【半激进挂】")
        print(f"🔽 策略5（主力价 - 1.5 × std）     = ¥{suggest_low5}  【波动中低挂】")
        print(f"🔽 策略6（主力价 - 2.0 × std）     = ¥{suggest_low6}  【极限低吸挂】")
        print(f"🤖 策略7（XGBoost预测）             = ¥{xgb_price1} / ¥{xgb_price2} 【AI模型】")
        print(f"🤖 策略8（LSTM预测）                = ¥{lstm_price1} / ¥{lstm_price2} 【AI趋势】")
        print(f"\n🎯 建议：可在 12:57~13:00 提前挂单，按2:2:1:1:1:1分布，或结合AI建议价择优挂单")

    except Exception as e:
        print(f"❌ 分析失败：{code} - 错误：{e}")