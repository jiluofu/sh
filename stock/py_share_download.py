import akshare as ak
import pandas as pd
from datetime import datetime
import os
import time

import utils.utils as st

# 记录程序开始时间
start_time = time.time()

# 用户输入起始日期和截止日期
start_date_str = "20180101"
end_date_str = "20250321"
end_date_str = st.get_end_date()

# 检查日期格式
try:
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    if start_date > end_date:
        raise ValueError("起始日期不能晚于截止日期")
except ValueError as e:
    print(f"日期格式错误: {e}")
    exit()

# 获取所有 A 股股票代码
stock_list = ak.stock_info_a_code_name()
# stock_list = stock_list[stock_list["code"].str.startswith(st.STOCK_LIST_WHITE_PRE)]["code"].tolist()
stock_list = stock_list["code"].tolist()

# 创建保存数据的目录（如果不存在）
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# # 手动指定股票代码列表（如果为空，则下载全部股票）
# target_stocks = ["600519", "000001"]  # 示例: 只下载贵州茅台和平安银行

# # 获取所有 A 股股票代码
# if target_stocks:
#     stock_list = stock_list[stock_list['code'].isin(target_stocks)]

# 遍历所有股票代码，获取日线行情数据并保存到文件
for stock_code in stock_list:
    
    try:
        print(stock_code)
        # 获取股票的历史行情数据
        stock_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date_str,
            end_date=end_date_str,
            adjust="qfq"  # 使用前复权数据
        )
        
        
        # 检查是否成功获取数据
        if stock_data.empty:
            print(f"未能获取股票 {stock_code} 的数据")
            continue

        # 清理列名，去掉多余的空格
        stock_data.columns = stock_data.columns.str.strip()

        # 将数据保存为 CSV 文件
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        stock_data.to_csv(file_path, index=False, encoding='utf-8')
        print(f"股票 {stock_code} 的数据已保存到 {file_path}")

    except Exception as e:
        print(f"获取股票 {stock_code} 数据时发生错误: {e}")

print("数据下载并保存完毕！")

st.print_elapsed_time(start_time)

