import requests
import re
import json
import subprocess
import sys
import os

# === 获取下载目录参数 ===
if len(sys.argv) < 3:
    print("❌ 用法: python download_bilibili.py https://www.bilibili.com/video/BV1n14y1Y7va /path/to/download_dir")
    sys.exit(1)

url = sys.argv[1]
download_dir = sys.argv[2]

if not os.path.isdir(download_dir):
    print(f"❌ 目录不存在: {download_dir}")
    sys.exit(1)

# 视频合集页面（可自行修改）
headers = {
    "User-Agent": "Mozilla/5.0"
}

# 获取 HTML
resp = requests.get(url, headers=headers)
html = resp.text

# 提取 INITIAL_STATE JSON
match = re.search(r'window\.__INITIAL_STATE__=({.*?});\(', html)
if not match:
    print("❌ 没有找到 INITIAL_STATE")
    sys.exit(1)

try:
    data = json.loads(match.group(1))
    sections = data['sectionsInfo']['sections']
    if not sections:
        print("❌ 没有分集信息 sections")
        sys.exit(1)

    episodes = sections[0]['episodes']

    for ep in episodes:
        bvid = ep['bvid']
        title = ep['title']
        video_url = f"https://www.bilibili.com/video/{bvid}"
        print(f"🎬 正在下载：{title} - {video_url}")
        
        # 调用 you-get，指定输出目录
        subprocess.run([
            "you-get",
            "--debug",
            "-o", download_dir,
            video_url
        ])

except Exception as e:
    print("❌ 下载失败：", e)