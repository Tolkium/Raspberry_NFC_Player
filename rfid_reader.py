#!/usr/bin/env python3
"""
RFID Reader Module
Handles communication with the MFRC-522 RC522 RFID reader.
"""

import logging
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

logger = logging.getLogger(__name__)

class RFIDReader:
    """
    Class for handling RFID reader operations.
    Implements error handling and fallback mode when reader is not connected.
    """
    
    def __init__(self, config):
        """
        Initialize the RFID reader.
        
        Args:
            config (dict): Configuration dictionary containing settings
        """
        self.config = config
        self.reader = None
        self.is_connected = False
        self.last_read_time = 0
        self.last_tag_id = None
        self.initialize_reader()
        
    def initialize_reader(self):
        """Initialize the RFID reader with error handling."""
        try:
            self.reader = SimpleMFRC522()
            self.is_connected = True
            logger.info("RFID reader initialized successfully")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"RFID reader initialization failed: {e}")
            logger.info("Running in fallback mode - RFID reader not available")
            
    def read_tag(self):
        """
        Read RFID tag if present.
        
        Returns:
            str: Tag ID if detected, None otherwise
        """
        if not self.is_connected:
            return None
            
        try:
            # Implement debouncing to prevent rapid re-reads
            current_time = time.time()
            if current_time - self.last_read_time < 1.0:  # 1 second debounce
                return None
                
            id, text = self.reader.read_no_block()
            
            if id is not None:
                self.last_read_time = current_time
                tag_id = str(id)
                
                # Only return new tag IDs to prevent duplicate reads
                if tag_id != self.last_tag_id:
                    self.last_tag_id = tag_id
                    logger.info(f"RFID tag detected: {tag_id}")
                    return tag_id
                    
            return None
            
        except Exception as e:
            logger.error(f"Error reading RFID tag: {e}")
            # Attempt to reinitialize reader on error
            self.initialize_reader()
            return None
            
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            if self.is_connected:
                GPIO.cleanup()
                logger.info("RFID reader GPIO resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up RFID reader: {e}")
            
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.cleanup() 