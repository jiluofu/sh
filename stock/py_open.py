import akshare as ak
import pandas as pd
import numpy as np
import datetime

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# 股票代码前缀白名单
STOCK_LIST_WHITE_PRE = ('600', '601', '603', '000', '001', '002')

def get_realtime_auction_data():
    """获取东方财富实时竞价数据"""
    try:
        print("尝试使用东方财富接口获取实时竞价数据...")
        df = ak.stock_zh_a_spot_em()
        print(f"✅ 获取到 {len(df)} 只股票的实时竞价数据")
        return df
    except Exception as e:
        print(f"⚠️ 获取实时竞价数据失败：{e}")
        return pd.DataFrame()

def save_raw_data(df):
    """保存原始实时竞价数据到CSV，带时间戳"""
    filename = f"data/realtime_auction_{timestamp}.csv"
    try:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"✅ 实时竞价数据已保存至 {filename}")
    except Exception as e:
        print(f"⚠️ 保存实时竞价数据失败：{e}")


def filter_buy_candidates(df):
    """筛选适合跟进买入的股票"""
    print("🔍 正在筛选适合跟进买入的股票...")

    # 数据预处理：只保留符合代码前缀的股票
    df = df[df["代码"].astype(str).str.startswith(STOCK_LIST_WHITE_PRE)].copy()

    # 使用 NaN 作为缺失值填充，避免类型不兼容警告
    df.loc[:, "今开"] = pd.to_numeric(df["今开"], errors='coerce').fillna(np.nan)
    df.loc[:, "昨收"] = pd.to_numeric(df["昨收"], errors='coerce').fillna(np.nan)
    df.loc[:, "量比"] = pd.to_numeric(df["量比"], errors='coerce').fillna(np.nan)
    df.loc[:, "成交额"] = pd.to_numeric(df["成交额"], errors='coerce').fillna(np.nan)
    df.loc[:, "换手率"] = pd.to_numeric(df["换手率"], errors='coerce').fillna(np.nan)
    df.loc[:, "总市值"] = pd.to_numeric(df["总市值"], errors='coerce').fillna(np.nan)
    df.loc[:, "名称"] = df["名称"].astype(str).fillna("")

    # 计算正确的竞价涨幅，保留1位小数
    df.loc[:, "涨幅"] = ((df["今开"] - df["昨收"]) / df["昨收"] * 100).round(1).fillna(np.nan)

    # 高开强势股策略
    high_open = df[
        (df["今开"] > df["昨收"]) &  # 高开
        (df["涨幅"] > 3) &         # 涨幅超过3%
        (df["量比"] > 2) &         # 量比大于2
        (df["成交额"] > 1e8)       # 成交额大于1亿
    ].copy()
    high_open = high_open.sort_values(by=["量比", "涨幅", "成交额"], ascending=[False, False, False])

    # 涨停打开回封策略
    limit_open = df[
        (df["涨幅"] >= 9) &        # 涨幅接近涨停
        (df["量比"] > 2) &         # 量比较高
        (df["成交额"] > 2e8)       # 成交额较大
    ].copy()
    limit_open = limit_open.sort_values(by=["量比", "涨幅", "成交额"], ascending=[False, False, False])

    # 题材热点股策略
    hot_topic = df[
        (df["涨幅"] > 5) &         # 涨幅超过5%
        (df["成交额"] > 5e8)       # 成交额较大
    ].copy()
    hot_topic = hot_topic.sort_values(by=["量比", "涨幅", "成交额"], ascending=[False, False, False])

    # 集合竞价强势股策略
    strong_auction = df[
        (df["涨幅"] > 1) & (df["涨幅"] < 4) &  # 集合竞价涨幅在1%-4%之间
        (df["量比"] > 5) &                      # 量比大于5
        (~df["名称"].str.contains("ST")) &       # 非ST股票
        (df["总市值"] < 100e8)                   # 总市值小于100亿
    ].copy()
    strong_auction = strong_auction.sort_values(by=["量比", "涨幅", "成交额"], ascending=[False, False, False])

    # print(f"✅ 筛选出 {len(high_open)} 只高开强势股")
    # print(f"✅ 筛选出 {len(limit_open)} 只涨停打开回封股")
    # print(f"✅ 筛选出 {len(hot_topic)} 只题材热点股")
    print(f"✅ 筛选出 {len(strong_auction)} 只集合竞价强势股")

    return {
        # "高开强势股": high_open,
        # "涨停打开回封股": limit_open,
        # "题材热点股": hot_topic,
        "集合竞价强势股": strong_auction
    }

def save_to_csv(selected_stocks):
    """保存筛选结果到CSV，列顺序与打印一致"""
    columns = ["代码", "名称", "量比", "涨幅", "成交额", "换手率", "今开", "昨收", "总市值"]
    for category, df in selected_stocks.items():
        # 替换 NaN 为 空字符串，导出时保证字段不丢失
        df = df.fillna("")
        filename = f"{category}_{timestamp}.csv"
        try:
            df.to_csv(filename, index=False, encoding="utf-8-sig", columns=columns)
            print(f"✅ {category} 结果已保存至 {filename}")
        except Exception as e:
            print(f"⚠️ 保存 {category} 数据到CSV时出错：{e}")

# 获取实时竞价数据
auction_df = get_realtime_auction_data()


# 保存实时竞价原始数据
if not auction_df.empty:
    save_raw_data(auction_df)
else:
    print("⚠️ 没有获取到实时竞价数据，跳过保存。")

# 筛选跟进买入候选股
selected_stocks = filter_buy_candidates(auction_df)

# 打印筛选结果
columns = ["代码", "名称", "量比", "涨幅", "成交额", "换手率", "今开", "昨收", "总市值"]
for category, df in selected_stocks.items():
    print(f"\n=== {category} ===")
    print(df[columns].head(10))

# 保存到CSV
save_to_csv(selected_stocks)