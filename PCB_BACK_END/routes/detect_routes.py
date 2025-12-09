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


def _resolve_image_input(payload: dict) -> ImageInput:
    image_base64 = payload.get("image_base64")
    if image_base64:
        return _decode_base64_image(image_base64)

    raise ValueError("Request JSON must include 'image_base64'.")


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
    try:
        payload = request.get_json(silent=True) or {}
        image_input = _resolve_image_input(payload)
        detections = handler(image_input)
        current_app.logger.info(f"Detections for '{context}': {detections}")
        image_base64 = annotate_image(image_input, detections)
        return success_response({"image_base64": image_base64, "detections": detections})
    except Exception as exc:  # pylint: disable=broad-except
        current_app.logger.exception("Failed to process %s detection: %s", context, exc)
        return error_response(str(exc), status_code=400)


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
