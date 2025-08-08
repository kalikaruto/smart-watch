# Smart-Watch Deployment

This guide provides instructions for deploying the Smart-Watch application on a Raspberry Pi.

## Prerequisites

- A Raspberry Pi with Raspberry Pi OS (or any other Debian-based Linux distribution).
- `git` and `python3` installed.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url> smart-watch
    cd smart-watch
    ```

2.  **Make the installation script executable:**
    ```bash
    chmod +x v2/deployment/install.sh
    ```

3.  **Run the installation script:**
    ```bash
    ./v2/deployment/install.sh
    ```

4.  **Follow the on-screen instructions:**
    - The script will create a Python virtual environment, install dependencies, and set up the `.env` file.
    - You will be prompted to edit the `.env` file to add your Telegram API credentials.
    - The script will then set up a `systemd` service to run the application automatically on boot.
    - Finally, it will launch the Camera Manager for you to add your cameras.

## Managing the Service

Once installed, you can manage the Smart-Watch service using the following commands:

- **Start the service:**
  ```bash
  sudo systemctl start smart-watch
  ```

- **Stop the service:**
  ```bash
  sudo systemctl stop smart-watch
  ```

- **Check the status and view logs:**
  ```bash
  sudo systemctl status smart-watch
  ```

- **View live logs:**
  ```bash
  journalctl -fu smart-watch
  ```
