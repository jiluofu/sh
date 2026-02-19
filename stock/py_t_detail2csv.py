import AppKit
import time

from Quartz.Accessibility import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    kAXChildrenAttribute,
    kAXRoleAttribute,
    kAXTitleAttribute,
    kAXValueAttribute
)


def get_app_element(app_name):
    """获取指定 App 的 AXUIElement"""
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()

    for app in apps:
        if app.localizedName() == app_name:
            pid = app.processIdentifier()
            print(f"✅ 找到 app：{app_name}, PID={pid}")
            return AXUIElementCreateApplication(pid)
    print(f"❌ 未找到名为 {app_name} 的应用")
    return None


def safe_get_attr(elem, attr):
    """安全地获取 AX 属性"""
    try:
        return AXUIElementCopyAttributeValue(elem, attr, None)
    except Exception:
        return None


def print_accessibility_tree(element, depth=0):
    """递归打印元素结构"""
    indent = "  " * depth
    role = safe_get_attr(element, kAXRoleAttribute)
    title = safe_get_attr(element, kAXTitleAttribute)
    value = safe_get_attr(element, kAXValueAttribute)

    if role or title or value:
        print(f"{indent}- Role: {role}, Title: {title}, Value: {value}")

    children = safe_get_attr(element, kAXChildrenAttribute)
    if children:
        for child in children:
            print_accessibility_tree(child, depth + 1)


def main():
    app_name = "访达"  # ✅ 改成 "微信", "东方财富", 或你的 App 名称
    app_elem = get_app_element(app_name)
    if not app_elem:
        return

    print("\n🧠 Dumping AXUIElement tree...\n")
    print_accessibility_tree(app_elem)


if __name__ == "__main__":
    main()