from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from ...services.images import STORAGE_DIR

router = APIRouter()

@router.get('/images/{filename}')
def serve_image(filename: str):
    # Security: prevent path traversal
    if '..' in filename or filename.startswith('/'):
        raise HTTPException(status_code=400, detail='Invalid filename')
    path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Image not found')
    return FileResponse(path, media_type='image/*')
