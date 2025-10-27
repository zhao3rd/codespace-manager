#!/usr/bin/env python3
"""
Streamlit Cloud环境配置加载测试
"""
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """测试配置加载功能"""
    print("=== 测试配置加载功能 ===")
    try:
        from config import Config

        # 测试加载Streamlit secrets
        print("🔍 测试Streamlit secrets加载...")
        streamlit_accounts = Config.load_streamlit_secrets()
        print(f"✅ 从Streamlit secrets加载了 {len(streamlit_accounts)} 个账户")
        for name in streamlit_accounts:
            print(f"   - {name}: {streamlit_accounts[name][:10]}...")

        # 测试加载本地文件
        print("\n🔍 测试本地文件加载...")
        local_accounts = Config.load_local_accounts()
        print(f"✅ 从本地文件加载了 {len(local_accounts)} 个账户")
        for name in local_accounts:
            print(f"   - {name}: {local_accounts[name][:10]}...")

        # 测试合并逻辑（模拟get_all_accounts的行为）
        print("\n🔍 测试账户合并逻辑...")
        merged_accounts = local_accounts.copy()
        merged_accounts.update(streamlit_accounts)
        print(f"✅ 合并后共 {len(merged_accounts)} 个账户")

        return True

    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keepalive_service_config_access():
    """测试保活服务的配置访问"""
    print("\n=== 测试保活服务配置访问 ===")
    try:
        # 直接测试KeepaliveService的方法
        from streamlit_app import KeepaliveService

        service = KeepaliveService()
        print("✅ KeepaliveService实例化成功")

        # 测试直接获取配置的方法
        accounts = service.get_accounts_directly()
        print(f"✅ 直接获取到 {len(accounts)} 个账户")

        if accounts:
            print("📋 账户列表:")
            for name, token in accounts.items():
                print(f"   - {name}: {token[:10]}...")
        else:
            print("⚠️ 未找到任何账户")

        return True

    except Exception as e:
        print(f"❌ 保活服务配置访问测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_with_cloud_accounts():
    """测试存储功能使用cloud账户"""
    print("\n=== 测试存储功能 ===")
    try:
        from keepalive_storage import KeepaliveStorage
        from config import Config

        # 获取一个可用的账户名称来测试
        accounts = Config.get_all_accounts()
        if not accounts:
            print("⚠️ 没有可用账户，跳过存储测试")
            return True

        test_account = list(accounts.keys())[0]
        print(f"📝 使用账户 {test_account} 进行存储测试")

        # 添加测试任务
        result = KeepaliveStorage.add_task(
            account_name=test_account,
            cs_name="test_cloud_cs",
            start_time=datetime.now(),
            keepalive_hours=1.0,
            created_by="cloud_test"
        )

        if result:
            print("✅ 测试任务添加成功")

            # 验证任务存在
            tasks = KeepaliveStorage.load_tasks()
            task_key = f"{test_account}_test_cloud_cs"
            if task_key in tasks:
                print("✅ 任务验证成功")
                # 清理测试数据
                KeepaliveStorage.remove_task(test_account, "test_cloud_cs")
                print("✅ 测试数据清理完成")
            else:
                print("❌ 任务验证失败")
                return False
        else:
            print("❌ 测试任务添加失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 存储功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("☁️ Streamlit Cloud配置测试")
    print("=" * 50)

    tests = [
        ("配置加载", test_config_loading),
        ("保活服务配置访问", test_keepalive_service_config_access),
        ("存储功能", test_storage_with_cloud_accounts),
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
    print(f"📊 Cloud配置测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 Cloud环境配置验证通过！")
        print("💡 现在应该可以在Streamlit Cloud中正常运行了")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)