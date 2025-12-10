from flask import Blueprint, jsonify
import sys
import os

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/health')
def health():
    """Health check endpoint for deployment monitoring"""
    try:
        from model.load_models import missing_model, burnt_model
        models_ready = (missing_model is not None) and (burnt_model is not None)
        
        return jsonify({
            "status": "healthy" if models_ready else "degraded",
            "models_loaded": models_ready,
            "message": "Application is running" if models_ready else "Models not loaded"
        }), 200 if models_ready else 503
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "models_loaded": False,
            "error": str(e)
        }), 503

@debug_bp.route('/status')
def status():
    status_info = {
        "python_version": sys.version,
        "opencv": "Not installed",
        "numpy": "Not installed",
        "torch": "Not installed",
        "ultralytics": "Not installed",
        "models_loaded": False
    }

    try:
        import cv2
        status_info["opencv"] = cv2.__version__
    except ImportError as e:
        status_info["opencv"] = str(e)

    try:
        import numpy
        status_info["numpy"] = numpy.__version__
    except ImportError as e:
        status_info["numpy"] = str(e)
        
    try:
        import torch
        status_info["torch"] = torch.__version__
    except ImportError as e:
        status_info["torch"] = str(e)

    try:
        import ultralytics
        status_info["ultralytics"] = ultralytics.__version__
    except ImportError as e:
        status_info["ultralytics"] = str(e)

    try:
        from model.load_models import missing_model, burnt_model
        status_info["models_loaded"] = (missing_model is not None) and (burnt_model is not None)
    except Exception as e:
        status_info["models_loaded_error"] = str(e)

    return jsonify(status_info)
