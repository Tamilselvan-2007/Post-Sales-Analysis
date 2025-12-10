# detect_routes.py
import base64
from typing import Callable, List, Union

import cv2
import numpy as np
from flask import Blueprint, current_app, request

from model.detect_burnt import run_burnt_detection
from model.detect_missing import run_missing_detection
from utils.annotate import annotate_image
from utils.response import error_response, success_response


detect_bp = Blueprint("detect", __name__, url_prefix="/detect")

ImageInput = np.ndarray


# replace existing _resolve_image_input + _decode_base64_image + _process_request
def _resolve_image_input(payload: dict) -> ImageInput:
    """
    Support two input styles:
      1) JSON body with "image_base64": "data:image/..;base64,AAAA..."
      2) multipart/form-data with file field "image" (FileStorage)
    """
    # 1) If JSON payload contained base64 string
    image_base64 = payload.get("image_base64") if payload is not None else None
    if image_base64:
        return _decode_base64_image(image_base64)

    # 2) If request had a file upload (multipart/form-data)
    if "image" in request.files:
        file = request.files["image"]
        file_bytes = file.read()
        array = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Uploaded file could not be decoded as an image.")
        return image

    # 3) If client sent raw bytes (rare)
    if request.data:
        array = np.frombuffer(request.data, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is not None:
            return image

    raise ValueError("Request must include image file (form field 'image') or JSON 'image_base64'.")


def _decode_base64_image(image_base64: str) -> np.ndarray:
    if "," in image_base64:
        image_base64 = image_base64.split(",", 1)[1]
    try:
        image_bytes = base64.b64decode(image_base64)
    except (base64.binascii.Error, ValueError) as exc:  # type: ignore[attr-defined]
        raise ValueError("Invalid base64 image data provided.") from exc

    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode base64 image data.")
    return image


def _process_request(handler: Callable[[ImageInput], List[dict]], context: str):
    """
    Robust request processor:
     - Accepts JSON base64 or file uploads
     - Returns JSON (success_response/error_response)
    """
    try:
        # try to parse JSON body first (if any)
        payload = request.get_json(silent=True)
        # If it's None (because form-data was used) pass empty dict so _resolve_image_input checks files
        payload = payload or {}
        image_input = _resolve_image_input(payload)
        detections, processed_image = handler(image_input)
        current_app.logger.info(f"Detections for '{context}': {detections}")
        annotated = annotate_image(processed_image, detections)

        return success_response({
            "image_base64": annotated,
            "detections": detections
        })
        return success_response({"image_base64": image_base64, "detections": detections})
    except ValueError as ve:
        current_app.logger.warning("Validation error on %s detection: %s", context, ve)
        return error_response(str(ve), status_code=400)
    except Exception as exc:  # pylint: disable=broad-except
        current_app.logger.exception("Failed to process %s detection: %s", context, exc)
        # generic 500 here so frontend won't get HTML page — we return JSON with the message
        return error_response("Internal server error during detection. See server logs.", status_code=500)

@detect_bp.route("/missing", methods=["POST"])
def detect_missing():
    return _process_request(run_missing_detection, "missing")


@detect_bp.route("/burnt", methods=["POST"])
def detect_burnt():
    return _process_request(run_burnt_detection, "burnt")


# -------------------------------------------------------------------------
# VOLTAGE MONITORING EXTENSIONS
# -------------------------------------------------------------------------
from flask_socketio import emit

# Global state to control ESP32 loop
# In a production app, use a database or Redis. For this demo, memory is fine.
SYSTEM_STATE = {
    "paused": False,
    "failed_point": None
}

# Expected voltages map (derived from fifth_page.html)
EXPECTED_VOLTAGES = {
    "A1": 0.0, "A2": 0.0, "A3": 0.0, "A4": 0.0, "A5": 0.0, "A6": 0.0, "A7": 0.0, "A8": 0.0, "A9": 0.0,
    "B1": 3.3, "B2": 3.3, "B3": 3.3, "B4": 3.3, "B5": 3.3, "B6": 3.3, "B7": 3.3, "B8": 3.3, "B9": 3.3,
    "C1": 0.0, "C2": 0.0,
    "D1": 3.3, "D2": 3.3, "D3": 3.3,
    "E1": 0.0, "E2": 0.0,
    "F1": 0.0, "F2": 0.0, "F3": 0.0, "F4": 0.0, "F5": 0.0,
    "G1": 3.3, "G2": 3.3, "G3": 3.3, "G4": 3.3, "G5": 3.3, "G6": 3.3,
    "H1": 0.0, "H2": 0.0,
    "I1": 0.0, "I2": 0.0,
    "J1": 0.0, "J2": 0.0,
    "K1": 0.0, "K2": 0.0,
    "L1": 3.3, "L2": 3.3, "L3": 3.3,
    "M1": 3.3, "M2": 3.3, "M3": 3.3,
    "N1": 3.3, "N2": 3.3, "N3": 3.3,
    "O1": 0.0, "O2": 0.0,
    "P1": 0.0, "P2": 0.0,
    "Q1": 0.0, "Q2": 0.0,
    "R1": 3.3, "R2": 3.3,
    "S1": 0.0, "S2": 0.0,
    "T1": 0.0, "T2": 0.0,
    "U1": 3.3, "U2": 3.3, "U3": 3.3,
    "V1": 0.0, "V2": 0.0,
    "W1": 0.0, "W2": 0.0,
    "X1": 0.0, "X2": 0.0,
    "Y1": 0.0, "Y2": 0.0,
    "Z1": 0.0, "Z2": 0.0,
    "RF": 0.0
}

@detect_bp.route("/esp_voltage", methods=["POST"])
def detect_esp_voltage():
    """
    Receives voltage data from ESP32.
    Format: {"point": "A1", "value": 3.28}
    """
    data = request.get_json(silent=True) or {}
    point = data.get("point")
    value = data.get("value")

    if point is None or value is None:
        return error_response("Missing 'point' or 'value'", status_code=400)

    # Determine Status
    expected = EXPECTED_VOLTAGES.get(point)
    status = "OK"
    
    if expected is not None:
        if expected == 0.0:
            # threshold for 0V (adjust if needed)
            if value > 0.25:
                status = "NOT OK"
        else:
            if abs(value - expected) > 0.25:
                status = "NOT OK"
    else:
        status = "UNKNOWN"

    # Emit to UI (broadcast)
    emit("voltage_update", {
        "point": point,
        "value": round(float(value), 3),
        "status": status,
        "expected": expected
    }, namespace="/", broadcast=True)

    # Control Logic
    if status == "NOT OK":
        SYSTEM_STATE["paused"] = True
        SYSTEM_STATE["failed_point"] = point
        return success_response({"command": "PAUSE", "point": point})
    
    return success_response({"command": "CONTINUE"})


@detect_bp.route("/check_resume", methods=["GET"])
def check_resume():
    """
    Endpoint for ESP32 to poll when paused.
    Returns {"command": "RESUME"} if technician clicked Recheck.
    """
    if not SYSTEM_STATE["paused"]:
        # Not paused => ESP32 can resume/continue
        return success_response({"command": "RESUME"})
    # Still paused => ask ESP32 to wait
    return success_response({"command": "WAIT"})


@detect_bp.route("/resume_loop", methods=["POST"])
def resume_loop():
    """
    Called by Frontend when 'Recheck' is clicked.
    """
    SYSTEM_STATE["paused"] = False
    SYSTEM_STATE["failed_point"] = None
    return success_response({"status": "Resumed"})

# Reset flag so UI can force ESP32 back to A1
reset_flag = False

@detect_bp.route('/reset_sequence', methods=['POST'])
def reset_sequence():
    global reset_flag
    reset_flag = True
    return {"success": True}

@detect_bp.route('/check_reset', methods=['GET'])
def check_reset():
    global reset_flag
    if reset_flag:
        reset_flag = False
        return {"reset": True}
    return {"reset": False}
