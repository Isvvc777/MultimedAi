import asyncio
import io
from minio import Minio
from minio.error import S3Error
from app.config import settings

class MinIOFileHandler:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_use_ssl
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as err:
            print(f"MinIO Initialization Error: {err}")

    async def upload_file(self, object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Uploads a file (bytes) to MinIO asynchronously.
        Returns the object name (key).
        """
        def _upload():
            data_stream = io.BytesIO(file_data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(file_data),
                content_type=content_type
            )
            return object_name
            
        return await asyncio.to_thread(_upload)

    async def download_file(self, object_name: str) -> bytes:
        """
        Downloads a file from MinIO asynchronously.
        Returns the raw bytes.
        """
        def _download():
            response = self.client.get_object(self.bucket_name, object_name)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
                
        return await asyncio.to_thread(_download)

    async def get_presigned_url(self, object_name: str, expires_timedelta=None) -> str:
        """
        Generates a temporary URL for direct access to the file.
        """
        def _get_url():
            return self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires_timedelta
            )
            
        return await asyncio.to_thread(_get_url)

file_handler = MinIOFileHandler()
