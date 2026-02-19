import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from texttable import Texttable  # 终端对齐打印表格

# ✅ 只需要输入股票代码
# # 0307-0312-5
# stock_codes = '603629,603108'
# # 0310-0313-3
# stock_codes = '002515,603629,603518,603006,600215'
# # 0311-0314-3
# stock_codes = '002893'
# # 0312-0317-3
# stock_codes = '600355,603108'
# # 0313-0318-3
# stock_codes = '603611'
# # 0314-0319-3
# stock_codes = '603918,603798,002893,601900'
# # 0317-0320-3
# stock_codes = '603918,002515,002893,002544,000791'
# # 0318-0321-3
# stock_codes = '002893,603798,002436'

# # 0319-0324-3
# stock_codes = '603629,002544,600398,002893,603006,600449,603798'
# # 0320-0325-3
# stock_codes = '603629,000791,000960,603006,600449'
# # 0321-0326-3
# stock_codes = '002342'
# # 0324-0327-3，macd、rise
# stock_codes = '000039,002978'
# # 0325-0328-3，macd、rise
# stock_codes = '601212,002634,600666'
# # 0326-0331-3，macd、rise
# stock_codes = '000936,000029'

# # 0327-0401-3，macd、rise
# stock_codes = '002535,603281'

# # 0328-0402-3，macd、rise、open
# stock_codes = '002294,603281,600746'

# # 0331-0403-3，macd、rise、open
# stock_codes = '002363,002559,603829,601059,600239'

# # 0401-0407-3，macd、rise、open
# stock_codes = '002877,603321,002988'

# # 0402-0408-3，macd、rise、open
# stock_codes = '002478,000792,603353'

# # 0403-0409-3，macd、rise、open
# stock_codes = '002478,000960,601717,600398,600039,600502,603068,002982'

# # 0407-0410-3，macd、rise、open
# stock_codes = '002535,601033,002960,601702,603836'

# # 0408-0411-3，macd、rise、open
# stock_codes = '601033,600039,002952,601702,002880'
# # 0408-0411-3，hvlr
# stock_codes = '000019,002299,002900,600161,601952'

# # 0409-0412-3，macd、rise、open
# stock_codes = '603383,600989,603970'
# # 0409-0412-3，hvlr
# stock_codes = '000019,002299,002900,600161,601952'

# 0410-0415-3，macd、rise、open
stock_codes = '601033,002973,002981'
# 0410-0415-3，hvlr
stock_codes = '002365,002734,002900,600161,601952,603609'





stock_codes = stock_codes.split(",")

# ✅ 默认投资金额 10000 元
default_investment = 10000

# ✅ 用户输入起始日期和截止日期
start_date_str = "20250411"
end_date_str = "20250414"

# ✅ 费用相关参数
stamp_tax_rate = 0.0005  # **A股印花税**（卖出金额 0.05%）
commission_rate = 0.00025  # **东方财富佣金**（万2.5）
min_commission = 5  # **最低佣金（5元）**

# ✅ 检查日期格式
try:
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    if start_date > end_date:
        raise ValueError("起始日期不能晚于截止日期")
except ValueError as e:
    print(f"日期格式错误: {e}")
    exit()

# ✅ 结果存储列表
results = []
high_gainers = []  # 记录涨幅超过 5% 的股票
total_investment = 0
total_final_value = 0

# ✅ 遍历股票代码
for stock_code in stock_codes:
    try:
        print(f"正在获取 {stock_code} 的数据...")

        # 获取股票历史数据
        stock_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date_str,
            end_date=end_date_str
        )

        # 检查数据是否为空
        if stock_data.empty:
            print(f"未能获取股票 {stock_code} 的数据")
            continue

        # 清理列名
        stock_data.columns = stock_data.columns.str.strip()

        # 获取起始价格和结束价格
        start_price = stock_data.iloc[0]["收盘"]
        end_price = stock_data.iloc[-1]["收盘"]

        # 计算涨幅
        increase_pct = ((end_price - start_price) / start_price) * 100

        # 计算购买的股数
        shares_bought = default_investment / start_price

        # 计算投资的剩余价值
        remaining_amount = shares_bought * end_price

        # 计算佣金（买入和卖出都要收取，佣金至少 5 元）
        buy_commission = max(default_investment * commission_rate, min_commission)
        sell_commission = max(remaining_amount * commission_rate, min_commission)

        # 计算印花税（仅对卖出金额收取）
        stamp_tax = remaining_amount * stamp_tax_rate

        # 计算最终卖出后可得金额（扣除印花税和佣金）
        final_amount = remaining_amount - stamp_tax - sell_commission

        # 计算最终收益
        profit = final_amount - default_investment - buy_commission  # 也扣除买入佣金

        # ✅ 计算收益率
        return_pct = (profit / default_investment) * 100

        # ✅ 更新总投资和最终总价值
        total_investment += default_investment
        total_final_value += final_amount

        # ✅ 存储结果
        results.append([
            stock_code,
            round(start_price, 2),
            round(end_price, 2),
            f"{round(increase_pct, 2)}%",
            default_investment,
            round(buy_commission, 2),
            round(sell_commission, 2),
            round(stamp_tax, 2),
            round(remaining_amount, 2),
            round(final_amount, 2),
            round(profit, 2),
            f"{round(return_pct, 2)}%"
        ])

        # ✅ 记录涨幅超过 5% 的股票
        if increase_pct > 5:
            high_gainers.append(stock_code)

    except Exception as e:
        print(f"获取股票 {stock_code} 数据时发生错误: {e}")

# ✅ **计算总收益和总收益率**
total_profit = total_final_value - total_investment
total_return_pct = (total_profit / total_investment) * 100 if total_investment > 0 else 0

# ✅ **方式 1: 终端打印对齐的表格**
table = Texttable()
table.set_cols_align(["c", "r", "r", "r", "r", "r", "r", "r", "r", "r", "r", "r"])  # 右对齐
table.set_cols_dtype(["t", "f", "f", "t", "i", "f", "f", "f", "f", "f", "f", "t"])  # 数据类型
table.set_cols_width([8, 10, 10, 8, 12, 8, 8, 8, 12, 14, 10, 10])  # 设置列宽

# ✅ 添加表头
table.add_rows([
    ["股票代码", "起始价格", "结束价格", "涨幅", "投资金额", "买入佣金", "卖出佣金", "印花税", "最终持有价值", "卖出后最终金额", "收益金额", "收益率"]
] + results)

print("\n投资收益计算结果：")
print(table.draw())

# ✅ **显示总收益和总收益率**
print(f"\n📊 总投资金额: {round(total_investment, 2)} 元")
print(f"📈 总最终价值: {round(total_final_value, 2)} 元")
print(f"💰 总收益: {round(total_profit, 2)} 元")
print(f"📊 总收益率: {round(total_return_pct, 2)}%")

# ✅ **方式 2: 保存为 CSV**
df_results = pd.DataFrame(results, columns=[
    "股票代码", "起始价格", "结束价格", "涨幅", "投资金额", "买入佣金", "卖出佣金", "印花税",
    "最终持有价值", "卖出后最终金额", "收益金额", "收益率"
])

# ✅ 添加总收益和总收益率（保留两位小数）
df_summary = pd.DataFrame([[
    "总计", "", "", "", round(total_investment, 2), "", "", "", round(total_final_value, 2), "", round(total_profit, 2), f"{round(total_return_pct, 2)}%"
]], columns=df_results.columns)

df_results = pd.concat([df_results, df_summary], ignore_index=True)

output_filename = f"stock_investment_results_with_tax.csv"
df_results.to_csv(output_filename, index=False, encoding="utf-8")

print(f"\n数据已保存为 {output_filename}")
