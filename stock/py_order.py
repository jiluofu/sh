import akshare as ak
import pandas as pd
import requests
import datetime

import utils.utils as st

# ======================== 获取当前时间戳 ========================
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# ======================== 获取 A 股所有股票的实时数据 ========================
df_stocks = ak.stock_zh_a_spot_em()

# **去除 ST 股票**
df_stocks = df_stocks[~df_stocks['名称'].str.contains('ST')].copy()

# **仅保留主板股票**
df_main_board = df_stocks[df_stocks['代码'].str.startswith(st.STOCK_LIST_WHITE_PRE)].copy()

# **判断涨停**
df_main_board['涨停幅度'] = df_main_board['名称'].apply(lambda x: 5.00 if 'ST' in x else 10.00)
df_limit_up = df_main_board[df_main_board['涨跌幅'] >= df_main_board['涨停幅度']].copy()

print(f"\n✅ 发现 {len(df_limit_up)} 只涨停股票，开始计算封单比...")

# ======================== 获取流通股数量和买一量，计算封单比 ========================
def get_circulating_shares(stock_code):
    """ 获取流通股数量 """
    try:
        df_info = ak.stock_individual_info_em(stock_code)
        circulating_shares = df_info.loc[df_info["item"] == "流通股", "value"].values[0]
        return float(circulating_shares)
    except Exception as e:
        print(f"⚠️ {stock_code} 获取流通股失败: {e}")
        return None

def get_buy_one_volume(stock_code):
    """ 获取实时买一量（手），转换为股 """
    try:
        formatted_code = st.format_stock_code(stock_code)
        url = f"http://qt.gtimg.cn/q={formatted_code}"
        response = requests.get(url)
        response.encoding = 'gbk'
        data = response.text.split('~')

        if len(data) > 10:
            buy_one_volume = int(data[10])  # 买一量（单位：手）
            return buy_one_volume * 100  # 转换为股
        else:
            return None
    except Exception as e:
        print(f"⚠️ {stock_code} 获取买一量失败: {e}")
        return None

# 遍历涨停股票，计算封单比
result_list = []
for _, row in df_limit_up.iterrows():
    stock_code = row["代码"]
    circulating_shares = get_circulating_shares(stock_code)
    buy_one_volume = get_buy_one_volume(stock_code)

    if circulating_shares and buy_one_volume:
        block_ratio = round((buy_one_volume / circulating_shares) * 100, 4)  # 百分比格式
    else:
        block_ratio = None

    print(f"📊 {stock_code} | 最新价: {row['最新价']} | 封单比: {block_ratio}%")

    result_list.append([stock_code, row["名称"], row["最新价"], row["涨跌幅"], row["涨停幅度"], circulating_shares, buy_one_volume, block_ratio])

# ======================== 输出封单比结果 ========================
df_block_ratio = pd.DataFrame(result_list, columns=["Stock Code", "Stock Name", "Latest Price", "Change %", "Limit Up %", "Circulating Shares", "Buy One Volume", "Block Ratio (%)"])

# **按照封单比降序排序**
df_block_ratio = df_block_ratio.sort_values(by="Block Ratio (%)", ascending=False)

print("\n📊 Block Ratio Results (Sorted by Descending Order):")
print(df_block_ratio)

# **带时间戳的文件名**
file_name = f"limit_up_block_ratio.csv"

# **保存到 CSV 文件**
df_block_ratio.to_csv(file_name, index=False, encoding="utf-8-sig")
print(f"\n✅ Results saved to `{file_name}`")

# ======================== 生成 `gold.txt` ========================
gold_stock_codes = df_block_ratio[df_block_ratio["Block Ratio (%)"] > 10]["Stock Code"].tolist()

if gold_stock_codes:
    gold_txt_path = "gold.txt"
    with open(gold_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(gold_stock_codes))
    print(f"\n🏆 `gold.txt` Created: {len(gold_stock_codes)} stocks saved")
else:
    print("\n❌ No stocks with Block Ratio > 10%")

print("\n✅ 完成所有任务！")