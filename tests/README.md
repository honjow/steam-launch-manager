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

### 1. CLI集成测试 (`test_cli_integration.py`) - 16个测试
标准的unittest集成测试，测试实际的命令行工具：

#### TestSteamLaunchManagerCLI (9个测试)
- ✅ `test_help_command` - 测试--help帮助信息
- ✅ `test_init_command` - 测试初始化配置目录
- ✅ `test_validate_command` - 测试配置验证
- ✅ `test_validate_invalid_config` - 测试无效配置处理
- ✅ `test_dry_run_mode` - 测试干运行模式
- ✅ `test_missing_app_id` - 测试缺少App ID的错误处理
- ✅ `test_missing_config_file` - 测试缺少配置文件的处理
- 🆕 `test_update_db_command` - 测试社区数据库更新命令
- 🆕 `test_directory_structure` - 测试目录分离结构

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
- 🆕 目录分离配置结构测试
- 🆕 配置优先级测试（用户 vs 社区）

### 3. Diff功能综合测试 (`test_diff_functionality.py`)
专门测试diff命令的各种场景：
- ✅ 创建真实的Steam VDF环境
- ✅ 测试各种diff场景（简单添加、复杂冲突、参数替换、空配置）
- ✅ Diff vs Dry-run 输出对比
- ✅ 输出格式验证（表情符号、分段显示）
- ✅ 边缘情况处理（空配置、缺失文件、无效App ID）
- 🆕 新配置类型测试（script、template、raw）
- 🆕 社区配置vs用户配置的diff显示

## 🔧 测试架构说明

### 配置目录结构测试

#### 新架构测试点
```
~/.config/steam-launch-manager/
├── custom/
│   └── games.yaml        # 用户自定义配置测试
└── community/
    ├── games.yaml        # 社区预设配置测试
    └── version.txt       # 版本信息测试
```

#### 测试场景
- **目录创建测试**：验证初始化时正确创建目录结构
- **配置优先级测试**：用户配置 > 社区配置 > 无配置
- **配置合并测试**：不同来源配置的合并逻辑
- **版本更新测试**：社区数据库更新机制

### 测试分类和职责

#### 1. 标准集成测试 (`test_cli_integration.py`)
```python
# 适合CI/CD集成，使用标准unittest框架
class TestSteamLaunchManagerCLI(unittest.TestCase):
    def test_help_command(self):
        result = self.run_command(['--help'])
        self.assertIn('Steam Launch Options Manager', result.stdout)
        
    def test_directory_structure(self):
        # 测试新的目录分离结构
        result = self.run_command(['init'])
        self.assertTrue(Path(config_dir / 'custom' / 'games.yaml').exists())
        self.assertTrue(Path(config_dir / 'community').exists())
```

**特点**:
- 标准unittest格式
- 适合自动化测试
- 覆盖所有CLI基础功能
- 错误断言和验证
- 🆕 支持新的目录结构测试

#### 2. 功能演示测试 (`test_merge_logic.py`)
```python
# 直接使用核心类进行功能演示
manager = SteamLaunchManager(config_path=temp_config)
custom_config, community_config = manager.get_game_config(app_id)
```

**特点**:
- 直接测试核心算法
- 详细的场景演示
- 可视化输出
- 教学和调试价值
- 🆕 支持配置优先级演示

#### 3. 专项功能测试 (`test_diff_functionality.py`)
```python
# 创建真实环境进行专项测试
class DiffFunctionalityTest:
    def create_directory_config(self, config_dir):
        # 创建目录分离的配置结构
        
    def test_config_source_display(self):
        # 测试配置来源显示
```

**特点**:
- 创建真实测试环境
- 专注特定功能
- 综合场景测试
- 输出格式验证
- 🆕 支持多种配置类型测试

## 🆕 新功能测试

### 社区数据库功能测试
```bash
# 测试update-db命令
python -m pytest tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_update_db_command -v

# 测试配置优先级
python tests/test_merge_logic.py
```

### 配置类型测试
```bash
# 测试脚本模式配置
python tests/test_diff_functionality.py

# 测试模板模式配置
python tests/test_merge_logic.py
```

### 目录结构测试
```bash
# 测试目录分离初始化
python -m pytest tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_directory_structure -v
```

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
- [ ] 网络连接正常（用于测试update-db功能）

## 🔍 调试和开发

### 保留临时文件进行调试
在测试类中可以临时注释清理代码：
```python
# shutil.rmtree(self.temp_dir)  # 注释这行保留临时文件
print(f"临时测试文件位置: {self.temp_dir}")
```

### 手动运行测试命令
```bash
# 查看测试创建的临时配置目录
ls -la /tmp/some_temp_dir/steam-launch-manager/

# 手动运行相同的命令
python3 src/bin/steam-launch-manager --config /tmp/some_temp_dir/steam-launch-manager diff 440
```

### 测试网络功能
```bash
# 测试update-db命令（需要网络）
python3 src/bin/steam-launch-manager --config /tmp/test-config update-db

# 测试离线模式
STEAM_LAUNCH_MANAGER_OFFLINE=1 python tests/test_merge_logic.py
```

## 📈 测试结果解读

### 成功的测试输出示例
```
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_help_command PASSED
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_init_command PASSED
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_update_db_command PASSED
tests/test_cli_integration.py::TestSteamLaunchManagerCLI::test_directory_structure PASSED
...
============================== 16 passed in 3.45s ==============================
```

### 演示脚本输出示例
```
🎯 Steam Launch Manager - 参数合并演示
================================================================================
📁 目录分离结构演示...
⚙️  配置优先级测试...
🔄 用户配置 vs 社区配置合并...

--- 场景1: 用户配置优先级 ---
说明: 用户自定义配置覆盖社区预设配置
配置来源: custom (用户自定义)
原始启动选项: DXVK_HUD=1 %command% -novid
合并后启动选项: DXVK_HUD=fps %command% -novid -high
```

## 🚨 注意事项

### 网络依赖测试
- `update-db` 命令测试需要网络连接
- 可通过环境变量 `STEAM_LAUNCH_MANAGER_OFFLINE=1` 跳过网络测试
- 使用本地镜像或模拟服务器进行离线测试

### 权限问题
- 测试会创建临时目录和文件
- 确保有足够的读写权限
- 清理临时文件避免空间不足

### 兼容性测试
- 在不同Python版本下运行测试
- 验证跨平台兼容性（Linux、macOS、Windows）
- 测试不同的Steam安装路径 