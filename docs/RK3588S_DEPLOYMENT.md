# RK3588S Deployment Guide

本指南介绍如何在 RK3588S 开发板上部署鸟类跟踪系统。

This guide explains how to deploy the bird tracking system on RK3588S development boards.

## 硬件准备 / Hardware Requirements

### 开发板 / Development Board

- RK3588S 开发板（推荐 8GB+ RAM）
- microSD 卡（32GB+ 推荐）
- 电源适配器（12V/2A 或更高）

### 摄像头 / Camera

- ONVIF 兼容的 PTZ 网络摄像头
- 支持 RTSP 流
- 建议分辨率：1080p 或更高

### 网络 / Network

- 以太网连接（推荐）或 WiFi
- 开发板和摄像头在同一网络

## 系统配置 / System Setup

### 1. 操作系统安装 / OS Installation

推荐使用：
- Ubuntu 20.04/22.04 for RK3588S
- Armbian for RK3588S
- 官方 Rockchip Linux SDK

### 2. 系统更新 / System Update

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. 安装依赖 / Install Dependencies

```bash
# 系统依赖
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y git wget curl

# OpenCV 额外依赖
sudo apt install -y libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libv4l-dev libxvidcore-dev libx264-dev
```

## 项目部署 / Project Deployment

### 1. 克隆项目 / Clone Project

```bash
cd ~
git clone https://github.com/WhyU-4/bkrc_bird_det.git
cd bkrc_bird_det
```

### 2. 运行安装脚本 / Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

或手动安装 / Or install manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置摄像头 / Configure Camera

编辑 `.env` 文件：

```bash
cp .env.example .env
nano .env
```

设置摄像头参数：
```
CAMERA_IP=192.168.1.100
CAMERA_PORT=80
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_password
RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream1
```

### 4. 配置系统参数 / Configure System

编辑 `config.yaml`：

```bash
nano config.yaml
```

针对 RK3588S 优化的配置：

```yaml
yolo:
  model_path: "yolo11n.pt"  # 使用 nano 模型
  conf_threshold: 0.25
  device: "cpu"              # RK3588S 使用 CPU
  img_size: 640              # 较小的输入尺寸

tracking:
  update_interval: 0.15      # 降低更新频率
  smoothing_factor: 0.5      # 增加平滑

video:
  source: 0                  # 或使用 RTSP URL
  display: true
```

## 性能优化 / Performance Optimization

### CPU 频率设置 / CPU Frequency

```bash
# 查看当前频率
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq

# 设置性能模式
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 内存优化 / Memory Optimization

编辑 `/etc/sysctl.conf`：

```bash
# 增加 swap 优先级
vm.swappiness=10

# 优化内存分配
vm.overcommit_memory=1
```

应用配置：
```bash
sudo sysctl -p
```

### YOLO 模型选择 / YOLO Model Selection

根据性能需求选择模型：

| 模型 | 速度 | 精度 | 推荐场景 |
|------|------|------|----------|
| yolo11n.pt | 最快 | 基本 | RK3588S 推荐 |
| yolo11s.pt | 快 | 良好 | 性能充足时 |
| yolo11m.pt | 中 | 很好 | 不推荐 |

## 测试运行 / Test Run

### 1. 测试摄像头连接 / Test Camera

```bash
python3 examples/test_ptz.py
```

### 2. 测试鸟类检测 / Test Detection

```bash
python3 examples/test_detection.py
```

### 3. 完整系统测试 / Full System Test

```bash
python3 main.py
```

## 开机自启动 / Auto Start on Boot

### 创建 Systemd 服务 / Create Systemd Service

创建服务文件：

```bash
sudo nano /etc/systemd/system/bird-tracker.service
```

添加以下内容：

```ini
[Unit]
Description=Bird Tracking System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/bkrc_bird_det
Environment="PATH=/home/your_username/bkrc_bird_det/venv/bin"
ExecStart=/home/your_username/bkrc_bird_det/venv/bin/python3 main.py --no-display
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable bird-tracker
sudo systemctl start bird-tracker
```

查看状态：

```bash
sudo systemctl status bird-tracker
```

查看日志：

```bash
sudo journalctl -u bird-tracker -f
```

## 远程访问 / Remote Access

### SSH 访问 / SSH Access

```bash
ssh user@rk3588s-ip-address
```

### VNC 访问（可选）/ VNC Access (Optional)

安装 VNC 服务器：

```bash
sudo apt install -y tightvncserver
vncserver :1
```

连接：使用 VNC 客户端连接到 `rk3588s-ip:5901`

## 故障排除 / Troubleshooting

### 性能问题 / Performance Issues

1. **降低分辨率**
   ```yaml
   yolo:
     img_size: 416  # 从 640 降低到 416
   ```

2. **降低处理帧率**
   ```python
   # 在主循环中添加延迟
   time.sleep(0.1)
   ```

3. **使用更轻量的模型**
   ```yaml
   yolo:
     model_path: "yolo11n.pt"
   ```

### 内存不足 / Out of Memory

```bash
# 增加 swap 空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 摄像头连接问题 / Camera Connection Issues

```bash
# 测试网络连接
ping camera-ip

# 测试 RTSP 流
ffplay rtsp://admin:password@camera-ip:554/stream1

# 检查 ONVIF 服务
python3 -c "from onvif import ONVIFCamera; cam = ONVIFCamera('camera-ip', 80, 'admin', 'password'); print('OK')"
```

## 性能基准 / Performance Benchmarks

在 RK3588S（8GB RAM）上的预期性能：

| 配置 | FPS | CPU 使用率 | 内存使用 |
|------|-----|-----------|----------|
| YOLO11n + 640px | 15-20 | 60-70% | 1.5GB |
| YOLO11n + 416px | 25-30 | 50-60% | 1.2GB |
| YOLO11s + 640px | 10-15 | 70-80% | 2.0GB |

## 维护建议 / Maintenance Recommendations

1. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **清理日志**
   ```bash
   sudo journalctl --vacuum-time=7d
   ```

3. **监控温度**
   ```bash
   cat /sys/class/thermal/thermal_zone*/temp
   ```

4. **备份配置**
   ```bash
   cp config.yaml config.yaml.backup
   cp .env .env.backup
   ```

## 技术支持 / Technical Support

如遇问题，请查看：
- GitHub Issues: https://github.com/WhyU-4/bkrc_bird_det/issues
- 文档：docs/ 目录
- 示例代码：examples/ 目录
