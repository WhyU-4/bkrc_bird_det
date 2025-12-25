"""
Main application entry point for Bird Tracking System
"""

import cv2
import yaml
import argparse
import logging
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from src.bird_tracker import BirdTracker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def main():
    """
    Main application loop
    """
    parser = argparse.ArgumentParser(
        description='Bird Tracking System with YOLO11 and ONVIF PTZ Control'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--source',
        type=str,
        help='Video source (camera index or RTSP URL). Overrides config file.'
    )
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Disable video display (headless mode)'
    )
    parser.add_argument(
        '--save-video',
        type=str,
        help='Save output video to specified path'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.source:
        config['video']['source'] = args.source
    if args.no_display:
        config['video']['display'] = False
    if args.save_video:
        config['video']['save_video'] = True
        config['video']['output_path'] = args.save_video
    
    # Initialize video source
    # Priority: source from config, fallback to rtsp_url if source is camera index 0
    video_source = config['video'].get('source', 0)
    
    # If source is default camera (0) and RTSP URL is configured, prefer RTSP
    if video_source == 0 and 'rtsp_url' in config['video'] and config['video']['rtsp_url']:
        video_source = config['video']['rtsp_url']
        logger.info(f"Using RTSP source: {video_source}")
    
    logger.info(f"Opening video source: {video_source}")
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        logger.error(f"Failed to open video source: {video_source}")
        sys.exit(1)
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        fps = 30
    
    logger.info(f"Video properties: {frame_width}x{frame_height} @ {fps} FPS")
    
    # Initialize video writer if saving
    video_writer = None
    if config['video'].get('save_video', False):
        output_path = config['video'].get('output_path', 'output.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps,
                                      (frame_width, frame_height))
        logger.info(f"Saving output to: {output_path}")
    
    # Initialize bird tracker
    logger.info("Initializing bird tracking system...")
    try:
        tracker = BirdTracker(config)
    except Exception as e:
        logger.error(f"Failed to initialize tracker: {e}")
        cap.release()
        sys.exit(1)
    
    logger.info("Bird tracking system ready!")
    logger.info("Press 'q' to quit, 'h' for home position, 's' to stop PTZ")
    
    # Main processing loop
    try:
        frame_time = time.time()
        display_fps = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame, retrying...")
                time.sleep(0.1)
                continue
            
            # Process frame
            annotated_frame, tracking_active = tracker.process_frame(frame)
            
            # Calculate and display FPS
            current_time = time.time()
            elapsed = current_time - frame_time
            if elapsed > 0:
                display_fps = 0.9 * display_fps + 0.1 * (1.0 / elapsed)
            frame_time = current_time
            
            fps_text = f"FPS: {display_fps:.1f}"
            cv2.putText(annotated_frame, fps_text, (frame_width - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Save frame if recording
            if video_writer:
                video_writer.write(annotated_frame)
            
            # Display frame
            if config['video'].get('display', True):
                cv2.imshow('Bird Tracking System', annotated_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("Quit requested by user")
                    break
                elif key == ord('h'):
                    logger.info("Returning to home position")
                    tracker.go_home()
                elif key == ord('s'):
                    logger.info("Stopping PTZ movement")
                    tracker.stop_ptz()
                elif key == ord('r'):
                    logger.info("Resetting tracking state")
                    tracker.reset_tracking()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    except Exception as e:
        logger.error(f"Error in main loop: {e}", exc_info=True)
    
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        tracker.stop_ptz()
        
        stats = tracker.get_statistics()
        logger.info(f"Statistics: {stats}")
        
        cap.release()
        if video_writer:
            video_writer.release()
        cv2.destroyAllWindows()
        
        logger.info("Shutdown complete")


if __name__ == '__main__':
    main()
