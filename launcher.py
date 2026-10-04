#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chromium指纹浏览器启动器 - 内核版本专用

用法:
    python launcher.py --profile=profile_001 --chrome=./chrome.exe
"""

import os
import sys
import json
import random
import subprocess
import argparse
from pathlib import Path

# 添加父目录到路径,导入指纹生成引擎
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.fingerprint_engine import FingerprintEngine

class ChromiumLauncher:
    """Chromium内核版本启动器"""
    
    def __init__(self, chrome_path: str, profiles_dir: str = "profiles"):
        self.chrome_path = Path(chrome_path)
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.fingerprint_engine = FingerprintEngine()
        
        if not self.chrome_path.exists():
            raise FileNotFoundError(f"Chrome可执行文件不存在: {self.chrome_path}")
    
    def create_profile(self, profile_name: str, proxy: str = None) -> dict:
        """创建新的指纹配置"""
        
        profile_dir = self.profiles_dir / profile_name
        profile_dir.mkdir(exist_ok=True)
        
        # 生成指纹
        fingerprint = self.fingerprint_engine.generate_fingerprint()
        
        # 转换为内核版本的配置格式
        config = self._convert_to_kernel_config(fingerprint, proxy)
        
        # 保存配置文件
        config_path = profile_dir / "fingerprint-config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置文件已创建: {config_path}")
        print(f"   CPU: {config['hardware']['cpu_model']}")
        print(f"   GPU: {config['hardware']['gpu_renderer']}")
        print(f"   内存: {config['hardware']['memory_gb']}GB")
        print(f"   分辨率: {config['hardware']['screen_width']}x{config['hardware']['screen_height']}")
        
        return config
    
    def _convert_to_kernel_config(self, fingerprint: dict, proxy: str = None) -> dict:
        """将指纹引擎格式转换为内核配置格式"""
        
        config = {
            "hardware": {
                "cpu_cores": fingerprint['hardware']['cpu_cores'],
                "cpu_threads": fingerprint['hardware']['cpu_threads'],
                "cpu_model": fingerprint['hardware']['cpu_model'],
                "memory_gb": fingerprint['hardware']['memory_total_gb'],
                "gpu_vendor": fingerprint['hardware']['gpu_vendor'],
                "gpu_renderer": fingerprint['hardware']['gpu_renderer'],
                "gpu_driver": fingerprint['hardware'].get('gpu_driver_version', '536.23'),
                "screen_width": fingerprint['hardware']['screen_width'],
                "screen_height": fingerprint['hardware']['screen_height'],
                "color_depth": fingerprint['hardware']['color_depth'],
                "pixel_depth": fingerprint['hardware']['pixel_depth']
            },
            "navigator": {
                "userAgent": fingerprint['browser']['user_agent'],
                "platform": fingerprint['browser']['platform'],
                "vendor": fingerprint['browser']['vendor'],
                "language": fingerprint['browser']['language'],
                "languages": fingerprint['browser']['languages']
            },
            "webgl": {
                "vendor": fingerprint['webgl']['vendor'],
                "renderer": fingerprint['webgl']['renderer'],
                "version": fingerprint['webgl'].get('version', 'WebGL 1.0'),
                "shadingLanguageVersion": fingerprint['webgl'].get('shading_language_version', 'WebGL GLSL ES 1.0'),
                "extensions": fingerprint['webgl']['extensions']
            },
            "canvas_noise_seed": fingerprint['canvas']['noise_seed'],
            "audio_noise_seed": fingerprint['audio']['noise_seed'],
            "timezone": fingerprint['network']['timezone'],
            "geolocation": {
                "latitude": fingerprint['network']['geolocation']['latitude'],
                "longitude": fingerprint['network']['geolocation']['longitude']
            },
            "fonts": fingerprint['fonts']['available_fonts'],
            "webrtc": {
                "local_ip": fingerprint['network'].get('local_ip', '192.168.1.100'),
                "block": fingerprint['network'].get('webrtc_block', False)
            }
        }
        
        # 添加代理配置(如果提供)
        if proxy:
            config['proxy'] = proxy
        
        return config
    
    def launch(self, profile_name: str, proxy: str = None, headless: bool = False) -> subprocess.Popen:
        """启动Chrome浏览器"""
        
        profile_dir = self.profiles_dir / profile_name
        config_path = profile_dir / "fingerprint-config.json"
        
        # 如果配置不存在,创建新配置
        if not config_path.exists():
            print(f"配置不存在,创建新配置: {profile_name}")
            self.create_profile(profile_name, proxy)
        
        # 构建启动参数
        args = [
            str(self.chrome_path),
            f"--fingerprint-config={config_path}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        
        # 代理设置
        if proxy:
            args.append(f"--proxy-server={proxy}")
        
        # 无头模式
        if headless:
            args.extend([
                "--headless",
                "--disable-gpu"
            ])
        
        # 启动浏览器
        print(f"🚀 启动浏览器...")
        print(f"   配置: {config_path}")
        print(f"   用户数据: {profile_dir}")
        if proxy:
            print(f"   代理: {proxy}")
        
        process = subprocess.Popen(args)
        
        print(f"✅ 浏览器已启动 (PID: {process.pid})")
        
        return process
    
    def list_profiles(self):
        """列出所有配置"""
        
        if not self.profiles_dir.exists():
            print("没有找到任何配置")
            return
        
        profiles = [p for p in self.profiles_dir.iterdir() if p.is_dir()]
        
        if not profiles:
            print("没有找到任何配置")
            return
        
        print(f"\n📋 已有配置 ({len(profiles)}个):\n")
        
        for profile in profiles:
            config_path = profile / "fingerprint-config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                print(f"  • {profile.name}")
                print(f"    CPU: {config['hardware']['cpu_model']}")
                print(f"    GPU: {config['hardware']['gpu_renderer']}")
                print(f"    内存: {config['hardware']['memory_gb']}GB")
                print(f"    分辨率: {config['hardware']['screen_width']}x{config['hardware']['screen_height']}")
                print()

def main():
    parser = argparse.ArgumentParser(description='Chromium指纹浏览器启动器')
    
    parser.add_argument('--chrome', type=str, required=True,
                        help='chrome.exe路径')
    parser.add_argument('--profile', type=str, default='default',
                        help='配置名称')
    parser.add_argument('--proxy', type=str,
                        help='代理服务器 (例如: http://127.0.0.1:7890)')
    parser.add_argument('--headless', action='store_true',
                        help='无头模式')
    parser.add_argument('--create', action='store_true',
                        help='仅创建配置,不启动')
    parser.add_argument('--list', action='store_true',
                        help='列出所有配置')
    
    args = parser.parse_args()
    
    try:
        launcher = ChromiumLauncher(args.chrome)
        
        if args.list:
            launcher.list_profiles()
            return
        
        if args.create:
            launcher.create_profile(args.profile, args.proxy)
            return
        
        # 启动浏览器
        launcher.launch(args.profile, args.proxy, args.headless)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
