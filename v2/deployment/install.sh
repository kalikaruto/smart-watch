#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# --- Helper Functions ---
echo_green() {
    echo -e "\033[0;32m$1\033[0m"
}

echo_yellow() {
    echo -e "\033[0;33m$1\033[0m"
}

echo_red() {
    echo -e "\033[0;31m$1\033[0m"
}
# Install python if not installed
if ! command -v python3 &> /dev/null; then
    echo_yellow "Python3 is not installed. Installing Python3..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip
    if [ $? -ne 0 ]; then
        echo_red "Error: Failed to install Python3."
        exit 1
    fi
fi

# --- Installation Steps ---

echo_green "Starting Smart-Watch Installation..."

# 1. Create Python Virtual Environment
echo_green "\n[1/5] Creating Python virtual environment($PROJECT_ROOT)..."
if [ ! -d "$PROJECT_ROOT/.venv"]
    python3 -m venv "$PROJECT_ROOT/.venv"
    if [ $? -ne 0 ]; then
        echo_red "Error: Failed to create virtual environment."
        exit 1
    fi
else
    echo "$PROJECT_ROOT/.venv/ already exists"
fi

# 2. Install Dependencies
echo_green "\n[2/5] Installing dependencies from requirements.txt..."
source "$PROJECT_ROOT/.venv/bin/activate"
pip install -r "$PROJECT_ROOT/app/requirements.txt"
if [ $? -ne 0 ]; then
    echo_red "Error: Failed to install dependencies."
    exit 1
fi
deactivate

# 3. Set up .env file
echo_green "\n[3/5] Setting up environment file..."
if [ ! -f "$PROJECT_ROOT/app/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$PROJECT_ROOT/app/.env"
    echo_yellow "An .env file has been created in v2/app."
    echo_yellow "Please edit this file to add your Telegram token and chat ID."
else
    echo_green ".env file already exists. Skipping."
fi

# 4. Set up systemd service
echo_green "\n[4/5] Setting up systemd service..."
SERVICE_FILE="$SCRIPT_DIR/smart-watch.service"

# Check if the user is pi, if not, ask for the username
if [ "$(whoami)" != "pi" ]; then
    read -p "Enter the username that will run the service (default: pi): " username
    username=${username:-pi}
    sed -i "s/User=pi/User=$username/g" "$SERVICE_FILE"
    sed -i "s/Group=pi/Group=$username/g" "$SERVICE_FILE"
    sed -i "s|/home/pi/smart-watch|/home/$username/smart-watch|g" "$SERVICE_FILE"
fi

sudo cp "$SERVICE_FILE" /etc/systemd/system/smart-watch.service
sudo systemctl daemon-reload
sudo systemctl enable smart-watch.service

if [ $? -ne 0 ]; then
    echo_red "Error: Failed to set up systemd service."
    exit 1
fi

# 5. Initial Camera Setup
echo_green "\n[5/5] Launching Camera Manager for initial setup..."
source "$PROJECT_ROOT/.venv/bin/activate"
python3 "$PROJECT_ROOT/app/cli.py"
deactivate

# --- Final Instructions ---
echo_green "\nInstallation Complete!"
echo_yellow "The Smart-Watch service is now enabled and will start on the next reboot."
echo_yellow "To start the service immediately, run: sudo systemctl start smart-watch"
echo_yellow "To check the status and logs, run: sudo systemctl status smart-watch"
echo_yellow "To stop the service, run: sudo systemctl stop smart-watch"
