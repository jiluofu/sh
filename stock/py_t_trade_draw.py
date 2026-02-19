import numpy as np
import matplotlib.pyplot as plt

# 参数配置
def calculate_profit(x):
    sell_price = x + 0.03
    shares = 10000
    commission_rate = 0.00012  # 万1.2
    stamp_tax_rate = 0.001  # 千1

    buy_amount = x * shares
    sell_amount = sell_price * shares

    # 成本
    buy_fee = buy_amount * commission_rate
    sell_fee = sell_amount * commission_rate
    stamp_tax = sell_amount * stamp_tax_rate

    profit = sell_amount - sell_fee - stamp_tax - buy_amount - buy_fee
    return profit

# 生成数据（限制在7.2到8之间）
x_values = np.linspace(7.2, 8.0, 100)
y_values = [calculate_profit(x) for x in x_values]

# 绘图
plt.figure(figsize=(10,6))
plt.plot(x_values, y_values, label="Net Profit vs Price", marker='o', markersize=3)
plt.title("Net Profit when Stock Price Increases by 0.03 (x in [7.2,8.0])")
plt.xlabel("Stock Price (x)")
plt.ylabel("Net Profit (y)")
plt.grid(True)
plt.legend()
plt.show()
