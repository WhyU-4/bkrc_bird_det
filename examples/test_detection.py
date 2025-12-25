#!/usr/bin/env python3
"""
Test YOLO11 bird detection without PTZ control
Use this to verify your detection setup
"""

import cv2
import yaml
from src.bird_detector import BirdDetector

def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("Testing YOLO11 bird detection...")
    
    try:
        # Initialize detector
        detector = BirdDetector(config)
        print("✓ YOLO11 model loaded successfully")
        
        # Open video source
        video_source = config['video'].get('source', 0)
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"✗ Cannot open video source: {video_source}")
            return
        
        print(f"✓ Video source opened: {video_source}")
        print("\nDetecting birds... Press 'q' to quit")
        
        detection_count = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect birds
            detections = detector.detect(frame)
            
            if detections:
                detection_count += 1
                print(f"Frame {frame_count}: Found {len(detections)} bird(s)")
                for det in detections:
                    print(f"  - Confidence: {det['confidence']:.2f}")
            
            # Draw detections
            annotated_frame = detector.draw_detections(frame, detections)
            
            # Display
            cv2.imshow('Bird Detection Test', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n✓ Test complete")
        print(f"  Processed {frame_count} frames")
        print(f"  Detected birds in {detection_count} frames")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("1. YOLO11 model is installed (will download on first run)")
        print("2. Video source is configured correctly in config.yaml")
        print("3. Camera is accessible")

if __name__ == '__main__':
    main()
