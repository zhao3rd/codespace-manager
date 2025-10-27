#!/usr/bin/env python3
"""
重构后的保活机制测试脚本
"""
import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_module():
    """测试配置模块"""
    print("=== 测试配置模块 ===")
    try:
        from config import Config

        # 测试默认值
        interval = Config.get_keepalive_check_interval()
        default_hours = Config.get_default_keepalive_hours()

        print(f"✅ 配置模块加载成功")
        print(f"✅ 保活检查间隔: {interval}秒")
        print(f"✅ 默认保活时长: {default_hours}小时")

        # 验证默认值
        assert interval == 120, f"期望120，实际{interval}"
        assert default_hours == 4.0, f"期望4.0，实际{default_hours}"

        print("✅ 配置验证通过")
        return True

    except Exception as e:
        print(f"❌ 配置模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_module():
    """测试存储模块"""
    print("\n=== 测试存储模块 ===")
    try:
        from keepalive_storage import KeepaliveStorage

        # 测试添加任务
        start_time = datetime.now()
        result = KeepaliveStorage.add_task(
            account_name="test_account",
            cs_name="test_codespace",
            start_time=start_time,
            keepalive_hours=2.0,
            created_by="test_user"
        )

        print(f"✅ 添加保活任务: {result}")

        # 测试加载任务
        tasks = KeepaliveStorage.load_tasks()
        print(f"✅ 加载任务数: {len(tasks)}")

        if tasks:
            # 检查任务结构
            task_key = "test_account_test_codespace"
            if task_key in tasks:
                task = tasks[task_key]
                print(f"✅ 任务字段检查:")
                print(f"   - account_name: {task.get('account_name')}")
                print(f"   - cs_name: {task.get('cs_name')}")
                print(f"   - created_by: {task.get('created_by')}")
                print(f"   - keepalive_hours: {task.get('keepalive_hours')}")

                # 验证字段
                assert task.get('account_name') == "test_account"
                assert task.get('cs_name') == "test_codespace"
                assert task.get('created_by') == "test_user"
                assert task.get('keepalive_hours') == 2.0

                print("✅ 任务结构验证通过")

        # 清理测试数据
        KeepaliveStorage.remove_task("test_account", "test_codespace")
        print("✅ 清理测试数据完成")

        return True

    except Exception as e:
        print(f"❌ 存储模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keepalive_service():
    """测试保活服务（仅初始化，不启动）"""
    print("\n=== 测试保活服务 ===")
    try:
        from streamlit_app import KeepaliveService

        # 创建服务实例（单例模式）
        service = KeepaliveService()

        print(f"✅ 保活服务初始化成功")
        print(f"✅ 服务状态: {service.get_status()}")

        # 测试状态获取
        status = service.get_status()
        assert isinstance(status, dict)
        assert 'running' in status
        assert 'last_check' in status

        print("✅ 保活服务验证通过")
        return True

    except Exception as e:
        print(f"❌ 保活服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """测试所有导入"""
    print("\n=== 测试模块导入 ===")

    modules_to_test = [
        'config',
        'keepalive_storage',
        'github_api'
    ]

    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name}: {e}")

    print(f"\n导入测试结果: {success_count}/{len(modules_to_test)} 成功")
    return success_count == len(modules_to_test)

def main():
    """主测试函数"""
    print("🚀 开始重构验证测试")
    print("=" * 50)

    tests = [
        ("模块导入", test_imports),
        ("配置模块", test_config_module),
        ("存储模块", test_storage_module),
        ("保活服务", test_keepalive_service),
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
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！重构成功")
        return True
    else:
        print("⚠️ 部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)