# calc_stock_profit.py

def calc_profit(buy_price, sell_price, shares, commission_rate=0.00012, stamp_tax_rate=0.001):
    """
    计算股票交易的实际盈利
    :param buy_price: 买入价格（元）
    :param sell_price: 卖出价格（元）
    :param shares: 股票数量（股）
    :param commission_rate: 佣金率（默认万1.2）
    :param stamp_tax_rate: 印花税率（默认千1）
    :return: 净盈利（元）
    """
    buy_amount = buy_price * shares
    sell_amount = sell_price * shares

    # 买入成本（含佣金）
    buy_cost = buy_amount * (1 + commission_rate)

    # 卖出收入（扣除佣金和印花税）
    sell_income = sell_amount * (1 - commission_rate - stamp_tax_rate)

    # 净盈利
    profit = sell_income - buy_cost
    return round(profit, 2)

if __name__ == "__main__":
    try:
        buy_price = float(input("请输入买入价格（元）: "))
        sell_price = float(input("请输入卖出价格（元）: "))
        shares = int(input("请输入股票数量（股）: "))

        for multiplier in [1, 2, 3, 4]:
            total_shares = shares * multiplier
            profit = calc_profit(buy_price, sell_price, total_shares)
            print(f"📈 {multiplier}倍股数（{total_shares}股）净盈利：¥{profit}")

    except ValueError:
        print("输入有误，请确保输入的是数字。")