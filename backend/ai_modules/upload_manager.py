from fastapi import UploadFile, HTTPException
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import mimetypes
from pydantic import BaseModel

class UploadConfig(BaseModel):
    bucket_name: str
    allowed_types: list[str]
    max_file_size: int  # in bytes
    expiration_hours: int = 24

class UploadResponse(BaseModel):
    file_url: str
    file_name: str
    content_type: str
    size: int
    expires_at: datetime

class UploadManager:
    def __init__(self, config: UploadConfig):
        self.config = config
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(config.bucket_name)

    async def upload_file(self, file: UploadFile) -> UploadResponse:
        """Upload a file to Google Cloud Storage."""
        try:
            # Validate file type
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            if content_type not in self.config.allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {content_type} not allowed. Allowed types: {self.config.allowed_types}"
                )

            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create blob and upload
            blob = self.bucket.blob(unique_filename)
            blob.content_type = content_type
            
            # Upload file
            content = await file.read()
            if len(content) > self.config.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {self.config.max_file_size} bytes"
                )
            
            blob.upload_from_string(content, content_type=content_type)
            
            # Generate signed URL
            expires_at = datetime.utcnow() + timedelta(hours=self.config.expiration_hours)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expires_at,
                method="GET"
            )
            
            return UploadResponse(
                file_url=signed_url,
                file_name=unique_filename,
                content_type=content_type,
                size=len(content),
                expires_at=expires_at
            )
            
        except GoogleCloudError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to Google Cloud Storage: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}"
            )

    async def delete_file(self, file_name: str) -> None:
        """Delete a file from Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_name)
            blob.delete()
        except GoogleCloudError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file from Google Cloud Storage: {str(e)}"
            )

    async def get_file_metadata(self, file_name: str) -> Dict[str, Any]:
        """Get metadata for a file in Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_name)
            blob.reload()  # Refresh metadata
            
            return {
                "name": blob.name,
                "content_type": blob.content_type,
                "size": blob.size,
                "created": blob.time_created,
                "updated": blob.updated,
                "md5_hash": blob.md5_hash
            }
        except GoogleCloudError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get file metadata from Google Cloud Storage: {str(e)}"
            )

    async def generate_upload_url(self, file_name: str, content_type: str) -> Dict[str, Any]:
        """Generate a signed URL for direct upload to Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_name)
            blob.content_type = content_type
            
            expires_at = datetime.utcnow() + timedelta(hours=self.config.expiration_hours)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expires_at,
                method="PUT",
                content_type=content_type
            )
            
            return {
                "upload_url": signed_url,
                "file_name": file_name,
                "content_type": content_type,
                "expires_at": expires_at
            }
        except GoogleCloudError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate upload URL: {str(e)}"
            ) 