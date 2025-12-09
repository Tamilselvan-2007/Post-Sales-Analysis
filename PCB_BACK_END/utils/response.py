from typing import Any, Dict

from flask import jsonify


def success_response(data: Dict[str, Any], status_code: int = 200):
    body = {"success": True, **data}
    return jsonify(body), status_code


def error_response(message: str, status_code: int = 400, **extra):
    error_payload: Dict[str, Any] = {"success": False, "error": {"message": message}}
    if extra:
        error_payload["error"].update(extra)
    return jsonify(error_payload), status_code
