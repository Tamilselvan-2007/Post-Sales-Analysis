from pathlib import Path

# Absolute directory of model folder: PCB_BACK_END/model/
BASE_DIR = Path(__file__).resolve().parent

# Absolute paths to model files
MODEL_MISSING = (BASE_DIR / "missing.pt").resolve()
MODEL_BURNT   = (BASE_DIR / "burnt.pt").resolve()

CONFIDENCE_THRESHOLD = 0.5


def ensure_model_path(path: Path) -> Path:
    """
    Accepts a FULL Path object.
    Ensures the file exists, else throws clear error.
    """
    if not path.exists():
        raise FileNotFoundError(f"❌ Model file not found at: {path}")
    return path
