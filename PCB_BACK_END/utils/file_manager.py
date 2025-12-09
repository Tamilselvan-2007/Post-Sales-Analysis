import os
from typing import Tuple

from flask import current_app


def get_upload_absolute_path(relative_path: str) -> str:
    """
    DEPRECATED: File storage is disabled.
    """
    raise NotImplementedError("File storage is disabled. Use in-memory processing.")


def get_upload_paths(filename: str) -> Tuple[str, str]:
    """
    DEPRECATED: File storage is disabled.
    """
    raise NotImplementedError("File storage is disabled. Use in-memory processing.")
