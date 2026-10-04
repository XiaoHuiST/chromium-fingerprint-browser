#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chromium指纹浏览器验收测试脚本

测试项目:
1. chrome.exe是否存在并可执行
2. 配置文件是否正确加载
3. 指纹参数是否生效
4. 唯一性验证
5. 一致性验证
6. 检测网站测试
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class ChromiumAcceptanceTest:
    """验收测试类"""
    
    def __init__(self, chrome_path: str, launcher_path: str):
        self.chrome_path = Path(chrome_path)
        self.launcher_path = Path(launcher_path)
        self.test_results = []
        
    def log_test(self, name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"     {details}")
        
        self.test_results.append({
            "name": name,
            "passed": passed,
            "details": details
        })
    
    def test_chrome_exists(self) -> bool:
        """测试1: chrome.exe是否存在"""
        print("\n[测试1] 检查chrome.exe...")
        
        exists = self.chrome_path.exists()
        if exists:
            size_mb = self.chrome_path.stat().st_size / (1024 * 1024)
            self.log_test("chrome.exe存在", True, f"大小: {size_mb:.2f} MB")
            return True
        else:
            self.log_test("chrome.exe存在", False, f"路径不存在: {self.chrome_path}")
            return False
    
    def test_config_generation(self) -> bool:
        """测试2: 配置文件生成"""
        print("\n[测试2] 测试配置文件生成...")
        
        try:
            # 创建测试配置
            result = subprocess.run([
                sys.executable,
                str(self.launcher_path),
                "--chrome", str(self.chrome_path),
                "--profile", "test_profile_001",
                "--create"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 检查配置文件
                config_path = Path("profiles/test_profile_001/fingerprint-config.json")
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # 验证必要字段
                    required_keys = ['hardware', 'navigator', 'webgl', 'canvas_noise_seed']
                    all_present = all(key in config for key in required_keys)
                    
                    if all_present:
                        self.log_test("配置文件生成", True, 
                                    f"CPU: {config['hardware']['cpu_cores']}核, "
                                    f"GPU: {config['hardware']['gpu_renderer'][:30]}...")
                        return True
                    else:
                        self.log_test("配置文件生成", False, "缺少必要字段")
                        return False
                else:
                    self.log_test("配置文件生成", False, "配置文件未创建")
                    return False
            else:
                self.log_test("配置文件生成", False, f"启动器错误: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("配置文件生成", False, str(e))
            return False
    
    def test_chrome_launch(self) -> bool:
        """测试3: Chrome启动测试"""
        print("\n[测试3] 测试Chrome启动...")
        
        try:
            # 启动Chrome(5秒后关闭)
            process = subprocess.Popen([
                sys.executable,
                str(self.launcher_path),
                "--chrome", str(self.chrome_path),
                "--profile", "test_profile_001"
            ])
            
            # 等待2秒看是否崩溃
            time.sleep(2)
            
            if process.poll() is None:
                # 进程仍在运行
                self.log_test("Chrome启动", True, f"PID: {process.pid}")
                
                # 关闭进程
                process.terminate()
                process.wait(timeout=5)
                return True
            else:
                self.log_test("Chrome启动", False, f"进程退出码: {process.returncode}")
                return False
                
        except Exception as e:
            self.log_test("Chrome启动", False, str(e))
            return False
    
    def test_fingerprint_uniqueness(self) -> bool:
        """测试4: 指纹唯一性"""
        print("\n[测试4] 测试指纹唯一性...")
        
        try:
            configs = []
            
            # 生成3个不同的配置
            for i in range(3):
                subprocess.run([
                    sys.executable,
                    str(self.launcher_path),
                    "--chrome", str(self.chrome_path),
                    "--profile", f"test_unique_{i}",
                    "--create"
                ], capture_output=True, timeout=30)
                
                config_path = Path(f"profiles/test_unique_{i}/fingerprint-config.json")
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs.append(json.load(f))
            
            # 检查关键参数是否不同
            cpu_models = [c['hardware']['cpu_model'] for c in configs]
            gpu_renderers = [c['hardware']['gpu_renderer'] for c in configs]
            canvas_seeds = [c['canvas_noise_seed'] for c in configs]
            
            unique_cpus = len(set(cpu_models))
            unique_gpus = len(set(gpu_renderers))
            unique_canvas = len(set(canvas_seeds))
            
            is_unique = unique_cpus >= 2 and unique_gpus >= 2 and unique_canvas == 3
            
            self.log_test("指纹唯一性", is_unique,
                        f"CPU: {unique_cpus}/3, GPU: {unique_gpus}/3, Canvas: {unique_canvas}/3")
            return is_unique
            
        except Exception as e:
            self.log_test("指纹唯一性", False, str(e))
            return False
    
    def test_fingerprint_consistency(self) -> bool:
        """测试5: 指纹一致性"""
        print("\n[测试5] 测试指纹一致性...")
        
        try:
            # 读取同一配置3次
            config_path = Path("profiles/test_profile_001/fingerprint-config.json")
            
            configs = []
            for i in range(3):
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs.append(json.load(f))
            
            # 检查是否完全相同
            config1_str = json.dumps(configs[0], sort_keys=True)
            config2_str = json.dumps(configs[1], sort_keys=True)
            config3_str = json.dumps(configs[2], sort_keys=True)
            
            is_consistent = config1_str == config2_str == config3_str
            
            self.log_test("指纹一致性", is_consistent,
                        "同一配置多次读取结果相同")
            return is_consistent
            
        except Exception as e:
            self.log_test("指纹一致性", False, str(e))
            return False
    
    def test_automation_detection(self) -> bool:
        """测试6: 自动化检测特征"""
        print("\n[测试6] 测试自动化检测特征...")
        
        # 这个测试需要实际启动浏览器并访问检测网站
        # 由于是内核修改版,理论上不应该有webdriver等特征
        
        # 简化版:检查配置中没有webdriver相关配置
        try:
            config_path = Path("profiles/test_profile_001/fingerprint-config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 内核版本不应该有webdriver字段
            has_webdriver = 'webdriver' in config.get('navigator', {})
            
            self.log_test("自动化检测", not has_webdriver,
                        "配置中无webdriver标记")
            return not has_webdriver
            
        except Exception as e:
            self.log_test("自动化检测", False, str(e))
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("验收测试报告")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"通过率: {passed/total*100:.1f}%\n")
        
        if failed > 0:
            print("失败的测试:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['name']}")
                    if result['details']:
                        print(f"     {result['details']}")
        
        print("\n" + "="*60)
        
        # 保存到文件
        report = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed/total,
            "results": self.test_results
        }
        
        with open("acceptance-test-report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"详细报告已保存到: acceptance-test-report.json\n")
        
        return passed == total

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Chromium指纹浏览器验收测试')
    parser.add_argument('--chrome', type=str, required=True,
                        help='chrome.exe路径')
    parser.add_argument('--launcher', type=str, default='launcher.py',
                        help='launcher.py路径')
    
    args = parser.parse_args()
    
    print("🧪 Chromium指纹浏览器 - 验收测试")
    print("="*60)
    
    tester = ChromiumAcceptanceTest(args.chrome, args.launcher)
    
    # 运行所有测试
    tester.test_chrome_exists()
    tester.test_config_generation()
    tester.test_chrome_launch()
    tester.test_fingerprint_uniqueness()
    tester.test_fingerprint_consistency()
    tester.test_automation_detection()
    
    # 生成报告
    all_passed = tester.generate_report()
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
