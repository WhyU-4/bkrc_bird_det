# API Documentation

## BirdDetector

YOLO11-based bird detector optimized for RK3588S.

### Constructor

```python
BirdDetector(config: dict)
```

**Parameters:**
- `config`: Configuration dictionary containing YOLO settings

**Configuration Options:**
```yaml
yolo:
  model_path: "yolo11n.pt"  # Path to YOLO model
  conf_threshold: 0.25      # Confidence threshold
  iou_threshold: 0.45       # IOU threshold for NMS
  device: "cpu"             # Device to use (cpu/gpu)
  classes: [14]             # Class IDs to detect (14 = bird)
  img_size: 640             # Input image size
```

### Methods

#### detect(frame)

Detect birds in the given frame.

```python
detections = detector.detect(frame)
```

**Parameters:**
- `frame`: Input image frame (BGR format, numpy array)

**Returns:**
List of detections, each containing:
- `bbox`: [x1, y1, x2, y2] - Bounding box coordinates
- `confidence`: float - Detection confidence (0.0-1.0)
- `class_id`: int - Class ID
- `class_name`: str - Class name

**Example:**
```python
detections = detector.detect(frame)
for det in detections:
    print(f"Bird at {det['bbox']} with confidence {det['confidence']:.2f}")
```

#### get_largest_detection(detections)

Get the largest detection by area.

```python
largest = detector.get_largest_detection(detections)
```

**Parameters:**
- `detections`: List of detections

**Returns:**
- Largest detection dictionary or None

#### get_detection_center(detection)

Get the center point of a detection.

```python
center_x, center_y = detector.get_detection_center(detection)
```

**Parameters:**
- `detection`: Detection dictionary

**Returns:**
- Tuple of (center_x, center_y)

#### draw_detections(frame, detections)

Draw bounding boxes and labels on frame.

```python
annotated_frame = detector.draw_detections(frame, detections)
```

**Parameters:**
- `frame`: Input frame
- `detections`: List of detections

**Returns:**
- Annotated frame with drawn detections

---

## PTZController

ONVIF PTZ camera controller.

### Constructor

```python
PTZController(config: dict)
```

**Parameters:**
- `config`: Configuration dictionary containing camera settings

**Configuration Options:**
```yaml
camera:
  ip: "192.168.1.100"
  port: 80
  username: "admin"
  password: "admin"
  ptz:
    pan_speed: 0.5
    tilt_speed: 0.5
    dead_zone_x: 50
    dead_zone_y: 50
    sensitivity: 0.001
```

### Methods

#### move_continuous(pan_velocity, tilt_velocity, duration)

Move camera continuously with specified velocities.

```python
ptz.move_continuous(pan_velocity=0.5, tilt_velocity=0.0, duration=1.0)
```

**Parameters:**
- `pan_velocity`: float (-1.0 to 1.0) - Negative=left, positive=right
- `tilt_velocity`: float (-1.0 to 1.0) - Negative=down, positive=up
- `duration`: float - Duration in seconds

#### stop()

Stop all PTZ movements.

```python
ptz.stop()
```

#### move_to_center_target(target_x, target_y, frame_center_x, frame_center_y)

Move camera to center the target in frame.

```python
ptz.move_to_center_target(target_x, target_y, frame_center_x, frame_center_y)
```

**Parameters:**
- `target_x`: int - X coordinate of target
- `target_y`: int - Y coordinate of target
- `frame_center_x`: int - X coordinate of frame center
- `frame_center_y`: int - Y coordinate of frame center

#### go_home()

Return camera to home position.

```python
ptz.go_home()
```

#### get_status()

Get current PTZ status.

```python
status = ptz.get_status()
```

**Returns:**
Dictionary with:
- `pan`: float - Current pan position
- `tilt`: float - Current tilt position
- `zoom`: float - Current zoom level
- `moving`: bool - Movement status

---

## BirdTracker

Bird tracking system that combines detection and PTZ control.

### Constructor

```python
BirdTracker(config: dict)
```

**Parameters:**
- `config`: Configuration dictionary

**Configuration Options:**
```yaml
tracking:
  frame_center_tolerance: 50
  update_interval: 0.1
  mode: "center"
  smoothing_factor: 0.3
```

### Methods

#### process_frame(frame)

Process a single frame: detect birds and control PTZ.

```python
annotated_frame, tracking_active = tracker.process_frame(frame)
```

**Parameters:**
- `frame`: Input frame (BGR format)

**Returns:**
- Tuple of (annotated_frame, tracking_active)

#### reset_tracking()

Reset tracking state.

```python
tracker.reset_tracking()
```

#### go_home()

Return camera to home position.

```python
tracker.go_home()
```

#### stop_ptz()

Stop all PTZ movements.

```python
tracker.stop_ptz()
```

#### get_statistics()

Get tracking statistics.

```python
stats = tracker.get_statistics()
```

**Returns:**
Dictionary with:
- `frames_processed`: int
- `detections`: int
- `ptz_moves`: int
- `ptz_enabled`: bool

---

## Usage Example

```python
import cv2
import yaml
from src.bird_tracker import BirdTracker

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize tracker
tracker = BirdTracker(config)

# Open video source
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        annotated_frame, tracking_active = tracker.process_frame(frame)
        
        # Display
        cv2.imshow('Bird Tracker', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tracker.stop_ptz()
    cap.release()
    cv2.destroyAllWindows()
```
