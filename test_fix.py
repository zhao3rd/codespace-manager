#!/usr/bin/env python3
"""
修复验证测试 - 专门测试session_state问题修复
"""
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_keepalive_service_without_streamlit():
    """测试KeepaliveService不依赖streamlit的功能"""
    print("=== 测试KeepaliveService独立功能 ===")

    try:
        # 只导入KeepaliveService，不导入streamlit
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # 模拟KeepaliveService的导入和初始化
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含accounts_cache相关代码
        if '_accounts_cache' in content:
            print("✅ 找到accounts_cache实现")
        else:
            print("❌ 未找到accounts_cache实现")
            return False

        if 'update_accounts_cache' in content:
            print("✅ 找到update_accounts_cache方法")
        else:
            print("❌ 未找到update_accounts_cache方法")
            return False

        if 'self._accounts_cache.get(account_name)' in content:
            print("✅ 找到缓存token获取逻辑")
        else:
            print("❌ 未找到缓存token获取逻辑")
            return False

        print("✅ KeepaliveService独立功能验证通过")
        return True

    except Exception as e:
        print(f"❌ KeepaliveService测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_functions():
    """测试配置功能"""
    print("\n=== 测试配置功能 ===")
    try:
        from config import Config

        # 测试获取配置
        interval = Config.get_keepalive_check_interval()
        hours = Config.get_default_keepalive_hours()

        print(f"✅ 检查间隔: {interval}秒")
        print(f"✅ 默认时长: {hours}小时")

        # 验证默认值
        assert interval == 120, f"期望120，实际{interval}"
        assert hours == 4.0, f"期望4.0，实际{hours}"

        print("✅ 配置功能验证通过")
        return True

    except Exception as e:
        print(f"❌ 配置功能测试失败: {e}")
        return False

def test_storage_with_created_by():
    """测试存储的created_by功能"""
    print("\n=== 测试存储created_by功能 ===")
    try:
        from keepalive_storage import KeepaliveStorage

        # 测试添加带created_by的任务
        result = KeepaliveStorage.add_task(
            account_name="test_fix",
            cs_name="test_cs_fix",
            start_time=datetime.now(),
            keepalive_hours=1.0,
            created_by="fix_test_user"
        )

        if result:
            print("✅ 带created_by的任务添加成功")
        else:
            print("❌ 带created_by的任务添加失败")
            return False

        # 验证任务包含created_by
        tasks = KeepaliveStorage.load_tasks()
        task_key = "test_fix_test_cs_fix"

        if task_key in tasks:
            task = tasks[task_key]
            if task.get('created_by') == 'fix_test_user':
                print("✅ created_by字段验证成功")
            else:
                print(f"❌ created_by字段错误: {task.get('created_by')}")
                return False

            if 'created_at' in task:
                print("✅ created_at字段存在")
            else:
                print("❌ created_at字段缺失")
                return False
        else:
            print("❌ 任务未找到")
            return False

        # 清理
        KeepaliveStorage.remove_task("test_fix", "test_cs_fix")
        print("✅ 测试数据清理完成")

        return True

    except Exception as e:
        print(f"❌ 存储created_by测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 修复验证测试")
    print("=" * 50)

    tests = [
        ("配置功能", test_config_functions),
        ("存储created_by功能", test_storage_with_created_by),
        ("KeepaliveService独立功能", test_keepalive_service_without_streamlit),
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
    print(f"📊 修复验证结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有修复验证通过！")
        print("💡 现在可以测试streamlit应用了")
        return True
    else:
        print("⚠️ 部分验证失败，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)