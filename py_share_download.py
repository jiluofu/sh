import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

# 获取当前日期并设置日期范围
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# 格式化日期为字符串
start_date_str = start_date.strftime("%Y%m%d")
end_date_str = end_date.strftime("%Y%m%d")

# 获取所有A股股票代码
stock_list = ak.stock_info_a_code_name()

# 创建保存数据的目录（如果不存在）
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 遍历所有股票代码，获取日线行情数据并保存到文件
for stock_code in stock_list['code']:
    try:
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

        # 将数据保存为CSV文件
        file_path = os.path.join(data_dir, f"{stock_code}.csv")
        stock_data.to_csv(file_path, index=False, encoding='utf-8')
        print(f"股票 {stock_code} 的数据已保存到 {file_path}")

    except Exception as e:
        print(f"获取股票 {stock_code} 数据时发生错误: {e}")

print("数据下载并保存完毕！")