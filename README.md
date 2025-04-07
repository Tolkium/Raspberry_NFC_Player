# Raspberry Pi 5 RFID-Activated Media Player

A Python-based media player application for Raspberry Pi 5 that uses RFID tags to control video playback on a touchscreen display.

## Features

- RFID tag-activated video playback
- 12.3-inch capacitive touchscreen support (1920x720)
- Physical button controls
- Battery monitoring and emergency shutdown
- Hardware-accelerated video playback
- Test mode for development
- Configurable GPIO pin assignments
- Comprehensive logging system

## Hardware Requirements

- Raspberry Pi 5 (4GB)
- 12.3-inch Capacitive Touch Display (1920x720)
- MFRC-522 RC522 RFID reader
- PCIe to M.2 NVMe SSD adapter with 128GB SSD
- UPS HAT supporting 4x 21700 Li batteries
- 5 large button modules (3 playback, 2 volume)

## Software Requirements

- Raspberry Pi OS (64-bit)
- Python 3.9+
- Required Python packages (see requirements.txt)

## Installation

### Quick Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/raspberry-nfc-player.git
cd raspberry-nfc-player
```

2. Make the installation script executable:
```bash
chmod +x install.sh
```

3. Run the installation script as root:
```bash
sudo ./install.sh
```

The installation script will:
- Update system packages
- Install all required dependencies
- Create necessary directories
- Set up Python virtual environment
- Install Python packages
- Configure systemd service
- Set up autologin
- Configure display settings
- Set up permissions
- Reboot the system

### Manual Installation

If you prefer to install manually:

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev git \
    libgl1-mesa-dev libgles2-mesa-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev libgstreamer-plugins-bad1.0-dev \
    libgstreamer-plugins-ugly1.0-dev \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav gstreamer1.0-tools \
    gstreamer1.0-alsa gstreamer1.0-pulseaudio \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libjpeg-dev libfreetype6-dev liblcms2-dev \
    libopenjp2-7-dev libtiff5-dev libwebp-dev libharfbuzz-dev \
    libfribidi-dev libxkbcommon-dev libdrm-dev libgbm-dev \
    libinput-dev libudev-dev libmtdev-dev libts-dev \
    libx11-dev libxext-dev libxrandr-dev libxcursor-dev \
    libxi-dev libxinerama-dev libxxf86vm-dev libxkbcommon-x11-dev \
    libdbus-1-dev libssl-dev libffi-dev libxml2-dev libxslt1-dev
```

2. Create application directory:
```bash
mkdir -p /home/box/raspberry-nfc-player
mkdir -p /home/box/raspberry-nfc-player/videos
mkdir -p /home/box/raspberry-nfc-player/logs
chown -R box:box /home/box/raspberry-nfc-player
```

3. Set up Python virtual environment:
```bash
cd /home/box/raspberry-nfc-player
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

4. Configure systemd service:
```bash
sudo cp media_player.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable media_player
sudo systemctl start media_player
```

5. Configure autologin:
```bash
sudo sed -i 's/^#autologin-user=.*/autologin-user=box/' /etc/lightdm/lightdm.conf
sudo sed -i 's/^#autologin-user-timeout=.*/autologin-user-timeout=0/' /etc/lightdm/lightdm.conf
```

6. Configure display settings:
```bash
sudo tee /boot/config.txt << EOF
# Enable VideoCore
gpu_mem=256
start_x=1

# Enable hardware acceleration
dtoverlay=vc4-kms-v3d
max_framebuffers=2

# Disable screen blanking
consoleblank=0

# Enable I2C and SPI
dtparam=i2c_arm=on
dtparam=spi=on
EOF
```

7. Set up permissions:
```bash
sudo usermod -a -G video,gpio,i2c,spi box
```

8. Reboot the system:
```bash
sudo reboot
```

## Configuration

Edit `config.json` to configure:

- RFID tag mappings
- GPIO pin assignments
- Display settings
- Player settings
- Battery thresholds

## Usage

1. Power on the system
2. The player will automatically start in fullscreen mode
3. Present an RFID tag to play the associated video
4. Use touchscreen or physical buttons to control playback
5. Press F10 to enter test mode

## Controls

### Touchscreen
- Left third: Rewind/backward
- Middle third: Play/pause
- Right third: Forward
- Bottom quarter: Progress bar

### Physical Buttons
- Button 1: Backward
- Button 2: Play/Pause
- Button 3: Forward
- Button 4: Volume Down
- Button 5: Volume Up

## Development

- Test mode: Press F10 to load test video
- Logs are stored in `media_player.log`
- Debug mode: Set logging level to DEBUG in code

## Troubleshooting

1. Check logs in `media_player.log`
2. Verify hardware connections
3. Ensure video files are in correct format
4. Check RFID tag mappings in config
5. Verify GPIO pin assignments

## Video Format Recommendations

For optimal performance on Raspberry Pi 5:

- Codec: H.264 (AVC) or H.265 (HEVC)
- Resolution: 1920x720
- Frame rate: 30fps
- Container: MP4
- Audio: AAC

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 