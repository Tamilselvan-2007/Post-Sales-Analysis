from pathlib import Path
from typing import Optional
from ultralytics import YOLO

from .config import (
    CONFIDENCE_THRESHOLD,
    MODEL_BURNT,
    MODEL_MISSING,
    ensure_model_path
)

missing_model: Optional[YOLO] = None
burnt_model: Optional[YOLO] = None


def _load_model(model_path: Path) -> YOLO:
    """Load YOLO model with confidence threshold."""
    model_path = ensure_model_path(model_path)
    model = YOLO(str(model_path))        # EXACT path YOLO accepts
    model.overrides["conf"] = CONFIDENCE_THRESHOLD
    return model


def load_models() -> None:
    """Load both models once globally."""
    global missing_model, burnt_model

    if missing_model is None:
        print(f"🔄 Loading missing model from: {MODEL_MISSING}")
        missing_model = _load_model(MODEL_MISSING)
        print("✅ Missing model loaded successfully!")

    if burnt_model is None:
        print(f"🔄 Loading burnt model from: {MODEL_BURNT}")
        burnt_model = _load_model(MODEL_BURNT)
        print("✅ Burnt model loaded successfully!")
