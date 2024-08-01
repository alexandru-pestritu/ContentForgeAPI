import os
import httpx
from pathlib import Path
from typing import Optional
from PIL import Image 
from app.services.wordpress_service import WordPressService

class ImageService:
    def __init__(self, wordpress_service: WordPressService):
        self.wordpress_service = wordpress_service
        self.image_dir = Path('images')  
        self.image_dir.mkdir(exist_ok=True)

    async def download_image(self, image_url: str) -> Path:
        """
        Download an image from the web and save it locally as a PNG file.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            
            # Save the image as PNG
            temp_image_path = self.image_dir / "temp_image.png"
            with open(temp_image_path, 'wb') as image_file:
                image_file.write(response.content)

        return temp_image_path

    def set_image_metadata(self, image_path: Path, new_file_name: str, alt_text: str = None) -> Path:
        """
        Set metadata like alt text or captions on an image and rename the file.
        """
        new_image_path = self.image_dir / f"{new_file_name}.png"
        image_path.rename(new_image_path)
        return new_image_path

    async def upload_image_to_wordpress(self, image_path: Path, file_name: str, alt_text: str) -> Optional[int]:
        """
        Upload the image to WordPress and return its ID.
        """
        image_id = await self.wordpress_service.upload_image(str(image_path), f"{file_name}.png", alt_text=alt_text)
        if(image_id):
            self.cleanup_local_images()
        return image_id

    async def get_image_info_from_wordpress(self, image_id: int) -> dict:
        """
        Fetch metadata about an image from WordPress using its ID.
        """
        image_info = await self.wordpress_service.get_image_info(image_id)
        return image_info

    def cleanup_local_images(self):
        """
        Clean up locally stored images.
        """
        for image_file in self.image_dir.glob('*'):
            image_file.unlink()
