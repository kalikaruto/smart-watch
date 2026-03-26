# api.py
import os
import sys
import subprocess
import threading
from collections import deque
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from config import load_cameras, save_cameras

app = Flask(__name__)

REQUIRED_FIELDS = ("name", "link", "desc")

BASE_DIR = Path(__file__).resolve().parent
LOG_BUFFER = deque(maxlen=1000)
PROCESS_LOCK = threading.Lock()
MAIN_PROCESS = None
LOG_THREAD = None


def _append_log(line):
    if line is None:
        return
    cleaned = line.rstrip("\n")
    if cleaned:
        LOG_BUFFER.append(cleaned)


def _drain_process_output(process):
    try:
        if process.stdout is None:
            return
        for line in process.stdout:
            _append_log(line)
    finally:
        return_code = process.poll()
        _append_log(f"[service] process exited with code {return_code}")


def _is_process_running(process):
    return process is not None and process.poll() is None


def get_service_status_payload():
    running = _is_process_running(MAIN_PROCESS)
    return {
        "running": running,
        "pid": MAIN_PROCESS.pid if running else None,
        "returncode": None if running or MAIN_PROCESS is None else MAIN_PROCESS.poll(),
    }


def start_main_service():
    global MAIN_PROCESS, LOG_THREAD

    with PROCESS_LOCK:
        if _is_process_running(MAIN_PROCESS):
            return False, "Service is already running"

        command = [sys.executable, str(BASE_DIR / "main.py")]
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        process = subprocess.Popen(
            command,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )

        MAIN_PROCESS = process
        LOG_BUFFER.clear()
        _append_log(f"[service] started main.py (pid={process.pid})")

        LOG_THREAD = threading.Thread(
            target=_drain_process_output,
            args=(process,),
            daemon=True,
        )
        LOG_THREAD.start()

    return True, None


def stop_main_service():
    global MAIN_PROCESS

    with PROCESS_LOCK:
        if not _is_process_running(MAIN_PROCESS):
            return False, "Service is not running"

        process = MAIN_PROCESS
        _append_log("[service] stopping process...")
        process.terminate()

    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        _append_log("[service] force killing process")
        process.kill()
        process.wait(timeout=3)

    return True, None


def read_cameras():
    cameras = load_cameras()
    return cameras if isinstance(cameras, list) else []


def validate_camera_payload(payload):
    if not isinstance(payload, dict):
        return None, "Request body must be a JSON object."

    cleaned = {}
    for field in REQUIRED_FIELDS:
        value = payload.get(field, "")
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
        if not value:
            return None, "All fields are required: name, link, desc"
        cleaned[field] = value

    return cleaned, None


def camera_response(camera, index):
    return {
        "id": index,  # index-based to match current CLI behavior
        "name": camera.get("name", ""),
        "link": camera.get("link", ""),
        "desc": camera.get("desc", ""),
    }


@app.get("/")
def homepage():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/api/cameras")
def list_cameras():
    cameras = read_cameras()
    return jsonify([camera_response(cam, i) for i, cam in enumerate(cameras)]), 200


@app.get("/api/cameras/<int:camera_id>")
def get_camera(camera_id):
    cameras = read_cameras()
    if camera_id < 0 or camera_id >= len(cameras):
        return jsonify({"error": "Camera not found"}), 404
    return jsonify(camera_response(cameras[camera_id], camera_id)), 200


@app.post("/api/cameras")
def create_camera():
    cameras = read_cameras()
    payload = request.get_json(silent=True)
    camera, error = validate_camera_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    cameras.append(camera)
    save_cameras(cameras)
    new_id = len(cameras) - 1
    return jsonify(camera_response(camera, new_id)), 201


@app.put("/api/cameras/<int:camera_id>")
def update_camera(camera_id):
    cameras = read_cameras()
    if camera_id < 0 or camera_id >= len(cameras):
        return jsonify({"error": "Camera not found"}), 404

    payload = request.get_json(silent=True)
    camera, error = validate_camera_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    cameras[camera_id] = camera
    save_cameras(cameras)
    return jsonify(camera_response(camera, camera_id)), 200


@app.delete("/api/cameras/<int:camera_id>")
def delete_camera(camera_id):
    cameras = read_cameras()
    if camera_id < 0 or camera_id >= len(cameras):
        return jsonify({"error": "Camera not found"}), 404

    deleted = cameras.pop(camera_id)
    save_cameras(cameras)
    return jsonify({"message": "Camera deleted", "deleted": deleted}), 200


@app.get("/api/service/status")
def get_service_status():
    return jsonify(get_service_status_payload()), 200


@app.post("/api/service/start")
def start_service():
    started, error = start_main_service()
    if not started:
        return jsonify({"error": error, "status": get_service_status_payload()}), 409
    return jsonify({"message": "Service started", "status": get_service_status_payload()}), 200


@app.post("/api/service/stop")
def stop_service():
    stopped, error = stop_main_service()
    if not stopped:
        return jsonify({"error": error, "status": get_service_status_payload()}), 409
    return jsonify({"message": "Service stopped", "status": get_service_status_payload()}), 200


@app.get("/api/service/logs")
def get_service_logs():
    limit_raw = request.args.get("limit", "200")
    try:
        limit = max(1, min(int(limit_raw), 1000))
    except ValueError:
        limit = 200

    logs = list(LOG_BUFFER)[-limit:]
    return jsonify({"logs": logs, "status": get_service_status_payload()}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)