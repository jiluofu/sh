import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

    # 多项式拟合
    coeffs = np.polyfit(x, y, degree)
    trendline = np.polyval(coeffs, x)

    # 计算偏差
    deviations = y - trendline  # 收盘价与趋势线的差值
    below_trend = deviations < 0  # 是否低于趋势线

    # 检查数据点完整性
    if np.any(np.isnan(y)) or np.any(np.isinf(y)):
        raise ValueError("输入数据包含 NaN 或 Inf 值，请检查数据。")

    if len(x) < degree + 1:
        raise ValueError(f"数据点数量不足以进行 {degree} 阶多项式拟合。")

    # 多项式拟合
    try:
        coeffs = np.polyfit(x, y, degree)
    except np.linalg.LinAlgError:
        print("警告：SVD 未收敛，尝试降低多项式阶数...")
        degree = max(1, degree - 1)
        coeffs = np.polyfit(x, y, degree)

    trendline = np.polyval(coeffs, x)

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
        days_2_to_1 = None
        days_between_batches = None

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

            plt.show()

    return valid_batches


# 示例调用
csv_data = """
日期,股票代码,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
2024-12-02,600601,4.92,4.76,5.09,4.6,7596503,3686678741.0,10.58,2.81,0.13,18.22
2024-12-03,600601,4.74,4.51,4.89,4.46,4972579,2287389311.0,9.03,-5.25,-0.25,11.92
2024-12-04,600601,4.44,4.38,4.63,4.34,3016128,1338942807.0,6.43,-2.88,-0.13,7.23
2024-12-05,600601,4.4,4.52,4.6,4.36,2855520,1284067639.0,5.48,3.2,0.14,6.85
2024-12-06,600601,4.56,4.46,4.56,4.4,1882913,839438329.0,3.54,-1.33,-0.06,4.52
2024-12-09,600601,4.45,4.48,4.59,4.41,1623299,729318639.0,4.04,0.45,0.02,3.89
2024-12-10,600601,4.65,4.48,4.7,4.47,2312732,1054137569.0,5.13,0.0,0.0,5.55
2024-12-11,600601,4.58,4.63,4.77,4.55,2734884,1266629313.0,4.91,3.35,0.15,6.56
2024-12-12,600601,4.64,4.52,4.66,4.45,1827905,825094443.0,4.54,-2.38,-0.11,4.38
2024-12-13,600601,4.47,4.33,4.51,4.32,1704658,748876094.0,4.2,-4.2,-0.19,4.09
2024-12-16,600601,4.29,4.27,4.38,4.25,1075569,463539174.0,3.0,-1.39,-0.06,2.58
2024-12-17,600601,4.27,4.24,4.42,4.19,1552025,666879337.0,5.39,-0.7,-0.03,3.72
2024-12-18,600601,4.25,4.3,4.35,4.19,1101107,472578588.0,3.77,1.42,0.06,2.64
2024-12-19,600601,4.27,4.52,4.59,4.19,2444185,1080501334.0,9.3,5.12,0.22,5.86
2024-12-20,600601,4.47,4.49,4.6,4.41,1794467,805430650.0,4.2,-0.66,-0.03,4.3
2024-12-23,600601,4.5,4.22,4.52,4.22,1329959,576213233.0,6.68,-6.01,-0.27,3.19
2024-12-24,600601,4.24,4.27,4.34,4.19,958575,408338727.0,3.55,1.18,0.05,2.3
2024-12-25,600601,4.28,4.36,4.47,4.11,1665797,716366943.0,8.43,2.11,0.09,3.99
2024-12-26,600601,4.32,4.8,4.8,4.31,2706042,1266469337.0,11.24,10.09,0.44,6.49
2024-12-27,600601,4.97,4.89,5.06,4.81,5085447,2504914559.0,5.21,1.88,0.09,12.19
"""

# 读取 CSV 数据
data = pd.read_csv(StringIO(csv_data))

# 调用函数
batches = analyze_below_trend_batches(data, "1111", 4.63, 3.96)