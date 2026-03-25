# api.py
from flask import Flask, jsonify, render_template, request
from config import load_cameras, save_cameras

app = Flask(__name__)

REQUIRED_FIELDS = ("name", "link", "desc")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)