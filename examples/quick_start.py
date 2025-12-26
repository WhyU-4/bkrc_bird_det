#!/usr/bin/env python3
"""
Quick start example for bird tracking system
This script demonstrates basic usage with default settings
"""

import cv2
import yaml
from src.bird_tracker import BirdTracker

def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize tracker
    print("Initializing bird tracker...")
    tracker = BirdTracker(config)
    
    # Open video source: prefer RTSP URL if provided, else use index
    video_cfg = config.get('video', {})
    video_source = video_cfg.get('rtsp_url') or video_cfg.get('source', 0)
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print(f"Error: Cannot open video source: {video_source}")
        return
    
    print("Bird tracking started. Press 'q' to quit.")
    display = bool(video_cfg.get('display', True))
    dw = int(video_cfg.get('display_width', 0) or 0)
    dh = int(video_cfg.get('display_height', 0) or 0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame, tracking_active = tracker.process_frame(frame)
            
            # Display (optional)
            if display:
                if dw > 0 and dh > 0:
                    annotated_frame = cv2.resize(annotated_frame, (dw, dh))
                cv2.imshow('Bird Tracker', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    
    finally:
        tracker.stop_ptz()
        cap.release()
        if display:
            cv2.destroyAllWindows()
        
        # Print statistics
        stats = tracker.get_statistics()
        print(f"\nStatistics: {stats}")

if __name__ == '__main__':
    main()
