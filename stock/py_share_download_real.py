import akshare as ak
import pandas as pd
import os
import sys
from datetime import datetime
import time

import utils.utils as st

# 记录程序开始时间
start_time = time.time()

# === 设置目录 ===
BASE_DIR = "real"
today_str = datetime.today().strftime("%Y%m%d")

# === 读取命令行参数（是否下载全部）
download_all = "-all" in sys.argv

# === 获取全部 A股股票代码 ===
# stock_df = ak.stock_info_a_code_name()
# stock_codes = stock_df[stock_df["code"].str.startswith(st.STOCK_LIST_WHITE_PRE)]["code"].tolist()
# stock_codes = stock_df["code"].tolist()
stock_codes = ['601398', '601988']

if download_all:
    print("🌐 检测到 -all 参数，开始下载全部A股实时数据...")
    stock_codes = st.get_main_board_stocks()


# === 循环下载每只股票的实时逐笔数据 ===
for code in stock_codes:
    try:
        symbol = f"sh{code}" if code.startswith("6") else f"sz{code}"
        df = ak.stock_zh_a_tick_tx_js(symbol=symbol)
        if df is not None and not df.empty:
            # 创建子目录 real/股票代码/
            stock_dir = os.path.join(BASE_DIR, code)
            os.makedirs(stock_dir, exist_ok=True)

            # 保存为 real/股票代码/20250416.csv
            file_path = os.path.join(stock_dir, f"{today_str}.csv")
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            print(f"✅ 已保存 {code} 到 {file_path}")
        else:
            print(f"⚠️ 无数据 {code}")
    except Exception as e:
        print(f"❌ 下载失败 {code}: {e}")

st.print_elapsed_time(start_time)