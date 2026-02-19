import json
import pandas as pd
import matplotlib.pyplot as plt

# 定义 N 字型模式检测逻辑
def identify_n_patterns(df, min_duration=2, retracement_limit=0.618):
    n_patterns = []

    for i in range(len(df) - 3 * min_duration):  # 确保足够范围
        # 第一段
        segment1 = df['close'].iloc[i:i + min_duration]
        if segment1.empty:
            continue
        if segment1.iloc[-1] > segment1.iloc[0]:  # 上涨
            direction1 = "up"
        else:
            direction1 = "down"

        # 第二段（回调/反弹）
        segment2 = df['close'].iloc[i + min_duration:i + 2 * min_duration]
        if segment2.empty:
            continue
        retracement = abs(segment2.iloc[-1] - segment1.iloc[-1]) / abs(segment1.iloc[-1] - segment1.iloc[0])
        if retracement <= retracement_limit:
            direction2 = "down" if direction1 == "up" else "up"
        else:
            continue

        # 第三段（继续上涨/下跌）
        segment3 = df['close'].iloc[i + 2 * min_duration:i + 3 * min_duration]
        if segment3.empty:
            continue
        if (direction1 == "up" and segment3.iloc[-1] > segment2.iloc[-1]) or (direction1 == "down" and segment3.iloc[-1] < segment2.iloc[-1]):
            direction3 = direction1
        else:
            continue

        # 记录符合条件的 N 字型
        n_patterns.append((df['date'].iloc[i], df['date'].iloc[i + 3 * min_duration - 1]))

    return n_patterns

def detect_after_low(df, min_duration=2, retracement_limit=0.618):
    # 找到历史最低价
    lowest_price = df['low'].min()
    lowest_date = df[df['low'] == lowest_price]['date'].iloc[0]

    # 提取最低价之后的数据
    df_after_low = df[df['date'] >= lowest_date]

    # 检测连续 N 字型模式
    n_patterns = identify_n_patterns(df_after_low, min_duration, retracement_limit)

    return lowest_date, n_patterns

# 绘制曲线图并高亮 N 字型区域
def plot_with_n_patterns(df, lowest_date, n_patterns):
    plt.figure(figsize=(14, 7))
    plt.plot(df['date'], df['close'], label='Close Price', color='blue')

    # 高亮历史最低价之后的 N 字型区域
    for start_date, end_date in n_patterns:
        plt.axvspan(start_date, end_date, color='green', alpha=0.3, label='N Pattern Area')

    # 标注历史最低价
    lowest_price = df[df['date'] == lowest_date]['close'].iloc[0]
    plt.scatter(lowest_date, lowest_price, color='red', label='Historical Low', zorder=5)
    plt.axvline(lowest_date, color='red', linestyle='--', label='Lowest Date')

    # 图形细节
    plt.title('Stock Price with N Patterns After Historical Low (Weekly)')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend(loc='upper left')
    plt.grid()
    plt.show()

# 读取 JSON 文件
file_path = 'a_shares_last_365_days_akshare.json'  # 替换为实际 JSON 文件路径

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"读取 JSON 文件失败: {e}")
    exit()

# 获取目标股票数据
stock_id = "001368"  # 替换为实际股票代码
if stock_id in data:
    stock_data = data[stock_id]["data"]  # 获取数据部分
    stock_name = data[stock_id]["name"]  # 获取股票名称
else:
    print(f"未找到股票代码 {stock_id} 的数据")
    exit()

# 转换为 DataFrame
df = pd.DataFrame(stock_data)

# 数据清洗
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# 将数据重采样为周线
df.set_index("date", inplace=True)
weekly_df = df.resample('W').agg({
    'open': 'first',
    'close': 'last',
    'high': 'max',
    'low': 'min',
    'volume': 'sum'
}).dropna().reset_index()

# 检测历史最低价后的 N 字型模式（按周计算）
min_duration = 2  # 每段最短持续周数
retracement_limit = 0.618  # 回调幅度限制
lowest_date, n_patterns = detect_after_low(weekly_df, min_duration, retracement_limit)

# 绘制图表
plot_with_n_patterns(weekly_df[weekly_df['date'] >= lowest_date], lowest_date, n_patterns)