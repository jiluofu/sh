import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime

# === 配置 ===
symbol = "601398"  # 默认股票代码
# symbol = "601988"  # 默认股票代码

# === 解析命令行参数 ===
if len(sys.argv) >= 2:
    date_str = sys.argv[1]  # 传入日期，比如 20250422
else:
    date_str = datetime.today().strftime("%Y%m%d")  # 默认今天

# === 文件路径 ===
file_path = os.path.join("real", symbol, f"{date_str}.csv")

# === 检查文件是否存在 ===
if not os.path.exists(file_path):
    print(f"❌ 文件不存在: {file_path}")
    sys.exit()

# === 读入数据 ===
df = pd.read_csv(file_path)

# 检查必要列
if not {"成交时间", "成交价格"}.issubset(df.columns):
    print("❌ 缺少成交时间或成交价格列")
    sys.exit()

# === 转换时间列 ===
try:
    df["成交时间"] = pd.to_datetime(df["成交时间"], format="%H:%M:%S")
except Exception as e:
    print(f"⚠️ 时间列转换出错: {e}")
    sys.exit()

# === 开始画图 ===
plt.figure(figsize=(14, 8))
plt.plot(df["成交时间"], df["成交价格"], marker='o', markersize=2, linestyle='-')

plt.title(f"Stock {symbol} - {date_str} Intraday Price")
plt.xlabel("Time")
plt.ylabel("Price")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()