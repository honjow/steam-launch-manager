# Steam Launch Manager

智能管理 Steam 游戏启动参数，支持前置/后置参数合并和冲突处理。

## 🚀 安装使用

### 1. 快速开始
```bash
# 生成配置模板
./steam-config-gen --list                    # 查看可用模板
./steam-config-gen --generate 440 730        # 为TF2和CS2生成配置

# 应用配置
./steam-launch-manager init                   # 初始化配置文件
./steam-launch-manager apply-all              # 应用所有配置
./steam-launch-manager dry-run 440            # 预览TF2的配置变更

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

## 📋 配置文件结构

### 基本格式 (`~/.config/steam-launch-manager.yaml`)
```yaml
global:
  backup_enabled: true
  backup_path: "~/.config/steam-backups"

games:
  "440":  # Steam App ID
    name: "Team Fortress 2"
    
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

## 🔧 命令参考

### steam-launch-manager
```bash
steam-launch-manager apply 440                # 应用单个游戏配置
steam-launch-manager apply-all                # 应用所有配置
steam-launch-manager dry-run 440              # 预览变更
steam-launch-manager diff 440                 # 显示差异
steam-launch-manager validate                 # 验证配置文件
steam-launch-manager init                     # 初始化配置
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

## 📊 实际效果示例

### 配置前
```
用户设置: -console +fps_max 60 -windowed
```

### 配置后  
```yaml
prefix:
  params: ["DXVK_HUD=fps", "LD_LIBRARY_PATH=/opt/lib"]
suffix:
  params: ["-novid", "-high"]
  conflicts:
    replace_rules: {"-windowed": "-fullscreen"}
```

### 最终结果
```
DXVK_HUD=fps LD_LIBRARY_PATH=/opt/lib %command% -console +fps_max 60 -fullscreen -novid -high
```

## 🛡️ 安全特性

- **自动备份**: 修改前自动备份原始配置
- **干运行模式**: 预览变更而不实际应用
- **Steam状态检测**: 确保Steam未运行时才修改配置
- **配置验证**: 检查配置文件格式和内容
- **回滚支持**: 可恢复到备份的配置

## 🎯 使用场景

### 1. 性能优化
```yaml
# GPU优化
prefix:
  params: 
    - "RADV_PERFTEST=aco"
    - "__GL_THREADED_OPTIMIZATIONS=1"
    - "DXVK_HUD=fps,memory"

# CPU优化  
suffix:
  params: ["-high", "-threads 8"]
```

### 2. Proton游戏
```yaml
prefix:
  params:
    - "PROTON_USE_WINED3D=0"
    - "PROTON_NO_ESYNC=0" 
    - "WINEDLLOVERRIDES=dinput8=n,b"

suffix:
  params: ["-windowed", "-noborder"]
```

### 3. 兼容性修复
```yaml
conflicts:
  replace_rules:
    "-safe": ""                    # 移除安全模式
    "-dxlevel 80": "-dxlevel 95"   # 升级DX版本
```

## 📝 注意事项

1. **Steam必须关闭**: 配置只在Steam未运行时生效
2. **App ID格式**: Steam App ID必须用引号包围 (`"440"`)
3. **备份重要**: 首次使用前建议手动备份Steam配置
4. **测试先行**: 使用`dry-run`模式预览变更

## 🔍 故障排除

```bash
# 检查Steam是否运行
pgrep steam

# 验证配置文件
steam-launch-manager validate

# 查看备份
ls ~/.config/steam-backups/

# 重置配置
rm ~/.config/steam-launch-manager.yaml
steam-launch-manager init
``` 