import sys
import subprocess
import os

def main():
    if len(sys.argv) < 2:
        print("❌ 用法: python run_shell.py /path/to/your/script.sh")
        sys.exit(1)

    shell_path = sys.argv[1]

    if not os.path.isfile(shell_path):
        print(f"❌ 脚本不存在: {shell_path}")
        sys.exit(2)

    try:
        print(f"▶️ 执行脚本: {shell_path}")
        result = subprocess.run(
            ["/bin/bash", shell_path],
            capture_output=True,
            check=True
        )
        print("✅ 脚本成功执行，输出：")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("❌ 脚本执行失败，错误输出：")
        print(e.stderr.decode())

if __name__ == "__main__":
    main()