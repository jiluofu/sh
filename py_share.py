# 49cdfd502977aa0bb0313a6c934e1f737479bd0d06898db822f85b08
# import tushare as ts
# import pandas as pd
# from datetime import datetime, timedelta

# # 设置 Tushare API Token
# ts.set_token('49cdfd502977aa0bb0313a6c934e1f737479bd0d06898db822f85b08')  # 请将 'your_token_here' 替换为您的实际 Token
# pro = ts.pro_api()

# # 计算日期范围
# end_date = datetime.today()
# start_date = end_date - timedelta(days=90)

# # 格式化日期为字符串
# start_date_str = start_date.strftime('%Y%m%d')
# end_date_str = end_date.strftime('%Y%m%d')

# # 获取贵州茅台最近三个月的日线行情数据
# df = pro.daily(ts_code='600519.SH', start_date=start_date_str, end_date=end_date_str)

# # 检查数据是否为空
# if not df.empty:
#     # 按交易日期升序排序
#     df = df.sort_values(by='trade_date', ascending=True)
#     # 输出结果
#     print(df[['trade_date', 'open', 'high', 'low', 'close', 'vol']])
# else:
#     print("未能获取数据，请检查日期范围或股票代码。")

# import tushare as ts
# import pandas as pd
# from datetime import datetime, timedelta
# import json

# # 设置 Tushare API Token
# ts.set_token('49cdfd502977aa0bb0313a6c934e1f737479bd0d06898db822f85b08')  # 替换为您的 Tushare Token
# pro = ts.pro_api()

# # 计算日期范围
# end_date = datetime.today()
# start_date = end_date - timedelta(days=90)

# # 格式化日期
# start_date_str = start_date.strftime('%Y%m%d')
# end_date_str = end_date.strftime('%Y%m%d')

# # 获取 A 股所有股票代码
# stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

# # 初始化数据存储
# all_data = {}

# # 遍历每只股票，获取近三个月的行情数据
# for index, row in stock_list.iterrows():
#     ts_code = row['ts_code']
#     stock_name = row['name']
#     print(f"正在获取 {stock_name}（{ts_code}） 的数据...")

#     try:
#         # 获取单只股票的行情数据
#         df = pro.daily(ts_code=ts_code, start_date=start_date_str, end_date=end_date_str)
#         if not df.empty:
#             # 将数据转换为 JSON 格式，并按股票代码存储
#             all_data[ts_code] = {
#                 "name": stock_name,
#                 "data": df.to_dict(orient='records')  # 将 DataFrame 转为字典列表
#             }
#     except Exception as e:
#         print(f"获取 {ts_code} 数据时出错：{e}")

# # 保存到本地 JSON 文件
# if all_data:
#     with open('a_shares_last_3_months.json', 'w', encoding='utf-8') as f:
#         json.dump(all_data, f, ensure_ascii=False, indent=4)
#     print("数据已保存到 'a_shares_last_3_months.json'")
# else:
#     print("未获取到任何数据！")




# import akshare as ak
# import pandas as pd
# import json
# from datetime import datetime, timedelta

# # 计算日期范围
# end_date = datetime.today()
# start_date = end_date - timedelta(days=90)

# # 格式化日期
# start_date_str = start_date.strftime('%Y%m%d')
# end_date_str = end_date.strftime('%Y%m%d')

# # 获取 A 股所有股票代码
# stock_list = ak.stock_info_a_code_name()

# # 初始化数据存储
# all_data = {}

# # 遍历每只股票，获取近三个月的行情数据
# for index, row in stock_list.iterrows():
#     ts_code = row['code']
#     stock_name = row['name']
#     print(f"正在获取 {stock_name}（{ts_code}） 的数据...")

#     try:
#         # 获取单只股票的行情数据
#         df = ak.stock_zh_a_hist(symbol=ts_code, period="daily", start_date=start_date_str, end_date=end_date_str, adjust="qfq")
        
#         if not df.empty:
#             # 动态匹配列名（akshare 默认列名为中文）
#             df.rename(columns=lambda x: x.strip(), inplace=True)  # 去除列名两端的空格
#             column_mapping = {
#                 "日期": "date",
#                 "开盘": "open",
#                 "收盘": "close",
#                 "最高": "high",
#                 "最低": "low",
#                 "成交量": "volume",
#                 "成交额": "amount",
#             }
#             # 仅重命名存在的列，避免因缺失字段导致报错
#             df = df.rename(columns={k: column_mapping[k] for k in column_mapping if k in df.columns})
#             df["date"] = df["date"].astype(str)
            
#             # 将数据转换为 JSON 格式，并按股票代码存储
#             all_data[ts_code] = {
#                 "name": stock_name,
#                 "data": df.to_dict(orient='records')  # 将 DataFrame 转为字典列表
#             }
#     except Exception as e:
#         print(f"获取 {ts_code} 数据时出错：{e}")

# # 保存到本地 JSON 文件
# if all_data:
#     with open('a_shares_last_3_months_akshare.json', 'w', encoding='utf-8') as f:
#         json.dump(all_data, f, ensure_ascii=False, indent=4)
#     print("数据已保存到 'a_shares_last_3_months_akshare.json'")
# else:
#     print("未获取到任何数据！")




import json
import pandas as pd

# 读取 JSON 文件
file_path = 'a_shares_last_3_months_akshare.json'  # 替换为实际 JSON 文件路径

# 加载 JSON 数据
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 初始化存储结果
falling_stocks = []

# 遍历 JSON 数据中的每只股票
for ts_code, stock_info in data.items():
    stock_name = stock_info['name']
    stock_data = stock_info['data']
    
    # 转换为 DataFrame 并按日期排序
    df = pd.DataFrame(stock_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    
    # 计算涨跌幅和下跌量
    df['pct_change'] = df['close'].pct_change() * 100  # 涨跌幅百分比
    df['price_change'] = df['close'] - df['close'].shift(1)  # 下跌量（绝对值）
    
    # 检查连续三天涨跌幅是否为负
    df['falling'] = df['pct_change'] < 0  # 标记跌幅
    df['consecutive_falling'] = (
        df['falling'] & df['falling'].shift(1) & df['falling'].shift(2)
    )  # 检查连续三天为 True
    
    # 如果有连续三天大跌的记录，则保存
    if df['consecutive_falling'].any():
        falling_info = {
            "ts_code": ts_code,
            "name": stock_name,
            "details": []
        }
        
        # 获取连续三天大跌的起始日期，并提取详细信息
        falling_days = df.loc[df['consecutive_falling']].index
        for idx in falling_days:
            three_days = df.iloc[idx-2:idx+1][['date', 'close', 'price_change', 'pct_change']]
            falling_info["details"].append(three_days)
        
        falling_stocks.append(falling_info)

# 将结果保存为文本文件
output_file = "falling_stocks_report.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    if falling_stocks:
        for stock in falling_stocks:
            f.write(f"股票 {stock['name']} ({stock['ts_code']}) 连续三天大跌详细信息：\n")
            for record in stock['details']:
                f.write("  三天记录：\n")
                for _, row in record.iterrows():
                    f.write(f"    日期: {row['date'].strftime('%Y-%m-%d')}, 收盘价: {row['close']:.2f}, 下跌量: {row['price_change']:.2f}, 跌幅: {row['pct_change']:.2f}%\n")
            f.write("\n")
    else:
        f.write("没有找到连续三天大跌的股票。\n")

print(f"结果已保存到 {output_file}")