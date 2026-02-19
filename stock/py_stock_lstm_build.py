import numpy as np
import pandas as pd
import os
import akshare as ak
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler

data_dir = "data"

# 开关：是否从 AkShare 在线获取数据
use_akshare = False  # True 使用在线数据, False 使用本地 CSV

# 配置开始和结束日期
START_DATE = "20240101"
END_DATE = "20250225"

NUM_DAYS = 5

# ✅ 在循环外创建模型
LOOKBACK = 60

# 获取 A 股主板深市和沪市所有股票代码（去掉创业板）
def get_main_board_stocks():
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]["code"].tolist()
    return main_board_stocks

def build_lstm_model(lookback, num_days=NUM_DAYS):
    """
    构建并返回 LSTM 模型
    """
    model = Sequential([
        Input(shape=(lookback, 1)),  # 避免 UserWarning
        LSTM(50, return_sequences=True),
        LSTM(50, return_sequences=False),
        Dense(num_days)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def process_stock_data(stock_code, df, model, lookback=LOOKBACK, num_days=NUM_DAYS):
    """
    处理单个股票的数据并进行蒙特卡洛模拟预测
    :param stock_code: 股票代码
    :param df: 股票数据 DataFrame
    :param num_simulations: 蒙特卡洛模拟次数
    :param num_days: 预测天数
    :return: 预测结果列表
    """
    if df.empty:
        print(f"❌ 未能获取 {stock_code} 的数据，请检查代码是否正确！")
        return None
    
    df = df.copy()
    # 处理数据（确保列名正确）
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"])
        df.set_index("日期", inplace=True)
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    else:
        print(f"❌ 数据 {stock_code} 中没有找到 '日期' 或 'date' 列，请检查数据格式！")
        return None

    # 提取收盘价
    if "收盘" in df.columns:
        df = df[["收盘"]]
    elif "close" in df.columns:
        df = df[["close"]]
    else:
        print(f"❌ 数据 {stock_code} 中没有找到 '收盘' 或 'close' 列，请检查数据格式！")
        return None

    # 归一化数据
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_scaled = scaler.fit_transform(df)

    # ✅ 确保数据量足够
    if len(df_scaled) < LOOKBACK + NUM_DAYS + 1:
        print(f"⚠️ {stock_code} 数据不足，跳过")
        return None

    # 生成 LSTM 训练数据
    X, y = [], []

    for i in range(len(df_scaled) - lookback - num_days):
        X.append(df_scaled[i:i + lookback])
        y.append(df_scaled[i + lookback:i + lookback + num_days])
    X, y = np.array(X), np.array(y)

    # # 构建 LSTM 模型
    # model = Sequential([
    #     Input(shape=(lookback, 1)),  # 使用 Input 代替 input_shape
    #     LSTM(50, return_sequences=True),
    #     LSTM(50, return_sequences=False),
    #     Dense(num_days)
    # ])
    # model.compile(optimizer='adam', loss='mean_squared_error')

    # 训练模型
    model.fit(X, y, epochs=20, batch_size=16, verbose=0)

    # ✅ 预测，避免重复创建 `@tf.function`
    @tf.function(reduce_retracing=True)  # 避免 retracing
    def predict_price(model, last_lookback):
        return model.predict(last_lookback)

    # 预测
    last_lookback = df_scaled[-lookback:].reshape(1, lookback, 1)
    predicted_scaled = model.predict(last_lookback)
    predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(-1, 1))
    price_mean = float(f"{np.mean(predicted_prices):.3f}")

    # 获取昨日收盘价
    yesterday_price = df.iloc[-2, 0] if len(df) > 1 else None

    # 计算预测价格相对于昨日收盘价的涨幅
    increase_percent = round(((price_mean - yesterday_price) / yesterday_price) * 100, 2) if yesterday_price else None

    print(f"{stock_code} 未来 {num_days} 天股价预测区间：")
    print(f" - 预测均值: {price_mean}")
    print(f" - 昨日收盘价: {yesterday_price}")
    print(f" - 预测比昨日收盘价变化百分比: {increase_percent}%")

    # 存储结果
    return [stock_code, price_mean, yesterday_price, increase_percent]

def analyze_stock_phase(stock_code, df, predicted_price, increase_percent):

    if increase_percent <= 0:
        return None
        
    if df.empty:
        print(f"❌ 未能获取 {stock_code} 的数据")
        return stock_code, "数据缺失"
    
    df.rename(columns={"日期": "date", "收盘": "close", "成交量": "volume", "换手率": "turnover"}, inplace=True)
    # df["date"] = pd.to_datetime(df["date"])
    # df.set_index("date", inplace=True)
    
    # 计算 60 日均线
    df["ma60"] = df["close"].rolling(window=60).mean()
    
    # 计算成交量均线（判断是否放量）
    df["vol_ma20"] = df["volume"].rolling(window=20).mean()
    
    # 计算换手率均线
    df["turnover_ma20"] = df["turnover"].rolling(window=20).mean()
    
    # **判断是否完成建仓**
    last_60 = df.iloc[-60:]  # 取最近 60 天数据
    low_volatility = last_60["close"].std() / last_60["close"].mean() < 0.05  # 低波动性
    moderate_volume = (last_60["volume"] > last_60["vol_ma20"] * 0.8).sum() > 30  # 震荡吸筹
    stable_turnover = (last_60["turnover"] < last_60["turnover_ma20"] * 1.2).sum() > 30  # 低换手
    
    completed_accumulation = low_volatility and moderate_volume and stable_turnover
    
    # **判断是否进入拉升**
    last_5 = df.iloc[-5:]  # 取最近 5 天数据
    breakout = (last_5["close"] > last_5["ma60"]).sum() > 3  # 连续突破 60 日均线
    high_volume = (last_5["volume"] > last_5["vol_ma20"] * 1.5).sum() > 2  # 放量
    strong_turnover = (last_5["turnover"] > last_5["turnover_ma20"] * 1.5).sum() > 3  # 换手率显著上升
    
    entering_rally = breakout and high_volume and strong_turnover
    
    # **如果满足条件，记录股票**
    if completed_accumulation and entering_rally:
        return [stock_code, predicted_price, increase_percent, "完成建仓，进入拉升"]
    elif completed_accumulation:
        return [stock_code, predicted_price, increase_percent, "完成建仓"]
    elif entering_rally:
        return [stock_code, predicted_price, increase_percent, "进入拉升"]
    else:
        return None


stock_codes = ["000892","002501","000529","002298","000868","603316","000816","600810","603389"]
# 获取主板股票代码
stock_codes = get_main_board_stocks()

# 存储结果的数据框
results = []

# 存储建仓结果的数据框
results_build = []


model = build_lstm_model(LOOKBACK, num_days=NUM_DAYS)

for stock_code in stock_codes:
    if use_akshare:
        print(f"🔄 正在从 AkShare 获取 {stock_code} 的数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=START_DATE, end_date=END_DATE, adjust="qfq")
    else:
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        if not os.path.exists(file_path):
            print(f"❌ 文件 {file_path} 不存在，请检查路径！")
            continue
        df = pd.read_csv(file_path)
    
    result = process_stock_data(stock_code, df, model)
    if result:
        results.append(result)
        result_build = analyze_stock_phase(stock_code, df, result[1], result[3])
        if result_build:
            results_build.append(result_build)

# 转换为 DataFrame 并排序
results_df = pd.DataFrame(results, columns=["股票代码", "预测价格", "昨日收盘价", "预测比昨日收盘价变化%"])
results_df.sort_values(by="预测比昨日收盘价变化%", ascending=False, inplace=True)

# 过滤出预测比昨日收盘价变化超过 1% 的股票
filtered_stocks = results_df[results_df["预测比昨日收盘价变化%"] > 1]

# 保存预测结果
results_df.to_csv("predicted_prices_lstm.csv", index=False, encoding='utf-8-sig')
print("✅ 预测结果已保存到 predicted_prices_lstm.csv，并按变化百分比排序")

# 提取所有预测比昨日收盘价变化大于 1% 的股票代码并保存到 txt 文件（双引号，逗号分隔）
with open("filtered_stocks_lstm.txt", "w", encoding="utf-8") as f:
    f.write(",".join([f'"{stock}"' for stock in filtered_stocks["股票代码"].tolist()]))

print("✅ 预测比昨日收盘价变化大于 1% 的股票代码已保存到 filtered_stocks_lstm.txt，格式为双引号包围，逗号分隔")

# 输出符合条件的股票
results_build_df = pd.DataFrame(results_build, columns=["股票代码", "预测价格", "预测比昨日收盘价变化%", "状态"])
status_order = {"完成建仓，进入拉升": 1, "进入拉升": 2, "完成建仓": 3, "无明显信号": 3}
results_build_df["排序顺序"] = results_build_df["状态"].map(status_order)
results_build_df.sort_values(by=["排序顺序", "股票代码"], ascending=[True, True], inplace=True)
results_build_df.drop(columns=["排序顺序"], inplace=True)
results_build_df.to_csv("rally_stocks_lstm.csv", index=False, encoding="utf-8-sig")

print("✅ 分析完成，结果已保存到 rally_stocks_lstm.csv")
