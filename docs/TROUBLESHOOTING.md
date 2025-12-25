# 故障排除指南 / Troubleshooting Guide

## 常见问题 / Common Issues

### 1. 安装问题 / Installation Issues

#### 问题：pip install 失败
**Problem: pip install fails**

```bash
# 解决方案 / Solution:
# 升级 pip
pip install --upgrade pip

# 使用国内镜像（中国用户）/ Use China mirror (for Chinese users)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 问题：OpenCV 安装失败
**Problem: OpenCV installation fails**

```bash
# Ubuntu/Debian
sudo apt-get install -y python3-opencv libopencv-dev

# 或使用预编译版本 / Or use pre-built version
pip install opencv-python-headless
```

#### 问题：ONVIF 依赖安装失败
**Problem: ONVIF dependencies fail to install**

```bash
# 安装系统依赖 / Install system dependencies
sudo apt-get install -y libxml2-dev libxslt1-dev

# 然后重试 / Then retry
pip install onvif-zeep zeep
```

---

### 2. 摄像头连接问题 / Camera Connection Issues

#### 问题：无法连接到摄像头
**Problem: Cannot connect to camera**

**检查清单 / Checklist:**

1. **网络连接 / Network Connection**
   ```bash
   # 测试网络连接
   ping 192.168.1.100
   ```

2. **ONVIF 端口 / ONVIF Port**
   ```bash
   # 测试端口是否开放
   telnet 192.168.1.100 80
   # 或 / Or
   nc -zv 192.168.1.100 80
   ```

3. **用户名密码 / Credentials**
   - 验证 .env 文件中的用户名和密码
   - 尝试在浏览器中登录摄像头网页界面

4. **ONVIF 支持 / ONVIF Support**
   - 确认摄像头支持 ONVIF 协议
   - 在摄像头设置中启用 ONVIF

**解决方案 / Solutions:**

```bash
# 运行测试脚本
python3 examples/test_ptz.py

# 如果失败，检查配置
nano config.yaml
```

#### 问题：RTSP 流无法访问
**Problem: Cannot access RTSP stream**

```bash
# 测试 RTSP 流（需要 ffmpeg）
ffplay rtsp://admin:password@192.168.1.100:554/stream1

# 或使用 VLC
vlc rtsp://admin:password@192.168.1.100:554/stream1
```

**常见 RTSP URL 格式：**
- Hikvision: `rtsp://user:pass@ip:554/Streaming/Channels/101`
- Dahua: `rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=0`
- Generic: `rtsp://user:pass@ip:554/stream1`

---

### 3. 检测性能问题 / Detection Performance Issues

#### 问题：FPS 太低
**Problem: FPS too low**

**解决方案 1：使用更轻量的模型**

```yaml
# config.yaml
yolo:
  model_path: "yolo11n.pt"  # 使用 nano 模型
```

**解决方案 2：降低输入分辨率**

```yaml
# config.yaml
yolo:
  img_size: 416  # 从 640 降低到 416
```

**解决方案 3：降低处理帧率**

```yaml
# config.yaml
tracking:
  update_interval: 0.2  # 增加到 200ms
```

**解决方案 4：禁用显示**

```bash
python3 main.py --no-display
```

#### 问题：检测不到鸟类
**Problem: Birds not detected**

**解决方案 1：降低置信度阈值**

```yaml
# config.yaml
yolo:
  conf_threshold: 0.15  # 从 0.25 降低到 0.15
```

**解决方案 2：检查类别设置**

```yaml
# config.yaml
yolo:
  classes: [14]  # COCO dataset: 14 = bird
```

**解决方案 3：改善光照条件**
- 确保充足的光照
- 避免背光
- 调整摄像头曝光设置

---

### 4. PTZ 控制问题 / PTZ Control Issues

#### 问题：云台不移动
**Problem: PTZ doesn't move**

**检查清单：**

1. **PTZ 是否启用**
   ```yaml
   # config.yaml
   camera:
     ptz:
       enabled: true
   ```

2. **运行测试**
   ```bash
   python3 examples/test_ptz.py
   ```

3. **检查权限**
   - 确认用户有 PTZ 控制权限
   - 某些摄像头需要管理员账户

#### 问题：云台移动不准确
**Problem: PTZ movement inaccurate**

**调整敏感度：**

```yaml
# config.yaml
camera:
  ptz:
    sensitivity: 0.002    # 增加敏感度
    pan_speed: 0.5        # 调整速度
    tilt_speed: 0.5
    dead_zone_x: 30       # 调整死区
    dead_zone_y: 30
```

**增加平滑度：**

```yaml
# config.yaml
tracking:
  smoothing_factor: 0.5   # 0.0-1.0，越大越平滑
```

#### 问题：云台抖动
**Problem: PTZ jittering**

**解决方案：**

```yaml
# config.yaml
camera:
  ptz:
    dead_zone_x: 100      # 增大死区
    dead_zone_y: 100

tracking:
  smoothing_factor: 0.7   # 增加平滑
  update_interval: 0.2    # 降低更新频率
```

---

### 5. 内存问题 / Memory Issues

#### 问题：内存不足
**Problem: Out of memory**

**解决方案 1：增加 Swap**

```bash
# 创建 4GB swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**解决方案 2：使用更小的模型**

```yaml
# config.yaml
yolo:
  model_path: "yolo11n.pt"  # Nano 模型使用最少内存
  img_size: 416              # 减小输入尺寸
```

**解决方案 3：关闭不必要的服务**

```bash
# 检查内存使用
free -h

# 关闭不必要的服务
sudo systemctl stop bluetooth
sudo systemctl stop cups
```

---

### 6. 视频显示问题 / Video Display Issues

#### 问题：无法显示窗口
**Problem: Cannot display window**

**无头模式 / Headless Mode:**

```bash
# 使用无显示模式运行
python3 main.py --no-display

# 或在配置中禁用
# config.yaml
video:
  display: false
```

**通过 VNC 远程显示：**

```bash
# 安装 VNC 服务器
sudo apt-get install -y tightvncserver

# 启动 VNC
vncserver :1

# 然后通过 VNC 客户端连接
```

#### 问题：显示延迟高
**Problem: High display latency**

```yaml
# config.yaml
video:
  display_width: 640   # 降低显示分辨率
  display_height: 480
```

---

### 7. 模型问题 / Model Issues

#### 问题：模型下载失败
**Problem: Model download fails**

**手动下载：**

```bash
# 方法 1：使用 Python
python3 -c "from ultralytics import YOLO; model = YOLO('yolo11n.pt')"

# 方法 2：手动下载
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo11n.pt

# 方法 3：使用其他镜像（中国用户）
# 从国内镜像站下载后放到项目目录
```

#### 问题：模型加载失败
**Problem: Model loading fails**

**检查路径：**

```yaml
# config.yaml
yolo:
  model_path: "yolo11n.pt"  # 确保文件存在
```

```bash
# 验证文件
ls -lh yolo11n.pt
```

---

### 8. RK3588S 特定问题 / RK3588S Specific Issues

#### 问题：CPU 温度过高
**Problem: CPU temperature too high**

**监控温度：**

```bash
# 查看温度
cat /sys/class/thermal/thermal_zone*/temp

# 持续监控
watch -n 1 cat /sys/class/thermal/thermal_zone*/temp
```

**解决方案：**
1. 确保良好散热
2. 添加散热片或风扇
3. 降低处理负载：
   ```yaml
   yolo:
     img_size: 416
   tracking:
     update_interval: 0.3
   ```

#### 问题：性能不足
**Problem: Insufficient performance**

**优化配置：**

```yaml
# config.yaml - RK3588S 优化配置
yolo:
  model_path: "yolo11n.pt"
  img_size: 416
  device: "cpu"

tracking:
  update_interval: 0.2
  smoothing_factor: 0.5

video:
  display: false  # 禁用显示以节省资源
```

**CPU 性能模式：**

```bash
# 设置为性能模式
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

---

### 9. 日志和调试 / Logging and Debugging

#### 启用详细日志
**Enable verbose logging**

修改 Python 文件中的日志级别：

```python
# main.py
logging.basicConfig(
    level=logging.DEBUG,  # 从 INFO 改为 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### 查看系统日志
**View system logs**

```bash
# 查看服务日志
sudo journalctl -u bird-tracker -f

# 查看最近的错误
sudo journalctl -u bird-tracker -p err

# 导出日志
sudo journalctl -u bird-tracker > tracker.log
```

---

### 10. 获取帮助 / Getting Help

如果问题仍未解决：

1. **查看文档**
   - README.md
   - docs/QUICKSTART.md
   - docs/API.md
   - docs/RK3588S_DEPLOYMENT.md

2. **运行诊断**
   ```bash
   python3 test_setup.py
   python3 examples/test_ptz.py
   python3 examples/test_detection.py
   ```

3. **收集信息**
   ```bash
   # 系统信息
   uname -a
   python3 --version
   pip list
   
   # 错误日志
   python3 main.py 2>&1 | tee error.log
   ```

4. **提交 Issue**
   - GitHub: https://github.com/WhyU-4/bkrc_bird_det/issues
   - 包含：系统信息、错误日志、配置文件

---

## 诊断清单 / Diagnostic Checklist

运行完整诊断：

```bash
#!/bin/bash
echo "=== System Information ==="
uname -a
python3 --version

echo ""
echo "=== Python Packages ==="
pip list | grep -E "ultralytics|opencv|onvif|numpy|torch"

echo ""
echo "=== Configuration ==="
cat config.yaml

echo ""
echo "=== Network Test ==="
ping -c 3 192.168.1.100

echo ""
echo "=== Module Import Test ==="
python3 test_setup.py

echo ""
echo "=== PTZ Test ==="
python3 examples/test_ptz.py

echo ""
echo "=== Diagnostic Complete ==="
```

保存为 `diagnose.sh`，运行：
```bash
chmod +x diagnose.sh
./diagnose.sh > diagnostic_report.txt 2>&1
```
