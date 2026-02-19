import tushare as ts
import pandas as pd


# 你的 Tushare API Token（需要自己申请）
ts.set_token("49cdfd502977aa0bb0313a6c934e1f737479bd0d06898db822f85b08")

# 股票列表（示例：贵州茅台、平安银行）
stock_list = ['001318', '002905']

# 获取实时数据（买一量 b1_v）
df = ts.get_realtime_quotes(stock_list)  # 获取股票实时行情数据

# 选择股票代码和买一量字段
df = df[['code', 'b1_v']]

# 转换买一量为整数（Tushare 返回的是字符串格式）
df['b1_v'] = pd.to_numeric(df['b1_v'], errors='coerce').fillna(0).astype(int)

# 遍历打印结果（股票代码 + 买一量股数）
print("\n📊 实时买一量（单位：股）：")
for index, row in df.iterrows():
    print(f"股票代码: {row['code']}, 买一量: {row['b1_v']*100} 股")