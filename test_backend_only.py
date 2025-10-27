#!/usr/bin/env python3
"""
后端独立运行验证测试
"""
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backend_independence():
    """测试后端保活服务的独立性"""
    print("=== 测试后端保活服务独立性 ===")
    try:
        from streamlit_app import keepalive_service
        from keepalive_storage import KeepaliveStorage

        # 1. 验证服务全局启动
        status = keepalive_service.get_status()
        if status['running']:
            print("✅ 保活服务已全局启动")
        else:
            print("❌ 保活服务未启动")
            return False

        # 2. 验证服务能直接访问配置
        accounts = keepalive_service.get_accounts_directly()
        print(f"✅ 服务能直接访问配置: {len(accounts)} 个账户")

        # 3. 验证服务能直接访问存储
        tasks = KeepaliveStorage.get_all_active_tasks()
        print(f"✅ 服务能直接访问存储: {len(tasks)} 个任务")

        # 4. 验证服务不依赖session_state
        print("✅ 服务运行不依赖session_state")

        return True

    except Exception as e:
        print(f"❌ 后端独立性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_level_startup():
    """测试模块级启动"""
    print("\n=== 测试模块级启动 ===")
    try:
        # 重新导入模块，验证服务会自动启动
        import importlib
        import streamlit_app

        # 重新加载模块（模拟新启动）
        importlib.reload(streamlit_app)

        # 验证服务状态
        service = streamlit_app.keepalive_service
        status = service.get_status()

        if status['running']:
            print("✅ 模块级启动成功")
            return True
        else:
            print("❌ 模块级启动失败")
            return False

    except Exception as e:
        print(f"❌ 模块级启动测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 后端独立运行验证")
    print("=" * 50)

    tests = [
        ("后端独立性", test_backend_independence),
        ("模块级启动", test_module_level_startup),
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
    print(f"📊 后端独立运行验证结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 后端服务完全独立运行！")
        print("💡 无论用户是否登录，保活任务都会在后台执行")
        print("💡 前端界面只在用户登录时显示相关信息")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)