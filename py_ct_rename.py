#!/usr/bin/env python3

import os
import sys
import pydicom
from pydicom.errors import InvalidDicomError


def modify_patient_name(root_dir, new_name):
    modified = 0
    skipped = 0
    failed = 0

    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            path = os.path.join(root, filename)

            # 跳过 macOS 隐藏文件
            if filename.startswith("."):
                continue

            try:
                # force=False：只读取正规的 DICOM 文件
                ds = pydicom.dcmread(path, force=False)

                old_name = str(ds.get("PatientName", ""))

                ds.PatientName = new_name
                ds.save_as(path)

                modified += 1
                print(f"[已修改] {path}")
                print(f"         {old_name}  ->  {new_name}")

            except InvalidDicomError:
                skipped += 1

            except Exception as e:
                failed += 1
                print(f"[失败] {path}")
                print(f"       {e}")

    print("\n========================")
    print(f"修改完成：{modified} 个 DICOM 文件")
    print(f"非 DICOM 跳过：{skipped} 个文件")
    print(f"处理失败：{failed} 个文件")
    print("========================")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：")
        print('  python3 rename_patient.py "CT目录" "新的病人姓名"')
        print()
        print("例如：")
        print('  python3 rename_patient.py "/Users/me/Desktop/CT2023" "HE WEN FANG 2023"')
        sys.exit(1)

    root_dir = sys.argv[1]
    new_name = sys.argv[2]

    if not os.path.isdir(root_dir):
        print(f"错误：目录不存在：{root_dir}")
        sys.exit(1)

    print(f"CT目录：{root_dir}")
    print(f"新姓名：{new_name}")
    print()

    modify_patient_name(root_dir, new_name)