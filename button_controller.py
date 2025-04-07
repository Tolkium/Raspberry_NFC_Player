#!/usr/bin/env python3
"""
Button Controller Module
Handles physical button inputs with proper debouncing and event handling.
"""

import logging
import time
import RPi.GPIO as GPIO
from threading import Thread, Event

logger = logging.getLogger(__name__)

class ButtonController:
    """
    Class for handling physical button inputs.
    Implements hardware and software debouncing.
    """
    
    def __init__(self, config):
        """
        Initialize the button controller.
        
        Args:
            config (dict): Configuration dictionary containing settings
        """
        self.config = config
        self.buttons = {}
        self.button_states = {}
        self.last_press_times = {}
        self.callbacks = {}
        self.stop_event = Event()
        self.initialize_buttons()
        
    def initialize_buttons(self):
        """Initialize all buttons with proper GPIO configuration."""
        try:
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            
            # Configure each button
            for button_name, pin in self.config['gpio_pins'].items():
                # Setup GPIO pin with pull-up resistor
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                
                # Store button configuration
                self.buttons[button_name] = pin
                self.button_states[button_name] = True  # True = not pressed (pull-up)
                self.last_press_times[button_name] = 0
                
                # Add event detection
                GPIO.add_event_detect(
                    pin,
                    GPIO.BOTH,
                    callback=lambda x, b=button_name: self._button_callback(b),
                    bouncetime=300  # Hardware debouncing
                )
                
            logger.info("Buttons initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize buttons: {e}")
            
    def _button_callback(self, button_name):
        """
        Handle button press/release events with software debouncing.
        
        Args:
            button_name (str): Name of the button that triggered the event
        """
        try:
            current_time = time.time()
            pin = self.buttons[button_name]
            
            # Software debouncing
            if current_time - self.last_press_times[button_name] < self.config['player_settings']['button_debounce_time']:
                return
                
            # Read current state
            current_state = GPIO.input(pin)
            
            # Only trigger on state change
            if current_state != self.button_states[button_name]:
                self.button_states[button_name] = current_state
                self.last_press_times[button_name] = current_time
                
                # Call registered callback if exists
                if button_name in self.callbacks:
                    self.callbacks[button_name](current_state)
                    
        except Exception as e:
            logger.error(f"Error in button callback: {e}")
            
    def register_callback(self, button_name, callback):
        """
        Register a callback function for a button.
        
        Args:
            button_name (str): Name of the button
            callback (function): Function to call when button state changes
        """
        self.callbacks[button_name] = callback
        logger.info(f"Callback registered for button: {button_name}")
        
    def get_button_state(self, button_name):
        """
        Get current state of a button.
        
        Args:
            button_name (str): Name of the button
            
        Returns:
            bool: True if button is not pressed, False if pressed
        """
        try:
            return self.button_states.get(button_name, True)
        except Exception as e:
            logger.error(f"Error getting button state: {e}")
            return True
            
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            # Remove event detection
            for pin in self.buttons.values():
                GPIO.remove_event_detect(pin)
                
            # Clean up GPIO
            GPIO.cleanup()
            logger.info("Button controller GPIO resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up button controller: {e}")
            
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.cleanup() 