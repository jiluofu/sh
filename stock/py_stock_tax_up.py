def calc_total_income(trades, exchange_rate):
    """
    计算多组股票交易的美元和人民币收入

    :param trades: 交易数据列表，每项为(dict): {"sell": 卖出价, "cost": 归属价, "qty": 数量}
    :param exchange_rate: 美元兑人民币汇率
    :return: 每组收入和总收入
    """
    results = []
    total_usd = 0
    total_rmb = 0

    for i, trade in enumerate(trades, 1):
        income_usd = (trade["sell"] - trade["cost"]) * trade["qty"]
        income_rmb = income_usd * exchange_rate
        total_usd += income_usd
        total_rmb += income_rmb
        results.append((i, income_usd, income_rmb))

    return results, total_usd, total_rmb


# 示例交易数据
trades = [
    {"sell": 115.83, "cost": 106.6003, "qty": 62},
    {"sell": 115.83, "cost": 77.0365, "qty": 62},
    {"sell": 115.83, "cost": 111.4028, "qty": 55},
    {"sell": 115.83, "cost": 113.5046, "qty": 30},
    {"sell": 115.83, "cost": 100.3141, "qty": 21},
    {"sell": 115.83, "cost": 100.4571, "qty": 39},
    {"sell": 115.83, "cost": 100.4571, "qty": 30}
]

exchange_rate = 7.1055

results, total_usd, total_rmb = calc_total_income(trades, exchange_rate)

# 输出结果
for i, usd, rmb in results:
    print(f"第{i}组：收入（美元）${usd:.2f}，收入（人民币）¥{rmb:.2f}")

print(f"\n总收入（美元）：${total_usd:.2f}")
print(f"总收入（人民币）：¥{total_rmb:.2f}")