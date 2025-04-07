# Installation Instructions

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS (64-bit)
- 12.3-inch Capacitive Touch Display (1920x720)
- MFRC-522 RC522 RFID reader
- PCIe to M.2 NVMe SSD adapter with 128GB SSD
- UPS HAT supporting 4x 21700 Li batteries
- 5 large button modules (3 playback, 2 volume)

## Installation Steps

1. **Prepare the Raspberry Pi**
   - Flash Raspberry Pi OS (64-bit) to your SD card
   - Boot the Pi and complete initial setup
   - Connect to the internet

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/raspberry-nfc-player.git
   cd raspberry-nfc-player
   ```

3. **Run the Installation Script**
   ```bash
   sudo chmod +x install.sh
   sudo ./install.sh
   ```

   The installation script will:
   - Update system packages
   - Install required dependencies
   - Create necessary directories
   - Set up Python virtual environment
   - Install Python packages
   - Configure systemd service
   - Set up autologin
   - Configure display settings
   - Set up permissions
   - Reboot the system

4. **Configure the Application**
   - Edit `config.json` to match your hardware setup:
     - Update GPIO pin assignments
     - Configure RFID tag mappings
     - Set display settings
     - Adjust player settings

5. **Place Video Files**
   - Copy your video files to the `videos` directory
   - Ensure videos are in the recommended format:
     - Codec: H.264 (AVC) or H.265 (HEVC)
     - Resolution: 1920x720
     - Frame rate: 30fps
     - Container: MP4
     - Audio: AAC

6. **Test the Installation**
   - The application should start automatically after reboot
   - Press F10 to enter test mode
   - Test RFID tag detection
   - Verify touch controls
   - Check physical button functionality

## Troubleshooting

1. **Display Issues**
   - Check `/boot/config.txt` settings
   - Verify touch calibration
   - Ensure proper power supply

2. **RFID Reader Problems**
   - Verify SPI interface is enabled
   - Check GPIO connections
   - Test with `python3 -m mfrc522`

3. **Video Playback Issues**
   - Check video format compatibility
   - Verify hardware acceleration
   - Monitor system resources

4. **Service Problems**
   - Check service status: `sudo systemctl status media_player`
   - View logs: `journalctl -u media_player`
   - Restart service: `sudo systemctl restart media_player`

## Hardware Connections

1. **RFID Reader**
   - VCC: 3.3V
   - RST: GPIO 25
   - GND: Ground
   - MISO: GPIO 9 (MISO)
   - MOSI: GPIO 10 (MOSI)
   - SCK: GPIO 11 (SCLK)
   - SDA: GPIO 8 (CE0)

2. **Physical Buttons**
   - Backward: GPIO 17
   - Play/Pause: GPIO 27
   - Forward: GPIO 22
   - Volume Down: GPIO 23
   - Volume Up: GPIO 24

3. **UPS HAT**
   - Follow manufacturer's instructions
   - Connect battery monitoring pins
   - Configure power button

## Maintenance

1. **Regular Updates**
   ```bash
   cd /home/pi/raspberry-nfc-player
   git pull
   sudo ./install.sh
   ```

2. **Log Management**
   - Logs are stored in `logs` directory
   - Rotate logs regularly
   - Monitor for errors

3. **Backup Configuration**
   - Regularly backup `config.json`
   - Save RFID tag mappings
   - Document hardware changes

## Support

For issues and feature requests, please:
1. Check the logs in `logs` directory
2. Review troubleshooting section
3. Open an issue on GitHub
4. Contact support with detailed error information 