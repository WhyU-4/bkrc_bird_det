"""
Bird Detection Module using Ultralytics YOLO11
Optimized for RK3588S hardware
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BirdDetector:
    """
    YOLO11-based bird detector optimized for RK3588S
    """
    
    def __init__(self, config: dict):
        """
        Initialize the bird detector
        
        Args:
            config: Configuration dictionary containing YOLO settings
        """
        self.config = config.get('yolo', {})
        self.model_path = self.config.get('model_path', 'yolo11n.pt')
        self.conf_threshold = self.config.get('conf_threshold', 0.25)
        self.iou_threshold = self.config.get('iou_threshold', 0.45)
        self.device = self.config.get('device', 'cpu')
        self.classes = self.config.get('classes', [14])  # Bird class in COCO
        self.img_size = self.config.get('img_size', 640)
        
        logger.info(f"Loading YOLO11 model: {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
            logger.info("YOLO11 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO11 model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """
        Detect birds in the given frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detections, each containing:
                - bbox: [x1, y1, x2, y2]
                - confidence: detection confidence
                - class_id: class ID
                - class_name: class name
        """
        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                classes=self.classes,
                device=self.device,
                verbose=False
            )
            
            detections = []
            if results and len(results) > 0:
                result = results[0]
                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    class_ids = result.boxes.cls.cpu().numpy()
                    
                    for box, conf, cls_id in zip(boxes, confidences, class_ids):
                        detection = {
                            'bbox': box.tolist(),
                            'confidence': float(conf),
                            'class_id': int(cls_id),
                            'class_name': result.names[int(cls_id)]
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def get_largest_detection(self, detections: List[dict]) -> Optional[dict]:
        """
        Get the largest detection (by area)
        
        Args:
            detections: List of detections
            
        Returns:
            Largest detection or None if no detections
        """
        if not detections:
            return None
        
        largest = None
        max_area = 0
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area = area
                largest = det
        
        return largest
    
    def get_detection_center(self, detection: dict) -> Tuple[int, int]:
        """
        Get the center point of a detection
        
        Args:
            detection: Detection dictionary
            
        Returns:
            (center_x, center_y) tuple
        """
        x1, y1, x2, y2 = detection['bbox']
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        return center_x, center_y
    
    def draw_detections(self, frame: np.ndarray, detections: List[dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on the frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with drawn detections
        """
        output = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            conf = det['confidence']
            class_name = det['class_name']
            
            # Draw bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {conf:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(output, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(output, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            # Draw center point
            center_x, center_y = self.get_detection_center(det)
            cv2.circle(output, (center_x, center_y), 5, (0, 0, 255), -1)
        
        return output
