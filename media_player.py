#!/usr/bin/env python3
"""
Raspberry Pi 5 RFID-Activated Media Player
Main application file containing core functionality and initialization.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
import RPi.GPIO as GPIO

# Import custom modules
from rfid_reader import RFIDReader
from battery_monitor import BatteryMonitor
from button_controller import ButtonController
from video_player import VideoPlayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('media_player.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MediaPlayerApp(App):
    """
    Main application class for the RFID-activated media player.
    Handles initialization, UI components, and core functionality.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = self.load_config()
        self.rfid_reader = None
        self.battery_monitor = None
        self.button_controller = None
        self.video_player = None
        self.current_video = None
        self.is_test_mode = False
        self.controls_visible = False
        self.last_touch_time = 0
        self.controls_timeout = 3.0  # Controls hide after 3 seconds
        
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def build(self):
        """Build the application UI."""
        # Set window properties
        Window.size = (
            self.config['display_settings']['resolution']['width'],
            self.config['display_settings']['resolution']['height']
        )
        Window.fullscreen = self.config['display_settings']['fullscreen']
        
        # Create main layout
        self.root = BoxLayout(orientation='vertical')
        
        # Create video container
        self.video_container = BoxLayout(orientation='vertical')
        self.root.add_widget(self.video_container)
        
        # Create controls overlay
        self.controls_overlay = BoxLayout(orientation='vertical', opacity=0)
        with self.controls_overlay.canvas.before:
            Color(0, 0, 0, self.config['player_settings']['overlay_transparency'])
            self.overlay_rect = Rectangle(size=self.controls_overlay.size,
                                       pos=self.controls_overlay.pos)
        
        # Add progress bar
        self.progress_bar = Slider(min=0, max=100, value=0)
        self.progress_bar.bind(value=self.on_progress_change)
        self.controls_overlay.add_widget(self.progress_bar)
        
        # Add status label
        self.status_label = Label(text="Insert Plate", font_size='32sp')
        self.controls_overlay.add_widget(self.status_label)
        
        self.root.add_widget(self.controls_overlay)
        
        # Initialize components
        self.initialize_components()
        
        # Start background tasks
        self.start_background_tasks()
        
        # Bind touch events
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_up=self.on_touch_up)
        
        return self.root

    def initialize_components(self):
        """Initialize all hardware and software components."""
        try:
            # Initialize RFID reader
            self.rfid_reader = RFIDReader(self.config)
            
            # Initialize battery monitor
            self.battery_monitor = BatteryMonitor(self.config)
            
            # Initialize button controller
            self.button_controller = ButtonController(self.config)
            
            # Initialize video player
            self.video_player = VideoPlayer(self.config)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def start_background_tasks(self):
        """Start background monitoring tasks."""
        # Start RFID scanning
        Clock.schedule_interval(self.scan_rfid, 
                              self.config['player_settings']['scan_interval'])
        
        # Start battery monitoring
        Clock.schedule_interval(self.check_battery, 60)  # Check every minute
        
        # Start resource optimization
        Clock.schedule_interval(self.optimize_resources, 300)  # Check every 5 minutes
        
        # Initialize system event handlers
        self.handle_system_events()
        
        logger.info("Background tasks started")

    def scan_rfid(self, dt):
        """Scan for RFID tags and handle detection."""
        if self.is_test_mode:
            return
            
        try:
            tag_id = self.rfid_reader.read_tag()
            if tag_id:
                self.handle_tag_detection(tag_id)
        except Exception as e:
            logger.error(f"RFID scanning error: {e}")

    def handle_tag_detection(self, tag_id):
        """Handle RFID tag detection and video loading."""
        try:
            # Find matching video in configuration
            for tag in self.config['rfid_tags']:
                if tag['tag_id'] == tag_id:
                    self.load_video(tag['video_path'])
                    return
            
            # If no match found and no video is playing
            if not self.current_video:
                self.show_message("Unidentified Tag Detected")
                
        except Exception as e:
            logger.error(f"Error handling tag detection: {e}")

    def load_video(self, video_path):
        """Load and prepare video for playback."""
        try:
            if os.path.exists(video_path):
                self.video_player.load(video_path)
                self.current_video = video_path
                self.show_message("Video Loaded - Press Play")
                
                # Schedule progress updates
                Clock.schedule_interval(self.update_progress, 0.1)
            else:
                self.show_message(f"File not found: {video_path}")
                logger.error(f"Video file not found: {video_path}")
        except Exception as e:
            self.show_message(f"Error loading video: {str(e)}")
            logger.error(f"Error loading video: {e}")

    def check_battery(self, dt):
        """Check battery level and handle low battery conditions."""
        try:
            battery_level = self.battery_monitor.get_level()
            
            if battery_level <= self.config['player_settings']['critical_battery_threshold']:
                self.handle_critical_battery()
            elif battery_level <= self.config['player_settings']['low_battery_threshold']:
                self.show_message(f"Low Battery: {battery_level}%")
                
        except Exception as e:
            logger.error(f"Battery monitoring error: {e}")

    def handle_critical_battery(self):
        """Handle critical battery level situation."""
        self.show_message("Critical Battery Level - Shutting Down in 5 seconds")
        time.sleep(5)  # Give user time to see the message
        self.shutdown_system()

    def shutdown_system(self):
        """Perform system shutdown."""
        try:
            # Save current state if needed
            if self.current_video:
                self.video_player.save_state()
            
            # Perform system shutdown
            os.system('sudo shutdown -h now')
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

    def on_touch_down(self, window, touch):
        """Handle touch down events for controls."""
        if not self.current_video:
            return
            
        # Show controls
        self.show_controls()
        
        # Get touch position relative to window width
        touch_x = touch.x / Window.width
        
        if touch_x < 0.33:  # Left third
            self.video_player.seek(self.video_player.get_position() - 10)
        elif touch_x > 0.66:  # Right third
            self.video_player.seek(self.video_player.get_position() + 10)
        else:  # Middle third
            if self.video_player.player.is_playing():
                self.video_player.pause()
                self.status_label.text = "Paused"
            else:
                self.video_player.play()
                self.status_label.text = "Playing"
                
    def on_touch_up(self, window, touch):
        """Handle touch up events for progress bar."""
        if not self.current_video:
            return
            
        # Check if touch was on progress bar
        if touch.y < self.progress_bar.height:
            # Calculate position based on touch x
            position = (touch.x / Window.width) * self.video_player.get_duration()
            self.video_player.seek(position)
            
    def on_progress_change(self, instance, value):
        """Handle progress bar value changes."""
        if not self.current_video:
            return
            
        # Update video position
        position = (value / 100) * self.video_player.get_duration()
        self.video_player.seek(position)
        
    def show_controls(self):
        """Show controls overlay."""
        self.controls_visible = True
        self.controls_overlay.opacity = 1
        self.last_touch_time = time.time()
        
    def hide_controls(self):
        """Hide controls overlay."""
        if self.controls_visible and not self.video_player.player.is_playing():
            self.controls_visible = False
            self.controls_overlay.opacity = 0
            
    def update_progress(self, dt):
        """Update progress bar and handle controls visibility."""
        if self.current_video:
            # Update progress bar
            position = self.video_player.get_position()
            duration = self.video_player.get_duration()
            if duration > 0:
                self.progress_bar.value = (position / duration) * 100
                
            # Handle controls visibility
            if self.controls_visible and time.time() - self.last_touch_time > self.controls_timeout:
                self.hide_controls()
                
    def show_message(self, message):
        """Display a message on the screen."""
        self.status_label.text = message
        self.show_controls()

    def on_keyboard(self, window, key, *args):
        """Handle keyboard events."""
        if key == 301:  # F10 key
            self.activate_test_mode()
        return True

    def activate_test_mode(self):
        """Activate test mode and load test video."""
        self.is_test_mode = True
        test_video = self.config['test_video']
        if os.path.exists(test_video):
            self.load_video(test_video)
        else:
            self.show_message("Test video not found")

    def optimize_resources(self):
        """Optimize system resource usage."""
        try:
            # Reduce CPU usage when idle
            if not self.current_video:
                # Lower process priority
                os.nice(10)  # Lower priority
                
                # Reduce update frequency
                Clock.unschedule(self.update_progress)
                
            else:
                # Restore normal priority
                os.nice(0)
                
                # Restore update frequency
                Clock.schedule_interval(self.update_progress, 0.1)
                
            logger.info("Resource optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing resources: {e}")
            
    def handle_system_events(self):
        """Handle system events like power button presses."""
        try:
            # Monitor power button GPIO pin
            power_button_pin = 3  # GPIO pin for power button
            GPIO.setup(power_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Add event detection for power button
            GPIO.add_event_detect(
                power_button_pin,
                GPIO.FALLING,
                callback=self._power_button_callback,
                bouncetime=300
            )
            
            logger.info("System event handlers initialized")
            
        except Exception as e:
            logger.error(f"Error setting up system event handlers: {e}")
            
    def _power_button_callback(self, channel):
        """Handle power button press."""
        try:
            # Start shutdown sequence
            self.show_message("Shutting Down...")
            time.sleep(2)
            self.shutdown_system()
            
        except Exception as e:
            logger.error(f"Error handling power button press: {e}")

if __name__ == '__main__':
    MediaPlayerApp().run() 