import os
import pandas as pd
import akshare as ak
from datetime import datetime
from tqdm import tqdm

# ======================== 配置 ========================
DATA_DIR = "data"
MIN_PE = 0
MAX_PE = 20
MAX_PB = 2.5
BACKTEST_DAYS = 20
OUTPUT_CSV = "value_backtest_results.csv"

# ======================== 获取估值数据 ========================
print("📊 获取实时估值数据...")
df_spot = ak.stock_zh_a_spot_em()
valuation_df = df_spot[["代码", "名称", "市盈率-动态", "市净率"]].copy()
valuation_df.columns = ["code", "name", "pe", "pb"]
valuation_df.dropna(subset=["pe", "pb"], inplace=True)

# 筛选低估值股票
valuation_df = valuation_df[
    (valuation_df["pe"] > MIN_PE) &
    (valuation_df["pe"] < MAX_PE) &
    (valuation_df["pb"] < MAX_PB)
].copy()

# 添加“被低估程度”指标（估值越小表示越低估）
valuation_df["undervalue_score"] = 1 / (valuation_df["pe"] * valuation_df["pb"])

# ======================== 加载行业信息 ========================
industry_path = os.path.join(DATA_DIR, "main_board_stocks.csv")
industry_df = pd.read_csv(industry_path, dtype=str)
industry_df.rename(columns={"股票代码": "code", "行业名称": "industry"}, inplace=True)
valuation_df = pd.merge(valuation_df, industry_df[["code", "industry"]], on="code", how="left")

# ======================== 回测函数 ========================
def backtest_kline(code, df):
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期").reset_index(drop=True)
    if len(df) <= BACKTEST_DAYS:
        return []

    buy_row = df.iloc[-(BACKTEST_DAYS + 1)]
    sell_row = df.iloc[-1]

    buy_price = buy_row["收盘"]
    buy_date = buy_row["日期"]
    sell_price = sell_row["收盘"]
    sell_date = sell_row["日期"]

    gain_pct = round((sell_price - buy_price) / buy_price * 100, 2)
    return [(buy_date.date(), sell_date.date(), buy_price, sell_price, gain_pct)]

# ======================== 遍历估值低的股票，执行回测 ========================
results = []

print("🚀 开始回测...")
for _, row in tqdm(valuation_df.iterrows(), total=len(valuation_df)):
    code = row["code"]
    name = row["name"]
    pe = row["pe"]
    pb = row["pb"]
    score = row["undervalue_score"]
    industry = row.get("industry", "")

    file_path = os.path.join(DATA_DIR, f"{code}.csv")
    if not os.path.exists(file_path):
        continue
    try:
        kline_df = pd.read_csv(file_path)
        if "日期" not in kline_df.columns or "收盘" not in kline_df.columns:
            continue
        for bt in backtest_kline(code, kline_df):
            results.append([
                code, name, industry, pe, pb, score
            ] + list(bt))
    except Exception as e:
        print(f"⚠️ {code} 读取失败: {e}")
        continue

# ======================== 保存结果 ========================
print("💾 保存结果中...")
df_result = pd.DataFrame(results, columns=[
    "股票代码", "股票名称", "行业名称", "PE", "PB", "被低估程度",
    "买入日期", "卖出日期", "买入价", "卖出价", "涨幅 (%)"
])

# 按照“被低估程度”降序排序
df_result = df_result.sort_values(by="被低估程度", ascending=False)

df_result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"✅ 完成，共 {len(results)} 条记录，已保存至 {OUTPUT_CSV}")