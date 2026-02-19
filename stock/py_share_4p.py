import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

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
# stock_code = "001368"
# file_path = f"./data/{stock_code}.csv"
# stock_data = pd.read_csv(file_path)

# # 调用函数寻找关键点
# result = find_key_points(stock_data, stock_code, rise_threshold=40, fall_threshold=-10, max_low_points=2, window=5)

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
    
    # 调用find_key_points函数，返回结果
    result = find_key_points(stock_data, stock_code, rise_threshold=40, fall_threshold=-10, max_low_points=2, window=5)
    
    # 如果返回值为False，跳过
    if not result:
        continue