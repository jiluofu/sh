import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime

# === 配置 ===
symbol = "601398"  # 股票代码
ONLY_RECENT_MINUTES = False  # ⬅️ 开关：True只画最近5分钟，False画全部
RECENT_MINUTES = 5           # 最近几分钟

# === 获取日期 ===
if len(sys.argv) > 1:
    date_str = sys.argv[1]
else:
    date_str = datetime.now().strftime("%Y%m%d")

# === 文件路径 ===
file_path = os.path.join("order", symbol, f"{date_str}.csv")
print(f"📂 读取文件: {file_path}")

# === 检查文件是否存在 ===
if not os.path.exists(file_path):
    print(f"❌ 文件不存在: {file_path}")
    sys.exit(1)

# === 读入数据 ===
df = pd.read_csv(file_path)

# === 转换时间列 ===
df["时间"] = pd.to_datetime(df["时间"], format="%H:%M:%S")

# === 买一到买五价位列 ===
buy_levels = ["买一", "买二", "买三", "买四", "买五"]

# === 提取所有出现过的挂单价格（去重）
all_prices = set()
for level in buy_levels:
    price_col = f"{level}_价格"
    all_prices.update(df[price_col].dropna().unique())

all_prices = sorted(all_prices)
print(f"📈 出现过的挂单价格：{all_prices}")

# === 生成撤单记录 ===
records = []

for i in range(len(df) - 1):
    current = df.iloc[i]
    next_row = df.iloc[i + 1]
    
    for level in buy_levels:
        price_col = f"{level}_价格"
        vol_col = f"{level}_挂单手数"
        
        current_price = current.get(price_col)
        next_price = next_row.get(price_col)
        current_vol = current.get(vol_col)
        next_vol = next_row.get(vol_col)
        latest_price = next_row.get("最新成交价")

        if pd.isna(current_price) or current_price == 0:
            continue
        
        if current_price == next_price:
            delta_vol = next_vol - current_vol
            if delta_vol < 0 and abs(latest_price - current_price) > 1e-5:
                records.append({
                    "时间": next_row["时间"],
                    "价格": current_price,
                    "撤单量": abs(delta_vol)
                })

# === 转成DataFrame
cancel_df = pd.DataFrame(records)

if cancel_df.empty:
    print("⚠️ 没有检测到撤单记录！")
    sys.exit(0)

# === 如果只画最近5分钟
if ONLY_RECENT_MINUTES:
    latest_time = cancel_df["时间"].max()
    cutoff_time = latest_time - pd.Timedelta(minutes=RECENT_MINUTES)
    cancel_df = cancel_df[cancel_df["时间"] >= cutoff_time]
    print(f"✅ 只画最近 {RECENT_MINUTES} 分钟的数据")

# === 开始画图 ===
plt.figure(figsize=(14, 8))
scatter = plt.scatter(
    cancel_df["时间"],
    cancel_df["价格"],
    s=cancel_df["撤单量"],      # 点大小 = 撤单量
    c=cancel_df["撤单量"],      # 点颜色 = 撤单量
    cmap="coolwarm",
    alpha=0.7,
    edgecolors="k"
)

plt.colorbar(scatter, label="Cancelled Volume (Lots)")
plt.title(f"Order Cancellation Scatter Plot - {symbol} - {date_str}")
plt.xlabel("Time")
plt.ylabel("Price")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()