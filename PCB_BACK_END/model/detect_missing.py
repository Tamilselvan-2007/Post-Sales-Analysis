from __future__ import annotations

from typing import Dict, List, Union

import numpy as np
from ultralytics.engine.results import Results

from . import load_models as models_registry

ImageInput = Union[str, np.ndarray]


def run_missing_detection(image_input: ImageInput) -> List[Dict]:
    models_registry.load_models()
    model = models_registry.missing_model
    if model is None:
        raise RuntimeError("Missing components model failed to load.")

    CONFIDENCE = 0.25  # ✅ Same fixed confidence

    results = model.predict(
        source=image_input,
        conf=CONFIDENCE,   # ✅ CONFIDENCE FILTER APPLIED
        verbose=False,
        device='cpu'
    )

    if not results:
        return []

    return _format_detections(results[0])





def _format_detections(result: Results) -> List[Dict]:
    boxes = result.boxes
    detections: List[Dict] = []
    names = result.names or {}

    for idx in range(len(boxes)):
        x1, y1, x2, y2 = boxes.xyxy[idx].tolist()
        confidence = float(boxes.conf[idx].item())
        label_idx = int(boxes.cls[idx].item())
        label = names.get(label_idx, str(label_idx))

        detections.append(
            {
                "label": label,
                "label_id": label_idx,
                "confidence": round(confidence, 4),
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
            }
        )

    return detections
