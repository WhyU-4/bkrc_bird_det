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
    
    # Open video source (use 0 for webcam or RTSP URL)
    video_source = config['video'].get('source', 0)
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print(f"Error: Cannot open video source: {video_source}")
        return
    
    print("Bird tracking started. Press 'q' to quit.")
    
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
        
        # Print statistics
        stats = tracker.get_statistics()
        print(f"\nStatistics: {stats}")

if __name__ == '__main__':
    main()
