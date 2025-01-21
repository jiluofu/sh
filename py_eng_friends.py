import re
from pathlib import Path
import chardet
from datetime import datetime, timedelta
import shlex

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
    content = re.sub(r"[\u4e00-\u9fff]+", "", content)  # 去掉中文字符
    content = re.sub(r"\{.*?\}", "", content)           # 去掉字幕样式（如{...}）
    return content.strip()

def format_time_add_seconds(time_str, seconds=0):
    """
    将时间从 hh:mm:ss.cs 格式转换为 hh:mm:ss，并增加指定秒数
    """
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    new_time = time_obj + timedelta(seconds=seconds)
    if new_time < datetime.strptime("00:00:00.000", "%H:%M:%S.%f"):
        new_time = datetime.strptime("00:00:00.000", "%H:%M:%S.%f")
    return new_time.strftime("%H:%M:%S")

def escape_filename(filename):
    """
    转义文件名中的特殊字符
    """
    return shlex.quote(filename)

def process_subtitles(directory, patterns, output_script="ff.sh", output_dir="output"):
    """
    遍历字幕文件目录，生成提取片段的 ffmpeg 命令脚本，并最终合并视频片段
    """
    Path(output_dir).mkdir(exist_ok=True)  # 确保输出目录存在
    ffmpeg_commands = []
    temp_files = []  # 存放零散视频文件路径

    for ass_file in sorted(Path(directory).glob("*.ass"), key=lambda x: x.name):
        encoding = detect_encoding(ass_file)
        with open(ass_file, "r", encoding=encoding, errors="ignore") as f:
            lines = f.readlines()
            video_file_name = ass_file.with_suffix(".mkv").name  # 假定视频文件与字幕文件同名
            print(f"\nProcessing file: {ass_file.name}")
            for line in lines:
                if line.startswith("Dialogue:"):
                    # 提取时间点
                    time_match = re.match(r"Dialogue: \d+,([\d:.]+),([\d:.]+)", line)
                    if not time_match:
                        continue
                    start_time = format_time_add_seconds(time_match.group(1), seconds=-4)  # 开始时间 -4秒
                    end_time = format_time_add_seconds(time_match.group(2), seconds=3)    # 结束时间 +3秒
                    
                    # 提取台词内容并清理
                    dialogue = line.split(",,")[-1]
                    english_content = clean_english_content(dialogue)

                    # 检查是否匹配句型
                    for name, pattern in patterns.items():
                        matches = re.findall(pattern, english_content, re.IGNORECASE)
                        if matches:
                            print(f"  Match found: ({start_time} --> {end_time})")
                            print(f"    Content: {english_content}")
                            print(f"    Matched: {', '.join(matches)}")
                            
                            # 生成输出文件名并构造 ffmpeg 命令
                            output_file = Path(output_dir) / f"{ass_file.stem}_clip_{start_time.replace(':', '-')}_{end_time.replace(':', '-')}.mp4"
                            command = (
                                f"ffmpeg -i {escape_filename(video_file_name)} "
                                f"-ss {start_time} -to {end_time} "
                                f"-vf subtitles={escape_filename(video_file_name)} "
                                f"-c:v libx264 -crf 23 -preset fast "
                                f"-c:a aac -b:a 128k -ac 2 "
                                f"{escape_filename(str(output_file))}"
                            )
                            ffmpeg_commands.append(command)
                            temp_files.append(output_file)
                            break

    # 写入 ffmpeg 提取命令到脚本文件
    with open(output_script, "w", encoding="utf-8") as script_file:
        script_file.write("#!/bin/bash\n\n")
        script_file.write("\n".join(ffmpeg_commands) + "\n")

    # 生成 concat_list 文件用于视频合并
    concat_list_file = Path(output_dir) / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for temp_file in temp_files:
            f.write(f"file '{temp_file.name}'\n")

    # 添加合并命令到脚本
    final_output = Path(output_dir) / "merged_output.mp4"
    merge_command = f"ffmpeg -f concat -safe 0 -i {escape_filename(str(concat_list_file))} -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k -ac 2 {escape_filename(str(final_output))}"
    with open(output_script, "a", encoding="utf-8") as script_file:
        script_file.write(f"\n# Merge video files\n{merge_command}\n")

    # 添加删除零散文件命令到脚本
    with open(output_script, "a", encoding="utf-8") as script_file:
        script_file.write("\n# Cleanup temporary files\n")
        for temp_file in temp_files:
            script_file.write(f"rm {escape_filename(str(temp_file))}\n")
        script_file.write(f"rm {escape_filename(str(concat_list_file))}\n")

    print(f"\nScript generated: {output_script}")
    print(f"Final merged video: {final_output}")

if __name__ == "__main__":
    # 定义字幕文件目录
    subtitle_directory = Path.home() / "Documents" / "eng"

    # 定义正则表达式模式
    search_patterns = {
        # "like doing sth": r"\blike \b\w+ing\b(?: [a-zA-Z]+)?",
        # "like to do sth": r"\blike to \b\w+\b",
        # "spend time doing": r"\bspend time \w+ing\b(?: [a-zA-Z]+)?",
        "not any more": r"not any ?more",
        # "make fun of": r"\bmake fun of\b"
    }

    # 运行处理函数
    process_subtitles(subtitle_directory, search_patterns)