# Bird Detection and Tracking System

基于 RK3588S 的鸟类检测与跟踪系统，集成 Ultralytics YOLO11 目标检测和 ONVIF PTZ 云台控制。

A bird detection and tracking system for RK3588S hardware, integrating Ultralytics YOLO11 object detection with ONVIF PTZ camera control.

## 功能特性 / Features

- 🎯 **YOLO11 鸟类检测** - 使用最新的 Ultralytics YOLO11 模型进行实时鸟类检测
- 📹 **ONVIF PTZ 控制** - 支持 ONVIF 协议的云台摄像头控制
- 🎮 **自动跟踪** - 自动调整云台保持鸟类在画面中心
- 🖥️ **RK3588S 优化** - 针对 RK3588S 硬件平台优化
- 📊 **实时可视化** - 实时显示检测结果和跟踪状态
- 🔧 **灵活配置** - 通过 YAML 配置文件自定义参数

## 系统架构 / Architecture

```
┌─────────────────┐
│  Video Source   │ (Camera/RTSP)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  YOLO11 Detector│ (Bird Detection)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Bird Tracker   │ (Tracking Logic)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PTZ Controller  │ (ONVIF Control)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Camera PTZ     │ (Physical Movement)
└─────────────────┘
```

## 环境要求 / Requirements

### 硬件 / Hardware
- RK3588S 开发板或兼容设备
- ONVIF 兼容的 PTZ 摄像头
- 网络连接（用于摄像头控制和 RTSP 流）

### 软件 / Software
- Python 3.8+
- OpenCV
- Ultralytics YOLO11
- ONVIF libraries

## 安装 / Installation

### 1. 克隆仓库 / Clone Repository

```bash
git clone https://github.com/WhyU-4/bkrc_bird_det.git
cd bkrc_bird_det
```

### 2. 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. 配置环境 / Configure Environment

复制示例环境文件并配置摄像头参数：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置摄像头 IP、用户名和密码。

### 4. 配置系统 / Configure System

编辑 `config.yaml` 文件，根据您的需求调整参数：

```yaml
# 摄像头配置
camera:
  ip: "192.168.1.100"     # 摄像头 IP 地址
  port: 80                 # ONVIF 端口
  username: "admin"        # 用户名
  password: "admin"        # 密码

# YOLO 配置
yolo:
  model_path: "yolo11n.pt" # 模型路径
  conf_threshold: 0.25     # 置信度阈值
  classes: [14]            # 鸟类类别 ID

# PTZ 配置
ptz:
  pan_speed: 0.5          # 水平速度
  tilt_speed: 0.5         # 垂直速度
  dead_zone_x: 50         # 中心死区 X
  dead_zone_y: 50         # 中心死区 Y
```

## 使用方法 / Usage

### 基本运行 / Basic Usage

```bash
python main.py
```

### 使用 RTSP 流 / With RTSP Stream

```bash
python main.py --source rtsp://admin:admin@192.168.1.100:554/stream1
```

### 无显示模式（用于服务器） / Headless Mode

```bash
python main.py --no-display
```

### 保存输出视频 / Save Output Video

```bash
python main.py --save-video output.mp4
```

### 自定义配置文件 / Custom Config

```bash
python main.py --config custom_config.yaml
```

## 快捷键 / Keyboard Controls

在显示窗口中可用的快捷键：

- `q` - 退出程序 / Quit
- `h` - 云台回到初始位置 / Return to home position
- `s` - 停止云台移动 / Stop PTZ movement
- `r` - 重置跟踪状态 / Reset tracking state

## 项目结构 / Project Structure

```
bkrc_bird_det/
├── main.py                 # 主程序入口
├── config.yaml            # 配置文件
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── README.md             # 项目文档
└── src/
    ├── __init__.py       # 包初始化
    ├── bird_detector.py  # YOLO11 检测器
    ├── ptz_controller.py # ONVIF PTZ 控制
    └── bird_tracker.py   # 鸟类跟踪逻辑
```

## 工作原理 / How It Works

1. **视频采集** - 从摄像头或 RTSP 流获取视频帧
2. **鸟类检测** - YOLO11 模型检测画面中的鸟类
3. **目标选择** - 选择最大（最近）的鸟类作为跟踪目标
4. **位置计算** - 计算鸟类相对于画面中心的偏移
5. **PTZ 控制** - 根据偏移量控制云台移动
6. **中心保持** - 持续调整使鸟类保持在画面中心

## 性能优化 / Performance Optimization

### RK3588S 优化建议 / RK3588S Optimization Tips

1. **使用轻量级模型** - YOLO11n (nano) 在 RK3588S 上性能最佳
2. **调整图像大小** - 较小的输入尺寸（如 640x640）可提高速度
3. **降低帧率** - 如果实时性要求不高，可降低处理帧率
4. **禁用显示** - 在无显示模式下运行以节省资源

### 配置示例 / Configuration Example

```yaml
yolo:
  model_path: "yolo11n.pt"  # 使用 nano 模型
  img_size: 640              # 较小的输入尺寸
  device: "cpu"              # RK3588S 使用 CPU

tracking:
  update_interval: 0.2       # 降低更新频率
  smoothing_factor: 0.5      # 增加平滑以减少抖动
```

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **无法连接摄像头**
   - 检查 IP 地址和端口是否正确
   - 确认摄像头支持 ONVIF 协议
   - 检查网络连接

2. **检测性能低**
   - 使用更轻量的模型（yolo11n.pt）
   - 降低输入图像尺寸
   - 减少置信度阈值

3. **PTZ 移动不准确**
   - 调整 `sensitivity` 参数
   - 增加 `dead_zone` 减少抖动
   - 调整 `smoothing_factor`

## 依赖项 / Dependencies

主要依赖：

- `ultralytics` - YOLO11 模型
- `opencv-python` - 图像处理
- `onvif-zeep` - ONVIF 协议支持
- `numpy` - 数值计算
- `pyyaml` - 配置文件解析

完整依赖列表见 `requirements.txt`

## 许可证 / License

MIT License

## 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

## 致谢 / Acknowledgments

- Ultralytics YOLO11
- ONVIF community
- OpenCV community

## 联系方式 / Contact

如有问题或建议，请提交 Issue。