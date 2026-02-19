#!/bin/bash

# 跑 Python 脚本生成 HTML
python3 ~/Documents/sh/stock/py_news.py

# 构建带 MIME 头的完整邮件体，临时保存
(
echo "Subject: 📬 Latest Business News (EN)"
echo "To: 1077246@qq.com"
echo "From: 1077246@qq.com"
echo "Content-Type: text/html; charset=UTF-8"
echo "MIME-Version: 1.0"
echo
cat /tmp/news_email.html
) > /tmp/news_mime.html

# 发送（这里不再用 -S 参数，直接传整个 MIME）
s-nail -t < /tmp/news_mime.html