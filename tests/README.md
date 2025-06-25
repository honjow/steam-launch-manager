# Steam Launch Manager - 测试套件

## 📋 测试概览

测试套件包含以下模块：
- `test_cli_integration.py` - CLI工具集成测试（主要测试）
- `test-merge-example.py` - 参数合并功能演示

## 🚀 运行测试

### 环境要求
```bash
pip install pyyaml
```

### 运行所有测试
```bash
# 使用pytest（推荐）
python -m pytest tests/ -v

# 或使用unittest
python -m unittest discover tests/ -v
```

### 运行单个测试模块
```bash
# CLI集成测试
python -m pytest tests/test_cli_integration.py -v

# 参数合并演示
python tests/test-merge-example.py
```

### 运行特定测试
```bash
# 测试帮助命令
python -m pytest tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_help_command -v

# 测试完整工作流程
python -m pytest tests/test_cli_integration.py::TestEndToEndWorkflow::test_complete_workflow -v
```

## 📊 测试覆盖范围

### CLI集成测试 (`test_cli_integration.py`) - 14个测试
这是主要的测试文件，测试实际的命令行工具：

#### TestSteamLaunchManagerCLI (7个测试)
- ✅ `test_help_command` - 测试--help帮助信息
- ✅ `test_init_command` - 测试初始化配置文件
- ✅ `test_validate_command` - 测试配置验证
- ✅ `test_validate_invalid_config` - 测试无效配置处理
- ✅ `test_dry_run_mode` - 测试干运行模式
- ✅ `test_missing_app_id` - 测试缺少App ID的错误处理
- ✅ `test_missing_config_file` - 测试缺少配置文件的处理

#### TestSteamConfigGenCLI (3个测试)
- ✅ `test_help_command` - 测试steam-config-gen帮助
- ✅ `test_list_templates` - 测试游戏模板列表
- ✅ `test_generate_config` - 测试配置文件生成

#### TestSteamWrapperCLI (2个测试)
- ✅ `test_wrapper_script_exists` - 测试包装器脚本存在
- ✅ `test_wrapper_help` - 测试包装器脚本运行

#### TestEndToEndWorkflow (2个测试)
- ✅ `test_complete_workflow` - 测试完整工作流程
- ✅ `test_error_handling_workflow` - 测试错误处理

### 参数合并演示 (`test-merge-example.py`)
- ✅ 展示核心参数合并逻辑的实际运行
- ✅ 使用真实的SteamLaunchManager类进行测试

## 🔧 测试工具和原理

### 测试是如何工作的

#### 1. CLI集成测试原理
```python
def run_command(self, args, expect_success=True):
    """运行steam-launch-manager命令的辅助方法"""
    # 构建完整的命令行
    cmd = ['python3', str(self.script_path)] + args
    
    # 实际执行命令（就像在终端里运行一样）
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 检查命令是否成功执行
    if expect_success:
        self.assertEqual(result.returncode, 0)
    
    return result
```

#### 2. 测试环境隔离
每个测试都会：
- 创建临时目录 (`tempfile.mkdtemp()`)
- 生成测试配置文件
- 在测试结束后清理所有临时文件

#### 3. 实际命令测试示例
```python
def test_help_command(self):
    """测试--help标志"""
    # 相当于在终端运行: python3 steam-launch-manager --help
    result = self.run_command(['--help'])
    
    # 检查输出是否包含预期内容
    self.assertIn('Steam Launch Options Manager', result.stdout)
```

## 📝 测试详细说明

### 每个测试类的作用

#### TestSteamLaunchManagerCLI
测试 `steam-launch-manager` 主程序的各种功能：

```python
def test_init_command(self):
    """测试init命令创建配置文件"""
    new_config_path = os.path.join(self.temp_dir, 'new-config.yaml')
    
    # 实际运行: steam-launch-manager --config new-config.yaml init
    result = self.run_command(['--config', new_config_path, 'init'])
    
    # 验证配置文件是否被创建
    self.assertTrue(os.path.exists(new_config_path))
    self.assertIn('Configuration file created/updated', result.stdout)
```

#### TestSteamConfigGenCLI  
测试 `steam-config-gen` 配置生成工具：

```python
def test_generate_config(self):
    """测试配置生成"""
    output_path = os.path.join(self.temp_dir, 'generated.yaml')
    
    # 实际运行: steam-config-gen --generate 440 730 --output generated.yaml
    result = self.run_command(['--generate', '440', '730', '--output', output_path])
    
    # 验证生成的配置文件
    with open(output_path) as f:
        config = yaml.safe_load(f)
    self.assertIn('440', config['games'])  # 检查TF2配置
```

#### TestEndToEndWorkflow
测试完整的使用流程：

```python
def test_complete_workflow(self):
    """测试：生成配置 -> 验证 -> 应用（干运行）"""
    # 步骤1：生成配置
    # 步骤2：验证配置  
    # 步骤3：以干运行模式应用
    # 确保整个流程能正常工作
```

## 🐛 调试测试

### 查看详细测试输出
```bash
# 查看单个测试的详细输出
python -m pytest tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_help_command -v -s

# 查看所有测试输出
python -m pytest tests/ -v -s
```

### 保留临时文件进行调试
```python
# 在测试类中临时修改tearDown方法
def tearDown(self):
    # shutil.rmtree(self.temp_dir)  # 注释这行来保留临时文件
    print(f"临时测试文件位置: {self.temp_dir}")
```

### 手动运行命令进行调试
```bash
# 你可以手动运行和测试相同的命令
cd /tmp/some_temp_dir
python3 ../../src/bin/steam-launch-manager --help
python3 ../../src/bin/steam-config-gen --list
```

## ✅ 测试检查清单

运行测试前确保：
- [ ] Python 3.6+ 已安装
- [ ] 已安装依赖: `pip install pyyaml`
- [ ] 有足够的临时目录空间
- [ ] 项目结构完整（src/bin/ 目录存在）

## 📈 测试结果示例

成功运行测试的输出应该类似：
```
==================================================== test session starts =====================================================
collected 14 items                                                                                                           

tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_dry_run_mode PASSED                                     [  7%]
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_help_command PASSED                                     [ 14%]
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_init_command PASSED                                     [ 21%]
...
tests/test_cli_integration.py::TestEndToEndWorkflow::test_error_handling_workflow PASSED                               [100%]

===================================================== 14 passed in 2.58s =====================================================
```

## 🎯 测试的目的

这些测试确保：
1. **命令行工具能正常工作** - 用户在终端运行命令时不会出错
2. **配置文件处理正确** - 能正确读取、验证、生成配置
3. **错误处理完善** - 遇到问题时能给出有用的错误信息
4. **完整工作流程** - 从配置生成到应用的整个过程都能正常工作 