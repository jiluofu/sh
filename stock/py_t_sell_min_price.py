# calc_min_sell_price.py

def calc_required_sell_price(buy_price, shares, target_profit, commission=0.00015, stamp_tax=0.001):
    """
    计算达到目标净利润所需的最低卖出价格
    :param buy_price: 买入单价（元）
    :param shares: 股数
    :param target_profit: 目标净利润（元）
    :param commission: 佣金比例（默认万1.5）
    :param stamp_tax: 印花税比例（默认千1）
    :return: 最小卖出价格
    """
    buy_amount = buy_price * shares
    buy_cost = buy_amount * (1 + commission)

    min_sell_price = (target_profit + buy_cost) / (shares * (1 - commission - stamp_tax))
    return round(min_sell_price, 4)


if __name__ == "__main__":
    # 示例输入
    buy_price = float(input("请输入买入价格（元）: "))
    shares = int(input("请输入买入股数: "))
    target_profit = float(input("请输入目标净利润（元）: "))

    min_price = calc_required_sell_price(buy_price, shares, target_profit)
    print(f"\n👉 若以 {buy_price} 元买入 {shares} 股，想要净赚 {target_profit} 元：")
    print(f"✅ 卖出价格至少需要达到：¥{min_price}")