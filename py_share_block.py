import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import os


def is_stable(prices, threshold=0.01):
    """
    判断价格是否基本平稳（基于波动率分析）。

    参数:
    - prices: List[float]，价格序列。
    - threshold: float，波动率的阈值，默认0.1（即10%）。

    返回:
    - bool: 如果价格波动率低于阈值，返回 True，否则返回 False。
    """
    mean_price = np.mean(prices)
    std_dev = np.std(prices)
    volatility = std_dev / mean_price
    return volatility < threshold

def find_blocks(stock_data, stock_code, days=50, peak_threshold=0.01, trough_threshold=0.01, min_groups=4):
    """
    在最近指定天数的数据中查找符合条件的波峰和波谷，分别使用波动率分析。

    参数:
    - stock_data: DataFrame，包含股票历史数据。
    - stock_code: 股票代码，用于打印和调试。
    - days: 从最新数据往旧查找的天数范围，默认50天。
    - peak_threshold: 波峰的波动率阈值，默认0.1（即10%）。
    - trough_threshold: 波谷的波动率阈值，默认0.1（即10%）。
    - min_groups: 至少满足条件的波峰波谷组数，默认4组。

    返回:
    - bool: 如果找到符合条件的波峰波谷组，返回 True；否则返回 False。
    """
    # 清理列名
    stock_data.columns = stock_data.columns.str.strip()

    # 转换日期列为标准时间格式
    stock_data['日期'] = pd.to_datetime(stock_data['日期'], errors='coerce')
    stock_data.sort_values('日期', inplace=True)

    # 获取最近指定天数的数据
    latest_date = stock_data['日期'].max()
    start_date = latest_date - pd.Timedelta(days=days)
    recent_data = stock_data[stock_data['日期'] > start_date]

    # 如果最近指定天数内没有数据，直接返回 False
    if recent_data.empty:
        print(f"股票代码 {stock_code}: 最近 {days} 天内没有数据。")
        return False

    # 查找波峰和波谷
    peaks_and_troughs = find_peaks_and_troughs(recent_data)

    # 分离波峰和波谷
    peaks = [pt for pt in peaks_and_troughs if pt['类型'] == '波峰']
    troughs = [pt for pt in peaks_and_troughs if pt['类型'] == '波谷']

    # 提取波峰和波谷的价格列表
    peak_prices = [p['价格'] for p in peaks]
    trough_prices = [t['价格'] for t in troughs]

    # 波动率分析
    if not is_stable(peak_prices, threshold=peak_threshold):
        print(f"股票代码 {stock_code}: 波峰波动率超过 {peak_threshold * 100}%。")
        return False

    if not is_stable(trough_prices, threshold=trough_threshold):
        print(f"股票代码 {stock_code}: 波谷波动率超过 {trough_threshold * 100}%。")
        return False

    # 检查连续的波峰和波谷组数是否满足条件
    valid_groups = 0
    for i in range(min(len(peaks), len(troughs))):
        if i + 1 < len(peaks) and i < len(troughs):
            if peaks[i]['日期'] > troughs[i]['日期'] and troughs[i]['日期'] > peaks[i-1]['日期']:
                valid_groups += 1

    if valid_groups < min_groups:
        print(f"股票代码 {stock_code}: 未找到连续 {min_groups} 组符合条件的波峰和波谷。")
        return False

    # 如果满足条件，打印结果并绘制图表
    print(f"股票代码 {stock_code}: 最近 {days} 天内找到 {valid_groups} 组符合条件的波峰和波谷。")

    # 绘制箱型波动区域图表（时间范围包含全部时间段）
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['日期'], stock_data['收盘'], color='blue', alpha=0.6)

    # 高亮显示波峰和波谷
    for pt in peaks_and_troughs:
        color = 'red' if pt['类型'] == '波峰' else 'green'
        plt.scatter(pt['日期'], pt['价格'], color=color, zorder=5)

    # 高亮显示箱型波动区域
    if peaks and troughs:
        max_peak = max(peak_prices)
        min_trough = min(trough_prices)
        plt.axhline(y=max_peak, color='orange', linestyle='--')
        plt.axhline(y=min_trough, color='purple', linestyle='--')

    plt.title(f"{stock_code} 波动分析（包含全部时间段）")
    plt.xlabel("日期")
    plt.ylabel("收盘价")
    plt.grid(True)
    plt.tight_layout()

    # 保存图表
    pic_filename = f'./pic/{stock_code}_box_wave_analysis_full_range.png'
    plt.savefig(pic_filename)
    print(f"箱型波动图表已保存到 {pic_filename}")

    # 显示图表
    # plt.show()

    return True

def find_peaks_and_troughs(block_data):
    """
    在给定的区间数据中找到波峰和波谷。

    参数:
    - block_data: DataFrame，区间数据。

    返回:
    - peaks_and_troughs: List[dict]，包含波峰和波谷的列表。
    """
    peaks_and_troughs = []
    for i in range(1, len(block_data) - 1):
        previous = block_data.iloc[i - 1]['收盘']
        current = block_data.iloc[i]['收盘']
        next_ = block_data.iloc[i + 1]['收盘']

        # 波峰
        if current > previous and current > next_:
            peaks_and_troughs.append({'类型': '波峰', '日期': block_data.iloc[i]['日期'], '价格': current})

        # 波谷
        if current < previous and current < next_:
            peaks_and_troughs.append({'类型': '波谷', '日期': block_data.iloc[i]['日期'], '价格': current})

    return peaks_and_troughs


# # 读取CSV文件
# # stock_code = "001368"
# stock_code = "300654"
# # stock_code = "600724"
# file_path = f"./data/{stock_code}.csv"
# stock_data = pd.read_csv(file_path)

# # 调用函数寻找关键点
# result = find_blocks(stock_data, stock_code, days=30, min_cycles=2, peak_to_trough_rate=10)


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
    result = find_blocks(stock_data, stock_code, days=30, peak_threshold=0.011, trough_threshold=0.011, min_groups=3)
    
    # 如果返回值为False，跳过
    if not result:
        continue