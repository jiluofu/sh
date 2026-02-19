import numpy as np
import tensorflow as tf
import gc
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import os
import time

# ======================== 限制 TensorFlow 线程数 ========================
os.environ["TF_NUM_INTEROP_THREADS"] = "2"  # 限制 TensorFlow 任务调度线程数
os.environ["TF_NUM_INTRAOP_THREADS"] = "2"  # 限制 TensorFlow 计算线程数

# ======================== GPU 检测 & 限制显存增长 ========================
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)  # 限制显存增长
        print("✅ GPU 运行模式已启用")
    except RuntimeError as e:
        print(f"❌ GPU 配置失败: {e}")
else:
    print("⚠️ 未检测到 GPU, 使用 CPU 运行")

# ======================== 生成时间序列数据 ========================
def generate_data(seq_length=100, lookback=10):
    np.random.seed(42)  # 设定随机种子，保证复现性
    data = np.cumsum(np.random.randn(seq_length))  # 生成累积随机数据（模拟股价）

    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data.reshape(-1, 1))  # 归一化数据

    X, y = [], []
    for i in range(len(data_scaled) - lookback):
        X.append(data_scaled[i : i + lookback])  # 过去 lookback 天的数据
        y.append(data_scaled[i + lookback])  # 预测目标

    return np.array(X), np.array(y), scaler  # 返回数据和标准化器

# ======================== 构建 LSTM 模型 ========================
def build_lstm_model(lookback):
    """创建 LSTM 模型"""
    model = Sequential([
        LSTM(50, activation="relu", return_sequences=True, input_shape=(lookback, 1)),
        LSTM(50, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    return model

# ======================== 运行 LSTM 测试 ========================
def run_lstm_test():
    print("\n🚀 开始 LSTM 测试...")
    
    lookback = 10  # 用过去 10 天数据预测未来 1 天
    X, y, scaler = generate_data(seq_length=100, lookback=lookback)

    # 划分训练集和测试集
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    # **清理旧计算图，避免 TensorFlow 残留占用显存**
    tf.keras.backend.clear_session()
    gc.collect()

    # 构建 LSTM 模型
    model = build_lstm_model(lookback)

    # **训练 LSTM**
    print("🚀 训练 LSTM...")
    history = model.fit(X_train, y_train, epochs=10, batch_size=8, verbose=1)

    # **删除训练历史，释放 NumPy 内存**
    del history.history
    gc.collect()

    # **优化 @tf.function，减少 retracing**
    @tf.function(reduce_retracing=True)
    def predict_lstm(input_data):
        return model(input_data, training=False)

    # **预测未来数据**
    y_pred_scaled = predict_lstm(tf.convert_to_tensor(X_test, dtype=tf.float32))
    y_pred = scaler.inverse_transform(y_pred_scaled.numpy())  # 反归一化，恢复原始尺度

    print("\n✅ LSTM 测试完成！")
    print(f"🔍 预测的最后 5 个值: {y_pred[-5:].flatten()}")

    # **清理内存**
    del model, X_train, y_train, X_test, y_test, X, y, scaler, y_pred_scaled, y_pred
    tf.keras.backend.clear_session()
    gc.collect()

# ======================== 运行测试 ========================
run_lstm_test()
time.sleep(1)
run_lstm_test()
time.sleep(1)
run_lstm_test()
time.sleep(1)
run_lstm_test()
time.sleep(1)
run_lstm_test()
time.sleep(1)
run_lstm_test()
time.sleep(1)
run_lstm_test()



