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

    df = df.rename(columns={"日期": "date", "开盘": "open", "最高": "high", "最低": "low", 
                            "收盘": "close", "成交量": "volume", "换手率": "turnover"})
    
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# ======================== 3. 计算技术指标 ========================
def compute_technical_indicators(df):
    """ 计算均线、MACD、RSI、KDJ、布林带等技术指标 """
    
    # # 移动均线（MA）
    # for period in [5, 10, 20, 60]:
    #     df[f"ma_{period}"] = df["close"].rolling(period).mean()
    
    # # 指数均线（EMA）
    # df["ema_12"] = df["close"].ewm(span=12).mean()
    # df["ema_26"] = df["close"].ewm(span=26).mean()
    
    # # MACD
    # df["macd"] = df["ema_12"] - df["ema_26"]
    
    # # RSI（相对强弱指数）
    # delta = df["close"].diff()
    # gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    # loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    # rs = gain / loss
    # df["rsi"] = 100 - (100 / (1 + rs))
    
    # # KDJ（随机指标）
    # low_min = df["low"].rolling(9).min()
    # high_max = df["high"].rolling(9).max()
    # df["kdj_k"] = 100 * (df["close"] - low_min) / (high_max - low_min)
    # df["kdj_d"] = df["kdj_k"].rolling(3).mean()
    # df["kdj_j"] = 3 * df["kdj_k"] - 2 * df["kdj_d"]
    
    # # 布林带（Bollinger Bands）
    # df["bollinger_mid"] = df["close"].rolling(20).mean()
    # df["bollinger_std"] = df["close"].rolling(20).std()
    # df["bollinger_upper"] = df["bollinger_mid"] + 2 * df["bollinger_std"]
    # df["bollinger_lower"] = df["bollinger_mid"] - 2 * df["bollinger_std"]
    
    return df

# ======================== 4. 生成特征和标签 ========================
def create_features(df, lookback_days):
    # feature_cols = ["open", "high", "low", "close", "volume", "turnover", 
    #                 "ma_5", "ma_10", "ma_20", "ma_60",
    #                 "ema_12", "ema_26", "macd", "rsi", "kdj_k", "kdj_d", "kdj_j",
    #                 "bollinger_upper", "bollinger_lower"]
    feature_cols = ["open", "high", "low", "close", "volume", "turnover"]                    
    
    X, y = [], []
    for i in range(len(df) - lookback_days):
        X.append(df[feature_cols].iloc[i : i + lookback_days].values.flatten())  
        y.append(df["close"].iloc[i + lookback_days])
    
    return np.array(X), np.array(y)

# ======================== 5. 预测函数 ========================
def forecast(stock_code, df):
    df = compute_technical_indicators(df)
    X, y = create_features(df, LOOKBACK_DAYS)
    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, objective="reg:squarederror")
    model.fit(X, y)

    last_window = X[-1].tolist()
    future_prices = [round(model.predict([last_window])[0], 3) for _ in range(N_DAYS)]

    last_price = df["close"].iloc[-1]
    last_predicted_price = future_prices[-1]
    price_change_percent = round(((last_predicted_price - last_price) / last_price) * 100, 2)

    # **打印每只股票预测结果**
    print(f"📊 预测结果 - {stock_code}")
    print(f" - 截止日价格: {last_price}")
    print(f" - 预测最后一天价格: {last_predicted_price}")
    print(f" - 预测涨幅: {price_change_percent:.2f}%\n")

    return pd.DataFrame({"股票代码": [stock_code], "截止日价格": [last_price], 
                         "预测最后一天价格": [last_predicted_price], "预测涨幅 (%)": [price_change_percent]})

# ======================== 6. 运行预测 ========================
all_results = []
for stock_code in STOCK_CODES:
    df = get_stock_data(stock_code)
    if df is None:
        continue
    all_results.append(forecast(stock_code, df))

# 保存预测结果
final_result_df = pd.concat(all_results).sort_values(by="预测涨幅 (%)", ascending=False)
final_result_df.to_csv("xgboost_forecast.csv", index=False, encoding="utf-8-sig")
print("✅ 预测完成，结果已保存到 xgboost_forecast.csv")