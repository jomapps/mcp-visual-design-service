"""Asset service for PayloadCMS integration."""

import asyncio
import io
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
from PIL import Image

from ..config import Settings


class AssetService:
    """Service for managing assets in PayloadCMS."""

    def __init__(self, settings: Settings) -> None:
        """Initialize asset service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.payloadcms_api_url
        self.api_key = settings.payloadcms_api_key
        self.timeout = 30

    async def upload_image(
        self,
        image_url: str,
        filename: str,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Upload image to PayloadCMS Media collection.

        Args:
            image_url: URL of the image to upload
            filename: Filename for the uploaded asset
            project_id: Optional project ID to associate with
            metadata: Additional metadata to attach

        Returns:
            PayloadCMS media record

        Raises:
            Exception: If upload fails
        """
        try:
            # Download the image
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content

            # Get image dimensions and format
            image_info = self._get_image_info(image_data)

            # Prepare metadata
            upload_metadata = {
                "visual": {
                    "source_url": image_url,
                    "width": image_info["width"],
                    "height": image_info["height"],
                    "format": image_info["format"],
                    "file_size": len(image_data),
                    **(metadata or {}),
                }
            }

            if project_id:
                upload_metadata["project_id"] = project_id

            # Upload to PayloadCMS
            return await self._upload_to_cms(
                image_data,
                filename,
                upload_metadata,
            )

        except Exception as e:
            raise Exception(f"Failed to upload image to PayloadCMS: {str(e)}")

    def _get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """Get image information from binary data.

        Args:
            image_data: Image binary data

        Returns:
            Dictionary with image info
        """
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format.lower() if img.format else "png",
                }
        except Exception:
            # Return defaults if image analysis fails
            return {
                "width": 0,
                "height": 0,
                "format": "png",
            }

    async def _upload_to_cms(
        self,
        image_data: bytes,
        filename: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Upload image data to PayloadCMS.

        Args:
            image_data: Image binary data
            filename: Filename for the asset
            metadata: Metadata to attach

        Returns:
            PayloadCMS response data
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"API-Key {self.api_key}"

            # Prepare multipart upload
            files = {
                "file": (filename, image_data, "image/png"),
            }
            
            # Add metadata as form data
            data = {}
            for key, value in metadata.items():
                if isinstance(value, dict):
                    # Handle nested objects
                    for nested_key, nested_value in value.items():
                        data[f"{key}.{nested_key}"] = str(nested_value)
                else:
                    data[key] = str(value)

            response = await client.post(
                f"{self.base_url}/media",
                headers=headers,
                files=files,
                data=data,
            )

            response.raise_for_status()
            return response.json()

    async def get_media_by_id(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get media record by ID.

        Args:
            media_id: Media record ID

        Returns:
            Media record or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"API-Key {self.api_key}"

                response = await client.get(
                    f"{self.base_url}/media/{media_id}",
                    headers=headers,
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception:
            return None

    async def update_media_metadata(
        self,
        media_id: str,
        metadata: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Update media record metadata.

        Args:
            media_id: Media record ID
            metadata: Metadata to update

        Returns:
            Updated media record or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Content-Type": "application/json",
                }
                if self.api_key:
                    headers["Authorization"] = f"API-Key {self.api_key}"

                response = await client.patch(
                    f"{self.base_url}/media/{media_id}",
                    headers=headers,
                    json=metadata,
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception:
            return None

    async def check_connection(self) -> bool:
        """Check if PayloadCMS is accessible.

        Returns:
            True if accessible, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"API-Key {self.api_key}"

                response = await client.get(
                    f"{self.base_url}/media",
                    headers=headers,
                    params={"limit": 1},  # Just check accessibility
                )

                return response.status_code in [200, 401]  # 401 means accessible but auth issue

        except Exception:
            return False