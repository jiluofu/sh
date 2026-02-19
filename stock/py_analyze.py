import os
import sys
import pandas as pd
from glob import glob
from datetime import datetime

# 目标文件前缀
prefixes = [
    "limit_up_status_xgboost_lstm_transformer_",
    "low_position_breakout_",
    "macd_ma20_status_xgboost_lstm_transformer_",
    "EOB_Buying_Method_",
    "predicted_rise_results_"
]

def is_valid_yyyymmdd(date_str):
    """检查字符串是否符合 YYYYMMDD 格式，并且是一个有效日期"""
    try:
        return datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        return None

def get_search_date():
    """获取命令行输入日期，如果未提供或格式错误，则使用当天日期"""
    default_date = datetime.now().strftime("%Y%m%d")
    input_date = sys.argv[1] if len(sys.argv) > 1 else default_date
    
    valid_date = is_valid_yyyymmdd(input_date)
    if valid_date:
        print(f"\n✅ 设定搜索日期: {input_date}")
        return valid_date
    else:
        print(f"\n⚠️ 无效日期格式，使用默认日期: {default_date}")
        return datetime.strptime(default_date, "%Y%m%d")

# 获取命令行输入日期
search_date = get_search_date()
search_date_str = search_date.strftime("%Y-%m-%d")  # 格式化日期方便比较

# 获取当前目录下所有 CSV 文件
csv_files = glob("*.csv")

# 选取**每个前缀**在 `search_date` 这一天修改的最新文件
valid_files = {}
missing_prefixes = []  # 记录没有找到当天文件的前缀

for prefix in prefixes:
    # 找出所有该前缀的文件
    matching_files = [f for f in csv_files if f.startswith(prefix)]

    if matching_files:
        # 过滤出 `search_date` 当天修改的文件
        same_day_files = [f for f in matching_files if datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d") == search_date_str]
        
        if same_day_files:
            # 选取 `search_date` 这一天修改的最新文件（修改时间最大的）
            latest_file = max(same_day_files, key=os.path.getmtime)
            valid_files[prefix] = latest_file
        else:
            missing_prefixes.append(prefix)
    else:
        missing_prefixes.append(prefix)

# 打印找到的文件
if valid_files:
    print("\n📂 选中的 CSV 文件（修改日期与 `search_date` 相同，选最新修改的）：")
    for prefix, file in valid_files.items():
        file_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  🔹 {prefix} => {file}（修改时间: {file_time}）")

# 提醒用户哪些前缀**没有找到符合 `search_date` 的文件**
if missing_prefixes:
    print(f"\n⚠️ 以下前缀未找到 `{search_date.strftime('%Y%m%d')}` 修改的 CSV 文件，不参与比较：")
    for prefix in missing_prefixes:
        print(f"  ❌ {prefix}")

# 如果没有符合条件的文件，直接退出
if not valid_files:
    print("\n❌ 未找到任何符合搜索日期的文件，退出分析。")
    sys.exit(0)

# 读取文件并提取股票代码，并记录在哪些文件中
stock_file_map = {}  # 记录股票代码在哪些前缀的文件中
stock_sets_by_prefix = {}  # 按前缀存储股票代码集合

for prefix, file in valid_files.items():
    # 强制以字符串方式读取 CSV，防止股票代码丢失前导 `0`
    df = pd.read_csv(file, dtype=str)

    # 自动寻找 "股票代码" 列（可能是 "股票代码" 或 "Stock Code"）
    possible_columns = ["股票代码", "Stock Code"]
    stock_column = next((col for col in possible_columns if col in df.columns), None)

    if stock_column:
        # 处理可能缺失的前导 `0`
        df[stock_column] = df[stock_column].str.zfill(6)
        
        stock_set = set(df[stock_column])
        stock_sets_by_prefix[prefix] = stock_set  # 按前缀存储股票代码

        # 记录股票在哪些前缀文件中出现
        for stock in stock_set:
            if stock not in stock_file_map:
                stock_file_map[stock] = set()
            stock_file_map[stock].add(prefix)
    else:
        print(f"\n⚠️ 警告: 文件 {file} 中未找到股票代码列，跳过此文件。")

# 计算**不同前缀**中的股票交集
if stock_sets_by_prefix:
    prefix_list = list(stock_sets_by_prefix.keys())
    common_stocks = set()

    print("\n🔍 正在比较以下不同前缀的文件：")
    
    # 遍历不同前缀的组合，计算交集
    for i in range(len(prefix_list)):
        for j in range(i + 1, len(prefix_list)):
            p1, p2 = prefix_list[i], prefix_list[j]
            print(f"  ✅ 比较 {valid_files[p1]} 和 {valid_files[p2]}")
            common_stocks.update(stock_sets_by_prefix[p1] & stock_sets_by_prefix[p2])
else:
    common_stocks = set()

# 输出分析结果
if common_stocks:
    print(f"\n✅ 共有的股票代码（符合至少两个不同策略）: ")
    for stock in common_stocks:
        files = ", ".join([valid_files[prefix] for prefix in stock_file_map[stock]])
        print(f"  🔹 {stock} 出现在: {files}")

    print(f"\n📊 共有 {len(common_stocks)} 只股票符合不同策略！")

    # 创建 DataFrame 记录每只股票在哪些文件中出现
    stock_details = [{"Stock Code": stock, "Files": ", ".join([valid_files[prefix] for prefix in stock_file_map[stock]])} for stock in common_stocks]
    common_df = pd.DataFrame(stock_details)

    # 保存到 CSV 文件
    output_filename = f"common_stocks_{search_date.strftime('%Y%m%d')}.csv"
    common_df.to_csv(output_filename, index=False)
    print(f"\n📁 结果已保存到 `{output_filename}`，可用 Excel 打开查看。")
else:
    print("\n⚠️ 没有找到符合多个策略的共同股票。")