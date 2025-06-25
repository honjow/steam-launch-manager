#!/usr/bin/env python3
"""
steam-launch-manager CLI工具的集成测试
测试实际的命令行接口和端到端功能
"""

import unittest
import tempfile
import os
import subprocess
import yaml
import shutil
from pathlib import Path

class TestSteamLaunchManagerCLI(unittest.TestCase):
    """测试steam-launch-manager命令行接口"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test-config.yaml')
        self.script_path = Path(__file__).parent.parent / 'src' / 'bin' / 'steam-launch-manager'
        
        # 创建测试配置
        self.test_config = {
            'global': {
                'backup_enabled': True,
                'backup_path': os.path.join(self.temp_dir, 'backups'),
                'dry_run': False
            },
            'games': {
                '440': {
                    'name': 'Team Fortress 2',
                    'prefix': {
                        'params': ['DXVK_HUD=fps'],
                        'user_handling': {'preserve': True, 'position': 'before'},
                        'conflicts': {'replace_keys': ['DXVK_HUD']}
                    },
                    'suffix': {
                        'params': ['-novid', '-high'],
                        'user_handling': {'preserve': True, 'position': 'before'},
                        'conflicts': {'replace_rules': {'-windowed': '-fullscreen'}}
                    }
                }
            }
        }
        
        # 写入测试配置文件
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def run_command(self, args, expect_success=True):
        """运行steam-launch-manager命令的辅助方法"""
        cmd = ['python3', str(self.script_path)] + args
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
        result = self.run_command(['--help'])
        self.assertIn('Steam Launch Options Manager', result.stdout)
        self.assertIn('apply', result.stdout)
        self.assertIn('validate', result.stdout)
    
    def test_init_command(self):
        """测试init命令创建配置文件"""
        new_config_path = os.path.join(self.temp_dir, 'new-config.yaml')
        result = self.run_command(['--config', new_config_path, 'init'])
        
        self.assertTrue(os.path.exists(new_config_path))
        self.assertIn('Configuration file created/updated', result.stdout)
        
        # 验证配置内容
        with open(new_config_path) as f:
            config = yaml.safe_load(f)
        
        self.assertIn('global', config)
        self.assertIn('games', config)
    
    def test_validate_command(self):
        """测试validate命令"""
        result = self.run_command(['--config', self.config_path, 'validate'])
        self.assertIn('Configuration is valid', result.stdout)
    
    def test_validate_invalid_config(self):
        """测试无效配置的validate命令"""
        invalid_config = {'invalid': 'config'}
        invalid_config_path = os.path.join(self.temp_dir, 'invalid.yaml')
        
        with open(invalid_config_path, 'w') as f:
            yaml.dump(invalid_config, f)
        
        result = self.run_command(['--config', invalid_config_path, 'validate'])
        # 应该仍然成功但可能显示警告
        self.assertEqual(result.returncode, 0)
    
    def test_dry_run_mode(self):
        """测试干运行功能"""
        result = self.run_command(['--config', self.config_path, '--dry-run', 'apply', '440'])
        # 应该成功但不做实际更改
        self.assertEqual(result.returncode, 0)
    
    def test_missing_app_id(self):
        """测试缺少App ID的错误处理"""
        result = self.run_command(['--config', self.config_path, 'apply'], expect_success=False)
        # 没有App ID的apply命令应该失败或显示用法说明
        # 检查是否适当处理了缺少的App ID
        self.assertTrue(
            result.returncode != 0 or 
            'usage:' in result.stdout.lower() or 
            'app id' in result.stdout.lower() or
            'apply-all' in result.stdout.lower()
        )
    
    def test_missing_config_file(self):
        """测试缺少配置文件的处理"""
        missing_config = os.path.join(self.temp_dir, 'missing.yaml')
        result = self.run_command(['--config', missing_config, 'validate'])
        # 应该创建默认配置并成功
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(missing_config))

class TestSteamConfigGenCLI(unittest.TestCase):
    """测试steam-config-gen命令行工具"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.script_path = Path(__file__).parent.parent / 'src' / 'bin' / 'steam-config-gen'
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def run_command(self, args, expect_success=True):
        """运行steam-config-gen命令的辅助方法"""
        cmd = ['python3', str(self.script_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)
        
        if expect_success:
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
        
        return result
    
    def test_help_command(self):
        """测试--help标志"""
        result = self.run_command(['--help'])
        self.assertIn('Steam Launch Options Config Generator', result.stdout)
        self.assertIn('--list', result.stdout)
        self.assertIn('--generate', result.stdout)
    
    def test_list_templates(self):
        """测试--list标志"""
        result = self.run_command(['--list'])
        self.assertIn('Available game templates', result.stdout)
        self.assertIn('440:', result.stdout)  # 应该显示TF2
        self.assertIn('730:', result.stdout)  # 应该显示CS2
    
    def test_generate_config(self):
        """测试配置生成"""
        output_path = os.path.join(self.temp_dir, 'generated.yaml')
        result = self.run_command(['--generate', '440', '730', '--output', output_path])
        
        self.assertTrue(os.path.exists(output_path))
        self.assertIn('Configuration saved', result.stdout)
        
        # 验证生成的配置
        with open(output_path) as f:
            config = yaml.safe_load(f)
        
        self.assertIn('games', config)
        self.assertIn('440', config['games'])
        self.assertIn('730', config['games'])

class TestSteamWrapperCLI(unittest.TestCase):
    """测试steam-wrapper脚本"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.script_path = Path(__file__).parent.parent / 'src' / 'bin' / 'steam-wrapper'
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_wrapper_script_exists(self):
        """测试包装器脚本存在且可执行"""
        self.assertTrue(self.script_path.exists())
        self.assertTrue(os.access(self.script_path, os.X_OK))
    
    def test_wrapper_help(self):
        """测试包装器脚本基本功能"""
        result = subprocess.run(['bash', str(self.script_path)], 
                              capture_output=True, text=True, timeout=5)
        # 包装器应该运行并到达steam执行部分
        # 当找不到steam时预期会失败并返回127
        # 我们主要测试脚本语法有效并能到达末尾
        self.assertIn('Starting Steam', result.stdout)
        # 脚本应该在exec steam步骤失败，这是预期的

class TestEndToEndWorkflow(unittest.TestCase):
    """测试完整工作流程场景"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'workflow-config.yaml')
        self.manager_script = Path(__file__).parent.parent / 'src' / 'bin' / 'steam-launch-manager'
        self.gen_script = Path(__file__).parent.parent / 'src' / 'bin' / 'steam-config-gen'
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """测试：生成配置 -> 验证 -> 应用（干运行）"""
        # 步骤1：生成配置
        result1 = subprocess.run([
            'python3', str(self.gen_script),
            '--generate', '440',
            '--output', self.config_path
        ], capture_output=True, text=True)
        self.assertEqual(result1.returncode, 0)
        
        # 步骤2：验证配置
        result2 = subprocess.run([
            'python3', str(self.manager_script),
            '--config', self.config_path,
            'validate'
        ], capture_output=True, text=True)
        self.assertEqual(result2.returncode, 0)
        
        # 步骤3：以干运行模式应用
        result3 = subprocess.run([
            'python3', str(self.manager_script),
            '--config', self.config_path,
            '--dry-run',
            'apply', '440'
        ], capture_output=True, text=True)
        self.assertEqual(result3.returncode, 0)
    
    def test_error_handling_workflow(self):
        """测试各种场景下的错误处理"""
        # 测试不存在的app ID
        result = subprocess.run([
            'python3', str(self.manager_script),
            '--config', self.config_path,
            'apply', '999999'
        ], capture_output=True, text=True)
        # 应该优雅地处理（可能成功并显示"未找到配置"消息）
        self.assertNotEqual(result.returncode, 127)  # 不是"命令未找到"

if __name__ == '__main__':
    unittest.main() 