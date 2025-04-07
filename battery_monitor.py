#!/usr/bin/env python3
"""
Battery Monitor Module
Handles monitoring of battery level and charging status.
"""

import logging
import time
import RPi.GPIO as GPIO
from pathlib import Path

logger = logging.getLogger(__name__)

class BatteryMonitor:
    """
    Class for monitoring battery status and level.
    Implements hardware abstraction for different UPS HAT models.
    """
    
    def __init__(self, config):
        """
        Initialize the battery monitor.
        
        Args:
            config (dict): Configuration dictionary containing settings
        """
        self.config = config
        self.battery_level = 100  # Default to 100% if monitoring fails
        self.is_charging = False
        self.initialize_monitor()
        
    def initialize_monitor(self):
        """Initialize battery monitoring hardware."""
        try:
            # Configure GPIO for battery monitoring
            GPIO.setmode(GPIO.BCM)
            
            # Setup battery level monitoring pins
            # Note: These pin numbers should be configured based on your specific UPS HAT
            self.battery_pin = 25  # Example pin, adjust based on your hardware
            GPIO.setup(self.battery_pin, GPIO.IN)
            
            # Setup charging status monitoring
            self.charging_pin = 26  # Example pin, adjust based on your hardware
            GPIO.setup(self.charging_pin, GPIO.IN)
            
            logger.info("Battery monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize battery monitor: {e}")
            
    def get_level(self):
        """
        Get current battery level.
        
        Returns:
            int: Battery level percentage (0-100)
        """
        try:
            # Read battery level from hardware
            # This is a simplified example - actual implementation will depend on your UPS HAT
            raw_value = GPIO.input(self.battery_pin)
            
            # Convert raw value to percentage
            # This conversion will need to be calibrated for your specific hardware
            self.battery_level = self._convert_to_percentage(raw_value)
            
            return self.battery_level
            
        except Exception as e:
            logger.error(f"Error reading battery level: {e}")
            return self.battery_level  # Return last known value
            
    def is_charging(self):
        """
        Check if battery is currently charging.
        
        Returns:
            bool: True if charging, False otherwise
        """
        try:
            self.is_charging = bool(GPIO.input(self.charging_pin))
            return self.is_charging
            
        except Exception as e:
            logger.error(f"Error checking charging status: {e}")
            return self.is_charging  # Return last known value
            
    def _convert_to_percentage(self, raw_value):
        """
        Convert raw ADC value to battery percentage.
        This method should be calibrated for your specific hardware.
        
        Args:
            raw_value (int): Raw value from ADC
            
        Returns:
            int: Battery percentage (0-100)
        """
        # Example conversion - adjust based on your hardware specifications
        # This is a placeholder - actual conversion will depend on your UPS HAT
        min_value = 0
        max_value = 1023  # Typical for 10-bit ADC
        
        percentage = ((raw_value - min_value) / (max_value - min_value)) * 100
        return max(0, min(100, int(percentage)))
        
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            GPIO.cleanup()
            logger.info("Battery monitor GPIO resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up battery monitor: {e}")
            
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.cleanup() 