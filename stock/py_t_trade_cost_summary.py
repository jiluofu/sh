import re

# === 原始成交文本记录 ===
# 0424
# text = """
# 已成 7.86 买 10000 T
# 已成 7.86 买 10000 T
# 已成 7.86 买 10000 T
# 已成 7.85 买 10000 T
# 已成 7.85 买 10000 T
# 已成 7.84 买 10000 T
# 已成 7.81 买 10000 T
# 已成 7.80 买 10000 T
# 已成 7.80 买 10000 T
# 已成 7.79 买 10000 T
# 已成 7.78 买 10000 T
# 已成 7.75 买 10000 T
# 已成 7.73 买 10000 T
# 已成 7.71 买 10000 T
# 已成 7.79 卖 70000 T
# 已成 7.72 买 10000 T
# 已成 7.71 买 10000 T
# 已成 7.70 买 40000 T
# 已成 7.69 买 10000 T
# 已成 7.69 买 5000 T
# 已成 7.70 买 5000 T
# 已成 7.71 买 1000 T
# 已成 7.69 买 1000 T
# 已成 7.70 买 2000 T
# 已成 7.68 买 5000 T
# 已成 7.68 买 5000 T
# 已成 7.65 买 5000 T
# """

text = """
已成 7.7609 买 143000 T
已成 7.55 卖 20000 T
已成 7.55 卖 5000 T
已成 7.55 卖 30000 T
已成 7.55 卖 20000 T
已成 7.55 卖 5000 T
已成 7.55 卖 5000 T
已成 7.56 卖 5000 T
已成 7.56 卖 5000 T
已成 7.58 卖 5000 T
已成 7.58 卖 5000 T
已成 7.57 卖 6000 T
已成 7.58 卖 5000 T
已成 7.58 卖 4000 T
已成 7.57 卖 3000 T
已成 7.58 卖 5000 T
已成 7.58 卖 10000 T
已成 7.59 卖 5000 T
"""

# 0729
text = """
已成 7.45 卖 10000
已成 7.44 卖 75300
已成 7.55 买 22300 T
已成 7.51 买 5000 T
已成 7.50 买 10000 T
已成 7.50 买 10000 T
已成 7.49 买 5000 T
已成 7.49 买 10000 T
已成 7.49 买 10000 T
已成 7.48 买 10000 T
已成 7.48 买 3000 T
"""

# 0729
text = """
已成 7.44 卖 32000 T
已成 7.48 买 2000 T
已成 7.46 买 3000 T
已成 7.45 买 5000 T
已成 7.43 买 5000 T
已成 7.43 买 2000 T
已成 7.43 买 5000 T
已成 7.43 买 10000 T
"""


# === 手续费设置 ===
commission_rate = 0.0001  # 万1.0（买入/卖出）
stamp_tax_rate = 0.001     # 千1（仅卖出）

# === 解析记录 ===
pattern = r"已成\s+([\d.]+)\s+(买|卖)\s+(\d+)"
matches = re.findall(pattern, text)

records = [{
    "price": float(price),
    "type": "buy" if act == "买" else "sell",
    "shares": int(shares)
} for price, act, shares in matches]

# ✅ 自动排序：先买后卖（防止卖空）
records.sort(key=lambda x: 0 if x["type"] == "buy" else 1)

# === 持仓 + 盈亏计算 ===
total_shares = 0
total_cost = 0.0
total_realized_profit = 0.0
sell_details = []

print("\n📋 逐笔交易盈亏记录（仅统计卖出）：")
print("-" * 40)

for r in records:
    price = r["price"]
    shares = r["shares"]

    if r["type"] == "buy":
        cost = price * shares * (1 + commission_rate)
        total_cost += cost
        total_shares += shares
    else:  # 卖出
        if total_shares < shares:
            raise ValueError("⚠️ 卖出数量超过当前持仓，发生卖空！")
        avg_cost = total_cost / total_shares
        sell_net = price * shares * (1 - commission_rate - stamp_tax_rate)
        profit = sell_net - (avg_cost * shares)
        total_realized_profit += profit

        # 更新成本与持仓
        total_cost -= avg_cost * shares
        total_shares -= shares

        # 记录详细卖出交易
        sell_details.append({
            "price": price,
            "shares": shares,
            "profit": profit
        })

        print(f"✅ 卖出 {shares} 股 @ {price}，盈亏：¥{profit:.2f}")

# === 输出当前持仓 ===
print("\n📌 当前持仓状态：")
if total_shares > 0:
    avg_price = total_cost / total_shares
    print(f"✅ 当前持股：{total_shares} 股")
    print(f"✅ 当前加权成本价（含手续费）：¥{avg_price:.4f}")
else:
    print("📭 当前无持仓")

# === 输出总盈亏 ===
print(f"\n💰 今日累计已实现盈亏：¥{total_realized_profit:.2f}")

# === 找出亏最多的那笔交易（如有） ===
max_loss = min(sell_details, key=lambda x: x["profit"], default=None)
if max_loss and max_loss["profit"] < 0:
    print(f"\n📉 其中最大亏损来自：卖出 {max_loss['shares']} 股 @ {max_loss['price']}，亏损 ¥{abs(max_loss['profit']):.2f}")