import os
import uuid
from PIL import Image
from datetime import datetime
from typing import Tuple

STORAGE_DIR = os.getenv('IMAGE_STORAGE_DIR', os.path.join(os.getcwd(), '..', '..', '..', 'storage', 'images'))
os.makedirs(STORAGE_DIR, exist_ok=True)

MAX_WIDTH = 1920
THUMB_SIZE = (400, 300)


def save_image_file(upload_file) -> Tuple[str, str]:
    """Save UploadFile to local storage, produce a thumbnail, and return (filename, thumb_filename)"""
    ext = os.path.splitext(upload_file.filename)[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(STORAGE_DIR, filename)

    with open(path, 'wb') as f:
        f.write(upload_file.file.read())

    # create thumbnail
    thumb_name = f"thumb_{uuid.uuid4().hex}{ext}"
    thumb_path = os.path.join(STORAGE_DIR, thumb_name)
    try:
        img = Image.open(path)
        img.thumbnail(THUMB_SIZE)
        img.save(thumb_path)
    except Exception:
        thumb_name = filename
        thumb_path = path

    # Return filenames only; serving endpoint will map to actual path
    return filename, thumb_name


def delete_image_file(filename: str) -> bool:
    """Delete image file and thumbnail from storage. Returns True if at least one file removed."""
    removed = False
    path = os.path.join(STORAGE_DIR, filename)
    thumb = os.path.join(STORAGE_DIR, f"thumb_{filename}")
    try:
        if os.path.exists(path):
            os.remove(path)
            removed = True
    except Exception:
        pass
    try:
        if os.path.exists(thumb):
            os.remove(thumb)
            removed = True
    except Exception:
        pass
    return removed
