#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import requests
from xhshow import Xhshow

FEED_API = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def parse_cookie_string(cookie: str) -> dict:
    result = {}
    for part in cookie.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def parse_note_url(url: str):
    url = unquote(url.strip())

    m = re.search(r"/(?:explore|discovery/item)/([0-9a-fA-F]+)", url)
    if not m:
        m = re.search(r"/user/profile/[^/]+/([0-9a-fA-F]+)", url)

    if not m:
        raise ValueError("无法从链接中提取作品ID，请确认是小红书笔记链接")

    note_id = m.group(1)
    query = parse_qs(urlparse(url).query)
    xsec_token = query.get("xsec_token", [""])[0]

    return note_id, xsec_token


def make_payload(note_id: str, xsec_token: str) -> dict:
    payload = {
        "source_note_id": note_id,
        "image_formats": ["jpg", "webp", "avif"],
        "extra": {"need_body_topic": "1"},
        "xsec_source": "pc_feed",
    }

    if xsec_token:
        payload["xsec_token"] = xsec_token

    return payload


def signed_post_feed(note_id: str, xsec_token: str, cookie: str) -> dict:
    cookies = parse_cookie_string(cookie)

    if "a1" not in cookies:
        raise RuntimeError("Cookie 里缺少 a1，无法生成 x-s 签名")

    payload = make_payload(note_id, xsec_token)

    signer = Xhshow()
    sign_headers = signer.sign_headers_post(
        uri=FEED_API,
        cookies=cookies,
        payload=payload,
    )

    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://www.xiaohongshu.com",
        "Referer": f"https://www.xiaohongshu.com/explore/{note_id}",
        **sign_headers,
    }

    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    r = requests.post(
        FEED_API,
        headers=headers,
        cookies=cookies,
        data=body.encode("utf-8"),
        timeout=25,
    )

    if r.status_code != 200:
        raise RuntimeError(f"接口请求失败 HTTP {r.status_code}\n{r.text[:1000]}")

    try:
        data = r.json()
    except Exception as e:
        raise RuntimeError(f"接口返回不是 JSON：{e}\n{r.text[:1000]}")

    if not data.get("success", False):
        raise RuntimeError(
            "接口返回失败：\n"
            + json.dumps(data, ensure_ascii=False, indent=2)[:2000]
        )

    return data


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk(x)


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\n\r\t]+', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "xhs_video"


def extract_title(data: dict, note_id: str) -> str:
    for d in walk(data):
        for key in ("title", "desc", "display_title"):
            val = d.get(key)
            if isinstance(val, str) and val.strip():
                return sanitize_filename(val.strip())[:80]

    return note_id


def score_video_url(url: str) -> int:
    u = url.lower()
    score = 0

    if ".mp4" in u:
        score += 100
    if "master" in u:
        score += 50
    if "h264" in u:
        score += 20
    if "h265" in u:
        score += 10
    if "watermark" in u or "wm" in u:
        score -= 100

    return score


def extract_video_urls(data: dict):
    urls = []

    for d in walk(data):
        for key in ("master_url", "backup_urls", "url", "video_url"):
            val = d.get(key)

            if isinstance(val, str) and val.startswith("http"):
                urls.append(val)

            elif isinstance(val, list):
                urls.extend(
                    x for x in val
                    if isinstance(x, str) and x.startswith("http")
                )

    urls = [
        u for u in dict.fromkeys(urls)
        if ("xhscdn" in u or ".mp4" in u or "video" in u.lower())
    ]

    urls.sort(key=score_video_url, reverse=True)

    return urls


def unique_output_path(out_dir: Path, title: str) -> Path:
    out_path = out_dir / f"{title}.mp4"

    i = 1
    while out_path.exists():
        out_path = out_dir / f"{title}_{i}.mp4"
        i += 1

    return out_path


def download(url: str, out_path: Path, cookie: str):
    cookies = parse_cookie_string(cookie)

    headers = {
        "User-Agent": UA,
        "Referer": "https://www.xiaohongshu.com/",
        "Accept": "*/*",
    }

    with requests.get(
        url,
        headers=headers,
        cookies=cookies,
        stream=True,
        timeout=60,
    ) as r:
        r.raise_for_status()

        total = int(r.headers.get("content-length", "0") or 0)
        tmp = out_path.with_suffix(out_path.suffix + ".part")
        got = 0

        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue

                f.write(chunk)
                got += len(chunk)

                if total:
                    print(
                        f"\r下载中 {got / total * 100:.1f}%  "
                        f"{got / 1024 / 1024:.1f}/"
                        f"{total / 1024 / 1024:.1f} MB",
                        end="",
                    )
                else:
                    print(f"\r下载中 {got / 1024 / 1024:.1f} MB", end="")

        tmp.rename(out_path)
        print(f"\n完成：{out_path}")


def main():
    p = argparse.ArgumentParser(
        description="独立小红书视频下载脚本：签名请求 + 提取视频直链 + 下载"
    )

    p.add_argument("url", help="小红书笔记链接")
    p.add_argument(
        "--cookie",
        required=True,
        help="完整 Cookie，例如：a1=...; web_session=...; webId=...",
    )
    p.add_argument("--dir", required=True, help="下载目录")
    p.add_argument(
        "--debug-json",
        action="store_true",
        help="保存接口返回 JSON，便于排错",
    )

    args = p.parse_args()

    out_dir = Path(args.dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    note_id, xsec_token = parse_note_url(args.url)

    print("note_id:", note_id)
    print("xsec_token:", (xsec_token[:24] + "...") if xsec_token else "无")

    data = signed_post_feed(note_id, xsec_token, args.cookie)

    if args.debug_json:
        debug_file = out_dir / f"{note_id}.json"
        debug_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("已保存 JSON:", debug_file)

    video_urls = extract_video_urls(data)

    if not video_urls:
        raise RuntimeError(
            "没有提取到视频地址。可能是图文笔记、Cookie 失效，或接口结构变化。"
            "可加 --debug-json 查看返回内容。"
        )

    title = extract_title(data, note_id)
    out_path = unique_output_path(out_dir, title)

    print("保存文件名:", out_path.name)
    print("选用视频地址:", video_urls[0][:160] + "...")

    download(video_urls[0], out_path, args.cookie)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n错误：", e, file=sys.stderr)
        sys.exit(1)