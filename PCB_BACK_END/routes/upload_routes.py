import base64
from typing import Tuple

from flask import Blueprint, request
from werkzeug.datastructures import FileStorage

from utils.response import error_response, success_response


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}


upload_bp = Blueprint("upload", __name__)


def _validate_file(file_storage: FileStorage) -> Tuple[bool, str]:
    if file_storage.filename == "":
        return False, "Empty filename provided."

    if not _is_allowed_extension(file_storage.filename):
        return False, "Unsupported file type. Allowed types: png, jpg, jpeg, bmp."

    return True, ""


def _is_allowed_extension(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return error_response("No file part in the request.", status_code=400)

    file_storage = request.files["file"]
    is_valid, error_msg = _validate_file(file_storage)
    if not is_valid:
        return error_response(error_msg, status_code=400)

    # Read file bytes and convert to base64
    file_bytes = file_storage.read()
    base64_bytes = base64.b64encode(file_bytes)
    base64_string = base64_bytes.decode("utf-8")
    
    # Prefix with data URI scheme if needed, but usually just the base64 string is enough 
    # or the frontend expects the full data URI. 
    # The requirement says: { "image_base64": "<BASE64_STRING>" }
    # I will return the raw base64 string, and let the frontend handle the data URI prefix if needed,
    # OR I can prepend it. 
    # Looking at the requirement: "Modify /upload to return base64 instead of file_path"
    # And "Modify detect_routes.py ... Only support JSON with: { "image_base64": "data:image/jpeg;base64,......" }"
    # So the detect route expects the data URI prefix.
    # The frontend upload flow: "FileReader -> base64 -> send to detectionEndpoint".
    # Wait, the requirement says: "Modify /upload to return base64 ... Return JSON: { "success": true, "image_base64": "<BASE64_STRING>" }"
    # And "Frontend must behave like this: UPLOAD MODE: FileReader -> base64 -> send to /detect/*"
    # AND "No more /upload route calls, so delete the code calling "/upload"."
    #
    # Wait, if the frontend is NOT calling /upload anymore, why am I refactoring it?
    # Requirement 2: "Modify /upload to return base64 instead of file_path"
    # Requirement 5: "No more /upload route calls, so delete the code calling "/upload"."
    #
    # This seems contradictory or I might be misinterpreting.
    # "Modify /upload to return base64" implies it might still be used.
    # But "No more /upload route calls" implies it won't.
    # Maybe the /upload route is kept for other purposes or legacy support? 
    # Or maybe the user meant "If /upload IS called, it should return base64".
    #
    # However, Requirement 5 says "Update third_page.html JS ... No more /upload route calls".
    # So the frontend won't use it.
    # But Requirement 2 explicitly asks to "Modify /upload".
    # I will modify it as requested to be safe.
    #
    # Regarding the format: `base64.b64encode` returns bytes, I decode to string.
    # I'll construct a data URI just in case, or just return the raw string.
    # The detect route expects `data:image/...`.
    # If I return just the base64 string here, it might be fine if the caller knows how to handle it.
    # I'll stick to returning the base64 string.
    
    # Actually, let's look at the detect route requirement again.
    # "Only support JSON with: { "image_base64": "data:image/jpeg;base64,......" }"
    # So the detect route expects the prefix.
    # If /upload is used, it should probably return something compatible or just the raw base64.
    # I'll return the raw base64 for now, as that's the standard interpretation of "base64 string".
    
    return success_response({"image_base64": base64_string})
