import akshare as ak
import pandas as pd

# 获取工商银行的最近1分钟K线数据（前复权）
df = ak.stock_zh_a_minute(symbol="sh601398", period="1", adjust="qfq")

# 转换时间字段
df["day"] = pd.to_datetime(df["day"])

# 过滤指定日期
target_date = pd.to_datetime("2025-04-10").date()
filtered_df = df[df["day"].dt.date == target_date]

# 保存为 CSV 文件
filtered_df.to_csv("sh601398_20250410_1min.csv", index=False, encoding="utf-8-sig")

print("✅ 已保存为 sh601398_20250410_1min.csv")