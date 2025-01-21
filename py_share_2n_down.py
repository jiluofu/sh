import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 定义新的 N 字型模式检测逻辑
def find_n_patterns(df, min_duration=3):
    """
    逐步寻找 N 字型模式，从上一个 N 字型结束后开始寻找下一个
    :param df: 股票数据 DataFrame
    :param min_duration: 每段最短持续时间跨度（单位：周）
    :return: 按顺序找到的所有 N 字型模式列表
    """
    n_patterns = []
    start_index = min_duration  # 从第一个可检测点开始

    while start_index < len(df) - 2 * min_duration:
        # 第一段：从低点上涨
        low1 = df.iloc[start_index - min_duration]['收盘']
        high = df.iloc[start_index]['收盘']
        low2 = df.iloc[start_index + min_duration]['收盘']

        # 判断是否符合 N 字型结构
        if low1 < high > low2 and low2 < high:
            # 记录 N 字型的起止日期
            n_patterns.append((df.iloc[start_index - min_duration]['日期'], df.iloc[start_index + min_duration]['日期']))
            # 更新起始点为当前 N 字型的结束点
            start_index += 2 * min_duration
        else:
            start_index += 1  # 未找到则继续向后搜索

    return n_patterns

# 获取股票数据
stock_code = "001368"
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

start_date_str = start_date.strftime("%Y%m%d")
end_date_str = end_date.strftime("%Y%m%d")

# 使用 AkShare 获取最近一年的周线数据
stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date_str, end_date=end_date_str, adjust="")

if stock_data.empty:
    print(f"未能获取股票 {stock_code} 的周线数据，请检查网络或代码输入。")
else:
    # 处理数据
    stock_data['日期'] = pd.to_datetime(stock_data['日期'])
    stock_data.sort_values('日期', inplace=True)
    
    # 筛选 2024 年 2 月之后的数据
    filtered_data = stock_data[stock_data['日期'] >= '2024-02-01']
    
    # 检测所有 N 字型模式
    n_patterns = find_n_patterns(filtered_data, min_duration=10)  # 每段最短持续 6 周
    
    # 绘制价格曲线图
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['日期'], stock_data['收盘'], label='Close Price', marker='o')
    plt.title(f"Price Line Chart for Stock {stock_code} (Weekly)")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.grid(True)
    plt.legend()
    
    # 高亮 N 字型区域
    if n_patterns:
        for start_date, end_date in n_patterns:
            plt.axvspan(start_date, end_date, color='green', alpha=0.3, label='N Pattern' if start_date == n_patterns[0][0] else "")
        print(f"从 2024 年 2 月开始检测到 {len(n_patterns)} 次 N 字型模式：")
        for i, pattern in enumerate(n_patterns, 1):
            print(f"第 {i} 次 N 字型: 起始日期 {pattern[0]} 至 {pattern[1]}")
    else:
        print("从 2024 年 2 月开始未检测到任何 N 字型模式。")

    plt.tight_layout()
    plt.show()