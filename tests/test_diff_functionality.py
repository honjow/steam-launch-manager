#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diff功能综合测试
测试diff命令的各种场景和输出格式
支持新的目录分离配置结构和多种配置类型
"""

import os
import shutil
import subprocess
import sys
import tempfile

import yaml

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "bin"))

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
        self.script_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "bin", "steam-launch-manager"
        )

    def create_steam_environment(self, steam_dir):
        """创建模拟的Steam环境"""
        user_dir = os.path.join(steam_dir, "userdata", "123456789", "config")
        os.makedirs(user_dir, exist_ok=True)

        # 创建包含各种复杂启动选项的VDF文件
        vdf_data = {
            "UserLocalConfigStore": {
                "Software": {
                    "Valve": {
                        "Steam": {
                            "Apps": {
                                "440": {  # TF2 - 简单启动选项
                                    "LaunchOptions": "-console"
                                },
                                "730": {  # CS2 - 复杂启动选项
                                    "LaunchOptions": "DXVK_HUD=memory -high -threads 4 -windowed"
                                },
                                "570": {  # Dota2 - 有环境变量和参数
                                    "LaunchOptions": "PROTON_USE_WINED3D=1 RADV_PERFTEST=aco %command% -console -novid"
                                },
                                "252490": {"LaunchOptions": ""},  # Rust - 空启动选项
                                "205950": {  # Jet Set Radio - 脚本模式测试
                                    "LaunchOptions": ""
                                },
                            }
                        }
                    }
                }
            }
        }

        vdf_file = os.path.join(user_dir, "localconfig.vdf")
        with open(vdf_file, "wb") as f:
            f.write(vdf.binary_dumps(vdf_data))

        return steam_dir

    def create_directory_config(self, config_dir, steam_dir):
        """创建目录分离的测试配置"""
        # 创建目录结构
        os.makedirs(os.path.join(config_dir, "custom"), exist_ok=True)
        os.makedirs(os.path.join(config_dir, "community"), exist_ok=True)

        # 用户自定义配置
        custom_config = {
            "global": {
                "steam_dir": steam_dir,
                "backup_enabled": True,
                "auto_update_community_db": False,  # 禁用自动更新
            },
            "games": {
                "440": {  # TF2 - 用户自定义，优先级最高
                    "name": "Team Fortress 2 - User Custom",
                    "prefix": {
                        "params": ["DXVK_HUD=fps", "RADV_PERFTEST=aco"],
                        "user_handling": {"preserve": True, "position": "before"},
                    },
                    "suffix": {
                        "params": ["-novid", "-high"],
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
                "730": {  # CS2 - 社区配置，复杂冲突处理
                    "name": "Counter-Strike 2 - Community",
                    "prefix": {
                        "params": ["DXVK_HUD=fps,memory", "PROTON_USE_WINED3D=0"],
                        "user_handling": {"preserve": True, "position": "after"},
                        "conflicts": {
                            "replace_keys": ["DXVK_HUD"]  # 替换现有的DXVK_HUD
                        },
                    },
                    "suffix": {
                        "params": ["-tickrate 128", "-fullscreen"],
                        "user_handling": {"preserve": True, "position": "before"},
                        "conflicts": {
                            "replace_rules": {
                                "-windowed": "-fullscreen"  # 替换窗口模式为全屏
                            }
                        },
                    },
                },
                "570": {  # Dota2 - 用户参数替换
                    "name": "Dota 2 - Community",
                    "prefix": {
                        "params": ["PROTON_USE_WINED3D=0", "DXVK_HUD=fps"],
                        "user_handling": {"preserve": False},  # 完全替换用户的前置参数
                    },
                    "suffix": {
                        "params": ["-dx11", "-high"],
                        "user_handling": {"preserve": True, "position": "after"},
                    },
                },
                "252490": {  # Rust - 从空开始
                    "name": "Rust - Community",
                    "prefix": {
                        "params": ["RADV_PERFTEST=aco", "__GL_THREADED_OPTIMIZATIONS=1"]
                    },
                    "suffix": {"params": ["-force-d3d11", "-high", "-maxMem=8192"]},
                },
                "205950": {  # Jet Set Radio - 脚本模式
                    "name": "Jet Set Radio - Community Script",
                    "type": "script",
                    "script_template": 'eval $(echo "%command%" | sed "s/jsrsetup.exe/jetsetradio.exe/")',
                    "description": "修复可执行文件路径问题",
                },
            },
        }

        # 写入配置文件
        with open(os.path.join(config_dir, "custom", "games.yaml"), "w") as f:
            yaml.dump(custom_config, f, default_flow_style=False, allow_unicode=True)

        with open(os.path.join(config_dir, "community", "games.yaml"), "w") as f:
            yaml.dump(community_config, f, default_flow_style=False, allow_unicode=True)

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
        config_dir = os.path.join(self.temp_dir, "steam-launch-manager")

        try:
            # 1. 创建测试环境
            print("📁 创建模拟Steam环境...")
            steam_dir = os.path.join(self.temp_dir, ".steam")
            self.create_steam_environment(steam_dir)

            print("⚙️  创建目录分离测试配置...")
            self.create_directory_config(config_dir, steam_dir)

            # 2. 测试各种diff场景
            scenarios = [
                ("440", "TF2 - 用户配置优先级", "diff"),
                ("730", "CS2 - 社区配置复杂冲突处理", "diff"),
                ("570", "Dota2 - 社区配置用户参数替换", "diff"),
                ("252490", "Rust - 社区配置从空配置开始", "diff"),
                ("205950", "Jet Set Radio - 脚本模式配置", "diff"),
                ("999", "不存在的游戏", "diff"),
                ("440", "TF2 - dry-run对比", "dry-run"),
            ]

            for app_id, description, command in scenarios:
                print(f"\n🎮 {description}")
                print("-" * 50)

                result = self.run_command(
                    [
                        "python3",
                        self.script_path,
                        "--config",
                        config_dir,
                        command,
                        app_id,
                    ]
                )

                if result:
                    if result.returncode == 0:
                        print("✅ 命令执行成功")
                        if result.stdout.strip():
                            print("输出:")
                            # 截取输出的前几行避免过长
                            lines = result.stdout.split("\n")[:15]
                            for line in lines:
                                print(line)
                            if len(result.stdout.split("\n")) > 15:
                                print("... (输出已截断)")
                    else:
                        print("❌ 命令执行失败")
                        if result.stderr:
                            print(f"错误: {result.stderr}")
                else:
                    print("❌ 命令运行异常")

                print()

            # 3. 测试配置来源显示
            print("\n" + "=" * 80)
            print("🔍 配置来源和优先级测试")
            print("=" * 80)

            print("\n📊 用户配置优先级测试 (440 - TF2):")
            print("-" * 40)

            diff_result = self.run_command(
                ["python3", self.script_path, "--config", config_dir, "diff", "440"]
            )

            if diff_result and diff_result.returncode == 0:
                output = diff_result.stdout
                if "custom" in output.lower() or "user" in output.lower():
                    print("✅ 正确显示用户配置来源")
                else:
                    print("❌ 未正确显示配置来源")

            print("\n📊 社区配置使用测试 (730 - CS2):")
            print("-" * 40)

            diff_result = self.run_command(
                ["python3", self.script_path, "--config", config_dir, "diff", "730"]
            )

            if diff_result and diff_result.returncode == 0:
                output = diff_result.stdout
                if "community" in output.lower():
                    print("✅ 正确显示社区配置来源")
                else:
                    print("❌ 未正确显示配置来源")

            # 4. 测试新配置类型
            print("\n" + "=" * 80)
            print("🚀 新配置类型测试")
            print("=" * 80)

            print("\n🔧 脚本模式配置测试 (205950 - Jet Set Radio):")
            print("-" * 50)

            script_result = self.run_command(
                ["python3", self.script_path, "--config", config_dir, "diff", "205950"]
            )

            if script_result and script_result.returncode == 0:
                output = script_result.stdout
                if "script" in output.lower() or "eval" in output:
                    print("✅ 正确处理脚本模式配置")
                else:
                    print("❌ 脚本模式配置处理异常")

                if "description" in output.lower() or "修复" in output:
                    print("✅ 正确显示配置描述")
                else:
                    print("❌ 未显示配置描述")

            # 5. 测试diff vs dry-run的区别
            print("\n" + "=" * 80)
            print("🔄 Diff vs Dry-run 对比测试")
            print("=" * 80)

            print("\n📊 Diff命令输出 (详细差异分析):")
            print("-" * 40)

            diff_result = self.run_command(
                [
                    "python3",
                    self.script_path,
                    "--config",
                    config_dir,
                    "diff",
                    "730",  # 使用复杂的CS2配置
                ]
            )

            if diff_result and diff_result.returncode == 0:
                output = diff_result.stdout

                # 检查输出格式
                checks = [
                    ("📋 Current configuration", "当前配置标识"),
                    ("🎯 Proposed configuration", "建议配置标识"),
                    ("🔄 Changes", "变更分析标识"),
                    ("Counter-Strike 2", "游戏名称显示"),
                    ("DXVK_HUD", "环境变量内容"),
                    ("-windowed", "参数冲突处理"),
                ]

                print("输出格式检查:")
                for check, description in checks:
                    if check in output:
                        print(f"  ✅ {description}")
                    else:
                        print(f"  ❌ {description} (缺失: {check})")

            print("\n📊 Dry-run命令输出 (应用预览):")
            print("-" * 40)

            dryrun_result = self.run_command(
                ["python3", self.script_path, "--config", config_dir, "dry-run", "730"]
            )

            if dryrun_result and dryrun_result.returncode == 0:
                print("✅ Dry-run命令执行成功")
                print(
                    "输出格式:",
                    "预览模式" if "dry" in dryrun_result.stdout.lower() else "标准模式",
                )

        finally:
            # 清理
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)
                print(f"\n🧹 清理临时文件: {self.temp_dir}")

    def test_edge_cases(self):
        """测试边缘情况"""
        print("\n🔍 边缘情况测试")
        print("=" * 50)

        self.temp_dir = tempfile.mkdtemp()
        config_dir = os.path.join(self.temp_dir, "steam-launch-manager")

        try:
            # 1. 空配置目录
            print("\n📂 空配置目录测试:")
            os.makedirs(config_dir, exist_ok=True)

            result = self.run_command(
                ["python3", self.script_path, "--config", config_dir, "diff", "440"]
            )

            if result:
                if result.returncode == 0:
                    print("✅ 空配置目录处理正常")
                else:
                    print("❌ 空配置目录处理失败")

            # 2. 无效配置文件
            print("\n📄 无效配置文件测试:")
            os.makedirs(os.path.join(config_dir, "custom"), exist_ok=True)

            with open(os.path.join(config_dir, "custom", "games.yaml"), "w") as f:
                f.write("invalid: yaml: content: [")

            result = self.run_command(
                ["python3", self.script_path, "--config", config_dir, "validate"]
            )

            if result:
                print(f"无效配置处理: {'正常' if result.returncode != 127 else '异常'}")

            # 3. 权限问题模拟（只读目录）
            print("\n🔒 权限问题模拟:")
            readonly_dir = os.path.join(self.temp_dir, "readonly")
            os.makedirs(readonly_dir, exist_ok=True)
            os.chmod(readonly_dir, 0o444)  # 只读

            result = self.run_command(
                ["python3", self.script_path, "--config", readonly_dir, "init"]
            )

            if result:
                print(
                    f"只读目录处理: {'正常' if result.returncode != 0 else '未检测到权限问题'}"
                )

            # 恢复权限以便清理
            os.chmod(readonly_dir, 0o755)

        finally:
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 清理测试文件: {self.temp_dir}")


def main():
    """主测试函数"""
    print("🎯 启动 Steam Launch Manager Diff 功能综合测试")
    print(f"Python版本: {sys.version}")
    print(f"测试脚本位置: {__file__}")
    print()

    test = DiffFunctionalityTest()

    try:
        # 主要功能测试
        test.test_diff_scenarios()

        # 边缘情况测试
        test.test_edge_cases()

        print("\n🎉 所有测试完成!")

    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n📋 测试结束")


if __name__ == "__main__":
    main()
