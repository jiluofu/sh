import numpy as np
import pandas as pd
import os
import akshare as ak
import xgboost as xgb
from datetime import datetime

# ======================== 配置 ========================
STOCK_CODES = ["600519", "000001"]  # 预测多个股票
START_DATE = "20180101"  # 历史数据起始日期
END_DATE = "20250227"  # 历史数据截止日期（最后一个训练数据点）
N_DAYS = 5  # 预测未来 N 个交易日的价格
LOOKBACK_DAYS = 365  # 过去多少天的数据作为输入窗口
use_akshare = False  # True: 使用 akshare 下载数据, False: 读取 data 目录下的 CSV 文件
data_dir = "data"  # 本地数据目录

# ======================== 1. 获取 A 股交易日历 ========================
china_trading_days = ak.tool_trade_date_hist_sina()
china_trading_days["trade_date"] = pd.to_datetime(china_trading_days["trade_date"].astype(str)).dt.strftime("%Y%m%d")

# 获取未来 N 个交易日的日期
future_dates = china_trading_days[china_trading_days["trade_date"] > END_DATE]["trade_date"].tolist()
future_dates = future_dates[:N_DAYS]  # 确保长度一致

print(f"📅 数据截止日期: {END_DATE}")
print(f"📅 预测目标日期: {future_dates[-1]}")  # 只显示预测的最后一天

# ======================== 2. 读取股票数据 ========================
def get_stock_data(stock_code):
    if use_akshare:
        print(f"📥 正在从 akshare 获取 {stock_code} 的数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=START_DATE, end_date=END_DATE, adjust="qfq")
    else:
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ 本地数据 {file_path} 不存在，跳过 {stock_code}。")
            return None
        print(f"📂 读取本地数据 {file_path}")
        df = pd.read_csv(file_path)

    if df.empty:
        print(f"❌ 无法获取 {stock_code} 的数据，跳过。")
        return None

    df = df.rename(columns={"日期": "date", "收盘": "close"})[["date", "close"]]
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 3. 生成特征和标签 ========================
def create_features(data, lookback_days):
    X, y = [], []
    for i in range(len(data) - lookback_days):
        X.append(data[i : i + lookback_days])  # 过去 lookback_days 天的数据
        y.append(data[i + lookback_days])  # 预测目标是未来一天的价格
    return np.array(X), np.array(y)

# ======================== 4. 预测函数 ========================
def forecast(stock_code, df, n_days, lookback_days, future_dates):
    """ 使用 XGBoost 训练模型并预测未来 n 天股价 """
    # 生成特征和标签
    X, y = create_features(df["close"].values, lookback_days)
    if len(X) < n_days:
        print(f"⚠️ {stock_code} 数据不足，无法预测未来 {n_days} 天，跳过。")
        return None

    # 拆分训练集和测试集
    X_train, X_test, y_train, y_test = X[:-n_days], X[-n_days:], y[:-n_days], y[-n_days:]

    # 训练 XGBoost
    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, objective="reg:squarederror")
    model.fit(X_train, y_train)

    # 评估模型
    y_pred = model.predict(X_test)
    mae = np.mean(np.abs(y_test - y_pred))
    rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
    print(f"📈 {stock_code} 训练完成：MAE = {mae:.2f}, RMSE = {rmse:.2f}")

    # 预测未来 n 天价格
    future_prices = []
    last_window = df["close"].values[-lookback_days:].tolist()  # 取最后 LOOKBACK_DAYS 天的数据

    for _ in range(n_days):
        next_price = model.predict([last_window])[0]  # 预测下一个交易日价格
        future_prices.append(round(next_price, 3))  # 预测价格保留 3 位小数
        last_window.pop(0)  # 滚动窗口：去掉最老的一天
        last_window.append(next_price)  # 加入预测的最新一天

    # 获取截止日期股价（**原始数据，不处理小数**）
    last_price = df.loc[df.index.max(), "close"]

    # 计算涨幅（针对最后一天的预测价格）
    last_predicted_price = future_prices[-1] if future_prices else None
    last_predicted_date = future_dates[-1] if future_dates else None
    price_change_percent = round(((last_predicted_price - last_price) / last_price) * 100, 2) if last_predicted_price else None

    # 打印关键数据
    print(f"📊 {stock_code} 预测数据")
    print(f" - 截止日期: {END_DATE}")
    print(f" - 截止日股价: {last_price}")  # **原始数据，不进行 round 处理**
    print(f" - 预测最后一天日期: {last_predicted_date}")
    print(f" - 预测最后一天价格: {last_predicted_price:.3f}")
    print(f" - 预测涨幅: {price_change_percent:.2f}%")

    return pd.DataFrame({
        "股票代码": [stock_code],
        "截止日价格": [last_price],
        "预测最后一天价格": [last_predicted_price],
        "预测涨幅": [price_change_percent]
    })

# ======================== 5. 运行预测 ========================
all_results = []

STOCK_CODES = ["603165", "601002", "601882", "002533", "600218", "000581", "002939", "002768", "603115"]

for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue  # 跳过数据缺失的股票

    result_df = forecast(stock_code, df, N_DAYS, LOOKBACK_DAYS, future_dates)
    if result_df is not None:
        all_results.append(result_df)

# ======================== 6. 保存所有股票预测结果 ========================
if all_results:
    final_result_df = pd.concat(all_results, ignore_index=True)

    # 计算涨幅百分比，并按降序排序
    final_result_df["预测涨幅 (%)"] = ((final_result_df["预测最后一天价格"] - final_result_df["截止日价格"]) / final_result_df["截止日价格"]) * 100
    final_result_df["预测涨幅 (%)"] = final_result_df["预测涨幅 (%)"].round(3)  # 保留三位小数

    # 按预测涨幅降序排序
    final_result_df = final_result_df.sort_values(by="预测涨幅 (%)", ascending=False)

    # 仅保留必要列
    final_result_df = final_result_df[["股票代码", "截止日价格", "预测最后一天价格", "预测涨幅 (%)"]]

    final_result_df.to_csv("xgboost_forecast.csv", index=False, encoding="utf-8-sig")
    print("\n✅ 预测完成，所有股票的预测结果已保存到 xgboost_forecast.csv（按预测涨幅降序排列）")
else:
    print("\n⚠️ 没有可用的预测结果，请检查数据源。")