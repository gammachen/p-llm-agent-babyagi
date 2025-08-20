#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本

运行所有单元测试并生成测试报告。
"""

import unittest
import sys
import os
from pathlib import Path
from io import StringIO

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("BabyAGI Agent 系统单元测试")
    print("=" * 60)
    
    # 发现并运行所有测试
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # 创建测试运行器
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True
    )
    
    # 运行测试
    result = runner.run(suite)
    
    # 输出结果
    output = stream.getvalue()
    print(output)
    
    # 生成摘要报告
    print("\n" + "=" * 60)
    print("测试摘要报告")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    success = total_tests - failures - errors - skipped
    
    print(f"总测试数: {total_tests}")
    print(f"成功: {success}")
    print(f"失败: {failures}")
    print(f"错误: {errors}")
    print(f"跳过: {skipped}")
    
    if failures > 0:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors > 0:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 计算成功率
    success_rate = (success / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n成功率: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 所有测试通过！")
    elif success_rate >= 80:
        print("✅ 大部分测试通过")
    else:
        print("❌ 需要修复失败的测试")
    
    return result.wasSuccessful()


def run_specific_test(test_name):
    """运行特定测试"""
    print(f"运行测试: {test_name}")
    print("=" * 40)
    
    # 加载特定测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def list_available_tests():
    """列出所有可用的测试"""
    print("可用的测试模块:")
    print("-" * 30)
    
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob('test_*.py'))
    
    for test_file in sorted(test_files):
        module_name = test_file.stem
        print(f"  - {module_name}")
        
        # 尝试导入模块并列出测试类
        try:
            module = __import__(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, unittest.TestCase) and 
                    attr != unittest.TestCase):
                    print(f"    └── {attr_name}")
                    
                    # 列出测试方法
                    for method_name in dir(attr):
                        if method_name.startswith('test_'):
                            print(f"        └── {method_name}")
        except ImportError as e:
            print(f"    └── 无法导入: {e}")
    
    print("\n使用方法:")
    print("  python run_tests.py                    # 运行所有测试")
    print("  python run_tests.py test_config        # 运行特定模块")
    print("  python run_tests.py --list             # 列出所有测试")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ['--list', '-l']:
            list_available_tests()
            return
        elif arg in ['--help', '-h']:
            print("BabyAGI Agent 测试运行器")
            print("\n用法:")
            print("  python run_tests.py [选项] [测试名称]")
            print("\n选项:")
            print("  --list, -l     列出所有可用测试")
            print("  --help, -h     显示帮助信息")
            print("\n示例:")
            print("  python run_tests.py                    # 运行所有测试")
            print("  python run_tests.py test_config        # 运行配置测试")
            print("  python run_tests.py test_tools.TestBaseTool  # 运行特定测试类")
            return
        else:
            # 运行特定测试
            success = run_specific_test(arg)
            sys.exit(0 if success else 1)
    else:
        # 运行所有测试
        success = run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()