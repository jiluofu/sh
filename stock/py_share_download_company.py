import akshare as ak
import pandas as pd
import os

# 配置
data_dir = "data"  # 数据保存目录
os.makedirs(data_dir, exist_ok=True)  # 确保目录存在

def get_main_board_stocks():
    """
    获取 A 股主板股票列表，只包括前缀为 '600', '601', '603', '000', '001', '002' 的股票
    """
    try:
        # 获取所有 A 股股票代码和公司名称
        stock_info_df = ak.stock_info_a_code_name()
        print("✅ 成功获取所有 A 股股票代码和公司名称")

        # 过滤指定前缀的股票代码
        # main_board_stocks = stock_info_df[stock_info_df["code"].str.startswith(('600', '601', '603', '000', '001', '002'))]
        main_board_stocks = stock_info_df.copy()
        print(f"✅ 过滤后主板股票数量: {len(main_board_stocks)}")

        return main_board_stocks

    except Exception as e:
        print(f"❌ 获取 A 股主板股票列表失败: {e}")
        return pd.DataFrame()

def get_stock_info(stock_code):
    """
    使用 akshare 获取股票的详细信息（名称和行业）
    """
    try:
        info_df = ak.stock_individual_info_em(symbol=stock_code)
        if info_df.empty:
            return None, None

        # 从返回的 DataFrame 中提取名称和行业
        stock_name = info_df.loc[info_df["item"] == "股票简称", "value"].values[0]
        industry_name = info_df.loc[info_df["item"] == "行业", "value"].values[0]

        return stock_name, industry_name

    except Exception as e:
        print(f"❌ 获取股票 {stock_code} 信息失败: {e}")
        return None, None

# 主程序
def main():
    stock_list = get_main_board_stocks()

    # 存放结果
    results = []

    # 遍历股票代码
    for index, row in stock_list.iterrows():
        stock_code = row["code"]
        print(f"🔄 正在处理股票代码: {stock_code}")

        # 获取股票名称和行业
        stock_name, industry_name = get_stock_info(stock_code)

        if stock_name and industry_name:
            print(f"✅ 成功获取 {stock_code} - {stock_name} - {industry_name}")
            results.append([stock_code, stock_name, industry_name])
        else:
            print(f"⚠️ 无法获取 {stock_code} 的名称或行业信息")

    # 保存到 CSV
    df = pd.DataFrame(results, columns=["股票代码", "股票名称", "行业名称"])
    output_path = os.path.join(data_dir, "main_board_stocks.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 数据已保存到: {output_path}")

if __name__ == "__main__":
    main()