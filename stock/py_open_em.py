import requests
import pandas as pd
import numpy as np
from datetime import datetime
import akshare as ak

def get_avg_volumes(stock_codes, days=5):
    """获取每只股票的5日平均成交量"""
    avg_volume_map = {}
    # for code in stock_codes:
    #     try:
    #         df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
    #         df = df.tail(days)
    #         avg_vol = df["成交量"].astype(float).mean()
    #         avg_volume_map[code] = avg_vol
    #     except Exception:
    #         avg_volume_map[code] = np.nan
    return avg_volume_map

def get_preopen_rank():
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "b1",
        "fs": "m:0+t:6",
        "fields": "f12,f14,f2,f3,f62,f10"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    print(f"📡 抓取集合竞价数据：{datetime.now().strftime('%H:%M:%S')}")
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()

    if "data" not in data or "diff" not in data["data"]:
        print("⚠️ 未获取到集合竞价数据")
        return pd.DataFrame()

    df = pd.DataFrame(data["data"]["diff"])
    df.rename(columns={
        "f12": "代码",
        "f14": "名称",
        "f2": "最新价",
        "f3": "涨跌幅(%)",
        "f62": "竞价量(股)"
    }, inplace=True)

    df["涨跌幅(%)"] = df["涨跌幅(%)"].replace("-", np.nan).astype(float).fillna(0).round(2)
    df["竞价量(股)"] = df["竞价量(股)"].replace("-", np.nan).astype(float).fillna(0)
    df["竞价量(万股)"] = (df["竞价量(股)"] / 10000).round(2)

    # 🔍 加载5日均量
    stock_codes = df["代码"].tolist()
    print("📊 加载5日平均成交量...")
    avg_volume_map = get_avg_volumes(stock_codes)

    # 🧮 计算量比
    df["5日均量(股)"] = df["代码"].map(avg_volume_map)
    df["量比"] = (df["竞价量(股)"] / df["5日均量(股)"]).round(2)
    df["量比"] = df["量比"].replace([np.inf, -np.inf], np.nan).fillna(0)

    df = df.sort_values(by="涨跌幅(%)", ascending=False)

    return df[["代码", "名称", "最新价", "涨跌幅(%)", "竞价量(万股)", "量比"]]

# ========== 主程序 ==========
if __name__ == "__main__":
    df = get_preopen_rank()

    if not df.empty:
        print("\n📈 集合竞价前100名（按量比排序）")
        print(df.head(20).to_string(index=False))

        filename = f"竞价异动_含量比_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n✅ 结果已保存到 {filename}")
    else:
        print("⚠️ 没有获取到有效数据")