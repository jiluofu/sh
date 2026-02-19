#!/bin/bash

start_time=$(date +%s)  # 记录开始时间

# 获取命令行参数
ARG1=${1:-""}  # 如果没有提供第1个参数，默认为空字符串
ARG2=${2:-""}  # 如果没有提供第2个参数，默认为空字符串

cd ~/Documents/share

# 运行 Python 脚本，并传递参数

# 下载最新股票数据
python3 ~/Documents/sh/stock/py_share_download.py "$ARG1" "$ARG2"

# 建仓
python3 ~/Documents/sh/stock/py_position_gold.py "$ARG1" "$ARG2"
# 预测
python3 ~/Documents/sh/stock/py_xgboost.py "$ARG1" "$ARG2"
python3 ~/Documents/sh/stock/py_lstm_gpu.py "$ARG1" "$ARG2"
# python3 ~/Documents/sh/stock/py_transformer.py "$ARG1" "$ARG2"
# 合并
python3 ~/Documents/sh/stock/py_merge_mcad_xgboost.py

# # 封单
# python3 ~/Documents/sh/stock/py_order.py
# # 预测
# python3 ~/Documents/sh/stock/py_xgboost.py "$ARG1" "$ARG2"
# python3 ~/Documents/sh/stock/py_lstm_gpu.py "$ARG1" "$ARG2"
# python3 ~/Documents/sh/stock/py_transformer.py "$ARG1" "$ARG2"
# # 合并
# python3 ~/Documents/sh/stock/py_merge_limit_xgboost.py

# # 尾盘eob
# python3 ~/Documents/sh/stock/py_eob.py
# # 预测
# python3 ~/Documents/sh/stock/py_xgboost.py "$ARG1" "$ARG2"
# python3 ~/Documents/sh/stock/py_lstm_gpu.py "$ARG1" "$ARG2"
# python3 ~/Documents/sh/stock/py_transformer.py "$ARG1" "$ARG2"
# # 合并
# python3 ~/Documents/sh/stock/py_merge_eob_xgboost.py

# # 筹码
# python3 ~/Documents/sh/stock/py_chip.py


end_time=$(date +%s)  # 记录结束时间
elapsed_time=$((end_time - start_time))  # 计算运行时间

hours=$((elapsed_time / 3600))
minutes=$(((elapsed_time % 3600) / 60))
seconds=$((elapsed_time % 60))

echo "脚本运行总时间: ${hours}小时 ${minutes}分钟 ${seconds}秒"

