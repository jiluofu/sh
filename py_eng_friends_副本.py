import os
import re
from pathlib import Path
import chardet
from datetime import datetime, timedelta

def detect_encoding(file_path):
    """
    自动检测文件编码
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(1024)
    result = chardet.detect(raw_data)
    return result["encoding"]

def clean_english_content(content):
    """
    去除中文和字幕样式，保留纯英文内容
    """
    # 去掉中文字符
    content = re.sub(r"[\u4e00-\u9fff]+", "", content)
    # 去掉字幕样式（{...} 或类似的样式标签）
    content = re.sub(r"\{.*?\}", "", content)
    return content.strip()

def format_time_add_seconds(time_str, seconds=0):
    """
    将时间从 hh:mm:ss.cs 格式转换为 hh:mm:ss，并增加指定秒数
    """
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    new_time = time_obj + timedelta(seconds=seconds)
    # 防止时间小于 0
    if new_time < datetime.strptime("00:00:00.000", "%H:%M:%S.%f"):
        new_time = datetime.strptime("00:00:00", "%H:%M:%S")
    return new_time.strftime("%H:%M:%S")

def process_ass_files(directory, patterns, output_script="ff.sh"):
    """
    遍历目录下所有 .ass 文件，提取符合句型的时间点和英文台词，并生成 ffmpeg 命令脚本
    """
    ffmpeg_commands = []
    for file_path in Path(directory).glob("*.ass"):
        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding, errors="ignore") as f:
            lines = f.readlines()
            video_file_name = file_path.with_suffix(".mkv").name  # 对应的视频文件名
            print(f"\nProcessing file: {file_path.name}")
            for line in lines:
                # 仅处理 [Events] 部分的对话内容
                if line.startswith("Dialogue:"):
                    # 提取时间点
                    time_match = re.match(r"Dialogue: \d+,([\d:.]+),([\d:.]+)", line)
                    if not time_match:
                        continue
                    start_time = format_time_add_seconds(time_match.group(1), seconds=-4)  # 起始时间 -4 秒
                    end_time = format_time_add_seconds(time_match.group(2), seconds=3)  # 结束时间 +3 秒
                    
                    # 提取英文台词部分并清理内容
                    dialogue = line.strip().split(",,")[-1]
                    english_content = clean_english_content(dialogue)

                    # 搜索正则表达式匹配的台词
                    for name, pattern in patterns.items():
                        matches = re.findall(pattern, english_content)
                        if matches:
                            # 打印匹配结果
                            print(f"  ({start_time} --> {end_time})")
                            print(f"    {english_content}")
                            print(f"      - Matched: {', '.join(matches)}")

                            # 生成 ffmpeg 命令
                            output_file = f"{file_path.stem}_clip_{start_time.replace(':', '-')}_{end_time.replace(':', '-')}.mkv"
                            command = f"ffmpeg -i {video_file_name} -ss {start_time} -to {end_time} -c copy {output_file}"
                            ffmpeg_commands.append(command)
                            break

    # 将 ffmpeg 命令写入脚本文件
    with open(output_script, "w", encoding="utf-8") as script_file:
        script_file.write("#!/bin/bash\n\n")
        script_file.write("\n".join(ffmpeg_commands))
    print(f"\nScript generated: {output_script}")

# 定义字幕文件目录
directory = Path.home() / "Documents" / "eng"

# 定义正则表达式模式
patterns = {
    "like doing sth": r"\blike \b\w+ing\b(?: [a-zA-Z]+)?",
    # "like to do sth": r"\blike to \b\w+\b"
}

# 执行脚本生成
process_ass_files(directory, patterns)