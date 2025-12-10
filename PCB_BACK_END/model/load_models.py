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
    """Load YOLO model with confidence threshold, and prepare backend on CPU."""
    model_path = ensure_model_path(model_path)
    model = YOLO(str(model_path))        # EXACT path YOLO accepts
    # set default confidence and device override
    model.overrides["conf"] = CONFIDENCE_THRESHOLD
    # Disable fusion (saves 150–300 MB RAM)
    model.fuse = lambda *args, **kwargs: model
    model.overrides["device"] = "cpu"
    # ensure backend model is on cpu and in eval mode to avoid re-fusing during request handling
    try:
        # ultralytics wrapper exposes .model (nn.Module) for lower-level ops
        if hasattr(model, "model") and getattr(model, "model") is not None:
            model.model.to("cpu")
            model.model.eval()
    except Exception:
        # don't fail load if the low-level attributes differ across ultralytics versions
        pass
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
