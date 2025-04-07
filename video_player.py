#!/usr/bin/env python3
"""
Video Player Module
Handles video playback with hardware acceleration and touch controls.
"""

import logging
import os
import json
import time
from pathlib import Path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

logger = logging.getLogger(__name__)

class VideoPlayer:
    """
    Class for handling video playback using GStreamer with hardware acceleration.
    Implements touch controls and state management.
    """
    
    def __init__(self, config):
        """
        Initialize the video player.
        
        Args:
            config (dict): Configuration dictionary containing settings
        """
        self.config = config
        self.pipeline = None
        self.bus = None
        self.current_video = None
        self.playback_position = 0
        self.volume = config['player_settings']['default_volume']
        self.is_playing = False
        self.initialize_player()
        
    def initialize_player(self):
        """Initialize GStreamer player with hardware acceleration."""
        try:
            # Initialize GStreamer
            Gst.init(None)
            
            # Create optimized pipeline for hardware acceleration
            pipeline_str = (
                f'filesrc location={{}} ! '
                'qtdemux ! '
                'h264parse ! '
                'v4l2h264dec ! '
                'videoconvert ! '
                'video/x-raw,format=RGBA ! '
                'glupload ! '
                'glcolorconvert ! '
                'glimagesink sync=false '
                'qtdemux.audio_0 ! '
                'aacparse ! '
                'faad ! '
                'audioconvert ! '
                'audioresample ! '
                'alsasink'
            )
            
            self.pipeline = Gst.parse_launch(pipeline_str)
            
            # Get bus for message handling
            self.bus = self.pipeline.get_bus()
            self.bus.add_signal_watch()
            self.bus.connect('message', self._on_message)
            
            # Set initial volume
            self.set_volume(self.volume)
            
            logger.info("Video player initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize video player: {e}")
            raise
            
    def _on_message(self, bus, message):
        """Handle GStreamer bus messages."""
        try:
            if message.type == Gst.MessageType.EOS:
                self._on_video_end()
            elif message.type == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                logger.error(f"GStreamer error: {err.message}")
                self.show_message(f"Playback Error: {err.message}")
        except Exception as e:
            logger.error(f"Error handling GStreamer message: {e}")
            
    def _on_video_end(self):
        """Handle video end event."""
        try:
            # Reset to first frame
            self.seek(0)
            self.pause()
            logger.info("Video ended, reset to first frame")
        except Exception as e:
            logger.error(f"Error handling video end: {e}")
            
    def load(self, video_path):
        """
        Load a video file.
        
        Args:
            video_path (str): Path to the video file
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
                
            # Stop current playback if any
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                
            # Set new file source
            filesrc = self.pipeline.get_by_name('filesrc0')
            filesrc.set_property('location', video_path)
            
            # Store current video path
            self.current_video = video_path
            
            # Load saved position if exists
            self.load_saved_position()
            
            # Pause on first frame
            self.play()  # Start playback to get first frame
            time.sleep(0.1)  # Wait for first frame
            self.pause()  # Pause on first frame
            
            logger.info(f"Video loaded: {video_path}")
            
        except Exception as e:
            logger.error(f"Error loading video: {e}")
            raise
            
    def play(self):
        """Start or resume video playback."""
        try:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.PLAYING)
                self.is_playing = True
                logger.info("Video playback started")
        except Exception as e:
            logger.error(f"Error starting playback: {e}")
            
    def pause(self):
        """Pause video playback."""
        try:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.PAUSED)
                self.is_playing = False
                logger.info("Video playback paused")
        except Exception as e:
            logger.error(f"Error pausing playback: {e}")
            
    def stop(self):
        """Stop video playback."""
        try:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                self.is_playing = False
                logger.info("Video playback stopped")
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
            
    def seek(self, position):
        """
        Seek to a specific position in the video.
        
        Args:
            position (float): Position in seconds
        """
        try:
            if self.pipeline:
                # Convert to nanoseconds
                seek_time = position * Gst.SECOND
                self.pipeline.seek_simple(
                    Gst.Format.TIME,
                    Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                    seek_time
                )
                logger.info(f"Seeked to position: {position}s")
        except Exception as e:
            logger.error(f"Error seeking video: {e}")
            
    def set_volume(self, volume):
        """
        Set playback volume.
        
        Args:
            volume (int): Volume level (0-100)
        """
        try:
            if self.pipeline:
                self.volume = max(0, min(100, volume))
                # Convert to linear volume (0.0 to 1.0)
                linear_volume = self.volume / 100.0
                alsasink = self.pipeline.get_by_name('alsasink0')
                alsasink.set_property('volume', linear_volume)
                logger.info(f"Volume set to: {volume}")
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            
    def get_position(self):
        """
        Get current playback position.
        
        Returns:
            float: Current position in seconds
        """
        try:
            if self.pipeline:
                success, position = self.pipeline.query_position(Gst.Format.TIME)
                if success:
                    return position / Gst.SECOND
            return 0
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return 0
            
    def get_duration(self):
        """
        Get video duration.
        
        Returns:
            float: Duration in seconds
        """
        try:
            if self.pipeline:
                success, duration = self.pipeline.query_duration(Gst.Format.TIME)
                if success:
                    return duration / Gst.SECOND
            return 0
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
            return 0
            
    def save_state(self):
        """Save current playback state."""
        try:
            if self.current_video:
                state = {
                    'video_path': self.current_video,
                    'position': self.get_position(),
                    'volume': self.volume
                }
                
                # Save to state file
                state_file = Path('playback_state.json')
                with open(state_file, 'w') as f:
                    json.dump(state, f)
                    
                logger.info("Playback state saved")
                
        except Exception as e:
            logger.error(f"Error saving playback state: {e}")
            
    def load_saved_position(self):
        """Load saved playback position if available."""
        try:
            state_file = Path('playback_state.json')
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    
                if state['video_path'] == self.current_video:
                    self.seek(state['position'])
                    self.set_volume(state['volume'])
                    logger.info("Saved playback state loaded")
                    
        except Exception as e:
            logger.error(f"Error loading saved position: {e}")
            
    def cleanup(self):
        """Clean up player resources."""
        try:
            if self.pipeline:
                self.save_state()
                self.pipeline.set_state(Gst.State.NULL)
                self.pipeline = None
                
            logger.info("Video player resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up video player: {e}")
            
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.cleanup() 