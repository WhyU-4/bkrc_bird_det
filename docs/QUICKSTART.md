# 快速入门指南 / Quick Start Guide

## 中文指南

### 1. 系统要求

- RK3588S 开发板（推荐 8GB RAM）
- ONVIF 兼容的 PTZ 网络摄像头
- Ubuntu 20.04/22.04 或 Armbian
- Python 3.8+

### 2. 快速安装

```bash
# 克隆项目
git clone https://github.com/WhyU-4/bkrc_bird_det.git
cd bkrc_bird_det

# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 3. 配置

#### 配置摄像头

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑配置（替换为你的摄像头信息）
nano .env
```

设置摄像头参数：
```
CAMERA_IP=192.168.1.100
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_password
```

#### 配置系统参数

编辑 `config.yaml`：

```yaml
camera:
  ip: "192.168.1.100"      # 摄像头 IP
  username: "admin"         # 用户名
  password: "admin"         # 密码

yolo:
  model_path: "yolo11n.pt" # YOLO 模型
  conf_threshold: 0.25      # 置信度阈值

video:
  source: 0                 # 0=本地摄像头，或使用 RTSP URL
```

### 4. 测试

#### 测试摄像头连接

```bash
source venv/bin/activate
python3 examples/test_ptz.py
```

期望输出：
```
✓ Successfully connected to camera
✓ Current position: Pan=0.00, Tilt=0.00
Testing PTZ movements...
✓ All tests passed!
```

#### 测试鸟类检测

```bash
python3 examples/test_detection.py
```

### 5. 运行系统

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动鸟类跟踪系统
python3 main.py
```

### 6. 快捷键操作

- `q` - 退出程序
- `h` - 云台返回初始位置
- `s` - 停止云台移动
- `r` - 重置跟踪状态

### 7. 常见问题

**问：检测速度慢怎么办？**

答：编辑 `config.yaml`，降低图像分辨率：
```yaml
yolo:
  img_size: 416  # 从 640 降低到 416
```

**问：云台移动不够准确？**

答：调整敏感度参数：
```yaml
camera:
  ptz:
    sensitivity: 0.002  # 增加敏感度
    dead_zone_x: 30     # 减小死区
```

**问：无法连接摄像头？**

答：
1. 检查 IP 地址和网络连接
2. 确认摄像头支持 ONVIF
3. 验证用户名和密码

---

## English Guide

### 1. Requirements

- RK3588S development board (8GB RAM recommended)
- ONVIF-compatible PTZ network camera
- Ubuntu 20.04/22.04 or Armbian
- Python 3.8+

### 2. Quick Installation

```bash
# Clone the repository
git clone https://github.com/WhyU-4/bkrc_bird_det.git
cd bkrc_bird_det

# Run installation script
chmod +x install.sh
./install.sh
```

### 3. Configuration

#### Configure Camera

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (replace with your camera info)
nano .env
```

Set camera parameters:
```
CAMERA_IP=192.168.1.100
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_password
```

#### Configure System

Edit `config.yaml`:

```yaml
camera:
  ip: "192.168.1.100"      # Camera IP
  username: "admin"         # Username
  password: "admin"         # Password

yolo:
  model_path: "yolo11n.pt" # YOLO model
  conf_threshold: 0.25      # Confidence threshold

video:
  source: 0                 # 0=local camera, or use RTSP URL
```

### 4. Testing

#### Test Camera Connection

```bash
source venv/bin/activate
python3 examples/test_ptz.py
```

Expected output:
```
✓ Successfully connected to camera
✓ Current position: Pan=0.00, Tilt=0.00
Testing PTZ movements...
✓ All tests passed!
```

#### Test Bird Detection

```bash
python3 examples/test_detection.py
```

### 5. Run System

```bash
# Activate virtual environment
source venv/bin/activate

# Start bird tracking system
python3 main.py
```

### 6. Keyboard Controls

- `q` - Quit
- `h` - Return to home position
- `s` - Stop PTZ movement
- `r` - Reset tracking state

### 7. FAQ

**Q: Detection is too slow?**

A: Edit `config.yaml` and reduce image resolution:
```yaml
yolo:
  img_size: 416  # Reduce from 640 to 416
```

**Q: PTZ movement not accurate?**

A: Adjust sensitivity parameters:
```yaml
camera:
  ptz:
    sensitivity: 0.002  # Increase sensitivity
    dead_zone_x: 30     # Reduce dead zone
```

**Q: Cannot connect to camera?**

A:
1. Check IP address and network connection
2. Verify camera supports ONVIF
3. Confirm username and password

---

## 命令行选项 / Command Line Options

```bash
# 使用 RTSP 流 / Use RTSP stream
python3 main.py --source rtsp://admin:admin@192.168.1.100:554/stream1

# 无显示模式 / Headless mode
python3 main.py --no-display

# 保存视频 / Save video
python3 main.py --save-video output.mp4

# 自定义配置 / Custom config
python3 main.py --config custom_config.yaml
```

## 性能建议 / Performance Tips

### RK3588S 优化 / RK3588S Optimization

1. **使用轻量级模型 / Use lightweight model**
   - YOLO11n (nano) - 最快 / Fastest
   - YOLO11s (small) - 平衡 / Balanced

2. **调整图像大小 / Adjust image size**
   - 640x640 - 标准 / Standard
   - 416x416 - 更快 / Faster

3. **降低帧率 / Reduce frame rate**
   ```yaml
   tracking:
     update_interval: 0.2  # 增加间隔 / Increase interval
   ```

4. **增加平滑度 / Increase smoothing**
   ```yaml
   tracking:
     smoothing_factor: 0.5  # 减少抖动 / Reduce jitter
   ```

## 下一步 / Next Steps

1. 查看完整文档：`docs/` 目录
2. 学习 API：`docs/API.md`
3. RK3588S 部署：`docs/RK3588S_DEPLOYMENT.md`
4. 查看示例代码：`examples/` 目录

## 技术支持 / Support

- GitHub Issues: https://github.com/WhyU-4/bkrc_bird_det/issues
- Documentation: `docs/` directory
- Examples: `examples/` directory
