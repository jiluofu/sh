import numpy as np
import pandas as pd
import os
import akshare as ak
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

data_dir = "data"

# 开关：是否从 AkShare 在线获取数据
use_akshare = False  # True 使用在线数据, False 使用本地 CSV

# 配置开始和结束日期
START_DATE = "20240101"
END_DATE = "20250225"

NUM_DAYS = 5

# 获取 A 股主板深市和沪市所有股票代码（去掉创业板）
def get_main_board_stocks():
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]["code"].tolist()
    return main_board_stocks

def process_stock_data(stock_code, df, num_days=NUM_DAYS):
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

    # 检查数据是否足够
    lookback = 60
    if len(df_scaled) - lookback - num_days <= 0:
        print(f"⚠️ {stock_code} 数据不足（仅 {len(df_scaled)} 条），跳过训练。")
        return None

    # 生成 XGBoost 训练数据
    X, y = [], []
    lookback = 60
    for i in range(len(df_scaled) - lookback - num_days):
        X.append(df_scaled[i:i + lookback].flatten())
        y.append(df_scaled[i + lookback + num_days - 1])
    X, y = np.array(X), np.array(y)

    # 拆分训练和测试数据
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 构建 XGBoost 模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.05, max_depth=5)
    model.fit(X_train, y_train)

    # 预测
    last_lookback = df_scaled[-lookback:].flatten().reshape(1, -1)
    predicted_scaled = model.predict(last_lookback)
    predicted_price = scaler.inverse_transform(predicted_scaled.reshape(-1, 1))[0, 0]
    price_mean = float(f"{np.mean(predicted_price):.3f}")

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

# stock_codes = ["000892","002501","000529","002298","000868","603316","000816","600810","603389","002097"]
# stock_codes = ["000892","002501","000529","002298","000868","603316","000816","600810","603389","002097","600203","600126","600355","600246","002580","000096","603166","002910","002058","603085","600302","002931","000801","002369","603040","600446","600996","603421","603991","603626","603429","002031","603949","603109","000880","603956","002889","603997","000528","603278","603915","002824","000536","601113","002765","600589","000573","600280","002323","600322","002896","000679","600225","000980","002034","600841","600458","600539","600602","603319","002222","002184","603667","603392","603236","603121","000887","600491","001223","600052","603013","002514","000815","603150","000066","002937","603189","603004","002403","000777","601777","002989","000710","603822","603218","603819","603583","000622","000811","002289","002490","002970","600592","002750","002569","603690","600289","002733","600608","600165","002838","603727","600965","600301","002855","002176","002474","002990","603992","002387","603360","002025","002392","603086","002536","001301","002698","603799","600114","603197","603101","601956","600130","002693","001228","600933","001207","603310","601033","000506","002456","002570","002938","002194","601231","600568","002642","603108","600611","603758","600808","002334","002183","002080","600168","000837","600689","002647","603895","002212","603958","603118","600360","002167","600650","603596","002345","002881","601127","600506","002361","600272","000004","002582","002253","600729","603286","603559","002685","601882","002903","000782","002442","603158","603298","601799","001319","002848","002380","002553","603009","000826","002592","603031","600438","601865","002324","000908","002487","002760","600686","603082","000779","603828","002165","002475","002173","002745","002101","002046","002454","603041","603375","002650","002139","002869","000759","603898","603055","002842","600337","603116","002123","000158","600694","600156","000838","601798","600481","002283","603586","600651","002792","600895","002329","002326","000678","002789","603306","002975","603217","600882","603665","001216","603072","603163","002202","603929","603659","000762","002813","600353","002446","002211","002689","603220","002232","600866","002703","002865","601086","600580","603283","002119","002906","600510","603668","000605","002779","600805","600736","603348","002921","002169","603728","603416","002248","002947","002512","603813","600761","002496","600418","002967","000425","603203","002766","603950","001270","600552","001208","002527","603297","601200","000572","002719","002863","000672","002129","002102","001318","002544","002079","002823","002384","603322","002526","600735","002351","002706","603033","001283","002254","002434","002979","002755","603216","002506","002822","002875","002306","002189","600847","600340","002355","002338","600814","603193","603048","001212","603214","002321","002227","002416","600815","600190","002284","600191","000410","603960","002708","002410","002354","603590","002620","603803","603901","600562","600654","002531","000338","002026","002418","000656","600641","000049","603036","603032","603806","600784","000676","601311","002664","002199","002893","600243","002050","603920","002660","002111","601002","603100","002241","002122","002405","603068","002272","000893","601965","002667","002920","603810","600110","603098","600288","603666","600676","002853","603386","002459","600419","002549","600120","603171","600741","002547","600863","600774","002762","001331","603051","002634","601136","600188","002339","603615","002862","000155","603351","002952","603679","603327"]
# 获取主板股票代码
stock_codes = get_main_board_stocks()


# 存储结果的数据框
results = []

# 存储建仓结果的数据框
results_build = []

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
    
    result = process_stock_data(stock_code, df)
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
results_df.to_csv("predicted_prices_xgboost.csv", index=False, encoding='utf-8-sig')
print("✅ 预测结果已保存到 predicted_prices_xgboost.csv，并按变化百分比排序")

# 提取所有预测比昨日收盘价变化大于 1% 的股票代码并保存到 txt 文件（双引号，逗号分隔）
with open("filtered_stocks_xgboost.txt", "w", encoding="utf-8") as f:
    f.write(",".join([f'"{stock}"' for stock in filtered_stocks["股票代码"].tolist()]))

print("✅ 预测比昨日收盘价变化大于 1% 的股票代码已保存到 filtered_stocks_xgboost.txt，格式为双引号包围，逗号分隔")

# 输出符合条件的股票
results_build_df = pd.DataFrame(results_build, columns=["股票代码", "预测价格", "预测比昨日收盘价变化%", "状态"])
status_order = {"完成建仓，进入拉升": 1, "进入拉升": 2, "完成建仓": 3, "无明显信号": 4}
results_build_df["排序顺序"] = results_build_df["状态"].map(status_order)
results_build_df.sort_values(by=["排序顺序", "股票代码"], ascending=[True, True], inplace=True)
results_build_df.drop(columns=["排序顺序"], inplace=True)
results_build_df.to_csv("rally_stocks_xgboost.csv", index=False, encoding="utf-8-sig")

print("✅ 分析完成，结果已保存到 rally_stocks_xgboost.csv")
