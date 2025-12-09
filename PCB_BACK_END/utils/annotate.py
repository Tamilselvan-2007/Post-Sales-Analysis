import base64
from typing import Dict, List, Union

import cv2
import numpy as np


COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 165, 0),
]
FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_COLOR = (255, 255, 255)
LABEL_BG_ALPHA = 0.5
BBOX_THICKNESS = 1
# Constant for the length of the callout line
CALLOUT_LENGTH = 30


ImageInput = Union[str, np.ndarray]


def annotate_image(image_input: ImageInput, detections: List[Dict]) -> str:
    if isinstance(image_input, np.ndarray):
        image = image_input.copy()
    else:
        image = cv2.imread(image_input)
        if image is None:
            raise FileNotFoundError(f"Unable to load image from path: {image_input}")

    # A simple heuristic to process detections from top to bottom can help
    # with label placement in some scenarios.
    detections.sort(key=lambda d: d["bbox"][1])

    for index, detection in enumerate(detections):
        _draw_detection(image, detection, index)

    success, buffer = cv2.imencode(".jpg", image)
    if not success:
        raise RuntimeError("Failed to encode annotated image to JPEG format.")

    base64_bytes = base64.b64encode(buffer.tobytes())
    return base64_bytes.decode("utf-8")


def _draw_detection(image: np.ndarray, detection: Dict, fallback_index: int) -> None:
    x1, y1, x2, y2 = [int(coord) for coord in detection["bbox"]]
    label = detection.get("label", "object")
    confidence = detection.get("confidence", 0.0)
    label_id = detection.get("label_id")
    color_index = label_id if isinstance(label_id, int) else fallback_index
    color = COLORS[color_index % len(COLORS)]
    caption = f"{label} {confidence:.2f}"

    # 1. Draw the bounding box
    cv2.rectangle(image, (x1, y1), (x2, y2), color, BBOX_THICKNESS)

    # 2. Calculate anchor points for the callout
    # Start point: center of the right edge of the bbox
    bbox_centerY = int((y1 + y2) / 2)
    bbox_anchor = (x2, bbox_centerY)
    # End point: a fixed distance to the right
    label_anchor = (x2 + CALLOUT_LENGTH, bbox_centerY)

    # 3. Check if label fits on the right. If not, try placing it to the left.
    h, w = image.shape[:2]
    FONT_SCALE, FONT_THICKNESS = _get_dynamic_font(image)
    text_size, _ = cv2.getTextSize(caption, FONT, FONT_SCALE, FONT_THICKNESS)
    text_width = text_size[0]
    padding = 6

    if label_anchor[0] + text_width + (2 * padding) > w:
        # Place to the left instead
        bbox_anchor = (x1, bbox_centerY)
        label_anchor = (x1 - CALLOUT_LENGTH, bbox_centerY)

    # 4. Draw the callout line
    # Ensure the line doesn't go outside the image
    label_anchor_clamped = (max(0, min(w, label_anchor[0])), label_anchor[1])
    cv2.line(image, bbox_anchor, label_anchor_clamped, color, BBOX_THICKNESS)

    # 5. Draw the label at the new anchor point
    is_left = label_anchor[0] < bbox_anchor[0]
    _draw_label(image, caption, label_anchor, color, is_left=is_left)


def _get_dynamic_font(image: np.ndarray):
    h, w = image.shape[:2]
    scale = max(min(w, h) / 1200, 0.5)   # Keeps font medium across all images
    thickness = max(int(scale * 2), 1)
    return scale, thickness

def _draw_label(image: np.ndarray, text: str, origin: tuple[int, int], bg_color: tuple[int, int, int], is_left: bool = False) -> None:
    FONT_SCALE, FONT_THICKNESS = _get_dynamic_font(image)

    text_size, baseline = cv2.getTextSize(text, FONT, FONT_SCALE, FONT_THICKNESS)
    text_width, text_height = text_size
    
    padding = 6
    
    # Calculate the label box coordinates, centered vertically on the origin.
    # The 'origin' is the end of the callout line.
    box_y1 = origin[1] - int(text_height / 2) - padding
    box_y2 = origin[1] + int(text_height / 2) + padding + baseline

    if is_left:
        # Label box is to the left of the origin
        box_x1 = origin[0] - text_width - (2 * padding)
        box_x2 = origin[0]
    else:
        # Label box is to the right of the origin
        box_x1 = origin[0]
        box_x2 = origin[0] + text_width + (2 * padding)

    # Clamp to image boundaries
    h, w = image.shape[:2]
    box_x1 = max(0, box_x1)
    box_y1 = max(0, box_y1)
    box_x2 = min(w, box_x2)
    box_y2 = min(h, box_y2)

    top_left = (box_x1, box_y1)
    bottom_right = (box_x2, box_y2)

    # Draw semi-transparent background
    overlay = image.copy()
    cv2.rectangle(overlay, top_left, bottom_right, bg_color, thickness=-1)

    if box_x2 > box_x1 and box_y2 > box_y1:
        image[box_y1:box_y2, box_x1:box_x2] = cv2.addWeighted(
            overlay[box_y1:box_y2, box_x1:box_x2],
            LABEL_BG_ALPHA,
            image[box_y1:box_y2, box_x1:box_x2],
            1 - LABEL_BG_ALPHA,
            0,
        )

        # Draw the text
        text_origin_x = box_x1 + padding
        # Vertically center the text
        text_origin_y = origin[1] + int(text_height / 2)
        
        cv2.putText(
            image,
            text,
            (text_origin_x, text_origin_y),
            FONT,
            FONT_SCALE,
            TEXT_COLOR,
            FONT_THICKNESS,
            cv2.LINE_AA,
        )