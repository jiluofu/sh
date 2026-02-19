import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.family'] = 'Source Han Sans SC'

# === 设置数据目录 ===
real_dir = "real"

# === 遍历股票代码子目录 ===
for code in os.listdir(real_dir):
    code_path = os.path.join(real_dir, code)
    if not os.path.isdir(code_path):
        continue

    # 获取该目录下最新日期的CSV文件
    csv_files = [f for f in os.listdir(code_path) if f.endswith(".csv")]
    if not csv_files:
        continue
    latest_file = sorted(csv_files)[-1]
    file_path = os.path.join(code_path, latest_file)

    try:
        # === 1. 加载逐笔数据 ===
        df = pd.read_csv(file_path)
        df["成交时间"] = pd.to_datetime(df["成交时间"], format="%H:%M:%S")

        # === 2. 聚合为分钟级数据 ===
        df["分钟"] = df["成交时间"].dt.floor("min")
        minute_data = df.groupby("分钟").agg(
            均价=("成交价格", "mean"),
            总成交量=("成交量", "sum"),
            买盘成交量=("成交量", lambda s: s[df.loc[s.index, "性质"] == "买盘"].sum()),
            卖盘成交量=("成交量", lambda s: s[df.loc[s.index, "性质"] == "卖盘"].sum())
        ).reset_index()

        # === 3. 主力密集成交区分析 ===
        volume_by_price = df.groupby("成交价格")["成交量"].sum()
        main_price = volume_by_price.idxmax()
        main_volume = volume_by_price.max()

        # === 4. 低吸挂单建议价位 ===
        suggest_low1 = round(main_price - 0.03, 2)
        suggest_low2 = round(minute_data["均价"].min() - 0.01, 2)

        # === 5. 判断低吸时段 ===
        low_volume_zone = minute_data[minute_data["均价"] <= suggest_low1]
        if not low_volume_zone.empty:
            suggested_time_range = (
                low_volume_zone["分钟"].min().strftime("%H:%M"),
                low_volume_zone["分钟"].max().strftime("%H:%M")
            )
        else:
            suggested_time_range = ("无明显区间", "建议观察盘口实时低点")

        # === 6. 输出策略建议 ===
        print(f"\n📈 股票代码：{code} - 日期：{latest_file.replace('.csv', '')}")
        print("📊 做T低吸策略建议")
        print(f"🔽 建议挂单价位1（主力价 - 0.03）：¥{suggest_low1}")
        print(f"🔽 建议挂单价位2（今日低均价 - 0.01）：¥{suggest_low2}")
        print(f"🕒 建议挂单时间窗口：{suggested_time_range[0]} ~ {suggested_time_range[1]}")
        print(f"🎯 操作建议：提前挂单 + 观察分时止跌 + 成交量变化 + 目标高抛")

        # # === 7. 更清晰的可视化图表 ===
        # plt.figure(figsize=(16, 6))
        # ax1 = plt.gca()

        # # 均价折线
        # ax1.plot(minute_data["分钟"], minute_data["均价"], label="成交均价", color="blue", linewidth=2)

        # # 主力成本线 & 低吸建议线
        # ax1.axhline(main_price, color="red", linestyle="--", linewidth=1.2, label=f"主力价位 ¥{main_price}")
        # ax1.axhline(suggest_low1, color="green", linestyle="--", linewidth=1.2, label=f"低吸建议价 ¥{suggest_low1}")

        # # 成交量柱状图（副轴）
        # ax2 = ax1.twinx()
        # ax2.bar(minute_data["分钟"], minute_data["总成交量"] / 1000, width=0.0008, color="gray", alpha=0.3, label="成交量（千手）")

        # # 图表美化
        # ax1.set_title(f"{code} - {latest_file.replace('.csv', '')} 做T分析图", fontsize=14)
        # ax1.set_xlabel("时间", fontsize=12)
        # ax1.set_ylabel("价格", fontsize=12)
        # ax2.set_ylabel("成交量（千手）", fontsize=12)

        # # 时间刻度优化：只显示整点
        # xticks = minute_data["分钟"].dt.strftime("%H:%M").tolist()
        # ax1.set_xticks(ax1.get_xticks()[::5])  # 只保留部分刻度
        # plt.xticks(rotation=45)

        # # 图例整合（合并双轴图例）
        # lines_1, labels_1 = ax1.get_legend_handles_labels()
        # lines_2, labels_2 = ax2.get_legend_handles_labels()
        # ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left", fontsize=10)

        # plt.grid(True, linestyle="--", alpha=0.3)
        # plt.tight_layout()
        # plt.show()

    except Exception as e:
        print(f"❌ 分析失败：{code} - 错误：{e}")