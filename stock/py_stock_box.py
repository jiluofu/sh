import pandas as pd
import numpy as np
import os

# 定义不同策略的突破周期和均线周期
strategies = {
    "短线": {"days": 20, "ma_period": 50},
    "波段": {"days": 50, "ma_period": 100},
    "长期": {"days": 100, "ma_period": 200},
}

# 数据目录
data_dir = "data"

# 获取本地数据目录下的所有股票文件
stock_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

# 结果存储
all_results = {}

# 遍历所有策略
for strategy_name, params in strategies.items():
    days = params["days"]
    ma_period = params["ma_period"]
    print(f"\n🚀 执行策略：{strategy_name} | 突破周期：{days} 天 | 均线周期：{ma_period} 天")

    # 定义箱体突破+均线策略
    def detect_box_breakout_with_ma_from_csv(file_path):
        """ 从本地 CSV 文件检测箱体突破，并结合均线判断有效性 """
        stock_code = file_path.replace(".csv", "")  # 提取股票代码
        df = pd.read_csv(os.path.join(data_dir, file_path))

        # **自动检测列名**
        col_close = "收盘" if "收盘" in df.columns else "收盘价"
        col_volume = "成交量" if "成交量" in df.columns else "成交额"

        # 确保数据足够计算均线
        if len(df) < ma_period:
            return None

        # 计算均线
        df["MA"] = df[col_close].rolling(ma_period).mean()

        # 取最近 `days` 天数据
        df_recent = df.iloc[-days:]

        # 计算箱体区间
        box_high = df_recent[col_close].max()  # 最高点
        box_low = df_recent[col_close].min()   # 最低点
        latest_close = df_recent.iloc[-1][col_close]  # 最新收盘价
        latest_ma = df.iloc[-1]["MA"]  # 最新均线值
        latest_volume = df_recent.iloc[-1][col_volume]  # 最新成交量
        prev_volume = df_recent.iloc[-2][col_volume]  # 前一天成交量

        # 判断突破
        breakout_up = latest_close > box_high  # 上破
        breakout_down = latest_close < box_low  # 下破
        volume_increase = latest_volume > prev_volume * 1.5  # 成交量放大
        above_ma = latest_close > latest_ma  # 价格站上均线

        # **打印每只股票的箱体范围**
        # print(f"\n📊 股票 {stock_code} 的箱体范围（{strategy_name} 策略）：")
        # print(f"   - 上沿（高点）：{box_high}")
        # print(f"   - 下沿（低点）：{box_low}")
        # print(f"   - 最新收盘价：{latest_close}")
        # print(f"   - {ma_period} 日均线：{latest_ma:.2f}")

        if breakout_up and volume_increase and above_ma:
            print("   ✅ 发生 **向上突破**（突破箱体上沿 + 放量 + 站上均线）")
            return {"stock": stock_code, "breakout": "up", "high": box_high, "close": latest_close, "MA": latest_ma}
        elif breakout_down and volume_increase:
            print("   ❌ 发生 **向下突破**（跌破箱体下沿 + 放量）")
            return {"stock": stock_code, "breakout": "down", "low": box_low, "close": latest_close, "MA": latest_ma}
        else:
            # print("   ⚠️ 未发生突破")
            return None

    # 遍历本地 CSV 文件，查找符合条件的股票
    breakout_stocks = [detect_box_breakout_with_ma_from_csv(file) for file in stock_files]
    breakout_stocks = [b for b in breakout_stocks if b is not None]

    # 转换为 DataFrame 并存储结果
    df_result = pd.DataFrame(breakout_stocks)

    # 存储不同策略的结果
    all_results[strategy_name] = df_result

    # 如果有符合条件的股票，打印出来
    if not df_result.empty:
        print("\n📈 符合箱体突破 + 均线条件的股票（策略：{}）：".format(strategy_name))
        print(df_result)
        file_path = f"箱体突破筛选结果_{strategy_name}.csv"
        df_result.to_csv(file_path, index=False, encoding="utf-8")
        print("\n✅ 结果已保存至：{}".format(file_path))
    else:
        print("\n🚫 没有符合条件的股票（策略：{}）".format(strategy_name))

print("\n🎉 所有策略执行完毕！请查看 CSV 文件。")