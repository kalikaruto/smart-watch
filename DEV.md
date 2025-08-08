# Developer Guide: Smart-Watch

This document provides a guide for developers who want to contribute to the Smart-Watch project. It outlines the project's architecture, development workflow, and deployment strategy.

## Project Architecture

The application is designed as a multi-stage, concurrent pipeline to maximize performance and robustness, especially on resource-constrained devices like a Raspberry Pi. It uses a combination of threading and multiprocessing to handle I/O-bound and CPU-bound tasks efficiently.

### Core Components

- **`main.py`**: The main entry point of the application. It orchestrates the entire pipeline, setting up the shared queues and managing the video streams, detection processes, and notification manager.

- **`video_stream.py`**: Handles all camera interactions. Each camera is managed in a dedicated **thread** (`VideoStream` class). This prevents I/O blocking, so a stalled or failed camera stream won't freeze the rest of the application.

- **`detection.py`**: Contains the `DetectionProcessor` class, which performs the CPU-intensive tasks of motion and human detection. To bypass Python's Global Interpreter Lock (GIL) and achieve true parallelism, instances of this class are run in a **process pool** managed by `main.py`.

- **`notifications.py`**: The `NotificationManager` class runs in its own dedicated **thread**. It listens for tasks on a queue and sends alerts (e.g., via Telegram) without blocking the main detection loop.

- **`config.py`**: Manages all configuration, loading camera data from `data.json` and environment variables from `.env`. It uses absolute paths to ensure the application can be run from any directory.

- **`cli.py`**: A simple command-line interface built with `npyscreen` for adding, editing, and removing cameras from `data.json`.

- **`logger.py`**: Configures a colored logger for clear and informative console output.

### Data Flow

1.  **Video Streams**: Each `VideoStream` thread continuously reads frames from its camera and puts them into a shared `frame_queue`.
2.  **Detection Pool**: The `detection_worker` processes in the pool pick up frames from the `frame_queue`.
3.  **Detection Logic**: Each `DetectionProcessor` analyzes the frame. If a human is detected after recent motion, it puts a notification task (timestamp, camera info, frame) onto the `notification_queue`.
4.  **Notification Manager**: The `NotificationManager` thread picks up tasks from the `notification_queue` and sends the alert.

This decoupled architecture ensures that a slow or failing component does not bring down the entire system.

## One-CLick Installation

For this read the file [install.sh](v2/deployment/install.sh) in the v2/deployment folder. It automates the setup process, including creating a Python virtual environment, installing dependencies, and configuring the application to run as a systemd service.


## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kalikaruto/smart-watch.git smart-watch
    cd smart-watch
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r v2/app/requirements.txt
    ```

4.  **Set up your environment variables:**
    Copy the example environment file and fill in your credentials:
    ```bash
    cp v2/deployment/.env.example v2/app/.env
    # Now, edit v2/app/.env with your details
    ```

5.  **Configure cameras:**
    Run the CLI to add your camera streams:
    ```bash
    python3 v2/app/cli.py
    ```

## Running the Application

- **To run the main detection application:**
  ```bash
  python3 v2/app/main.py
  ```

- **To show the video feeds in a GUI window:**
  ```bash
  python3 v2/app/main.py --show
  ```

## Testing the Deployment

We use Docker to test the installation process in a clean, isolated environment that mimics a Raspberry Pi.

1.  **Ensure Docker is installed.**

2.  **Enable QEMU for ARM emulation (one-time setup):**
    ```bash
    docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
    ```

3.  **Build the test image:**
    From the project root, run:
    ```bash
    docker build -t smart-watch-test -f v2/testing/Dockerfile .
    ```

4.  **Run the container interactively to see the installation script in action:**
    ```bash
    docker run -it --rm smart-watch-test
    ```

This will simulate the entire installation process as the end-user would experience it on a fresh system.
