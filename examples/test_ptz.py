#!/usr/bin/env python3
"""
Test ONVIF PTZ connection without bird detection
Use this to verify your camera setup
"""

import yaml
from src.ptz_controller import PTZController
import time

def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("Testing ONVIF PTZ connection...")
    print(f"Camera IP: {config['camera']['ip']}")
    
    try:
        # Initialize PTZ controller
        ptz = PTZController(config)
        print("✓ Successfully connected to camera")
        
        # Get status
        status = ptz.get_status()
        if status:
            print(f"✓ Current position: Pan={status['pan']:.2f}, Tilt={status['tilt']:.2f}")
        
        # Test movements
        print("\nTesting PTZ movements...")
        
        print("Moving right...")
        ptz.move_continuous(0.3, 0, duration=1.0)
        time.sleep(0.5)
        
        print("Moving left...")
        ptz.move_continuous(-0.3, 0, duration=1.0)
        time.sleep(0.5)
        
        print("Moving up...")
        ptz.move_continuous(0, 0.3, duration=1.0)
        time.sleep(0.5)
        
        print("Moving down...")
        ptz.move_continuous(0, -0.3, duration=1.0)
        time.sleep(0.5)
        
        print("Returning to home position...")
        ptz.go_home()
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("1. Camera IP address and port in config.yaml")
        print("2. Camera username and password")
        print("3. Camera is powered on and connected to network")
        print("4. Camera supports ONVIF protocol")

if __name__ == '__main__':
    main()
