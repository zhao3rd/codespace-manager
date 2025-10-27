#!/usr/bin/env python3
"""
无用户登录状态下的保活服务测试
"""
import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_global_keepalive_service():
    """测试全局保活服务启动"""
    print("=== 测试全局保活服务启动 ===")
    try:
        from streamlit_app import keepalive_service

        print("✅ 保活服务实例创建成功")

        # 检查服务状态
        status = keepalive_service.get_status()
        print(f"✅ 服务运行状态: {status['running']}")
        print(f"✅ 最后检查时间: {status['last_check']}")

        if status['running']:
            print("🎉 保活服务已全局启动，不依赖用户会话")
        else:
            print("⚠️ 保活服务未运行")
            return False

        return True

    except Exception as e:
        print(f"❌ 全局保活服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_access_without_session():
    """测试无会话状态下的配置访问"""
    print("\n=== 测试无会话状态下的配置访问 ===")
    try:
        from streamlit_app import keepalive_service

        # 直接调用配置获取方法
        accounts = keepalive_service.get_accounts_directly()
        print(f"✅ 无会话状态下获取到 {len(accounts)} 个账户")

        if accounts:
            print("📋 账户列表:")
            for name, token in accounts.items():
                print(f"   - {name}: {token[:10]}...")
        else:
            print("⚠️ 未找到账户（请检查配置文件或secrets）")

        return True

    except Exception as e:
        print(f"❌ 无会话配置访问测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_access_without_session():
    """测试无会话状态下的存储访问"""
    print("\n=== 测试无会话状态下的存储访问 ===")
    try:
        from keepalive_storage import KeepaliveStorage

        # 直接访问存储
        tasks = KeepaliveStorage.get_all_active_tasks()
        print(f"✅ 无会话状态下获取到 {len(tasks)} 个活跃任务")

        if tasks:
            print("📋 任务列表:")
            for task_key, task in tasks.items():
                account_name = task['account_name']
                cs_name = task['cs_name']
                created_by = task.get('created_by', 'unknown')
                elapsed_hours = (datetime.now() - task['start_time']).total_seconds() / 3600
                remaining_hours = task['keepalive_hours'] - elapsed_hours

                print(f"   - {task_key}: {remaining_hours:.1f}h left (by {created_by})")
        else:
            print("📭 无活跃任务")

        return True

    except Exception as e:
        print(f"❌ 无会话存储访问测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_management_without_login():
    """测试无登录状态下的任务管理"""
    print("\n=== 测试无登录状态下的任务管理 ===")
    try:
        from keepalive_storage import KeepaliveStorage
        from config import Config

        # 获取可用账户进行测试
        accounts = Config.get_all_accounts()
        if not accounts:
            print("⚠️ 没有可用账户，跳过任务管理测试")
            return True

        test_account = list(accounts.keys())[0]

        # 添加测试任务
        result = KeepaliveStorage.add_task(
            account_name=test_account,
            cs_name="test_no_login",
            start_time=datetime.now(),
            keepalive_hours=0.5,  # 30分钟后过期
            created_by="no_login_test"
        )

        if result:
            print("✅ 无登录状态下添加任务成功")

            # 验证任务可以被保活服务访问
            tasks = KeepaliveStorage.get_all_active_tasks()
            task_key = f"{test_account}_test_no_login"
            if task_key in tasks:
                print("✅ 任务可被保活服务访问")
                print("💡 这意味着即使没有用户登录，保活服务也会处理此任务")

                # 清理测试数据
                KeepaliveStorage.remove_task(test_account, "test_no_login")
                print("✅ 测试数据清理完成")
            else:
                print("❌ 任务无法被保活服务访问")
                return False
        else:
            print("❌ 无登录状态下添加任务失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 无登录任务管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚫 无用户登录状态测试")
    print("=" * 50)

    tests = [
        ("全局保活服务启动", test_global_keepalive_service),
        ("无会话配置访问", test_config_access_without_session),
        ("无会话存储访问", test_storage_access_without_session),
        ("无登录任务管理", test_task_management_without_login),
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
    print(f"📊 无登录状态测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 保活服务完全独立运行！")
        print("💡 无论用户是否登录，保活任务都会正常执行")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)