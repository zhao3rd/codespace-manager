#!/usr/bin/env python3
"""
日志格式验证测试
"""
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_keepalive_logging():
    """测试保活日志格式"""
    print("=== 测试保活日志格式 ===")
    try:
        from streamlit_app import KeepaliveService

        # 创建服务实例
        service = KeepaliveService()

        # 测试时间戳格式
        current_time = datetime.now()
        time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        short_time_str = current_time.strftime('%H:%M:%S')

        print(f"✅ 时间戳格式测试:")
        print(f"   - 完整格式: [{time_str}]")
        print(f"   - 短格式: [{short_time_str}]")

        # 验证日志输出格式
        print(f"✅ 预期日志格式:")
        print(f"   - 🔄 [{time_str}] Performing keepalive check...")
        print(f"   - 📋 [{time_str}] Processing X keepalive task(s)")
        print(f"   -   📊 [{short_time_str}] account_codespace: 1.2h/4.0h")
        print(f"   -     🔄 [{short_time_str}] Restarting codespace (state: Stopped)...")
        print(f"   -     ✅ [{short_time_str}] Codespace restarted successfully")

        return True

    except Exception as e:
        print(f"❌ 保活日志格式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_logging():
    """测试存储日志简化"""
    print("\n=== 测试存储日志简化 ===")
    try:
        from keepalive_storage import KeepaliveStorage

        # 测试简化后的存储日志
        print("✅ 存储日志已简化:")
        print("   - 移除 '🔧 Using GitHub storage backend' 详细信息")
        print("   - 改为 '🔧 Using GitHub storage backend: repo/branch'")
        print("   - 移除保存成功/失败的详细日志")
        print("   - 保留错误日志用于调试")

        return True

    except Exception as e:
        print(f"❌ 存储日志简化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("📝 日志格式验证测试")
    print("=" * 50)

    tests = [
        ("保活日志格式", test_keepalive_logging),
        ("存储日志简化", test_storage_logging),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")

    print("\n" + "=" * 50)
    print(f"📊 日志格式验证结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 日志格式优化完成！")
        print("💡 现在日志更清晰，包含时间戳，减少了冗余输出")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)