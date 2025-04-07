#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="raspberry-nfc-player"
APP_DIR="/home/box/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="media_player"
USER="box"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_status() {
    echo -e "${GREEN}[*] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[!] $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    libgstreamer-plugins-ugly1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-alsa \
    gstreamer1.0-pulseaudio \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxkbcommon-dev \
    libdrm-dev \
    libgbm-dev \
    libinput-dev \
    libudev-dev \
    libmtdev-dev \
    libts-dev \
    libx11-dev \
    libxext-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxi-dev \
    libxinerama-dev \
    libxxf86vm-dev \
    libxkbcommon-x11-dev \
    libdbus-1-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    liblcms2-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxkbcommon-dev \
    libdrm-dev \
    libgbm-dev \
    libinput-dev \
    libudev-dev \
    libmtdev-dev \
    libts-dev \
    libx11-dev \
    libxext-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxi-dev \
    libxinerama-dev \
    libxxf86vm-dev \
    libxkbcommon-x11-dev \
    libdbus-1-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev

# Create application directory
print_status "Creating application directory..."
mkdir -p $APP_DIR
chown $USER:$USER $APP_DIR

# Create required directories
print_status "Creating required directories..."
mkdir -p $APP_DIR/videos
mkdir -p $APP_DIR/logs
chown -R $USER:$USER $APP_DIR

# Create virtual environment
print_status "Creating Python virtual environment..."
su - $USER -c "python3 -m venv $VENV_DIR"

# Activate virtual environment and install Python packages
print_status "Installing Python packages..."
su - $USER -c "source $VENV_DIR/bin/activate && pip install --upgrade pip"

# Install Python packages from requirements.txt
if [ -f "requirements.txt" ]; then
    su - $USER -c "source $VENV_DIR/bin/activate && pip install -r requirements.txt"
else
    print_warning "requirements.txt not found. Please install required packages manually."
fi

# Create systemd service
print_status "Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Raspberry Pi RFID Media Player
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python $APP_DIR/media_player.py
Restart=always
RestartSec=10
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER/.Xauthority

[Install]
WantedBy=graphical.target
EOF

# Enable and start service
print_status "Enabling and starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Configure autologin
print_status "Configuring autologin..."
if [ -f "/etc/lightdm/lightdm.conf" ]; then
    sed -i 's/^#autologin-user=.*/autologin-user=box/' /etc/lightdm/lightdm.conf
    sed -i 's/^#autologin-user-timeout=.*/autologin-user-timeout=0/' /etc/lightdm/lightdm.conf
fi

# Configure display settings
print_status "Configuring display settings..."
cat > /boot/config.txt << EOF
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

# Configure X11 settings
print_status "Configuring X11 settings..."
cat > /etc/X11/xorg.conf.d/99-calibration.conf << EOF
Section "InputClass"
    Identifier "calibration"
    MatchProduct "FT5406 memory based driver"
    Option "Calibration" "3800 200 200 3800"
    Option "SwapAxes" "0"
EndSection
EOF

# Set up permissions
print_status "Setting up permissions..."
usermod -a -G video,gpio,i2c,spi $USER

# Reboot prompt
print_status "Installation complete!"
print_warning "The system needs to reboot to apply all changes."
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    reboot
fi
