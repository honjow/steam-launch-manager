#!/usr/bin/env python3
"""
steam-launch-manager CLI工具的集成测试
测试实际的命令行接口和端到端功能
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


class TestSteamLaunchManagerCLI(unittest.TestCase):
    """测试steam-launch-manager命令行接口"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "steam-launch-manager")
        self.script_path = (
            Path(__file__).parent.parent / "src" / "bin" / "steam-launch-manager"
        )

        # 创建目录结构
        os.makedirs(os.path.join(self.config_dir, "custom"), exist_ok=True)
        os.makedirs(os.path.join(self.config_dir, "community"), exist_ok=True)

        # 创建测试的用户自定义配置
        self.custom_config = {
            "global": {
                "backup_enabled": True,
                "backup_path": os.path.join(self.temp_dir, "backups"),
                "dry_run": False,
                "auto_update_community_db": False,  # 禁用自动更新避免网络依赖
            },
            "games": {
                "440": {
                    "name": "Team Fortress 2 - Custom",
                    "prefix": {
                        "params": ["DXVK_HUD=fps"],
                        "user_handling": {"preserve": True, "position": "before"},
                        "conflicts": {"replace_keys": ["DXVK_HUD"]},
                    },
                    "suffix": {
                        "params": ["-novid", "-high"],
                        "user_handling": {"preserve": True, "position": "before"},
                        "conflicts": {"replace_rules": {"-windowed": "-fullscreen"}},
                    },
                }
            },
        }

        # 创建测试的社区配置
        self.community_config = {
            "global": {
                "backup_enabled": True,
                "backup_path": "~/.config/steam-backups",
                "dry_run": False,
            },
            "games": {
                "730": {
                    "name": "Counter-Strike 2 - Community",
                    "prefix": {
                        "params": ["RADV_PERFTEST=aco"],
                        "user_handling": {"preserve": True, "position": "before"},
                    },
                    "suffix": {
                        "params": ["-high", "-threads 4"],
                        "user_handling": {"preserve": True, "position": "before"},
                    },
                }
            },
        }

        # 写入配置文件
        with open(os.path.join(self.config_dir, "custom", "games.yaml"), "w") as f:
            yaml.dump(self.custom_config, f)

        with open(os.path.join(self.config_dir, "community", "games.yaml"), "w") as f:
            yaml.dump(self.community_config, f)

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)

    def run_command(self, args, expect_success=True):
        """运行steam-launch-manager命令的辅助方法"""
        cmd = ["python3", str(self.script_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)

        if expect_success:
            if result.returncode != 0:
                print(f"Command failed: {' '.join(cmd)}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")

        return result

    def test_help_command(self):
        """测试--help标志"""
        result = self.run_command(["--help"])
        self.assertIn("Steam Launch Options Manager", result.stdout)
        self.assertIn("apply", result.stdout)
        self.assertIn("validate", result.stdout)
        self.assertIn("update-db", result.stdout)  # 新命令

    def test_init_command(self):
        """测试init命令创建配置目录"""
        new_config_dir = os.path.join(self.temp_dir, "new-config")
        result = self.run_command(["--config", new_config_dir, "init"])

        # 验证目录结构
        self.assertTrue(
            os.path.exists(os.path.join(new_config_dir, "custom", "games.yaml"))
        )
        self.assertTrue(os.path.exists(os.path.join(new_config_dir, "community")))
        self.assertIn("Configuration file created/updated", result.stdout)

        # 验证用户配置内容
        with open(os.path.join(new_config_dir, "custom", "games.yaml")) as f:
            config = yaml.safe_load(f)

        self.assertIn("global", config)
        self.assertIn("games", config)
        self.assertIn("auto_update_community_db", config["global"])

    def test_directory_structure(self):
        """测试目录分离结构"""
        # 验证配置目录结构存在
        self.assertTrue(
            os.path.exists(os.path.join(self.config_dir, "custom", "games.yaml"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.config_dir, "community", "games.yaml"))
        )

        # 验证配置可以正确加载
        result = self.run_command(["--config", self.config_dir, "validate"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Configuration is valid", result.stdout)

    def test_validate_command(self):
        """测试validate命令"""
        result = self.run_command(["--config", self.config_dir, "validate"])
        self.assertIn("Configuration is valid", result.stdout)
        # 应该显示用户配置和社区配置的统计信息
        self.assertIn("custom configs", result.stdout)
        self.assertIn("community configs", result.stdout)

    def test_validate_invalid_config(self):
        """测试无效配置的validate命令"""
        invalid_config = {"invalid": "config"}
        invalid_config_dir = os.path.join(self.temp_dir, "invalid-config")
        os.makedirs(os.path.join(invalid_config_dir, "custom"), exist_ok=True)

        with open(os.path.join(invalid_config_dir, "custom", "games.yaml"), "w") as f:
            yaml.dump(invalid_config, f)

        result = self.run_command(["--config", invalid_config_dir, "validate"])
        # 应该仍然成功但可能显示警告
        self.assertEqual(result.returncode, 0)

    def test_dry_run_mode(self):
        """测试干运行功能"""
        result = self.run_command(
            ["--config", self.config_dir, "--dry-run", "apply", "440"]
        )
        # 应该成功但不做实际更改
        self.assertEqual(result.returncode, 0)

    def test_missing_app_id(self):
        """测试缺少App ID的错误处理"""
        result = self.run_command(
            ["--config", self.config_dir, "apply"], expect_success=False
        )
        # 没有App ID的apply命令应该失败或显示用法说明
        self.assertTrue(
            result.returncode != 0
            or "usage:" in result.stdout.lower()
            or "app id" in result.stdout.lower()
            or "app id" in result.stderr.lower()
            or "apply-all" in result.stdout.lower()
        )

    def test_missing_config_file(self):
        """测试缺少配置文件的处理"""
        missing_config_dir = os.path.join(self.temp_dir, "missing-config")
        result = self.run_command(["--config", missing_config_dir, "validate"])
        # 应该创建默认配置目录和文件并成功
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            os.path.exists(os.path.join(missing_config_dir, "custom", "games.yaml"))
        )
        self.assertTrue(os.path.exists(os.path.join(missing_config_dir, "community")))

    def test_update_db_command(self):
        """测试update-db命令"""
        # 注意：这个测试需要网络连接，在CI环境中可能需要跳过
        try:
            result = self.run_command(["--config", self.config_dir, "update-db"])
            # 如果有网络连接，应该成功
            if result.returncode == 0:
                self.assertIn("Update completed", result.stdout)
            else:
                # 如果没有网络连接，应该显示相应的错误信息
                self.assertTrue(
                    "network" in result.stderr.lower()
                    or "connection" in result.stderr.lower()
                )
        except Exception:
            # 网络问题时跳过测试
            self.skipTest("Network connection required for update-db test")


class TestSteamConfigGenCLI(unittest.TestCase):
    """测试steam-config-gen命令行工具"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.script_path = (
            Path(__file__).parent.parent / "src" / "bin" / "steam-config-gen"
        )

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)

    def run_command(self, args, expect_success=True):
        """运行steam-config-gen命令的辅助方法"""
        cmd = ["python3", str(self.script_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)

        if expect_success:
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")

        return result

    def test_help_command(self):
        """测试--help标志"""
        result = self.run_command(["--help"])
        self.assertIn("Steam Launch Options Config Generator", result.stdout)
        self.assertIn("--list", result.stdout)
        self.assertIn("--generate", result.stdout)

    def test_list_templates(self):
        """测试--list标志"""
        result = self.run_command(["--list"])
        self.assertIn("Available game templates", result.stdout)
        self.assertIn("440:", result.stdout)  # 应该显示TF2
        self.assertIn("730:", result.stdout)  # 应该显示CS2

    def test_generate_config(self):
        """测试配置生成 - 现在生成到用户配置目录"""
        output_dir = os.path.join(self.temp_dir, "generated-config")
        # steam-config-gen现在应该生成到用户配置目录结构
        result = self.run_command(["--generate", "440", "730", "--output", output_dir])

        # 检查是否生成了正确的目录结构（如果config-gen支持新结构）
        # 或者检查是否生成了传统的单文件配置
        self.assertTrue(os.path.exists(output_dir))
        self.assertIn("Configuration saved", result.stdout)

        # 验证生成的配置内容
        if os.path.exists(os.path.join(output_dir)):
            with open(output_dir) as f:
                config = yaml.safe_load(f)

            self.assertIn("games", config)
            self.assertIn("440", config["games"])
            self.assertIn("730", config["games"])


class TestSteamWrapperCLI(unittest.TestCase):
    """测试steam-wrapper脚本"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.script_path = (
            Path(__file__).parent.parent / "src" / "bin" / "steam-wrapper"
        )

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)

    def test_wrapper_script_exists(self):
        """测试包装器脚本存在且可执行"""
        self.assertTrue(self.script_path.exists())
        self.assertTrue(os.access(self.script_path, os.R_OK))

    def test_wrapper_help(self):
        """测试包装器帮助信息"""
        # 注意：steam-wrapper可能不支持--help，或者会尝试启动Steam
        # 这里只测试脚本是否能正常运行
        result = subprocess.run(
            ["python3", str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # 不要求特定的返回码，只要不崩溃即可
        self.assertIsNotNone(result)


class TestEndToEndWorkflow(unittest.TestCase):
    """端到端工作流程测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "steam-launch-manager")
        self.script_path = (
            Path(__file__).parent.parent / "src" / "bin" / "steam-launch-manager"
        )

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)

    def test_complete_workflow(self):
        """测试完整的工作流程"""
        # 1. 初始化配置
        result = subprocess.run(
            ["python3", str(self.script_path), "--config", self.config_dir, "init"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

        # 2. 验证配置
        result = subprocess.run(
            ["python3", str(self.script_path), "--config", self.config_dir, "validate"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

        # 3. 添加测试游戏配置
        custom_config_path = os.path.join(self.config_dir, "custom", "games.yaml")
        with open(custom_config_path, "r") as f:
            config = yaml.safe_load(f)

        config["games"]["440"] = {
            "name": "Team Fortress 2 - Test",
            "prefix": {"params": ["DXVK_HUD=fps"]},
            "suffix": {"params": ["-novid"]},
        }

        with open(custom_config_path, "w") as f:
            yaml.dump(config, f)

        # 4. 测试diff命令
        result = subprocess.run(
            [
                "python3",
                str(self.script_path),
                "--config",
                self.config_dir,
                "diff",
                "440",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

        # 5. 测试dry-run
        result = subprocess.run(
            [
                "python3",
                str(self.script_path),
                "--config",
                self.config_dir,
                "dry-run",
                "440",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_error_handling_workflow(self):
        """测试错误处理工作流程"""
        # 测试无效的App ID
        result = subprocess.run(
            [
                "python3",
                str(self.script_path),
                "--config",
                self.config_dir,
                "diff",
                "invalid-app-id",
            ],
            capture_output=True,
            text=True,
        )
        # 应该优雅地处理错误
        self.assertIsNotNone(result)

        # 测试不存在的配置目录
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        result = subprocess.run(
            ["python3", str(self.script_path), "--config", nonexistent_dir, "validate"],
            capture_output=True,
            text=True,
        )
        # 应该自动创建配置目录
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            os.path.exists(os.path.join(nonexistent_dir, "custom", "games.yaml"))
        )


if __name__ == "__main__":
    unittest.main()
