import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime

# === 配置 ===
symbol = "601398"  # 股票代码
ONLY_LAST_5_MINUTES = True  # 🔥 控制是否只画最近5分钟

# === 获取日期参数 ===
if len(sys.argv) > 1:
    date_str = sys.argv[1]
else:
    date_str = datetime.now().strftime("%Y%m%d")

# === 文件路径 ===
file_path = os.path.join("order", symbol, f"{date_str}.csv")
print(f"📂 读取文件: {file_path}")

# === 检查文件存在性
if not os.path.exists(file_path):
    print(f"❌ 文件不存在: {file_path}")
    sys.exit(1)

# === 买一-买五 ===
buy_levels = ["买一", "买二", "买三", "买四", "买五"]

# === 收集所有时间、价格、挂单手数 ===
records = []

df = pd.read_csv(file_path)

for i in range(len(df)):
    row = df.iloc[i]
    time_value = row.get("时间")
    if pd.isna(time_value):
        continue

    for level in buy_levels:
        price_col = f"{level}_价格"
        vol_col = f"{level}_挂单手数"

        price = row.get(price_col)
        volume = row.get(vol_col)

        if pd.isna(price) or pd.isna(volume) or price == 0:
            continue

        records.append({
            "时间": time_value,
            "价格": round(price, 2),
            "挂单手数": volume
        })

# === 转成DataFrame
data = pd.DataFrame(records)

if data.empty:
    print("⚠️ 没有挂单记录，退出。")
    sys.exit(0)

# === 时间列转换
data["时间"] = pd.to_datetime(data["时间"], format="%H:%M:%S")

# === 只保留最近5分钟的数据（如果开关打开）
if ONLY_LAST_5_MINUTES:
    latest_time = data["时间"].max()
    time_threshold = latest_time - pd.Timedelta(minutes=5)
    data = data[data["时间"] >= time_threshold]
    print(f"⏳ 当前最新时间: {latest_time.time()}，只分析最近5分钟内的数据。")

# === 获取所有去重后的价格
unique_prices = sorted(data["价格"].unique())

# === 开始画图
plt.figure(figsize=(14, 8))

for price in unique_prices:
    subset = data[data["价格"] == price]
    plt.plot(subset["时间"], subset["挂单手数"], label=f"{price:.2f}元", marker="o", markersize=3)

plt.title(f"Order Volume by Price Level Over Time - {symbol} - {date_str}")
plt.xlabel("Time")
plt.ylabel("Order Volume (Lots)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()