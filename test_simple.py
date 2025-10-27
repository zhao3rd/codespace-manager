#!/usr/bin/env python3
"""
简化的重构测试 - 不依赖streamlit
"""
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """测试基本功能"""
    print("=== 基本功能测试 ===")

    # 测试配置
    try:
        from config import Config
        print("✅ Config导入成功")
        print(f"   - 检查间隔: {Config.get_keepalive_check_interval()}秒")
        print(f"   - 默认时长: {Config.get_default_keepalive_hours()}小时")
    except Exception as e:
        print(f"❌ Config失败: {e}")
        return False

    # 测试存储
    try:
        from keepalive_storage import KeepaliveStorage

        # 测试添加任务
        result = KeepaliveStorage.add_task(
            account_name="test",
            cs_name="test_cs",
            start_time=datetime.now(),
            keepalive_hours=1.0,
            created_by="test_user"
        )
        print(f"✅ 存储测试成功: {result}")

        # 清理
        KeepaliveStorage.remove_task("test", "test_cs")

    except Exception as e:
        print(f"❌ 存储失败: {e}")
        return False

    print("✅ 基本功能测试通过")
    return True

if __name__ == "__main__":
    print("🚀 简化重构测试")

    if test_basic_functionality():
        print("🎉 测试成功")
    else:
        print("❌ 测试失败")
        sys.exit(1)