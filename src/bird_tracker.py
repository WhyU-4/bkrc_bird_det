"""
Bird Tracking System
Integrates YOLO11 detection with ONVIF PTZ control
"""

import cv2
import numpy as np
import logging
import time
from typing import Optional, Tuple
from .bird_detector import BirdDetector
from .ptz_controller import PTZController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BirdTracker:
    """
    Bird tracking system that combines detection and PTZ control
    """
    
    def __init__(self, config: dict):
        """
        Initialize the bird tracker
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.tracking_config = config.get('tracking', {})
        
        # Initialize detector and PTZ controller
        logger.info("Initializing bird detector...")
        self.detector = BirdDetector(config)
        
        logger.info("Initializing PTZ controller...")
        try:
            self.ptz_controller = PTZController(config)
            self.ptz_enabled = True
        except Exception as e:
            logger.warning(f"PTZ controller initialization failed: {e}")
            logger.warning("Continuing without PTZ control")
            self.ptz_enabled = False
        
        # Tracking parameters
        self.frame_center_tolerance = self.tracking_config.get('frame_center_tolerance', 50)
        self.update_interval = self.tracking_config.get('update_interval', 0.1)
        self.smoothing_factor = self.tracking_config.get('smoothing_factor', 0.3)
        
        # Tracking state
        self.last_target_pos = None
        self.last_update_time = 0
        self.smoothed_offset_x = 0
        self.smoothed_offset_y = 0
        
        # Statistics
        self.frame_count = 0
        self.detection_count = 0
        self.tracking_count = 0
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Process a single frame: detect birds and control PTZ
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (annotated_frame, tracking_active)
        """
        self.frame_count += 1
        frame_height, frame_width = frame.shape[:2]
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2
        
        # Detect birds
        detections = self.detector.detect(frame)
        
        # Draw detections
        annotated_frame = self.detector.draw_detections(frame, detections)
        
        # Draw frame center
        cv2.line(annotated_frame, (frame_center_x - 20, frame_center_y),
                (frame_center_x + 20, frame_center_y), (255, 0, 0), 2)
        cv2.line(annotated_frame, (frame_center_x, frame_center_y - 20),
                (frame_center_x, frame_center_y + 20), (255, 0, 0), 2)
        
        # Draw dead zone
        if self.ptz_enabled:
            dead_zone_color = (200, 200, 200)
            cv2.rectangle(annotated_frame,
                         (frame_center_x - self.ptz_controller.dead_zone_x,
                          frame_center_y - self.ptz_controller.dead_zone_y),
                         (frame_center_x + self.ptz_controller.dead_zone_x,
                          frame_center_y + self.ptz_controller.dead_zone_y),
                         dead_zone_color, 1)
        
        tracking_active = False
        
        if detections:
            self.detection_count += 1
            
            # Get largest detection (closest/most prominent bird)
            target = self.detector.get_largest_detection(detections)
            
            if target:
                target_x, target_y = self.detector.get_detection_center(target)
                
                # Calculate offset from center
                offset_x = target_x - frame_center_x
                offset_y = target_y - frame_center_y
                
                # Apply smoothing
                self.smoothed_offset_x = (self.smoothing_factor * self.smoothed_offset_x +
                                         (1 - self.smoothing_factor) * offset_x)
                self.smoothed_offset_y = (self.smoothing_factor * self.smoothed_offset_y +
                                         (1 - self.smoothing_factor) * offset_y)
                
                # Draw line from center to target
                cv2.line(annotated_frame, (frame_center_x, frame_center_y),
                        (target_x, target_y), (0, 255, 255), 2)
                
                # Display offset
                offset_text = f"Offset: ({offset_x:+.0f}, {offset_y:+.0f})"
                cv2.putText(annotated_frame, offset_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Control PTZ if enabled
                if self.ptz_enabled:
                    current_time = time.time()
                    if current_time - self.last_update_time >= self.update_interval:
                        self.ptz_controller.move_to_center_target(
                            target_x, target_y,
                            frame_center_x, frame_center_y
                        )
                        self.last_update_time = current_time
                        self.tracking_count += 1
                        tracking_active = True
                
                self.last_target_pos = (target_x, target_y)
        
        # Display statistics
        stats_text = f"Frame: {self.frame_count} | Detections: {self.detection_count}"
        cv2.putText(annotated_frame, stats_text, (10, frame_height - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if self.ptz_enabled:
            ptz_text = f"PTZ Moves: {self.tracking_count}"
            cv2.putText(annotated_frame, ptz_text, (10, frame_height - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            ptz_text = "PTZ: Disabled"
            cv2.putText(annotated_frame, ptz_text, (10, frame_height - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return annotated_frame, tracking_active
    
    def reset_tracking(self):
        """
        Reset tracking state
        """
        self.last_target_pos = None
        self.smoothed_offset_x = 0
        self.smoothed_offset_y = 0
        logger.info("Tracking state reset")
    
    def go_home(self):
        """
        Return camera to home position
        """
        if self.ptz_enabled:
            self.ptz_controller.go_home()
    
    def stop_ptz(self):
        """
        Stop all PTZ movements
        """
        if self.ptz_enabled:
            self.ptz_controller.stop()
    
    def get_statistics(self) -> dict:
        """
        Get tracking statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'frames_processed': self.frame_count,
            'detections': self.detection_count,
            'ptz_moves': self.tracking_count,
            'ptz_enabled': self.ptz_enabled
        }
