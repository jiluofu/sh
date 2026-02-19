import re

# 参数设置
# commission_rate = 0.0001  # 万1
# stamp_tax_rate = 0.001    # 千1（卖出）
commission_rate = 0  # 万1
stamp_tax_rate = 0    # 千1（卖出）

# 输入成交记录
text = """
已成 7.43 买 1000 T
已成 7.40 买 2000 T
已成 7.35 买 2000 T
已成 7.30 买 4000 T
已成 7.22 买 6000 T
已成 7.20 买 8000 T
"""

# 提取交易记录
records = re.findall(r"已成 ([\d.]+) (买|卖) (\d+)", text)

buy_total = 0.0
buy_shares = 0
buy_commission = 0.0

sell_total = 0.0
sell_shares = 0
sell_commission = 0.0
stamp_tax = 0.0

for price, typ, amount in records:
    price = float(price)
    amount = int(amount)

    if typ == "买":
        buy_total += price * amount
        buy_shares += amount
        buy_commission += price * amount * commission_rate
    elif typ == "卖":
        sell_total += price * amount
        sell_shares += amount
        sell_commission += price * amount * commission_rate
        stamp_tax += price * amount * stamp_tax_rate

# 计算剩余仓位与成本
net_shares = buy_shares - sell_shares
net_amount = buy_total + buy_commission - (sell_total - sell_commission - stamp_tax)

# 输出结果
if net_shares > 0:
    avg_cost = net_amount / net_shares
    print(f"📊 当前剩余持仓：{net_shares} 股")
    print(f"📈 平均买入成本（含万1佣金、千1印花税）：{avg_cost:.4f} 元")
elif net_shares == 0:
    print("📭 当前无持仓")
else:
    print(f"❌ 卖出股数大于买入股数，净持仓为负：{net_shares} 股")