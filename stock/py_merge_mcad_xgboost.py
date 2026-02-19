import pandas as pd

# ======================== 读取文件 ========================
file1_path = "macd_ma20_chip_status.csv"
file2_path = "xgboost_forecast.csv"
file3_path = "lstm_forecast.csv"
file4_path = "transformer_forecast.csv"
name_path = "data/main_board_stocks.csv"  # 新增：股票名称和行业名称文件

df_name_industry = pd.read_csv(name_path, dtype={'股票代码': str})  # 新增：股票名称和行业名称
df_macd = pd.read_csv(file1_path, dtype={'股票代码': str})
df_xgboost = pd.read_csv(file2_path, dtype={'股票代码': str})
df_lstm = pd.read_csv(file3_path, dtype={'股票代码': str})
df_transformer = pd.read_csv(file4_path, dtype={'股票代码': str})

print("📥 数据读取完成！")

# ======================== 过滤 MACD 数据 ========================
filtered_macd = df_macd[df_macd['MACD 检测结果'].isin(["MACD上方金叉 + 日线接近20日均线 🚀", "月线MACD上方金叉 ✅"])]
print(f"📊 MACD 筛选后剩余股票数：{len(filtered_macd)}")

# ======================== 合并股票名称和行业名称 ========================
merged_df = pd.merge(
    filtered_macd,
    df_name_industry[['股票代码', '股票名称', '行业名称']],
    on="股票代码",
    how="left"
)

print("🔄 股票名称和行业名称合并完成！")

# ======================== 合并 XGBoost 预测数据 ========================
merged_df = pd.merge(
    merged_df,
    df_xgboost[['股票代码', '截止日价格', '预测最后一天价格', '预测涨幅 (%)']],
    on="股票代码",
    how="left"
)

print("🔄 XGBoost 预测数据合并完成！")

# ======================== 合并 LSTM 预测数据 ========================
merged_df = pd.merge(
    merged_df,
    df_lstm[['股票代码', '预测涨幅 (%)']],
    on="股票代码",
    how="left",
    suffixes=('_XGBoost', '_LSTM')
)

print("🔄 LSTM 预测数据合并完成！")

# ======================== 合并 Transformer 预测数据 ========================
df_transformer.rename(columns={'预测涨幅 (%)': '预测涨幅 (%)_Transformer'}, inplace=True)

merged_df = pd.merge(
    merged_df,
    df_transformer[['股票代码', '预测涨幅 (%)_Transformer']],
    on="股票代码",
    how="left"
)

print("🔄 Transformer 预测数据合并完成！")

# ======================== 处理 NaN 值 ========================
merged_df.fillna(0, inplace=True)
merged_df['预测涨幅 (%)_XGBoost'] = merged_df['预测涨幅 (%)_XGBoost'].astype(float)
merged_df['预测涨幅 (%)_LSTM'] = merged_df['预测涨幅 (%)_LSTM'].astype(float)
merged_df['预测涨幅 (%)_Transformer'] = merged_df['预测涨幅 (%)_Transformer'].astype(float)

print("✅ NaN 值处理完成！")

# ======================== 计算上涨次数 ========================
merged_df['上涨次数'] = (
    (merged_df['预测涨幅 (%)_XGBoost'] > 0).astype(int) +
    (merged_df['预测涨幅 (%)_LSTM'] > 0).astype(int) +
    (merged_df['预测涨幅 (%)_Transformer'] > 0).astype(int)
)

print("📊 上涨次数计算完成！")

# ======================== 按优先级排序（上涨次数 -> XGBoost -> LSTM -> Transformer） ========================
merged_df = merged_df.sort_values(
    by=['上涨次数', '预测涨幅 (%)_XGBoost', '预测涨幅 (%)_LSTM', '预测涨幅 (%)_Transformer'],
    ascending=[False, False, False, False]
)

print("🔄 排序完成！")

# ======================== 保存 CSV 结果 ========================
output_path = "macd_ma20_status_xgboost_lstm_transformer.csv"
merged_df.drop(columns=['上涨次数'], inplace=True)  # 删除辅助列
merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ 分析完成，结果已保存到 {output_path}")

# ======================== 生成 TXT 文件 ========================
output_txt_path = "macd_ma20_status_xgboost_lstm_transformer.txt"
stock_codes = merged_df['股票代码'].tolist()
stock_codes_str = ",".join(stock_codes)

with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write(stock_codes_str)

print(f"✅ 股票代码已导出到 {output_txt_path}")