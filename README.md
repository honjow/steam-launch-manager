# Steam Launch Manager

智能管理 Steam 游戏启动参数，支持前置/后置参数合并和冲突处理。

## 🚀 安装使用

### 1. 快速开始
```bash
# 生成配置模板
./steam-config-gen --list                    # 查看可用模板
./steam-config-gen --generate 440 730        # 为TF2和CS2生成配置

# 应用配置
./steam-launch-manager init                   # 初始化配置目录和文件
./steam-launch-manager apply-all              # 应用所有配置
./steam-launch-manager dry-run 440            # 预览TF2的配置变更
./steam-launch-manager update-db              # 手动更新社区数据库

# 使用包装器（推荐）
./steam-wrapper                               # 自动应用配置后启动Steam
```

### 2. 安装为系统命令
```bash
sudo cp steam-launch-manager /usr/bin/
sudo cp steam-wrapper /usr/bin/
sudo chmod +x /usr/bin/steam-*

# 替换Steam启动（可选）
sudo mv /usr/bin/steam /usr/bin/steam-original
sudo ln -s /usr/bin/steam-wrapper /usr/bin/steam
```

## 📂 配置文件结构

### 目录分离架构
```
~/.config/steam-launch-manager/
├── custom/
│   └── games.yaml        # 用户自定义配置（优先级最高）
└── community/
    ├── games.yaml        # 社区预设配置（自动更新）
    └── version.txt       # 版本信息
```

### 配置优先级
1. **用户自定义配置** (`custom/games.yaml`) - 最高优先级
2. **社区预设配置** (`community/games.yaml`) - 自动从网络更新
3. **无配置** - 不做任何修改

### 用户自定义配置格式 (`~/.config/steam-launch-manager/custom/games.yaml`)
```yaml
global:
  backup_enabled: true
  backup_path: "~/.config/steam-backups"
  auto_update_community_db: true
  
  # 网络配置（可选）
  network:
    quick_timeout_seconds: 2
    retry_attempts: 3
    background_update: true

games:
  "440":  # Steam App ID
    name: "Team Fortress 2 - Custom"
    
    prefix:  # %command% 前的内容（环境变量等）
      params:
        - "DXVK_HUD=fps"
        - "LD_LIBRARY_PATH=/opt/lib"
      
      user_handling:
        preserve: true      # 保留用户的前置参数
        position: "before"  # before|after|replace
      
      conflicts:
        replace_keys: ["DXVK_HUD"]              # 强制替换这些环境变量
        merge_keys: 
          "LD_LIBRARY_PATH": "prepend"          # prepend|append 合并路径
    
    suffix:  # %command% 后的内容（启动参数）
      params:
        - "-novid"
        - "-high"
      
      user_handling:
        preserve: true
        position: "before"  # 用户参数 + 我们的参数
      
      conflicts:
        replace_rules:
          "-safe": ""               # 移除安全模式
          "-windowed": "-fullscreen" # 替换为全屏
```

### 高级配置类型

#### 1. 简单模式（默认）
```yaml
"730":
  name: "Counter-Strike 2"
  type: "simple"  # 可省略
  prefix:
    params: ["RADV_PERFTEST=aco"]
  suffix:
    params: ["-high", "-threads 4"]
```

#### 2. 脚本模式（复杂启动逻辑）
```yaml
"205950":
  name: "Jet Set Radio"
  type: "script"
  script_template: 'eval $(echo "%command%" | sed "s/jsrsetup.exe/jetsetradio.exe/")'
  description: "修复可执行文件路径问题"
```

#### 3. 模板模式（变量替换）
```yaml
"example_template":
  name: "Template Example"
  type: "template"
  template: "GAME_DIR=${game_dir} RESOLUTION=${width}x${height} %command% -windowed"
  variables:
    game_dir: "/opt/games"
    width: 1920
    height: 1080
```

#### 4. 原始模式（完全替换）
```yaml
"example_raw":
  name: "Raw Example"
  type: "raw"
  raw_options: "CUSTOM_ENV=1 /usr/bin/custom-launcher %command% --special-mode"
```

## 🔧 命令参考

### steam-launch-manager
```bash
# 配置管理
steam-launch-manager init                     # 初始化配置目录
steam-launch-manager validate                 # 验证配置文件

# 应用配置
steam-launch-manager apply 440                # 应用单个游戏配置
steam-launch-manager apply-all                # 应用所有配置

# 预览变更
steam-launch-manager dry-run 440              # 预览变更（不实际应用）
steam-launch-manager diff 440                 # 显示详细差异对比

# 数据库管理
steam-launch-manager update-db                # 手动更新社区数据库
```

### steam-config-gen
```bash
steam-config-gen --list                       # 列出预设模板
steam-config-gen --generate 440 730 570       # 生成多个游戏配置
steam-config-gen --output ~/my-config.yaml    # 指定输出文件
```

### steam-wrapper
```bash
steam-wrapper                                 # 应用配置后启动Steam
steam-wrapper -bigpicture                     # 启动大屏模式
```

## 🌐 社区数据库

### 自动更新
- 程序启动时自动检查更新（1小时间隔）
- 从多个镜像源下载最新配置：
  - GitHub（主源）
  - Gitee（国内镜像）
  - jsDelivr CDN（备用）

### 手动更新
```bash
steam-launch-manager update-db
```

### 包含的游戏配置
社区数据库包含30+个游戏的优化配置，涵盖：
- **SteamDeck兼容性修复**：博德之门3、地平线系列等
- **音频问题修复**：Alan Wake、Heavy Rain等
- **性能优化**：Psychonauts 2、Nex Machina等
- **启动器跳过**：多个游戏的启动器绕过
- **复杂脚本修复**：Jet Set Radio等路径问题

## 📊 实际效果示例

### 简单配置示例
#### 配置前
```
用户设置: -console +fps_max 60 -windowed
```

#### 应用配置后  
```yaml
# 社区配置（Counter-Strike 2）
prefix:
  params: ["RADV_PERFTEST=aco"]
suffix:
  params: ["-high", "-threads 4"]
  conflicts:
    replace_rules: {"-windowed": "-fullscreen"}
```

#### 最终结果
```
RADV_PERFTEST=aco %command% -console +fps_max 60 -fullscreen -high -threads 4
```

### 复杂脚本示例
#### Jet Set Radio 路径修复
```yaml
# 社区预设配置
"205950":
  name: "Jet Set Radio"
  type: "script"
  script_template: 'eval $(echo "%command%" | sed "s/jsrsetup.exe/jetsetradio.exe/")'
```

## 🛡️ 安全特性

- **自动备份**: 修改前自动备份原始配置
- **干运行模式**: 预览变更而不实际应用
- **Steam状态检测**: 确保Steam未运行时才修改配置
- **配置验证**: 检查配置文件格式和内容
- **回滚支持**: 可恢复到备份的配置
- **网络超时控制**: 防止网络请求阻塞程序启动
- **多镜像容错**: 支持多个下载源确保可用性

## 🎯 使用场景

### 1. 性能优化
```yaml
# GPU优化（AMD显卡）
prefix:
  params: 
    - "RADV_PERFTEST=aco"
    - "__GL_THREADED_OPTIMIZATIONS=1"
    - "DXVK_HUD=fps,memory"

# CPU优化  
suffix:
  params: ["-high", "-threads 8"]
```

### 2. SteamDeck兼容性
```yaml
# 禁用SteamDeck模式
prefix:
  params: ["SteamDeck=0"]

# 跳过启动器
suffix:
  params: ["--skip-launcher"]
```

### 3. Proton游戏优化
```yaml
prefix:
  params:
    - "PROTON_USE_WINED3D=0"
    - "PROTON_NO_ESYNC=0" 
    - 'WINEDLLOVERRIDES="dinput8=native,builtin"'

suffix:
  params: ["-windowed", "-noborder"]
```

### 4. 音频修复
```yaml
# 音频库覆盖
prefix:
  params:
    - 'WINEDLLOVERRIDES="xaudio2_7=native,builtin"'

# 音频延迟调整
prefix:
  params:
    - "PULSE_LATENCY_MSEC=60"
```

### 5. 复杂启动脚本
```yaml
# 注册表修复（音频驱动）
type: "script"
script_template: |
  IFS=:; for PROTON_PATH in ${STEAM_COMPAT_TOOL_PATHS}; do 
    if [ -f "$PROTON_PATH/dist/bin/wine" ]; then 
      WINEPREFIX=$STEAM_COMPAT_DATA_PATH/pfx $PROTON_PATH/dist/bin/wine \
      "C:\\windows\\system32\\reg.exe" ADD \
      "HKLM\\System\\CurrentControlSet\\Control\\Session Manager\\Environment" \
      /v "SDL_AUDIODRIVER" /d "directsound" /f; 
      break; 
    fi; 
  done; %command%
```

## 📝 注意事项

1. **Steam必须关闭**: 配置只在Steam未运行时生效
2. **App ID格式**: Steam App ID必须用引号包围 (`"440"`)
3. **配置优先级**: 用户配置会覆盖社区配置
4. **网络依赖**: 自动更新需要网络连接，可通过配置禁用
5. **备份重要**: 首次使用前建议手动备份Steam配置
6. **测试先行**: 使用`dry-run`或`diff`模式预览变更

## 🔍 故障排除

### 基本检查
```bash
# 检查Steam是否运行
pgrep steam

# 验证配置文件
steam-launch-manager validate

# 查看备份
ls ~/.config/steam-backups/

# 检查配置目录结构
ls -la ~/.config/steam-launch-manager/
```

### 网络问题
```bash
# 手动更新数据库
steam-launch-manager update-db

# 禁用自动更新（编辑配置文件）
# auto_update_community_db: false
```

### 配置问题
```bash
# 重置配置
rm -rf ~/.config/steam-launch-manager/
steam-launch-manager init

# 查看详细日志
STEAM_LAUNCH_MANAGER_DEBUG=1 steam-launch-manager apply 440
```

### 常见问题

**Q: 为什么配置没有生效？**
A: 确保Steam已关闭，并检查App ID格式（必须用引号）

**Q: 社区数据库更新失败怎么办？**
A: 可以禁用自动更新，或检查网络连接

**Q: 如何查看我的游戏使用了哪个配置？**
A: 使用`diff`命令查看配置来源和详细内容

**Q: 可以同时使用社区配置和自己的配置吗？**
A: 用户自定义配置优先级更高，会覆盖社区配置

**Q: 如何贡献游戏配置到社区数据库？**
A: 在项目GitHub页面提交Issue或Pull Request 