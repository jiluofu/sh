import akshare as ak
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor

# === 🧩 可配置项 ===
FUTURE_MINUTES = 60  # 👉 改这里，想预测未来几分钟都行

# === 1. 获取工商银行逐笔成交数据 ===
symbol = "sh601398" #工商银行
# symbol = "sh601988" #中国银行
# symbol = "sz002734" #利民股份
df = ak.stock_zh_a_tick_tx_js(symbol=symbol)
print(df.tail())

# === 2. 清洗 + 转换时间格式 ===
df["成交时间"] = pd.to_datetime(pd.Timestamp.now().date().strftime("%Y-%m-%d") + " " + df["成交时间"])
df.set_index("成交时间", inplace=True)

# === 3. 聚合为每分钟特征 ===
minute_df = df.resample("1min").agg({
    "成交价格": "mean",
    "成交量": "sum",
    "成交金额": "sum",
    "性质": lambda x: (x == "买盘").sum() / len(x) if len(x) > 0 else 0
}).dropna()

# === 4. 构造目标值：未来 N 分钟价格 ===
minute_df[f"未来{FUTURE_MINUTES}分钟价格"] = minute_df["成交价格"].shift(-FUTURE_MINUTES)
minute_df.dropna(inplace=True)

# === 5. 准备训练数据 ===
X = minute_df[["成交价格", "成交量", "成交金额", "性质"]]
y = minute_df[f"未来{FUTURE_MINUTES}分钟价格"]
X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

# === 6. 训练随机森林回归模型 ===
model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
model.fit(X_train, y_train)

# === 7. 用系统当前时间为参考进行预测 ===
current_time = pd.Timestamp.now().floor("min")
future_time = current_time + timedelta(minutes=FUTURE_MINUTES)

latest = minute_df.iloc[[-1]]  # 最新一分钟特征
current_price = latest["成交价格"].values[0]
predicted_price = model.predict(latest[["成交价格", "成交量", "成交金额", "性质"]])[0]

# === 8. 输出预测结果 ===
print(f"🕒 当前时间: {current_time}")
print(f"💰 当前价格: {current_price:.2f}")
print(f"🕒 预测未来时间: {future_time}")
print(f"📈 预测未来价格: {predicted_price:.2f}")