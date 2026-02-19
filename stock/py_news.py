from openai import OpenAI
import requests
from datetime import datetime
import subprocess


# === 配置 ===
NEWS_API_KEY = "9416ce00889149a79ea50fe71db7ed77"
GNEWS_API_KEY = "5f3b6bc697f30e497cfdc40361f7ac5b"  # https://gnews.io 注册后获得

# === NewsAPI 财经头条 ===
def fetch_newsapi():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "language": "en",
        "country": "us",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])
    for a in articles:
        a["source_from"] = "NewsAPI"
    return articles

# === GNews 精选关键词新闻 ===
def fetch_gnews():
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": (
            '"ICBC" OR "Bank of China" OR '
            '"工商银行" OR "中国银行"'
        ),
        "lang": "en",
        "token": GNEWS_API_KEY,
        "max": 20
    }
    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])
    for a in articles:
        a["source_from"] = "GNews"
    print(len(articles))
    return articles

# === 构建 HTML 内容 ===
def build_html(articles):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>财经新闻双来源日报</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }}
    h2 {{ color: #2c3e50; }}
    h3 {{ color: #2980b9; }}
    p {{ margin: 0.5em 0; }}
    hr {{ margin: 1.5em 0; }}
    .gnews-badge {{ color: gray; font-size: 0.9em; }}
  </style>
</head>
<body>
<h2>📈 财经新闻日报（{now}）</h2>
<hr>
"""

    for i, a in enumerate(articles, 1):
        title = a.get("title", "No title")
        desc = a.get("description", "No description available")
        url = a.get("url", "#")
        source_name = a.get("source", {}).get("name", "Unknown Source")
        pubtime = a.get("publishedAt", "Unknown Time")

        # 如果是 GNews，标注
        if a.get("source_from") == "GNews":
            source_name += ' <span class="gnews-badge">[GNews]</span>'

        html += f"""
<h3>{i}. <a href="{url}">{title}</a></h3>
<p><b>摘要：</b>{desc}</p>
<p><b>来源：</b>{source_name} | <b>发布时间：</b>{pubtime}</p>
<hr>
"""

    html += "</body></html>\n"
    return html

def send_email_via_s_nail():
    mime_path = "/tmp/news_mime.html"
    html_path = "/tmp/news_email.html"
    recipient = "1077246@qq.com"
    sender = "1077246@qq.com"

    # 拼接 MIME 邮件体
    with open(mime_path, "w", encoding="utf-8") as f:
        f.write(f"""Subject: 📬 Latest Business News (EN)
To: {recipient}
From: {sender}
Content-Type: text/html; charset=UTF-8
MIME-Version: 1.0

""")  # 两个换行之后是正文

        with open(html_path, "r", encoding="utf-8") as html_file:
            f.write(html_file.read().strip() + "\n")  # 防止尾部乱码 %

    # 使用 s-nail 发送邮件
    try:
        subprocess.run(["s-nail", "-t"], input=open(mime_path, "rb").read(), check=True)
        print("✅ 邮件发送成功！")
    except subprocess.CalledProcessError as e:
        print("❌ 邮件发送失败：", e)
# === 主程序 ===
if __name__ == "__main__":
    articles_newsapi = fetch_newsapi()
    articles_gnews = fetch_gnews()
    all_articles = articles_newsapi + articles_gnews

    html = build_html(all_articles)

    with open("/tmp/news_email.html", "w", encoding="utf-8") as f:
        f.write(html)

    # 发送邮件
    send_email_via_s_nail()

