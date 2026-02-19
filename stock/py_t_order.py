from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 1. 启动浏览器
driver = webdriver.Chrome()
driver.get("https://quote.eastmoney.com/sh601398.html")

# 2. 注入 WebSocket Hook
ws_hook_script = """
(function() {
    const origWebSocket = window.WebSocket;
    window.WebSocket = function(...args) {
        const ws = new origWebSocket(...args);
        ws.addEventListener('message', function(event) {
            console.log('📥 WebSocket推送:', event.data);
            setTimeout(() => {
                try {
                    const buy1 = document.querySelector('挂单买一元素selector').innerText;
                    const sell1 = document.querySelector('挂单卖一元素selector').innerText;
                    console.log('🛒 买一:', buy1, '🛒 卖一:', sell1);
                } catch (e) {
                    console.log('读取DOM挂单出错', e);
                }
            }, 0);
        });
        return ws;
    };
})();
"""
driver.execute_script(ws_hook_script)

print("✅ 注入完成，监听中...")

# 3. 持续运行
while True:
    time.sleep(1)