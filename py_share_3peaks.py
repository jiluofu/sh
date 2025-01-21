import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def find_peaks(stock_data, stock_code, window=1):
    """
    找到股票数据中的所有波峰和波谷点，并返回仅包含波峰和波谷点的stock_data，同时生成两张波浪图。

    参数:
    - stock_data: DataFrame，包含股票历史数据。
    - stock_code: 股票代码，用于命名图表文件。
    - window: 滑动窗口大小，用于寻找高低点，默认值为1。

    返回:
    - reduced_stock_data: DataFrame，仅包含波峰和波谷点的数据。
    """
    # 清理列名
    stock_data.columns = stock_data.columns.str.strip()

    # 转换日期列为标准时间格式
    stock_data['日期'] = pd.to_datetime(stock_data['日期'], errors='coerce')
    stock_data.sort_values('日期', inplace=True)

    # 定义存储波峰和波谷的列表
    peaks_dates = []
    peaks = []  # 用于存储打印的波峰波谷信息

    # 定义条件检查函数
    def is_peak_or_trough(current_price, prev_prices, next_prices, peak=True):
        """
        判断当前点是否是波峰或波谷。
        """
        if peak:
            return current_price > prev_prices.max() and current_price > next_prices.max()
        else:
            return current_price < prev_prices.min() and current_price < next_prices.min()

    # 遍历数据寻找波浪点
    for i in range(window, len(stock_data) - window):
        current_row = stock_data.iloc[i]
        date = current_row['日期']
        price = current_row['收盘']

        # 获取滑动窗口内的前后价格
        prev_prices = stock_data.iloc[i-window:i]['收盘']
        next_prices = stock_data.iloc[i+1:i+window+1]['收盘']

        # 判断是否是波峰
        if is_peak_or_trough(price, prev_prices, next_prices, peak=True):
            peaks_dates.append(date)
            peaks.append({'类型': '波峰', '日期': date, '价格': price})

        # 判断是否是波谷
        if is_peak_or_trough(price, prev_prices, next_prices, peak=False):
            peaks_dates.append(date)
            peaks.append({'类型': '波谷', '日期': date, '价格': price})

    # # 打印波峰和波谷
    # print("\n找到的波浪点：")
    # for peak in peaks:
    #     print(f"{peak['类型']} - 日期: {peak['日期']}, 价格: {peak['价格']}")

    # 根据波浪点的日期保留原始数据中的相关行
    reduced_stock_data = stock_data[stock_data['日期'].isin(peaks_dates)].reset_index(drop=True)

    # # 打印保留的波浪点数据
    # print("\n保留的波浪点数据：")
    # print(reduced_stock_data)

    # # 绘制波浪图（原始数据）
    # plt.figure(figsize=(12, 6))
    # plt.plot(stock_data['日期'], stock_data['收盘'], label='收盘价', color='blue')
    # for peak in peaks:
    #     color = 'red' if peak['类型'] == '波峰' else 'green'
    #     plt.scatter(peak['日期'], peak['价格'], color=color, label=f"{peak['类型']} ({peak['价格']:.2f})", zorder=5)

    # # 图表设置
    # plt.title(f"股票波浪点分析（原始数据） - {stock_code}")
    # plt.xlabel("日期")
    # plt.ylabel("收盘价")
    # plt.legend(loc="best")
    # plt.grid(True)
    # plt.tight_layout()

    # # 保存图表
    # original_pic_filename = f'./pic/{stock_code}_original_peaks_and_troughs.png'
    # plt.savefig(original_pic_filename)
    # print(f"原始数据图表已保存到 {original_pic_filename}")

    # # 显示图表
    # plt.show()

    # # 绘制波浪图（仅波峰和波谷数据）
    # plt.figure(figsize=(12, 6))
    # plt.plot(reduced_stock_data['日期'], reduced_stock_data['收盘'], label='波浪点收盘价', color='blue', marker='o')
    # for _, row in reduced_stock_data.iterrows():
    #     color = 'red' if row['收盘'] == reduced_stock_data['收盘'].max() else 'green'
    #     plt.scatter(row['日期'], row['收盘'], color=color, label=f"{row['日期']} ({row['收盘']:.2f})", zorder=5)

    # # 图表设置
    # plt.title(f"股票波浪点分析（仅波峰和波谷数据） - {stock_code}")
    # plt.xlabel("日期")
    # plt.ylabel("收盘价")
    # plt.legend(loc="best")
    # plt.grid(True)
    # plt.tight_layout()

    # # 保存图表
    # reduced_pic_filename = f'./pic/{stock_code}_reduced_peaks_and_troughs.png'
    # plt.savefig(reduced_pic_filename)
    # print(f"仅波浪点数据图表已保存到 {reduced_pic_filename}")

    # # 显示图表
    # plt.show()

    return reduced_stock_data

def find_three_waves(stock_data, stock_code, h1, l1, h2, l2, h3, window=5):
    """
    函数用于在股票数据中查找符合三浪形态的波浪点，并绘制波浪走势图。
    
    参数:
    - stock_data: DataFrame，股票历史数据。
    - stock_code: 股票代码，用于命名图表文件。
    - h1: 第1个高点相对最低点的最小涨幅百分比。
    - l1: 第1个低点相对于H1的最小跌幅百分比。
    - h2: 第2个高点相对最低点的最小涨幅百分比，且不能超过H1。
    - l2: 第2个低点相对于H2的最小跌幅百分比。
    - h3: 第3个高点相对最低点的最小涨幅百分比。
    - window: 滑动窗口大小，用于寻找高低点，默认值为5。

    返回:
    - bool: 如果找到符合形态的三浪走势，返回 True；否则返回 False。
    """
    # 清理列名
    stock_data.columns = stock_data.columns.str.strip()

    # 转换日期列为标准时间格式
    stock_data['日期'] = pd.to_datetime(stock_data['日期'], errors='coerce')
    stock_data.sort_values('日期', inplace=True)

    # 找最低点
    min_price = stock_data['最低'].min()
    min_date = stock_data.loc[stock_data['最低'].idxmin(), '日期']
    print(f"最低点 - 日期: {min_date}, 价格: {min_price}")

    data_after_min = stock_data[stock_data['日期'] >= min_date]
    waves = [{'类型': '最低点', '日期': min_date, '价格': min_price}]

    # 初始化变量
    h1_found, l1_found, h2_found, l2_found, h3_found = False, False, False, False, False

    # 遍历数据寻找波浪点
    for i in range(window, len(data_after_min) - window):
        row = data_after_min.iloc[i]
        date = row['日期']
        price = row['收盘']

        # 找第1个高点
        if not h1_found:
            if price > min_price * (1 + h1 / 100):
                waves.append({'类型': 'H1', '日期': date, '价格': price})
                h1_price = price
                h1_date = date
                h1_found = True
                print(f"H1 - 日期: {date}, 价格: {price}")
            continue

        # 找第1个低点
        if h1_found and not l1_found:
            # print(date, price, h1_price * (1 + l1 / 100))
            if date > h1_date and price < h1_price * (1 + l1 / 100):
                waves.append({'类型': 'L1', '日期': date, '价格': price})
                l1_price = price
                l1_date = date
                l1_found = True
                print(f"L1 - 日期: {date}, 价格: {price}")
            continue

        # 找第2个高点
        if l1_found and not h2_found:
            if date > l1_date and price > min_price * (1 + h2 / 100) and price < h1_price:
                waves.append({'类型': 'H2', '日期': date, '价格': price})
                h2_price = price
                h2_date = date
                h2_found = True
                print(f"H2 - 日期: {date}, 价格: {price}")
            continue

        # 找第2个低点
        if h2_found and not l2_found:
            # print(date, price, h2_price * (1 + l1 / 100))
            if date > h2_date and price < h2_price * (1 + l2 / 100):
                waves.append({'类型': 'L2', '日期': date, '价格': price})
                l2_price = price
                l2_date = date
                l2_found = True
                print(f"L2 - 日期: {date}, 价格: {price}")
            continue

        # 找第3个高点
        if l2_found and not h3_found:
            if date > l2_date and price > min_price * (1 + h3 / 100):
                waves.append({'类型': 'H3', '日期': date, '价格': price})
                h3_found = True
                print(f"H3 - 日期: {date}, 价格: {price}")
                break

    # 检查是否找到完整的三浪形态
    if not h3_found:
        print("未找到符合三浪形态的波浪点。")
        return False

    # 打印找到的波浪点
    print("\n符合三浪形态的波浪点：")
    for wave in waves:
        print(f"{wave['类型']} - 日期: {wave['日期']}, 价格: {wave['价格']}")

    # 绘制波浪图
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['日期'], stock_data['收盘'], label='收盘价', color='blue')
    for wave in waves:
        plt.scatter(wave['日期'], wave['价格'], label=f"{wave['类型']} ({wave['价格']:.2f})", zorder=5)

    # 图表设置
    plt.title(f"股票三浪形态分析 - {stock_code}")
    plt.xlabel("日期")
    plt.ylabel("价格")
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()

    # 创建保存图片的文件夹（如果不存在）
    os.makedirs('./pic', exist_ok=True)

    # 保存图表
    pic_filename = f'./pic/{stock_code}_three_waves.png'
    plt.savefig(pic_filename)
    print(f"图表已保存到 {pic_filename}")

    return True

def find_key_points(stock_data, stock_code, rise_threshold=100, fall_threshold=-40, max_low_points=2, window=5):
    """
    函数用来从股票数据中寻找符合条件的关键点（高点和低点）。
    
    参数:
    - stock_data: DataFrame，包含股票的历史数据
    - stock_code: 股票代码，用来命名保存的图表
    - rise_threshold: 高点涨幅阈值（%），默认值为40%
    - fall_threshold: 低点跌幅阈值（%），默认值为-10%
    - max_low_points: 要找到的低点个数，默认值为2
    - window: 用于寻找高低点的滑动窗口大小，默认值为5

    返回:
    - bool: 如果找到指定数量的低点，则返回True，否则返回False
    """

    # 清理列名
    stock_data.columns = stock_data.columns.str.strip()

    # 转换日期列为标准时间格式
    stock_data['日期'] = pd.to_datetime(stock_data['日期'], errors='coerce')
    stock_data.sort_values('日期', inplace=True)

    # 找最低点
    min_price = stock_data['最低'].min()
    min_date = stock_data.loc[stock_data['最低'].idxmin(), '日期']

    print(f"最低点 - 日期: {min_date}, 价格: {min_price}")

    # 从最低点那一天往后开始寻找高点和低点
    data_after_min = stock_data[stock_data['日期'] >= min_date]

    # 初始化变量
    points = [{'日期': min_date, '价格': min_price, '类型': '最低点', '变化率': 0.0}]  # 初始化最低点
    low_point_count = 0  # 符合条件的低点计数
    last_low_point = None  # 记录最后一个低点

    # 遍历数据，寻找高点和低点
    for i in range(window, len(data_after_min) - window):
        current_date = data_after_min.iloc[i]['日期']
        current_price = data_after_min.iloc[i]['收盘']
        
        # 判断是否为高点
        if current_price > data_after_min.iloc[i-window:i]['收盘'].max() and current_price > data_after_min.iloc[i+1:i+window+1]['收盘'].max():
            last_low_price = points[0]['价格']  # 相对最低点
            change_rate = (current_price - last_low_price) / last_low_price * 100
            if change_rate > rise_threshold:  # 涨幅超过指定值
                points.append({'日期': current_date, '价格': current_price, '类型': '高点', '变化率': change_rate})
        
        # 判断是否为低点
        if current_price < data_after_min.iloc[i-window:i]['收盘'].min() and current_price < data_after_min.iloc[i+1:i+window+1]['收盘'].min():
            if len(points) > 1 and points[-1]['类型'] == '高点':  # 确保有前一个高点
                last_high_price = points[-1]['价格']
                change_rate = (current_price - last_high_price) / last_high_price * 100
                if change_rate < fall_threshold:  # 跌幅超过指定值
                    points.append({'日期': current_date, '价格': current_price, '类型': '低点', '变化率': change_rate})
                    low_point_count += 1
                    last_low_point = {'日期': current_date, '价格': current_price, '变化率': change_rate}
                    # 打印低点的详细信息
                    print(f"低点 - 日期: {current_date}, 价格: {current_price}, 相对前一个高点的变化率: {change_rate:.2f}%")
                    
                    if low_point_count == max_low_points:  # 找到指定个数的低点
                        # 如果找到2个低点，返回True
                        print(f"已找到 {max_low_points} 个低点，符合条件。")
                        break  # 找到符合条件的低点后停止循环

    # 如果没有找到2个低点，返回False
    if low_point_count < max_low_points:
        print(f"未找到 {max_low_points} 个符合条件的低点。")
        return False  # 如果没有找到2个低点，返回False

    # 打印找到的所有关键点
    print("\n符合条件的关键点：")
    for point in points:
        print(f"{point['类型']} - 日期: {point['日期']}, 价格: {point['价格']}, 变化率: {point['变化率']:.2f}%")

    # 绘制图表
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['日期'], stock_data['收盘'], label='收盘价', color='blue')

    # 高亮关键点
    seen_labels = set()  # 用于去重标签
    for point in points:
        if point['类型'] == '最低点':
            label = f"{point['类型']} ({point['变化率']:.2f}%)"
            plt.scatter(point['日期'], point['价格'], color='red', label=label, zorder=5)
        elif point['类型'] == '高点':
            label = f"{point['类型']} ({point['变化率']:.2f}%)"
            plt.scatter(point['日期'], point['价格'], color='green', label=label, zorder=5)
        elif point['类型'] == '低点':
            label = f"{point['类型']} ({point['变化率']:.2f}%)"
            plt.scatter(point['日期'], point['价格'], color='orange', label=label, zorder=5)

    # 图表设置
    plt.title(f"股票关键点分析 - {stock_code}")
    plt.xlabel("日期")
    plt.ylabel("价格")
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()

    # 创建保存图片的文件夹（如果不存在）
    os.makedirs('./pic', exist_ok=True)

    # 保存图表
    pic_filename = f'./pic/{stock_code}_points.png'
    plt.savefig(pic_filename)
    print(f"图表已保存到 {pic_filename}")

    # plt.show()

    return True  # 如果找到了符合条件的低点，返回True


# # 读取CSV文件
# # stock_code = "001368"
# stock_code = "300654"
# # stock_code = "002388"
# file_path = f"./data/{stock_code}.csv"
# stock_data = pd.read_csv(file_path)

# # 调用函数寻找关键点
# # result = find_key_points(stock_data, stock_code, rise_threshold=40, fall_threshold=-10, max_low_points=2, window=5)
# # result = find_three_waves(stock_data, stock_code, h1=100, l1=-30, h2=80, l2=-19, h3=90, window=1)
# # result = find_three_waves(stock_data, stock_code, h1=110, l1=-30, h2=90, l2=-19, h3=90, window=1)
# stock_data_peaks = find_peaks(stock_data, stock_code, window=1)
# result = find_three_waves(stock_data_peaks, stock_code, h1=110, l1=-30, h2=80, l2=-19, h3=90, window=1)

# # 打印结果
# if result:
#     print("找到了符合条件的低点。")
# else:
#     print("未找到符合条件的低点。")

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
    # result = find_key_points(stock_data, stock_code, rise_threshold=40, fall_threshold=-10, max_low_points=2, window=5)
    # result = find_three_waves(stock_data, stock_code, h1=100, l1=-30, h2=80, l2=-19, h3=90, window=1)
    # result = find_three_waves(stock_data, stock_code, h1=110, l1=-30, h2=90, l2=-19, h3=90, window=1)
    stock_data_peaks = find_peaks(stock_data, stock_code, window=1)
    # 调用三浪分析前检查
    if stock_data_peaks.empty:
        print("错误：stock_data_peaks 为空，无法执行 find_three_waves。")
    elif '最低' not in stock_data_peaks.columns:
        print("错误：stock_data_peaks 缺少 '最低' 列，无法执行 find_three_waves。")
    else:
        result = find_three_waves(stock_data_peaks, stock_code, h1=110, l1=-30, h2=80, l2=-19, h3=90, window=1)
        print("三浪分析结果:", result)
    
    # 如果返回值为False，跳过
    if not result:
        continue