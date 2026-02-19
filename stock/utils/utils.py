import sys
import time
import os
from datetime import datetime, timedelta

import akshare as ak


STOCK_LIST_WHITE_PRE = ('600', '601', '603', '605', '000', '001', '002', '003')
# ======================== 获取上周一日期 ========================
def get_last_monday():
    today = datetime.today()
    # weekday(): 周一为0，周日为6
    offset = today.weekday() + 7
    last_monday = today - timedelta(days=offset)
    return last_monday.strftime('%Y-%m-%d')

# ======================== 计时函数 ========================
def print_elapsed_time(start_time):
    """打印代码运行时间，并自动调整时间单位"""
    elapsed_time = time.time() - start_time
    if elapsed_time > 3600:
        print(f"\n⏱️ 总运行时间: {elapsed_time / 3600:.2f} 小时")
    elif elapsed_time > 60:
        print(f"\n⏱️ 总运行时间: {elapsed_time / 60:.2f} 分钟")
    else:
        print(f"\n⏱️ 总运行时间: {elapsed_time:.2f} 秒")

# ======================= 读取命令行第1个参数作为截止日期 =====
def is_valid_yyyymmdd(date_str):
    """检查字符串是否符合 YYYYMMDD 格式，并且是一个有效日期"""
    try:
        datetime.strptime(date_str, "%Y%m%d")  # 尝试解析日期
        return True  # 如果解析成功，则是有效的日期
    except ValueError:
        return False  # 解析失败，说明日期格式错误或无效
# 读取命令行第1个参数作为截止日期，如果没有参数，默认用当天日期
def get_end_date():
    """获取命令行第1个参数，如果没有提供或格式不正确，则返回当天日期（格式 YYYYMMDD）"""
    default_date = datetime.now().strftime("%Y%m%d")

    # 读取第1个参数，去除两侧空格
    input_date = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else ""

    # 检查是否是有效的 YYYYMMDD 日期
    if is_valid_yyyymmdd(input_date):
        print(f"\n✅ 用户提供的有效截止日期: {input_date}")
        return input_date
    else:
        print(f"\n📅 无效或缺失参数，使用默认日期: {default_date}")
        return default_date
# ======================= 读取命令行第2个参数作为预测天数 =====
def get_prediction_days(default=3):
    ndays = default 
    """读取命令行第2个参数作为预测天数，如果无效则返回默认值"""
    try:
        # 读取第2个参数（索引2，因为 sys.argv[0] 是脚本名）
        days = sys.argv[2] if len(sys.argv) > 2 else ""

        # 转换为整数，确保是数字
        ndays =  int(days) if days.isdigit() else default
        print(f"\n📥 读参数，设定预测天数: {ndays}")
        return ndays
    except ValueError:
        print(f"\n📥 读参数，设定预测天数: {ndays}")
        return ndays  # 如果转换失败，返回默认值

# ======================== 获取 A 股主板股票 ========================
def get_main_board_stocks():
    """获取 A 股主板（非创业板）的股票列表"""
    print("\n📥 获取主板股票列表...")
    stock_list = ak.stock_info_a_code_name()
    main_board_stocks = stock_list[stock_list["code"].str.startswith(STOCK_LIST_WHITE_PRE)]["code"].tolist()
    print(f"✅ 获取 {len(main_board_stocks)} 只主板股票")
    return main_board_stocks

# ======================== 读取 gold.txt 的股票代码 ========================
def get_gold_stocks():
    """从 gold.txt 读取符合 MACD 金叉的股票代码"""
    print("\n📂 尝试从 gold.txt 读取股票代码...")
    if os.path.exists("gold.txt"):
        with open("gold.txt", "r", encoding="utf-8") as f:
            gold_stocks = [line.strip() for line in f.readlines() if line.strip()]
        if gold_stocks:
            print(f"✅ 从 gold.txt 读取 {len(gold_stocks)} 只股票")
            return gold_stocks
    print("⚠️ gold.txt 为空或不存在，使用主板股票列表")
    return get_main_board_stocks()

# ======================== 格式化股票代码 ========================
def format_stock_code(stock_code):
    """ 格式化股票代码：适配腾讯接口（sh600519 / sz000001）"""
    if stock_code.startswith(("600", "601", "603")):
        return f"sh{stock_code}"
    elif stock_code.startswith(("000", "001", "002")):
        return f"sz{stock_code}"
    else:
        return stock_code  # 其他情况返回原代码