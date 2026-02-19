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

# === ✅ 数据目录 ===
real_dir = "real"

# === 遍历每只股票子目录 ===
for code in os.listdir(real_dir):
    code_path = os.path.join(real_dir, code)
    if not os.path.isdir(code_path):
        continue

    csv_files = [f for f in sorted(os.listdir(code_path)) if f.endswith(".csv")]
    if not csv_files:
        continue

    print(f"\n📈 股票代码：{code}")
    print("日期\t开盘价\t最低价\t最低出现分钟数")

    for csv_file in csv_files:
        file_path = os.path.join(code_path, csv_file)

        try:
            df = pd.read_csv(file_path)
            if df.empty or "成交时间" not in df.columns or "成交价格" not in df.columns:
                continue

            # 转换时间
            df["成交时间"] = pd.to_datetime(df["成交时间"], format="%H:%M:%S")
            df["分钟"] = df["成交时间"].dt.floor("min")

            # 分钟聚合
            minute_data = df.groupby("分钟").agg(
                均价=("成交价格", "mean")
            ).reset_index()

            if minute_data.empty:
                continue

            # 开盘价
            opening_price = minute_data["均价"].iloc[0]

            # 找最低价及出现时间
            min_price_idx = minute_data["均价"].idxmin()
            min_price_time = minute_data.loc[min_price_idx, "分钟"]
            min_price_value = minute_data.loc[min_price_idx, "均价"]

            # 计算开盘后多少分钟出现最低价
            open_time = pd.to_datetime("09:30", format="%H:%M")
            minutes_after_open = int((min_price_time - open_time).total_seconds() / 60)

            # 输出
            date_str = csv_file.replace(".csv", "")
            print(f"{date_str}\t¥{opening_price:.2f}\t¥{min_price_value:.2f}\t{minutes_after_open}分钟")

        except Exception as e:
            print(f"❌ 分析失败：{csv_file} - 错误：{e}")