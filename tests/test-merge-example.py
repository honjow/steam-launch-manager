#!/usr/bin/env python3
"""
Steam启动参数合并演示
直接使用 steam-launch-manager 的核心逻辑进行演示
"""

import sys
import os
from pathlib import Path
import importlib.util

# 动态导入 steam-launch-manager 脚本
script_path = Path(__file__).parent.parent / 'src' / 'bin' / 'steam-launch-manager'

# 直接执行脚本文件来导入
with open(script_path, 'r') as f:
    script_content = f.read()

# 创建一个模块对象并执行脚本内容
steam_launch_manager = type(sys)('steam_launch_manager')
exec(script_content, steam_launch_manager.__dict__)

# 现在可以使用 SteamLaunchManager 类
SteamLaunchManager = steam_launch_manager.SteamLaunchManager

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_scenario(title, description):
    print(f"\n--- {title} ---")
    print(f"说明: {description}")

def show_merge_result(original, final_prefix, final_suffix):
    print(f"\n原始启动选项: {original}")
    
    if final_prefix:
        prefix_str = ' '.join(final_prefix)
        if final_suffix:
            final_options = f"{prefix_str} %command% {final_suffix}"
        else:
            final_options = f"{prefix_str} %command%"
    else:
        if final_suffix:
            final_options = f"%command% {final_suffix}"
        else:
            final_options = "%command%"
    
    print(f"合并后启动选项: {final_options}")

def main():
    # 创建一个临时的 SteamLaunchManager 实例用于演示
    # 使用 /tmp 路径避免影响用户的实际配置
    temp_config = "/tmp/steam-launch-demo.yaml"
    manager = SteamLaunchManager(config_path=temp_config)
    
    print_separator("Steam启动参数合并演示")
    print("使用 steam-launch-manager 的真实核心逻辑")
    
    # 场景1: 基础环境变量合并
    print_scenario("场景1", "基础环境变量合并 - 用户设置了DXVK_HUD=1，管理配置要求DXVK_HUD=fps")
    
    current_options = "DXVK_HUD=1 %command% -novid"
    user_prefix, user_suffix = manager.parse_current_params(current_options)
    
    config_prefix = {'params': ['DXVK_HUD=fps']}
    user_handling = {'preserve': True, 'position': 'before'}
    conflicts = {'replace_keys': ['DXVK_HUD']}
    
    final_prefix = manager.merge_prefix_params(user_prefix, config_prefix, user_handling, conflicts)
    final_suffix = user_suffix
    
    print(f"用户当前前置参数: {user_prefix}")
    print(f"管理配置参数: {config_prefix['params']}")
    print(f"冲突处理规则: 替换 DXVK_HUD")
    print(f"合并后前置参数: {final_prefix}")
    
    show_merge_result(current_options, final_prefix, final_suffix)
    
    # 场景2: 路径合并
    print_scenario("场景2", "路径环境变量合并 - LD_LIBRARY_PATH前置合并")
    
    current_options = "LD_LIBRARY_PATH=/user/lib %command% -high"
    user_prefix, user_suffix = manager.parse_current_params(current_options)
    
    config_prefix = {'params': ['LD_LIBRARY_PATH=/opt/steam/lib']}
    user_handling = {'preserve': True, 'position': 'before'}
    conflicts = {'merge_keys': {'LD_LIBRARY_PATH': 'prepend'}}
    
    final_prefix = manager.merge_prefix_params(user_prefix, config_prefix, user_handling, conflicts)
    
    print(f"用户当前前置参数: {user_prefix}")
    print(f"管理配置参数: {config_prefix['params']}")
    print(f"冲突处理规则: LD_LIBRARY_PATH前置合并")
    print(f"合并后前置参数: {final_prefix}")
    
    show_merge_result(current_options, final_prefix, user_suffix)
    
    # 场景3: 后置参数替换
    print_scenario("场景3", "后置参数冲突替换 - 用户设置了-windowed，管理配置要求-fullscreen")
    
    current_options = "%command% -windowed -novid"
    user_prefix, user_suffix = manager.parse_current_params(current_options)
    
    config_suffix = {'params': ['-high', '-threads 4']}
    user_handling = {'preserve': True, 'position': 'before'}
    conflicts = {'replace_rules': {'-windowed': '-fullscreen'}}
    
    final_suffix = manager.merge_suffix_params(user_suffix, config_suffix, user_handling, conflicts)
    
    print(f"用户当前后置参数: {user_suffix.split()}")
    print(f"管理配置参数: {config_suffix['params']}")
    print(f"冲突处理规则: -windowed 替换为 -fullscreen")
    print(f"合并后后置参数: {final_suffix}")
    
    show_merge_result(current_options, user_prefix, final_suffix)
    
    # 场景4: 复杂混合场景
    print_scenario("场景4", "复杂混合场景 - 多种环境变量和参数的综合处理")
    
    current_options = "DXVK_HUD=1 LD_LIBRARY_PATH=/user/lib RADV_PERFTEST=gfx10_3 %command% -windowed -console -novid"
    user_prefix, user_suffix = manager.parse_current_params(current_options)
    
    # 前置参数配置
    config_prefix = {'params': ['DXVK_HUD=fps', 'LD_LIBRARY_PATH=/opt/steam/lib', 'MANGOHUD=1']}
    prefix_user_handling = {'preserve': True, 'position': 'before'}
    prefix_conflicts = {
        'replace_keys': ['DXVK_HUD'],  # 强制替换DXVK_HUD
        'merge_keys': {'LD_LIBRARY_PATH': 'prepend'}  # 路径前置合并
    }
    
    # 后置参数配置
    config_suffix = {'params': ['-high', '-threads 4', '-nojoy']}
    suffix_user_handling = {'preserve': True, 'position': 'before'}
    suffix_conflicts = {
        'replace_rules': {
            '-windowed': '-fullscreen',  # 窗口模式替换为全屏
            '-console': ''  # 删除控制台参数
        }
    }
    
    final_prefix = manager.merge_prefix_params(user_prefix, config_prefix, prefix_user_handling, prefix_conflicts)
    final_suffix = manager.merge_suffix_params(user_suffix, config_suffix, suffix_user_handling, suffix_conflicts)
    
    print(f"用户当前前置参数: {user_prefix}")
    print(f"管理前置配置: {config_prefix['params']}")
    print(f"前置冲突规则: 替换DXVK_HUD, 合并LD_LIBRARY_PATH")
    print(f"合并后前置参数: {final_prefix}")
    print()
    print(f"用户当前后置参数: {user_suffix.split()}")
    print(f"管理后置配置: {config_suffix['params']}")
    print(f"后置冲突规则: -windowed→-fullscreen, 删除-console")
    print(f"合并后后置参数: {final_suffix}")
    
    show_merge_result(current_options, final_prefix, final_suffix)
    
    # 场景5: 不保留用户参数的场景
    print_scenario("场景5", "完全替换模式 - 不保留用户参数，完全使用管理配置")
    
    current_options = "DXVK_HUD=1 %command% -windowed -console"
    user_prefix, user_suffix = manager.parse_current_params(current_options)
    
    config_prefix = {'params': ['MANGOHUD=1', 'RADV_PERFTEST=aco']}
    prefix_user_handling = {'preserve': False}  # 不保留用户参数
    
    config_suffix = {'params': ['-fullscreen', '-high']}
    suffix_user_handling = {'preserve': False}  # 不保留用户参数
    
    final_prefix = manager.merge_prefix_params(user_prefix, config_prefix, prefix_user_handling, {})
    final_suffix = manager.merge_suffix_params(user_suffix, config_suffix, suffix_user_handling, {})
    
    print(f"用户当前参数被完全替换")
    print(f"最终前置参数: {final_prefix}")
    print(f"最终后置参数: {final_suffix}")
    
    show_merge_result(current_options, final_prefix, final_suffix)
    
    # 场景6: 真实配置文件演示
    print_scenario("场景6", "使用真实配置文件的完整流程演示")
    
    # 创建一个真实的配置文件
    demo_config = {
        'global': {
            'backup_enabled': True,
            'backup_path': '~/.config/steam-backups',
            'dry_run': False
        },
        'games': {
            '440': {
                'name': 'Team Fortress 2',
                'prefix': {
                    'params': ['DXVK_HUD=fps', 'MANGOHUD=1'],
                    'user_handling': {'preserve': True, 'position': 'before'},
                    'conflicts': {
                        'replace_keys': ['DXVK_HUD'],
                        'merge_keys': {'LD_LIBRARY_PATH': 'prepend'}
                    }
                },
                'suffix': {
                    'params': ['-novid', '-high', '-threads 4'],
                    'user_handling': {'preserve': True, 'position': 'before'},
                    'conflicts': {
                        'replace_rules': {'-windowed': '-fullscreen', '-safe': ''}
                    }
                }
            }
        }
    }
    
    # 保存临时配置文件
    import yaml
    with open(temp_config, 'w') as f:
        yaml.dump(demo_config, f, default_flow_style=False, indent=2)
    
    # 重新加载管理器以使用新配置
    manager = SteamLaunchManager(config_path=temp_config)
    
    # 模拟用户当前的启动选项
    current_options = "DXVK_HUD=1 LD_LIBRARY_PATH=/custom/lib %command% -windowed -safe -console"
    print(f"模拟用户当前启动选项: {current_options}")
    
    # 使用配置文件中的规则进行合并
    user_prefix, user_suffix = manager.parse_current_params(current_options)
    game_config = manager.config['games']['440']
    
    # 应用前置参数合并
    final_prefix = manager.merge_prefix_params(
        user_prefix, 
        game_config['prefix'], 
        game_config['prefix']['user_handling'], 
        game_config['prefix']['conflicts']
    )
    
    # 应用后置参数合并
    final_suffix = manager.merge_suffix_params(
        user_suffix, 
        game_config['suffix'], 
        game_config['suffix']['user_handling'], 
        game_config['suffix']['conflicts']
    )
    
    print(f"应用配置文件规则后:")
    print(f"- 前置参数: {final_prefix}")
    print(f"- 后置参数: {final_suffix}")
    
    show_merge_result(current_options, final_prefix, final_suffix)
    
    # 清理临时文件
    try:
        os.remove(temp_config)
    except:
        pass
    
    print_separator("演示结束")
    print("✅ 所有演示都使用了 steam-launch-manager 的真实核心逻辑")
    print("✅ 确保了测试与实际代码的一致性")
    print("✅ 避免了重复代码和潜在的不一致问题")
    print("\n通过这些例子可以看到参数合并的各种策略：")
    print("1. 环境变量冲突处理 (替换/合并)")
    print("2. 启动参数冲突处理 (替换/删除)")  
    print("3. 用户参数保留策略 (保留/替换)")
    print("4. 参数位置控制 (前置/后置)")
    print("5. 真实配置文件的完整流程")

if __name__ == "__main__":
    main() 