from playwright.sync_api import sync_playwright
import time
import threading
import os
import pandas as pd
from datetime import datetime

# === 全局 ===
stop_monitoring = threading.Event()
last_snapshot = {}
symbol = "601398"  # 股票代码
order_dir = os.path.join("order", symbol)  # 股票子目录
os.makedirs(order_dir, exist_ok=True)
URL = f"https://quote.eastmoney.com/sh{symbol}.html"

# === 辅助函数 ===
def parse_number(text):
    """把数量字符串转成整数（单位：手）"""
    try:
        if text.endswith("万"):
            return int(float(text[:-1]) * 10000)
        else:
            return int(float(text))
    except:
        return 0

def get_today_order_file():
    """根据当前日期生成文件路径"""
    today_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(order_dir, f"{today_str}.csv")

def monitor_order_book():
    global last_snapshot

    while not stop_monitoring.is_set():
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(URL)

                page.wait_for_selector(".sider_quote_price table tbody tr")
                print("✅ 页面加载完成，开始监控挂单...\n")

                while not stop_monitoring.is_set():
                    if page.is_closed():
                        print("❌ 页面关闭，准备重新启动浏览器...")
                        break

                    try:
                        rows = page.query_selector_all(".sider_quote_price table tbody tr")
                        now_snapshot = {}

                        for idx, row in enumerate(rows):
                            cells = row.query_selector_all("td")
                            if len(cells) == 4:
                                position = cells[0].inner_text().strip()
                                price = cells[1].inner_text().strip()
                                volume = cells[2].inner_text().strip()

                                if position in ["买一", "买二", "买三", "买四", "买五"]:
                                    now_snapshot[position] = {
                                        "price": float(price) if price != "-" else 0,
                                        "volume": parse_number(volume)
                                    }

                        # 最新成交价
                        try:
                            latest_price_text = page.query_selector(".zxj").inner_text().strip()
                            latest_price = float(latest_price_text) if latest_price_text != "-" else None
                        except:
                            latest_price = None

                        # === 保存到CSV ===
                        record = {
                            "时间": time.strftime('%H:%M:%S'),
                            "最新成交价": latest_price,
                        }
                        for level in ["买一", "买二", "买三", "买四", "买五"]:
                            if level in now_snapshot:
                                record[f"{level}_价格"] = now_snapshot[level]["price"]
                                record[f"{level}_挂单手数"] = now_snapshot[level]["volume"]
                            else:
                                record[f"{level}_价格"] = None
                                record[f"{level}_挂单手数"] = None

                        order_file = get_today_order_file()
                        df_new = pd.DataFrame([record])
                        if not os.path.exists(order_file):
                            df_new.to_csv(order_file, index=False, encoding="utf-8-sig")
                        else:
                            df_new.to_csv(order_file, mode="a", header=False, index=False, encoding="utf-8-sig")

                        last_snapshot = now_snapshot
                        time.sleep(1)

                    except Exception as inner_e:
                        print(f"⚠️ 页面操作失败，自动重启页面: {inner_e}")
                        break

        except Exception as outer_e:
            print(f"🔥 Playwright崩溃，准备重新启动: {outer_e}")
            time.sleep(3)

def wait_for_enter():
    input("\n🔔 按回车键结束监控...\n")
    stop_monitoring.set()

# === 🔥 主程序 ===
monitor_thread = threading.Thread(target=monitor_order_book)
input_thread = threading.Thread(target=wait_for_enter)

monitor_thread.start()
input_thread.start()

monitor_thread.join()
input_thread.join()

print("✅ 程序已退出。")