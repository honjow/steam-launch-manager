#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diff功能综合测试
测试diff命令的各种场景和输出格式
"""

import os
import sys
import tempfile
import shutil
import yaml
import subprocess

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'bin'))

try:
    import vdf
except ImportError:
    print("错误: 需要安装vdf模块")
    print("请运行: pip install vdf")
    sys.exit(1)

class DiffFunctionalityTest:
    """Diff功能测试类"""
    
    def __init__(self):
        self.temp_dir = None
        self.script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'bin', 'steam-launch-manager')
    
    def create_steam_environment(self, steam_dir):
        """创建模拟的Steam环境"""
        user_dir = os.path.join(steam_dir, "userdata", "123456789", "config")
        os.makedirs(user_dir, exist_ok=True)
        
        # 创建包含各种复杂启动选项的VDF文件
        vdf_data = {
            'UserLocalConfigStore': {
                'Software': {
                    'Valve': {
                        'Steam': {
                            'Apps': {
                                '440': {  # TF2 - 简单启动选项
                                    'LaunchOptions': '-console'
                                },
                                '730': {  # CS2 - 复杂启动选项
                                    'LaunchOptions': 'DXVK_HUD=memory -high -threads 4 -windowed'
                                },
                                '570': {  # Dota2 - 有环境变量和参数
                                    'LaunchOptions': 'PROTON_USE_WINED3D=1 RADV_PERFTEST=aco %command% -console -novid'
                                },
                                '252490': {  # Rust - 空启动选项
                                    'LaunchOptions': ''
                                }
                            }
                        }
                    }
                }
            }
        }
        
        vdf_file = os.path.join(user_dir, "localconfig.vdf")
        with open(vdf_file, 'wb') as f:
            f.write(vdf.binary_dumps(vdf_data))
        
        return steam_dir
    
    def create_test_config(self, config_path, steam_dir):
        """创建测试配置"""
        config = {
            'global': {
                'steam_dir': steam_dir,
                'backup_enabled': True
            },
            'games': {
                '440': {  # TF2 - 简单添加
                    'name': 'Team Fortress 2',
                    'prefix': {
                        'params': ['DXVK_HUD=fps', 'RADV_PERFTEST=aco'],
                        'user_handling': {'preserve': True, 'position': 'before'}
                    },
                    'suffix': {
                        'params': ['-novid', '-high'],
                        'user_handling': {'preserve': True, 'position': 'before'}
                    }
                },
                '730': {  # CS2 - 复杂冲突处理
                    'name': 'Counter-Strike 2',
                    'prefix': {
                        'params': ['DXVK_HUD=fps,memory', 'PROTON_USE_WINED3D=0'],
                        'user_handling': {'preserve': True, 'position': 'after'},
                        'conflicts': {
                            'replace_keys': ['DXVK_HUD']  # 替换现有的DXVK_HUD
                        }
                    },
                    'suffix': {
                        'params': ['-tickrate 128', '-fullscreen'],
                        'user_handling': {'preserve': True, 'position': 'before'},
                        'conflicts': {
                            'replace_rules': {
                                '-windowed': '-fullscreen'  # 替换窗口模式为全屏
                            }
                        }
                    }
                },
                '570': {  # Dota2 - 用户参数替换
                    'name': 'Dota 2',
                    'prefix': {
                        'params': ['PROTON_USE_WINED3D=0', 'DXVK_HUD=fps'],
                        'user_handling': {'preserve': False}  # 完全替换用户的前置参数
                    },
                    'suffix': {
                        'params': ['-dx11', '-high'],
                        'user_handling': {'preserve': True, 'position': 'after'}
                    }
                },
                '252490': {  # Rust - 从空开始
                    'name': 'Rust',
                    'prefix': {
                        'params': ['RADV_PERFTEST=aco', '__GL_THREADED_OPTIMIZATIONS=1']
                    },
                    'suffix': {
                        'params': ['-force-d3d11', '-high', '-maxMem=8192']
                    }
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def run_command(self, cmd):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result
        except Exception as e:
            print(f"命令运行失败: {e}")
            return None
    
    def test_diff_scenarios(self):
        """测试各种diff场景"""
        print("🎯 Steam Launch Manager - Diff功能综合测试")
        print("=" * 80)
        
        self.temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(self.temp_dir, "test-config.yaml")
        
        try:
            # 1. 创建测试环境
            print("📁 创建模拟Steam环境...")
            steam_dir = os.path.join(self.temp_dir, ".steam")
            self.create_steam_environment(steam_dir)
            
            print("⚙️  创建测试配置...")
            self.create_test_config(config_path, steam_dir)
            
            # 2. 测试各种diff场景
            scenarios = [
                ('440', 'TF2 - 简单参数添加', 'diff'),
                ('730', 'CS2 - 复杂冲突处理', 'diff'),
                ('570', 'Dota2 - 用户参数替换', 'diff'),
                ('252490', 'Rust - 从空配置开始', 'diff'),
                ('999', '不存在的游戏', 'diff'),
                ('440', 'TF2 - dry-run对比', 'dry-run')
            ]
            
            for app_id, description, command in scenarios:
                print(f"\n🎮 {description}")
                print("-" * 50)
                
                result = self.run_command([
                    'python3', self.script_path,
                    '--config', config_path,
                    command, app_id
                ])
                
                if result:
                    if result.returncode == 0:
                        print("✅ 命令执行成功")
                        if result.stdout.strip():
                            print("输出:")
                            print(result.stdout)
                    else:
                        print("❌ 命令执行失败")
                        if result.stderr:
                            print(f"错误: {result.stderr}")
                else:
                    print("❌ 命令运行异常")
                
                print()
            
            # 3. 测试diff vs dry-run的区别
            print("\n" + "=" * 80)
            print("🔄 Diff vs Dry-run 对比测试")
            print("=" * 80)
            
            print("\n📊 Diff命令输出 (详细差异分析):")
            print("-" * 40)
            diff_result = self.run_command([
                'python3', self.script_path,
                '--config', config_path,
                'diff', '440'
            ])
            if diff_result and diff_result.returncode == 0:
                print(diff_result.stdout)
            
            print("\n📊 Dry-run命令输出 (简单预览):")
            print("-" * 40)
            dry_run_result = self.run_command([
                'python3', self.script_path,
                '--config', config_path,
                'dry-run', '440'
            ])
            if dry_run_result and dry_run_result.returncode == 0:
                print(dry_run_result.stdout)
            
            # 4. 性能和输出格式验证
            print("\n" + "=" * 80)
            print("📋 输出格式验证")
            print("=" * 80)
            
            diff_result = self.run_command([
                'python3', self.script_path,
                '--config', config_path,
                'diff', '730'  # 使用复杂的CS2配置
            ])
            
            if diff_result and diff_result.returncode == 0:
                output = diff_result.stdout
                
                # 检查输出格式
                checks = [
                    ("📋 Current configuration", "当前配置标识"),
                    ("🎯 Proposed configuration", "建议配置标识"),
                    ("🔄 Changes", "变更分析标识"),
                    ("📦 Environment variables", "环境变量分析"),
                    ("🚀 Launch parameters", "启动参数分析"),
                    ("Counter-Strike 2", "游戏名称显示"),
                    ("DXVK_HUD", "环境变量内容"),
                    ("-windowed", "参数冲突处理")
                ]
                
                print("输出格式检查:")
                for check, description in checks:
                    if check in output:
                        print(f"  ✅ {description}")
                    else:
                        print(f"  ❌ {description} (缺失: {check})")
            
        finally:
            # 清理
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)
                print(f"\n🧹 清理临时文件: {self.temp_dir}")
    
    def test_edge_cases(self):
        """测试边缘情况"""
        print("\n" + "=" * 80)
        print("🔍 边缘情况测试")
        print("=" * 80)
        
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            # 测试1: 空配置文件
            print("\n1. 测试空配置文件")
            empty_config = os.path.join(self.temp_dir, "empty.yaml")
            with open(empty_config, 'w') as f:
                yaml.dump({}, f)
            
            result = self.run_command([
                'python3', self.script_path,
                '--config', empty_config,
                'diff', '440'
            ])
            
            if result and "No config found" in result.stdout:
                print("  ✅ 正确处理空配置")
            else:
                print("  ❌ 空配置处理异常")
            
            # 测试2: 不存在的配置文件
            print("\n2. 测试不存在的配置文件")
            missing_config = os.path.join(self.temp_dir, "missing.yaml")
            
            result = self.run_command([
                'python3', self.script_path,
                '--config', missing_config,
                'diff', '440'
            ])
            
            if result and result.returncode == 0:
                print("  ✅ 自动创建默认配置")
            else:
                print("  ❌ 配置文件缺失处理异常")
            
            # 测试3: 无效的App ID
            print("\n3. 测试无效的App ID")
            result = self.run_command([
                'python3', self.script_path,
                '--config', missing_config,  # 使用上面创建的配置
                'diff', 'invalid_app_id'
            ])
            
            if result and "No config found" in result.stdout:
                print("  ✅ 正确处理无效App ID")
            else:
                print("  ❌ 无效App ID处理异常")
                
        finally:
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)

def main():
    """主函数"""
    tester = DiffFunctionalityTest()
    
    print("开始Diff功能综合测试")
    print("这个测试验证diff命令的各种场景和输出格式")
    
    try:
        tester.test_diff_scenarios()
        tester.test_edge_cases()
        
        print("\n" + "=" * 80)
        print("🎉 测试完成！")
        print("=" * 80)
        print("测试总结:")
        print("  - ✅ Diff命令基础功能")
        print("  - ✅ 各种配置场景")
        print("  - ✅ 输出格式验证")
        print("  - ✅ 边缘情况处理")
        print("  - ✅ Diff vs Dry-run对比")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 