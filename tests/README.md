# Steam Launch Manager - 测试套件

## 📋 测试概览

重构后的测试套件包含以下模块：
- `test_cli_integration.py` - CLI工具集成测试（标准unittest）
- `test_merge_logic.py` - 参数合并功能演示和测试
- `test_diff_functionality.py` - Diff功能综合测试

## 🚀 运行测试

### 环境要求
```bash
pip install pyyaml vdf
```

### 运行所有测试
```bash
# 使用pytest（推荐）
python -m pytest tests/ -v

# 或使用unittest
python -m unittest discover tests/ -v

# 运行单个演示脚本
python tests/test_merge_logic.py
python tests/test_diff_functionality.py
```

### 运行特定测试模块
```bash
# CLI集成测试（标准unittest）
python -m pytest tests/test_cli_integration.py -v

# 参数合并逻辑演示
python tests/test_merge_logic.py

# Diff功能综合测试
python tests/test_diff_functionality.py
```

## 📊 测试覆盖范围

### 1. CLI集成测试 (`test_cli_integration.py`) - 14个测试
标准的unittest集成测试，测试实际的命令行工具：

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

### 2. 参数合并逻辑测试 (`test_merge_logic.py`)
直接使用SteamLaunchManager核心类的演示和测试：
- ✅ 环境变量冲突处理（替换/合并）
- ✅ 启动参数冲突处理（替换/删除）
- ✅ 用户参数保留策略（保留/替换）
- ✅ 参数位置控制（前置/后置）
- ✅ 复杂混合场景处理
- ✅ 真实配置文件流程演示

### 3. Diff功能综合测试 (`test_diff_functionality.py`)
专门测试diff命令的各种场景：
- ✅ 创建真实的Steam VDF环境
- ✅ 测试各种diff场景（简单添加、复杂冲突、参数替换、空配置）
- ✅ Diff vs Dry-run 输出对比
- ✅ 输出格式验证（表情符号、分段显示）
- ✅ 边缘情况处理（空配置、缺失文件、无效App ID）

## 🔧 测试架构说明

### 测试分类和职责

#### 1. 标准集成测试 (`test_cli_integration.py`)
```python
# 适合CI/CD集成，使用标准unittest框架
class TestSteamLaunchManagerCLI(unittest.TestCase):
    def test_help_command(self):
        result = self.run_command(['--help'])
        self.assertIn('Steam Launch Options Manager', result.stdout)
```

**特点**:
- 标准unittest格式
- 适合自动化测试
- 覆盖所有CLI基础功能
- 错误断言和验证

#### 2. 功能演示测试 (`test_merge_logic.py`)
```python
# 直接使用核心类进行功能演示
manager = SteamLaunchManager(config_path=temp_config)
final_prefix = manager.merge_prefix_params(user_prefix, config_prefix, ...)
```

**特点**:
- 直接测试核心算法
- 详细的场景演示
- 可视化输出
- 教学和调试价值

#### 3. 专项功能测试 (`test_diff_functionality.py`)
```python
# 创建真实环境进行专项测试
class DiffFunctionalityTest:
    def create_steam_environment(self, steam_dir):
        # 创建真实VDF文件
    
    def test_diff_scenarios(self):
        # 测试各种diff场景
```

**特点**:
- 创建真实测试环境
- 专注特定功能
- 综合场景测试
- 输出格式验证

## 🎯 测试运行示例

### 快速验证
```bash
# 运行标准测试套件
python -m pytest tests/test_cli_integration.py -v

# 查看参数合并演示
python tests/test_merge_logic.py

# 测试diff功能
python tests/test_diff_functionality.py
```

### 详细测试输出
```bash
# 查看详细的测试过程
python -m pytest tests/ -v -s

# 运行特定测试并查看输出
python -m pytest tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_help_command -v -s
```

## 📋 测试检查清单

运行测试前确保：
- [ ] Python 3.6+ 已安装
- [ ] 已安装依赖: `pip install pyyaml vdf`
- [ ] 有足够的临时目录空间
- [ ] 项目结构完整（src/bin/ 目录存在）

## 🔍 调试和开发

### 保留临时文件进行调试
在测试类中可以临时注释清理代码：
```python
# shutil.rmtree(self.temp_dir)  # 注释这行保留临时文件
print(f"临时测试文件位置: {self.temp_dir}")
```

### 手动运行测试命令
```bash
# 查看测试创建的临时配置
cat /tmp/some_temp_dir/test-config.yaml

# 手动运行相同的命令
python3 src/bin/steam-launch-manager --config /tmp/some_temp_dir/test-config.yaml diff 440
```

## 📈 测试结果解读

### 成功的测试输出示例
```
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_help_command PASSED
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_init_command PASSED
...
============================== 14 passed in 2.34s ==============================
```

### 演示脚本输出示例
```
🎯 Steam Launch Manager - Diff功能综合测试
================================================================================
📁 创建模拟Steam环境...
⚙️  创建测试配置...

🎮 TF2 - 简单参数添加
--------------------------------------------------
✅ 命令执行成功
输出:
Configuration diff for app 440 (Team Fortress 2):
============================================================
📋 Current configuration: -console
🎯 Proposed configuration: DXVK_HUD=fps RADV_PERFTEST=aco %command% -console -novid -high
...
```

## 🎉 测试重构总结

### 重构前的问题
- 5个测试文件，1188行代码
- 功能重复（simple_cli_test.py vs test_cli_integration.py）
- 演示分散（demo_diff.py, test_with_fake_data.py）
- 命名不规范（test-merge-example.py）

### 重构后的优势
- 3个测试文件，职责清晰
- 消除重复，保留精华
- 标准化命名和结构
- 更好的测试覆盖和组织

### 文件对应关系
- `test_cli_integration.py` ← 保留原有的标准测试
- `test_merge_logic.py` ← 重命名自 test-merge-example.py
- `test_diff_functionality.py` ← 合并 demo_diff.py + test_with_fake_data.py
- ~~simple_cli_test.py~~ ← 删除（重复功能） 