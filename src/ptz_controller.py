"""
ONVIF PTZ Camera Controller
Handles pan-tilt-zoom operations for ONVIF-compatible cameras
"""

import logging
import time
from typing import Optional, Tuple
from onvif import ONVIFCamera
from zeep.exceptions import Fault

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PTZController:
    """
    ONVIF PTZ Camera Controller
    """
    
    def __init__(self, config: dict):
        """
        Initialize PTZ controller
        
        Args:
            config: Configuration dictionary containing camera settings
        """
        self.camera_config = config.get('camera', {})
        self.ptz_config = self.camera_config.get('ptz', {})
        
        self.ip = self.camera_config.get('ip', '192.168.1.100')
        self.port = self.camera_config.get('port', 80)
        self.username = self.camera_config.get('username', 'admin')
        self.password = self.camera_config.get('password', 'admin')
        
        self.pan_speed = self.ptz_config.get('pan_speed', 0.5)
        self.tilt_speed = self.ptz_config.get('tilt_speed', 0.5)
        self.dead_zone_x = self.ptz_config.get('dead_zone_x', 50)
        self.dead_zone_y = self.ptz_config.get('dead_zone_y', 50)
        self.sensitivity = self.ptz_config.get('sensitivity', 0.001)
        
        self.camera = None
        self.ptz_service = None
        self.media_service = None
        self.profile = None
        
        # Last movement timestamp for rate limiting
        self.last_move_time = 0
        self.min_move_interval = 0.1  # Minimum seconds between moves
        
        self._connect()
    
    def _connect(self):
        """
        Connect to the ONVIF camera and initialize PTZ service
        """
        try:
            logger.info(f"Connecting to ONVIF camera at {self.ip}:{self.port}")
            self.camera = ONVIFCamera(
                self.ip,
                self.port,
                self.username,
                self.password
            )
            
            # Get media service and profile
            self.media_service = self.camera.create_media_service()
            profiles = self.media_service.GetProfiles()
            
            if not profiles:
                raise Exception("No media profiles found")
            
            self.profile = profiles[0]
            logger.info(f"Using media profile: {self.profile.Name}")
            
            # Get PTZ service
            self.ptz_service = self.camera.create_ptz_service()
            logger.info("PTZ service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to ONVIF camera: {e}")
            raise
    
    def move_continuous(self, pan_velocity: float, tilt_velocity: float, duration: float = 0.5):
        """
        Move camera continuously with specified velocities
        
        Args:
            pan_velocity: Pan velocity (-1.0 to 1.0, negative = left, positive = right)
            tilt_velocity: Tilt velocity (-1.0 to 1.0, negative = down, positive = up)
            duration: Duration of movement in seconds
        """
        if not self.ptz_service:
            logger.warning("PTZ service not initialized")
            return
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_move_time < self.min_move_interval:
            return
        
        try:
            # Clamp velocities to valid range
            pan_velocity = max(-1.0, min(1.0, pan_velocity))
            tilt_velocity = max(-1.0, min(1.0, tilt_velocity))
            
            # Create velocity vector
            request = self.ptz_service.create_type('ContinuousMove')
            request.ProfileToken = self.profile.token
            
            if request.Velocity is None:
                request.Velocity = self.ptz_service.GetStatus({'ProfileToken': self.profile.token}).Position
            
            request.Velocity.PanTilt.x = pan_velocity
            request.Velocity.PanTilt.y = tilt_velocity
            request.Velocity.Zoom.x = 0
            
            # Execute move
            self.ptz_service.ContinuousMove(request)
            self.last_move_time = current_time
            
            # Schedule stop after duration
            time.sleep(duration)
            self.stop()
            
        except Fault as e:
            logger.error(f"ONVIF Fault during continuous move: {e}")
        except Exception as e:
            logger.error(f"Error during continuous move: {e}")
    
    def stop(self):
        """
        Stop all PTZ movements
        """
        if not self.ptz_service:
            return
        
        try:
            request = self.ptz_service.create_type('Stop')
            request.ProfileToken = self.profile.token
            request.PanTilt = True
            request.Zoom = True
            self.ptz_service.Stop(request)
        except Exception as e:
            logger.error(f"Error stopping PTZ: {e}")
    
    def move_to_center_target(self, target_x: int, target_y: int, 
                              frame_center_x: int, frame_center_y: int):
        """
        Move camera to center the target in the frame
        
        Args:
            target_x: X coordinate of target
            target_y: Y coordinate of target
            frame_center_x: X coordinate of frame center
            frame_center_y: Y coordinate of frame center
        """
        # Calculate offset from center
        offset_x = target_x - frame_center_x
        offset_y = target_y - frame_center_y
        
        # Check if within dead zone
        if abs(offset_x) < self.dead_zone_x and abs(offset_y) < self.dead_zone_y:
            logger.debug("Target within dead zone, no movement needed")
            return
        
        # Calculate velocities based on offset and sensitivity
        pan_velocity = offset_x * self.sensitivity * self.pan_speed
        tilt_velocity = -offset_y * self.sensitivity * self.tilt_speed  # Invert Y
        
        # Clamp velocities
        pan_velocity = max(-1.0, min(1.0, pan_velocity))
        tilt_velocity = max(-1.0, min(1.0, tilt_velocity))
        
        logger.debug(f"Moving PTZ: pan={pan_velocity:.3f}, tilt={tilt_velocity:.3f}")
        
        # Execute movement
        self.move_continuous(pan_velocity, tilt_velocity, duration=0.2)
    
    def go_home(self):
        """
        Return camera to home position
        """
        if not self.ptz_service:
            return
        
        try:
            request = self.ptz_service.create_type('GotoHomePosition')
            request.ProfileToken = self.profile.token
            self.ptz_service.GotoHomePosition(request)
            logger.info("Returning to home position")
        except Exception as e:
            logger.warning(f"Could not go to home position: {e}")
    
    def get_status(self) -> Optional[dict]:
        """
        Get current PTZ status
        
        Returns:
            Dictionary with position and movement status
        """
        if not self.ptz_service:
            return None
        
        try:
            status = self.ptz_service.GetStatus({'ProfileToken': self.profile.token})
            return {
                'pan': status.Position.PanTilt.x if status.Position else None,
                'tilt': status.Position.PanTilt.y if status.Position else None,
                'zoom': status.Position.Zoom.x if status.Position else None,
                'moving': status.MoveStatus if hasattr(status, 'MoveStatus') else None
            }
        except Exception as e:
            logger.error(f"Error getting PTZ status: {e}")
            return None
