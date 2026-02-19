import pandas as pd

# ======================== 读取文件 ========================
file1_path = "limit_up_block_ratio.csv"  # 涨停封单比数据
file2_path = "xgboost_forecast.csv"      # XGBoost 预测数据
file3_path = "lstm_forecast.csv"         # LSTM 预测数据
file4_path = "transformer_forecast.csv"  # Transformer 预测数据
name_path = "data/main_board_stocks.csv"  # 新增：股票名称和行业名称文件

df_name_industry = pd.read_csv(name_path, dtype={'股票代码': str})  # 新增：股票名称和行业名称
df_limit_up = pd.read_csv(file1_path, dtype={'Stock Code': str})[['Stock Code', 'Block Ratio (%)']]  # 只保留封单比信息
df_xgboost = pd.read_csv(file2_path, dtype={'股票代码': str})
df_lstm = pd.read_csv(file3_path, dtype={'股票代码': str})
df_transformer = pd.read_csv(file4_path, dtype={'股票代码': str})

print("📥 数据读取完成！")

# ======================== 过滤封单比超过 10% 的股票 ========================
df_limit_up = df_limit_up[df_limit_up['Block Ratio (%)'] > 10]
print(f"📊 封单比 > 10% 的股票数：{len(df_limit_up)}")

# ======================== 合并股票名称和行业名称 ========================
df_name_industry.rename(columns={'股票代码': 'Stock Code'}, inplace=True)
merged_df = pd.merge(
    df_limit_up,
    df_name_industry[['Stock Code', '股票名称', '行业名称']],
    on="Stock Code",
    how="left"
)


# ======================== 统一股票代码字段名称 ========================
df_xgboost.rename(columns={'股票代码': 'Stock Code'}, inplace=True)
df_lstm.rename(columns={'股票代码': 'Stock Code'}, inplace=True)
df_transformer.rename(columns={'股票代码': 'Stock Code'}, inplace=True)

# ======================== 合并 XGBoost 预测数据 ========================
merged_df = pd.merge(
    merged_df,
    df_xgboost[['Stock Code', '截止日价格', '预测最后一天价格', '预测涨幅 (%)']],
    on="Stock Code",
    how="left"
)

print("🔄 XGBoost 预测数据合并完成！")

# ======================== 合并 LSTM 预测数据 ========================
merged_df = pd.merge(
    merged_df,
    df_lstm[['Stock Code', '预测涨幅 (%)']],
    on="Stock Code",
    how="left",
    suffixes=('_XGBoost', '_LSTM')
)

print("🔄 LSTM 预测数据合并完成！")

# ======================== 合并 Transformer 预测数据 ========================
df_transformer.rename(columns={'预测涨幅 (%)': '预测涨幅 (%)_Transformer'}, inplace=True)

merged_df = pd.merge(
    merged_df,
    df_transformer[['Stock Code', '预测涨幅 (%)_Transformer']],
    on="Stock Code",
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
output_path = "limit_up_status_xgboost_lstm_transformer.csv"
merged_df.drop(columns=['上涨次数'], inplace=True)  # 删除辅助列
merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ 分析完成，结果已保存到 {output_path}")

# ======================== 生成 TXT 文件 ========================
output_txt_path = "limit_up_status_xgboost_lstm_transformer.txt"
stock_codes = merged_df['Stock Code'].tolist()
stock_codes_str = ",".join(stock_codes)

with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write(stock_codes_str)

print(f"✅ 股票代码已导出到 {output_txt_path}")