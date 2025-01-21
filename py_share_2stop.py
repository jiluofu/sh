import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from io import StringIO

def analyze_below_trend_batches(stock_data, stock_code, max_point, min_point, degree=3):
    """
    分析股票数据中连续低于多项式拟合趋势线的批次。

    参数:
    - stock_data: DataFrame，股票数据，必须包含 '日期' 和 '收盘' 列。
    - stock_code: str，股票代码，用于保存文件名。
    - max_point: float，最高点价格。
    - min_point: float，最低点价格。
    - degree: int，多项式的阶数，默认值为3。

    返回:
    - List[Tuple[int, DataFrame]]: 包含批次ID和对应数据的列表。
    """
    # 转换日期为时间索引
    stock_data["日期"] = pd.to_datetime(stock_data["日期"])
    x = np.arange(len(stock_data))  # 时间索引
    y = stock_data["收盘"].values

    # 检查数据点完整性
    if np.any(np.isnan(y)) or np.any(np.isinf(y)):
        print("输入数据包含 NaN 或 Inf 值，跳过分析。")
        return []

    if len(x) < degree + 1:
        print(f"数据点不足以支持 {degree} 阶多项式拟合，跳过分析。")
        return []

    # 多项式拟合
    try:
        coeffs = np.polyfit(x, y, degree)
        trendline = np.polyval(coeffs, x)
    except np.linalg.LinAlgError:
        print("警告：SVD 未收敛，跳过当前分析。")
        return []

    # 计算偏差
    deviations = y - trendline  # 收盘价与趋势线的差值
    below_trend = deviations < 0  # 是否低于趋势线

    # 标记连续低于趋势线的天数
    batch_id = 0
    batches = []
    current_batch = []

    for i, below in enumerate(below_trend):
        if below:  # 低于趋势线
            current_batch.append(stock_data.iloc[i])
        elif current_batch:  # 结束当前批次
            if len(current_batch) >= 4:  # 确保连续天数大于等于4天
                batch_id += 1
                batches.append((batch_id, pd.DataFrame(current_batch)))
            current_batch = []

    # 检查最后一个批次
    if current_batch and len(current_batch) >= 4:
        batch_id += 1
        batches.append((batch_id, pd.DataFrame(current_batch)))

    # 检查批次是否超出 max_point 和 min_point 范围
    valid_batches = []
    for batch_id, batch_data in batches:
        if (batch_data["收盘"].max() <= max_point * 1.02) and (batch_data["收盘"].min() >= min_point * 0.98):
            valid_batches.append((batch_id, batch_data))

    # 计算新增变量
    if len(valid_batches) >= 2:
        first_batch = valid_batches[0][1]
        second_batch = valid_batches[1][1]

        days_2_to_1 = (first_batch["日期"].iloc[0] - stock_data["日期"].iloc[0]).days
        days_between_batches = (second_batch["日期"].iloc[0] - first_batch["日期"].iloc[-1]).days
    else:
        days_2_to_1 = 0
        days_between_batches = 0

    print(f"days_2_to_1: {days_2_to_1}, days_between_batches: {days_between_batches}")

    if days_2_to_1 <= 2 and days_between_batches <= 4:
        # 可视化
        if len(valid_batches) >= 2:
            plt.figure(figsize=(12, 6))
            plt.plot(stock_data["日期"], stock_data["收盘"], label="实际收盘价", color="blue", marker="o")
            plt.plot(stock_data["日期"], trendline, label=f"{degree}阶多项式拟合", color="orange", linestyle="--")

            # 标注低于趋势线的批次
            for _, batch_data in valid_batches:
                plt.scatter(batch_data["日期"], batch_data["收盘"], label="低于趋势线", color="red", zorder=5)

            # 图表设置
            plt.title(f"{stock_code} 连续低于趋势线的批次")
            plt.xlabel("日期")
            plt.ylabel("收盘价")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            # 保存图表
            pic_filename = f'./pic/{stock_code}_below_trend_batches.png'
            plt.savefig(pic_filename)
            print(f"图表已保存到 {pic_filename}")

            # plt.show()

    return valid_batches

def find_2high(stock_data, stock_code, start_date, end_date):
    """
    查找股票数据中指定日期范围内连续两天涨停的情况，分批次返回，并绘制结果。
    - 连续两天涨停加入同一个批次。
    - 如果出现不连续的天数，则新建一个批次。

    参数:
    - stock_data: DataFrame，包含股票日线数据，需包含 '日期'、'涨跌幅'、'收盘' 和 '开盘' 列。
    - stock_code: str，股票代码，用于文件命名。
    - start_date: str，开始日期（格式 'YYYY-MM-DD'）。
    - end_date: str，结束日期（格式 'YYYY-MM-DD'）。

    返回:
    - List[List[dict]]: 每批次的连续两天涨停数据，格式为 [{日期, 收盘价, 涨跌幅, 开盘价}, ...]。
    """
    # 筛选日期范围内的数据
    stock_data['日期'] = pd.to_datetime(stock_data['日期'])
    filtered_data = stock_data[(stock_data['日期'] >= start_date) & (stock_data['日期'] <= end_date)]

    if filtered_data.empty:
        print("指定日期范围内无数据。")
        return []

    # 初始化结果列表
    results = []
    batch = []

    # 遍历筛选后的数据，查找连续两天涨停
    for i in range(1, len(filtered_data)):
        today = filtered_data.iloc[i]
        yesterday = filtered_data.iloc[i - 1]

        # 检查连续两天涨停条件（涨跌幅 >= 9.9%）
        if yesterday['涨跌幅'] >= 9.9 and today['涨跌幅'] >= 9.9:
            if not batch:
                batch.append({'日期': yesterday['日期'], '收盘价': yesterday['收盘'], '开盘价': yesterday['开盘'], '涨跌幅': yesterday['涨跌幅']})
            batch.append({'日期': today['日期'], '收盘价': today['收盘'], '开盘价': today['开盘'], '涨跌幅': today['涨跌幅']})
        else:
            if batch:
                results.append(batch)
                batch = []

    # 如果最后一批次未存入结果，补充存储
    if batch:
        results.append(batch)

    # 创建保存图片的目录
    os.makedirs('./pic', exist_ok=True)

    # 绘制结果
    for i, batch in enumerate(results, start=1):
        print(f"批次 {i}:")
        for entry in batch:
            print(f"  日期: {entry['日期']}, 收盘价: {entry['收盘价']}, 开盘价: {entry['开盘价']}, 涨跌幅: {entry['涨跌幅']}%")

        # 获取批次中的日期范围
        batch_dates = [entry['日期'] for entry in batch]
        batch_data = filtered_data[filtered_data['日期'].isin(batch_dates)]

        # # 绘制图表
        # plt.figure(figsize=(12, 6))
        # plt.plot(filtered_data['日期'], filtered_data['收盘'], label='收盘价', color='blue', alpha=0.5)
        # plt.scatter(batch_data['日期'], batch_data['收盘'], color='red', label='连续涨停点', zorder=5)

        # plt.title(f"{stock_code} 批次 {i} 连续涨停点")
        # plt.xlabel("日期")
        # plt.ylabel("价格")
        # plt.grid(True)
        # plt.legend()
        # plt.tight_layout()

        # # 保存图表
        # pic_filename = f"./pic/{stock_code}_batch_{i}_{start_date}_to_{end_date}.png"
        # plt.savefig(pic_filename)
        # print(f"图表已保存到 {pic_filename}")

        # plt.close()

    return results

def process_all_batches(find_2high_results, stock_data, stock_code):
    """
    遍历 find_2high 返回的所有批次数据，获取每个批次中第一个元素，
    并从 stock_data 中提取涨停点下一天开始到结束的数据以传递给 analyze_below_trend_batches。

    返回:
    - bool: 如果至少一个批次返回的分析结果大于等于 2，则返回 True；否则返回 False。

    参数:
    - find_2high_results: List[DataFrame or list]，find_2high 返回的所有批次数据。
    - stock_data: DataFrame，包含完整的股票数据。
    - stock_code: str，股票代码，用于分析和文件命名。
    """
    if not find_2high_results:
        print("没有批次数据。")
        return False

    print(f"共找到 {len(find_2high_results)} 个批次数据。")

    has_valid_batches = False

    for i, batch in enumerate(find_2high_results, start=1):
        print(f"\n处理批次 {i}:")

        # 如果批次是 list，将其转换为 DataFrame
        if isinstance(batch, list):
            batch = pd.DataFrame(batch)

        # 检查批次是否为空
        if batch.empty:
            print(f"批次 {i} 数据为空，跳过。")
            continue

        # 打印批次列名（调试用）
        print(f"批次 {i} 列名: {batch.columns.tolist()}")

        # 检查并统一列名（根据实际数据列名调整）
        column_mapping = {
            'date': '日期',
            'close': '收盘',
            'change': '涨跌幅'
        }
        batch.rename(columns=column_mapping, inplace=True)

        if '日期' not in batch.columns:
            print(f"批次 {i} 列名不符合预期，跳过。")
            continue

        # 获取第一个元素的日期
        start_date = pd.to_datetime(batch.iloc[0]['日期'])

        # 获取涨停点的下一天日期
        next_day_index = stock_data[stock_data['日期'] == start_date].index + 1
        if next_day_index.empty or next_day_index[0] >= len(stock_data):
            print(f"批次 {i}: 涨停点下一天的数据不存在，跳过。")
            continue

        next_day_date = stock_data.iloc[next_day_index[0]]['日期']

        # 提取 stock_data 中从 next_day_date 到结束的数据
        filtered_stock_data = stock_data[stock_data['日期'] >= next_day_date]

        if filtered_stock_data.empty:
            print(f"批次 {i}: 从日期 {next_day_date} 开始未找到相关数据，跳过。")
            continue

        # 打印提取的数据（调试用）
        print(f"批次 {i} 提取数据行数: {len(filtered_stock_data)}")

        # 计算 max_point 和 min_point
        max_point = batch['收盘价'].iloc[-1]  # 最新涨停的收盘价
        min_point = batch['开盘价'].iloc[0]  # 第一个涨停的开盘价
        print(f"批次 {i}: max_point = {max_point}, min_point = {min_point}")

        # 调用 analyze_below_trend_batches
        batch_result = analyze_below_trend_batches(filtered_stock_data, stock_code, max_point, min_point)

        # 判断返回结果
        if len(batch_result) >= 2:
            print(f"批次 {i} 的分析结果 >= 2，满足条件。")
            has_valid_batches = True
        else:
            print(f"批次 {i} 的分析结果 < 2，不满足条件。")

    return has_valid_batches

# # 读取CSV文件
# stock_code = "000006"
# file_path = f"./data/{stock_code}.csv"
# stock_data = pd.read_csv(file_path)

# # 调用函数寻找关键点
# result = find_2high(stock_data, stock_code, start_date='2024-09-26', end_date='2024-12-27')
# process_all_batches(result, stock_data, stock_code)



# 遍历data目录下所有股票数据文件，执行find_key_points
data_directory = './data'  # 假设所有CSV文件保存在data文件夹下

# 获取所有CSV文件名
stock_files = [f for f in os.listdir(data_directory) if f.endswith('.csv')]

# 遍历所有CSV文件，执行find_key_points
for stock_file in stock_files:
    stock_code = stock_file.split('.')[0]  # 获取股票代码
    file_path = os.path.join(data_directory, stock_file)
    
    # 读取股票数据
    stock_data = pd.read_csv(file_path)

    # 跳过以688、300开头以及包含"st"的股票代码（不区分大小写）
    if stock_code.startswith("688") or stock_code.startswith("300") or "st" in stock_code.lower():
        print(f"股票代码 {stock_code} 被排除（688、300开头或包含st）。")
        continue

    # 检查是否有"流通盘"列并过滤掉流通盘大于50亿的股票
    if "流通盘" in stock_data.columns:
        circulating_shares = stock_data["流通盘"].iloc[0]  # 假设流通盘信息在第一行
        if circulating_shares > 50_000_000_000:  # 50 亿
            print(f"股票代码 {stock_code} 被排除（流通盘大于50亿）。")
            continue
    
    # 调用find_key_points函数，返回结果
    result = find_2high(stock_data, stock_code, start_date='2024-09-01', end_date='2024-12-27')
    process_all_batches(result, stock_data, stock_code)
    