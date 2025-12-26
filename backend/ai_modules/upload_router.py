from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from .upload_manager import UploadManager, UploadConfig
from typing import Dict, Any
import os

router = APIRouter()

# Configuration
UPLOAD_CONFIG = UploadConfig(
    bucket_name=os.getenv("GCLOUD_BUCKET_NAME", "your-bucket-name"),
    allowed_types=[
        "image/jpeg",
        "image/png",
        "image/gif",
        "video/mp4",
        "video/quicktime",
        "application/pdf",
        "text/plain",
        "application/json"
    ],
    max_file_size=100 * 1024 * 1024,  # 100MB
    expiration_hours=24
)

# Initialize upload manager
upload_manager = UploadManager(UPLOAD_CONFIG)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a file to Google Cloud Storage."""
    result = await upload_manager.upload_file(file)
    return result.dict()

@router.delete("/files/{file_name}")
async def delete_file(file_name: str) -> Dict[str, str]:
    """Delete a file from Google Cloud Storage."""
    await upload_manager.delete_file(file_name)
    return {"message": f"File {file_name} deleted successfully"}

@router.get("/files/{file_name}/metadata")
async def get_file_metadata(file_name: str) -> Dict[str, Any]:
    """Get metadata for a file in Google Cloud Storage."""
    return await upload_manager.get_file_metadata(file_name)

@router.post("/generate-upload-url")
async def generate_upload_url(file_name: str, content_type: str) -> Dict[str, Any]:
    """Generate a signed URL for direct upload to Google Cloud Storage."""
    return await upload_manager.generate_upload_url(file_name, content_type) 