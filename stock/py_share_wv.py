import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import os
from scipy.signal import argrelextrema
import datetime


# ✅ 开关：
use_csv = True  # 是否从 data 目录读取 CSV 数据
scan_all = True  # 是否自动遍历 data 目录中的所有 CSV 文件
data_dir = "data"  # CSV 文件存放目录
pic_dir = "pic"  # 图片存放目录

# **确保 pic/ 目录及子目录存在**
year_2025_dir = os.path.join(pic_dir, "2025")
tmp_dir = os.path.join(pic_dir, "tmp")
os.makedirs(year_2025_dir, exist_ok=True)
os.makedirs(tmp_dir, exist_ok=True)

# **确保 pic/now 目录存在**
now_dir = os.path.join(pic_dir, "now")
os.makedirs(now_dir, exist_ok=True)

plt.figure(figsize=(12, 6))  # 这行可以省略，因为 figsize 可以在 subplots() 里定义
# ✅ 创建 Figure 和 Axes
fig, ax = plt.subplots(figsize=(12, 6))

# ✅ 记录本周 W 底形态的股票代码
weekly_w_bottom_stocks = []

# **自动匹配系统内的中文字体**
def set_chinese_font():
    font_list = ["SimHei", "Arial Unicode MS", "Noto Sans CJK SC", "STHeiti"]
    for font in font_list:
        if font in [f.name for f in fm.fontManager.ttflist]:
            plt.rcParams["font.sans-serif"] = font
            plt.rcParams["axes.unicode_minus"] = False
            print(f"✅ 选择字体: {font}")
            return
    print("⚠️ 没有找到合适的中文字体，可能会乱码！")

set_chinese_font()

# **扫描 data 目录下所有 CSV 文件**
def scan_data_directory():
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    stock_list = [f.split(".csv")[0] for f in csv_files]
    # ✅ 只保留沪深A股股票代码（沪市60xxxx，深市00xxxx和30xxxx）
    stock_list = [code for code in stock_list if code.startswith(("60", "00"))]

    print(f"✅ 在 {data_dir}/ 目录中找到 {len(stock_list)} 只股票: {stock_list}")
    return stock_list

# **从 data 目录读取 CSV**
def load_stock_data_from_csv(stock_code):
    file_path = os.path.join(data_dir, f"{stock_code}.csv")

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df["日期"] = pd.to_datetime(df["日期"])  # 确保日期格式正确
            print(f"✅ 从 {file_path} 读取数据 ({len(df)} 条记录)")
            return df
        except Exception as e:
            print(f"❌ 读取 {file_path} 失败: {e}")
            return None
    else:
        print(f"⚠️ {file_path} 不存在，跳过该股票")
        return None

# **识别 W 底形态**
def detect_w_bottom(df, stock_code, total_stocks, current_index, window=10):
    df = df.copy()
    df["index"] = df["日期"]

    df["min"] = df["收盘"].iloc[argrelextrema(df["收盘"].values, np.less_equal, order=window)]
    df["max"] = df["收盘"].iloc[argrelextrema(df["收盘"].values, np.greater_equal, order=window)]
    
    lows = df.dropna(subset=["min"])
    highs = df.dropna(subset=["max"])

    for i in range(len(lows) - 1):
        low1 = lows.iloc[i]
        low2 = lows.iloc[i + 1]

        highs_between = highs[(highs["index"] > low1["index"]) & (highs["index"] < low2["index"])]
        if len(highs_between) == 0:
            continue

        high1 = highs_between.iloc[0]
        highs_after = highs[highs["index"] > low2["index"]]

        if len(highs_after) == 0:
            continue

        high2 = highs_after.iloc[0]

        # **计算涨幅**
        increase_1 = (high1["收盘"] - low1["收盘"]) / low1["收盘"] * 100
        increase_2 = (high2["收盘"] - low2["收盘"]) / low2["收盘"] * 100

        # **检查低点和高点变化**
        second_low_is_lower = low2["收盘"] < low1["收盘"]
        second_high_is_lower = high2["收盘"] < high1["收盘"]

        # **文件名标识**
        file_suffix = "_up" if (increase_1 > 20 or increase_2 > 20 or second_low_is_lower or second_high_is_lower) else ""

        second_peak_date = high2["日期"].date()

        # **成交量放大验证**
        second_peak_date = high2["日期"].date()
        second_peak_ts = pd.Timestamp(second_peak_date)  # 转换为 Timestamp

        # ✅ 确保日期存在，避免 IndexError
        if second_peak_ts in df["日期"].values:
            latest_volume = df[df["日期"] == second_peak_ts]["成交量"].values[0]
            previous_volume = df[df["日期"] < second_peak_ts]["成交量"].iloc[-5:].mean()

            if latest_volume < previous_volume * 1.5:
                print(f"⚠️ 股票 {stock_code} 突破时成交量未放大，可能是假信号 {latest_volume} {previous_volume}")
                continue  # 突破时成交量未放大，可能是假信号
        else:
            print(f"⚠️ 股票 {stock_code} 在 {second_peak_date} 没有交易数据，跳过成交量验证")
            continue

        print(f"⚡ 识别到 W 底形态！股票 {stock_code}，时间范围 {low1['日期'].date()} - {second_peak_date}，第二个高点日期: {second_peak_date}")

        # **调用绘图函数**
        plot_w_pattern(df, stock_code, low1, high1, low2, high2, second_peak_date, file_suffix)

    # **计算进度**
    progress = (current_index + 1) / total_stocks * 100
    print(f"✅ 进度：{progress:.2f}% （{current_index + 1}/{total_stocks}） 完成")

# **绘制 W 形态，并按日期保存**
def plot_w_pattern(df, stock_code, low1, high1, low2, high2, second_peak_date, file_suffix):
    # 假设 df 已经定义，low1, low2, high1, high2 也已定义
    

    start_date = low1["日期"] - pd.Timedelta(days=14)  # 提前 2 周
    end_date = high2["日期"] + pd.Timedelta(days=140)   # 延后 20 周

    df_filtered = df[(df["日期"] >= start_date) & (df["日期"] <= end_date)]

    
    global fig, ax
    ax.clear()  # 清除上一次绘图

    # ✅ 在 ax 上绘制收盘价折线
    ax.plot(df_filtered["日期"], df_filtered["收盘"], label="收盘价", color="blue")

    # ✅ 在 ax 上绘制低点和高点
    ax.scatter([low1["日期"], low2["日期"]], [low1["收盘"], low2["收盘"]], color="red", marker="o", s=100, label="低点")
    ax.scatter([high1["日期"], high2["日期"]], [high1["收盘"], high2["收盘"]], color="green", marker="^", s=100, label="高点")

    # ✅ 设置标题、标签、图例
    ax.set_xlabel("时间")
    ax.set_ylabel("价格")
    ax.set_title(f"W 底形态检测 - {stock_code}")
    ax.legend()

    # ✅ **判断 second_peak_date 是否在本周**
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())  # 获取本周一的日期
    end_of_week = start_of_week + datetime.timedelta(days=6)  # 获取本周日的日期


    # **确定保存路径**
    if file_suffix == "_up":
        pic_path = os.path.join(tmp_dir, f"{stock_code}_{second_peak_date}{file_suffix}.png")
        return
    elif second_peak_date.year == 2025:

        if start_of_week <= second_peak_date <= end_of_week:
            pic_path = os.path.join(now_dir, f"{stock_code}_{second_peak_date}.png")
            weekly_w_bottom_stocks.append(stock_code)
        else:
            pic_path = os.path.join(year_2025_dir, f"{stock_code}_{second_peak_date}.png")
            weekly_w_bottom_stocks.append(stock_code)
            # return
    else:
        pic_path = os.path.join(pic_dir, f"{stock_code}_{second_peak_date}.png")
        return

    plt.savefig(pic_path, dpi=300, bbox_inches="tight")
    print(f"📊 图表已保存: {pic_path}")

# ✅ **程序结束后，保存本周 W 底形态的股票代码**
def save_weekly_w_bottoms():
    if weekly_w_bottom_stocks:
        # 先清空文件（即使后面没有内容要写入）
        open("weekly_w_bottoms.txt", "w").close()

        with open("weekly_w_bottoms.txt", "w", encoding="utf-8") as f:
            f.write(str(weekly_w_bottom_stocks))
        print(f"\n📄 本周 W 底形态的股票代码已保存到 weekly_w_bottoms.txt：{weekly_w_bottom_stocks}")
    else:
        print("\n📄 本周未检测到 W 底形态的股票，未生成文件。")

# **运行 W 底检测**
stock_list = scan_data_directory() if scan_all else ["600519", "000001", "002594"]
total_stocks = len(stock_list)


for index, stock_code in enumerate(stock_list):
    df = load_stock_data_from_csv(stock_code) if use_csv else None
    if df is not None:
        detect_w_bottom(df, stock_code, total_stocks, index, window=5)

# ✅ **程序结束时，保存本周 W 底形态的股票代码**
save_weekly_w_bottoms()        

plt.close(fig)  # 释放内存（避免累积多个图像对象）