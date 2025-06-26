#!/usr/bin/env python3
"""
Steam启动参数合并演示
直接使用 steam-launch-manager 的核心逻辑进行演示
支持新的目录分离配置结构和配置优先级演示
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

# 动态导入 steam-launch-manager 脚本
script_path = Path(__file__).parent.parent / "src" / "bin" / "steam-launch-manager"

# 直接执行脚本文件来导入
with open(script_path, "r") as f:
    script_content = f.read()

# 创建一个模块对象并执行脚本内容
steam_launch_manager = type(sys)("steam_launch_manager")
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
        prefix_str = " ".join(final_prefix)
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


def create_test_configs(config_dir):
    """创建测试用的目录分离配置"""
    os.makedirs(os.path.join(config_dir, "custom"), exist_ok=True)
    os.makedirs(os.path.join(config_dir, "community"), exist_ok=True)

    # 用户自定义配置
    custom_config = {
        "global": {
            "backup_enabled": True,
            "backup_path": "~/.config/steam-backups",
            "dry_run": False,
            "auto_update_community_db": False,
        },
        "games": {
            "440": {  # TF2 - 用户自定义配置
                "name": "Team Fortress 2 - User Custom",
                "prefix": {
                    "params": ["DXVK_HUD=fps_user", "CUSTOM_VAR=user_value"],
                    "user_handling": {"preserve": True, "position": "before"},
                    "conflicts": {"replace_keys": ["DXVK_HUD"]},
                },
                "suffix": {
                    "params": ["-novid_user", "-high_user"],
                    "user_handling": {"preserve": True, "position": "before"},
                },
            }
        },
    }

    # 社区预设配置
    community_config = {
        "global": {
            "backup_enabled": True,
            "backup_path": "~/.config/steam-backups",
            "dry_run": False,
        },
        "games": {
            "440": {  # TF2 - 社区配置（会被用户配置覆盖）
                "name": "Team Fortress 2 - Community",
                "prefix": {
                    "params": [
                        "DXVK_HUD=fps_community",
                        "COMMUNITY_VAR=community_value",
                    ],
                    "user_handling": {"preserve": True, "position": "before"},
                },
                "suffix": {
                    "params": ["-novid_community", "-high_community"],
                    "user_handling": {"preserve": True, "position": "before"},
                },
            },
            "730": {  # CS2 - 只有社区配置
                "name": "Counter-Strike 2 - Community Only",
                "prefix": {
                    "params": ["RADV_PERFTEST=aco", "PROTON_USE_WINED3D=0"],
                    "user_handling": {"preserve": True, "position": "before"},
                },
                "suffix": {
                    "params": ["-high", "-threads 4"],
                    "user_handling": {"preserve": True, "position": "before"},
                    "conflicts": {"replace_rules": {"-windowed": "-fullscreen"}},
                },
            },
        },
    }

    # 写入配置文件
    with open(os.path.join(config_dir, "custom", "games.yaml"), "w") as f:
        yaml.dump(custom_config, f, default_flow_style=False)

    with open(os.path.join(config_dir, "community", "games.yaml"), "w") as f:
        yaml.dump(community_config, f, default_flow_style=False)


def main():
    # 创建临时目录进行测试
    temp_dir = tempfile.mkdtemp()
    config_dir = os.path.join(temp_dir, "steam-launch-manager")

    try:
        print_separator("Steam启动参数合并演示 - 目录分离配置版本")
        print("使用 steam-launch-manager 的真实核心逻辑")
        print(f"测试配置目录: {config_dir}")

        # 创建测试配置
        create_test_configs(config_dir)

        # 创建 SteamLaunchManager 实例
        manager = SteamLaunchManager(config_path=config_dir)

        # 演示1: 配置优先级系统
        print_separator("配置优先级系统演示")

        print_scenario("场景1", "用户配置优先级 - TF2有用户配置，应该使用用户配置")

        game_config, config_source = manager.get_game_config("440", verbose=True)
        if game_config:
            print(f"配置来源: {config_source}")
            print(f"游戏名称: {game_config.get('name', 'Unknown')}")
            print(f"前置参数: {game_config.get('prefix', {}).get('params', [])}")
            print(f"后置参数: {game_config.get('suffix', {}).get('params', [])}")
        else:
            print("未找到配置")

        print_scenario("场景2", "社区配置使用 - CS2只有社区配置，应该使用社区配置")

        game_config, config_source = manager.get_game_config("730", verbose=True)
        if game_config:
            print(f"配置来源: {config_source}")
            print(f"游戏名称: {game_config.get('name', 'Unknown')}")
            print(f"前置参数: {game_config.get('prefix', {}).get('params', [])}")
            print(f"后置参数: {game_config.get('suffix', {}).get('params', [])}")
        else:
            print("未找到配置")

        print_scenario("场景3", "无配置游戏 - Dota2没有任何配置")

        game_config, config_source = manager.get_game_config("570", verbose=True)
        if game_config:
            print(f"配置来源: {config_source}")
            print(f"游戏名称: {game_config.get('name', 'Unknown')}")
        else:
            print("未找到配置（符合预期）")

        # 演示2: 参数合并逻辑（使用用户配置）
        print_separator("参数合并逻辑演示")

        print_scenario("场景4", "用户配置参数合并 - 基础环境变量冲突处理")

        # 模拟用户当前的启动选项
        current_options = "DXVK_HUD=1 OLD_VAR=old_value %command% -console"
        user_prefix, user_suffix = manager.parse_current_params(current_options)

        # 获取用户配置
        game_config, _ = manager.get_game_config("440")
        if game_config and "prefix" in game_config:
            config_prefix = game_config["prefix"]
            user_handling = config_prefix.get("user_handling", {})
            conflicts = config_prefix.get("conflicts", {})

            final_prefix = manager.merge_prefix_params(
                user_prefix, config_prefix, user_handling, conflicts
            )

            print(f"用户当前前置参数: {user_prefix}")
            print(f"用户配置参数: {config_prefix['params']}")
            print(f"冲突处理规则: {conflicts}")
            print(f"合并后前置参数: {final_prefix}")

            show_merge_result(current_options, final_prefix, user_suffix)

        # 演示3: 社区配置参数合并
        print_scenario("场景5", "社区配置参数合并 - CS2复杂冲突处理")

        current_options = "DXVK_HUD=memory %command% -windowed -high"
        user_prefix, user_suffix = manager.parse_current_params(current_options)

        # 获取社区配置
        game_config, _ = manager.get_game_config("730")
        if game_config:
            # 处理前置参数
            if "prefix" in game_config:
                config_prefix = game_config["prefix"]
                user_handling = config_prefix.get("user_handling", {})
                conflicts = config_prefix.get("conflicts", {})

                final_prefix = manager.merge_prefix_params(
                    user_prefix, config_prefix, user_handling, conflicts
                )
            else:
                final_prefix = user_prefix

            # 处理后置参数
            if "suffix" in game_config:
                config_suffix = game_config["suffix"]
                user_handling = config_suffix.get("user_handling", {})
                conflicts = config_suffix.get("conflicts", {})

                final_suffix = manager.merge_suffix_params(
                    user_suffix, config_suffix, user_handling, conflicts
                )
            else:
                final_suffix = user_suffix

            print(f"用户当前前置参数: {user_prefix}")
            print(f"社区前置配置: {game_config.get('prefix', {}).get('params', [])}")
            print(f"合并后前置参数: {final_prefix}")
            print()
            print(f"用户当前后置参数: {user_suffix.split()}")
            print(f"社区后置配置: {game_config.get('suffix', {}).get('params', [])}")
            print(f"冲突处理规则: {game_config.get('suffix', {}).get('conflicts', {})}")
            print(f"合并后后置参数: {final_suffix}")

            show_merge_result(current_options, final_prefix, final_suffix)

        # 演示4: 路径合并
        print_scenario("场景6", "路径环境变量合并 - LD_LIBRARY_PATH前置合并")

        current_options = "LD_LIBRARY_PATH=/user/lib %command% -high"
        user_prefix, user_suffix = manager.parse_current_params(current_options)

        # 创建一个包含路径合并的配置
        config_prefix = {"params": ["LD_LIBRARY_PATH=/opt/steam/lib"]}
        user_handling = {"preserve": True, "position": "before"}
        conflicts = {"merge_keys": {"LD_LIBRARY_PATH": "prepend"}}

        final_prefix = manager.merge_prefix_params(
            user_prefix, config_prefix, user_handling, conflicts
        )

        print(f"用户当前前置参数: {user_prefix}")
        print(f"管理配置参数: {config_prefix['params']}")
        print("冲突处理规则: LD_LIBRARY_PATH前置合并")
        print(f"合并后前置参数: {final_prefix}")

        show_merge_result(current_options, final_prefix, user_suffix)

        # 演示5: 不保留用户参数的场景
        print_scenario("场景7", "完全替换模式 - 不保留用户参数，完全使用管理配置")

        current_options = "DXVK_HUD=1 %command% -windowed -console"
        user_prefix, user_suffix = manager.parse_current_params(current_options)

        config_prefix = {"params": ["MANGOHUD=1", "RADV_PERFTEST=aco"]}
        prefix_user_handling = {"preserve": False}  # 不保留用户参数

        config_suffix = {"params": ["-fullscreen", "-high"]}
        suffix_user_handling = {"preserve": False}  # 不保留用户参数

        final_prefix = manager.merge_prefix_params(
            user_prefix, config_prefix, prefix_user_handling, {}
        )
        final_suffix = manager.merge_suffix_params(
            user_suffix, config_suffix, suffix_user_handling, {}
        )

        print("用户当前参数被完全替换")
        print(f"最终前置参数: {final_prefix}")
        print(f"最终后置参数: {final_suffix}")

        show_merge_result(current_options, final_prefix, final_suffix)

        # 演示6: 目录结构和配置文件展示
        print_separator("配置文件结构展示")

        print("📂 配置目录结构:")
        print(f"  {config_dir}/")
        print("  ├── custom/")
        print("  │   └── games.yaml      # 用户自定义配置")
        print("  └── community/")
        print("      └── games.yaml      # 社区预设配置")

        print("\n📄 用户自定义配置内容:")
        with open(os.path.join(config_dir, "custom", "games.yaml"), "r") as f:
            custom_content = f.read()
        print("```yaml")
        print(
            custom_content[:500] + "..."
            if len(custom_content) > 500
            else custom_content
        )
        print("```")

        print("\n📄 社区预设配置内容:")
        with open(os.path.join(config_dir, "community", "games.yaml"), "r") as f:
            community_content = f.read()
        print("```yaml")
        print(
            community_content[:500] + "..."
            if len(community_content) > 500
            else community_content
        )
        print("```")

        print_separator("演示总结")
        print("✅ 目录分离配置结构测试完成")
        print("✅ 配置优先级系统验证完成（用户 > 社区 > 无配置）")
        print("✅ 参数合并逻辑演示完成")
        print("✅ 环境变量冲突处理演示完成")
        print("✅ 启动参数替换演示完成")
        print("✅ 路径合并演示完成")
        print("✅ 完全替换模式演示完成")

    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)
        print(f"\n🧹 清理临时文件: {temp_dir}")


if __name__ == "__main__":
    main()
