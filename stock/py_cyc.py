import os
import pandas as pd
from datetime import datetime
import akshare as ak

import utils.utils as st

# ========== ✅ 全局配置 ==========
DATA_DIR = "data"
# START_DATE = "2023-10-01"
START_DATE = "2025-03-01"
END_DATE = "2025-04-14"
# ================================

def get_all_a_stock_codes():
    """获取全部A股代码"""
    stock_df = ak.stock_info_a_code_name()
    return stock_df["code"].tolist()

def load_stock_data(code, start_date, end_date):
    """从CSV加载数据并筛选日期"""
    path = os.path.join(DATA_DIR, f"{code}.csv")
    if not os.path.exists(path):
        return None

    try:
        df = pd.read_csv(path)
        df["日期"] = pd.to_datetime(df["日期"])
        df = df[(df["日期"] >= start_date) & (df["日期"] <= end_date)].copy()
        df = df.sort_values("日期").reset_index(drop=True)
        if "收盘" not in df.columns:
            return None
        return df
    except Exception as e:
        print(f"⚠️ 读取失败: {code}, {e}")
        return None

def detect_cyc_buy_signals(df):
    """识别 CYC13 买入信号"""
    df["cyc13"] = df["收盘"].rolling(window=13).mean()
    df["deviation"] = (df["收盘"] - df["cyc13"]) / df["cyc13"]
    df["prev_dev"] = df["deviation"].shift(1)
    df["buy_signal"] = (df["prev_dev"] < -0.15) & (df["deviation"] >= -0.15)
    return df[df["buy_signal"]][["日期", "收盘"]]

def scan_all_stocks_for_cyc_signals(start_date_str, end_date_str):
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)
    # all_codes = get_all_a_stock_codes()
    all_codes = st.get_main_board_stocks()

    # 读取股票名称和行业信息
    stock_info_path = os.path.join(DATA_DIR, "main_board_stocks.csv")
    stock_info_df = pd.read_csv(stock_info_path, dtype={"股票代码": str})
    stock_info_df = stock_info_df.rename(columns={"行业名称": "所属行业"})  # 重命名兼容列名

    result = []
    for code in all_codes:
        df = load_stock_data(code, start_date, end_date)
        if df is not None and len(df) >= 14:
            buy_signals = detect_cyc_buy_signals(df)
            if not buy_signals.empty:
                stock_row = stock_info_df.loc[stock_info_df["股票代码"] == code]
                name = stock_row["股票名称"].values[0] if not stock_row.empty else "未知"
                industry = stock_row["所属行业"].values[0] if not stock_row.empty else "未知"
                print(f"✅ 命中: {code} {name}（{industry}），共 {len(buy_signals)} 个买点")

                for _, row in buy_signals.iterrows():
                    result.append({
                        "股票代码": code,
                        "股票名称": name,
                        "所属行业": industry,
                        "买入日期": row["日期"].strftime("%Y-%m-%d"),
                        "买入价格": round(row["收盘"], 2)
                    })

    result_df = pd.DataFrame(result)
    if not result_df.empty:
        result_df = result_df[["股票代码", "股票名称", "所属行业", "买入日期", "买入价格"]]

    return result_df

# === 主执行入口 ===
if __name__ == "__main__":
    df_result = scan_all_stocks_for_cyc_signals(START_DATE, END_DATE)

    if not df_result.empty:
        # ✅ 排序：先按买入日期降序，再按所属行业升序
        df_result = df_result.sort_values(by=["买入日期", "所属行业"], ascending=[False, True])

        # ✅ 保存
        df_result.to_csv("cyc_signals_result.csv", index=False, encoding="utf-8-sig")

    print(f"\n🎯 总共命中 {len(df_result)} 条买入记录，结果已保存至 cyc_signals_result.csv")