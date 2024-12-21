from pathlib import Path
from typing import Optional
import uuid
import mimetypes
from PIL import Image
import httpx
from app.services.wordpress_service import WordPressService
from app.services.image_metadata_service import ImageMetadataService
from app.services.settings_service import SettingsService
from app.services.placeholder_service import PlaceholderService

class ImageService:
    def __init__(self, wordpress_service: WordPressService):
        self.wordpress_service = wordpress_service  
        self.placeholder_service = PlaceholderService()
        self.metadata_service = ImageMetadataService(self.placeholder_service)
        self.image_dir = Path('images')
        self.image_dir.mkdir(exist_ok=True)

    async def process_image(
        self, entity_type: str, entity: object, image_url: str, output_json: Optional[dict] = None
    ) -> Optional[int]:
        """
        Process an image for a given entity type (e.g., store, product, article).
        """
        try:
            width = SettingsService.get_setting_value(f"{entity_type}_image_width")
            height = SettingsService.get_setting_value(f"{entity_type}_image_height")

            file_name, alt_text = self.metadata_service.generate_metadata(entity_type, entity, output_json)

            image_path = await self.download_image(image_url)
            renamed_image_path = self.rename_image(image_path, file_name)

            resized_image_path = self.resize_image(renamed_image_path, width, height)

            image_id = await self.upload_image_to_wordpress(resized_image_path, file_name, alt_text)
            return image_id

        except Exception as e:
            print(f"Error processing image for {entity_type}: {e}")
            return None
        finally:
            self.cleanup_local_images()

    async def download_image(self, image_url: str) -> Path:
        """
        Download an image from the web and save it locally.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(image_url)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            extension = mimetypes.guess_extension(content_type) or ".jpg"

            temp_filename = f"{uuid.uuid4()}{extension}"
            temp_image_path = self.image_dir / temp_filename
            with open(temp_image_path, 'wb') as image_file:
                image_file.write(response.content)

        return temp_image_path

    def rename_image(self, image_path: Path, new_file_name: str) -> Path:
        """
        Rename the image file to the specified file name.
        """
        new_image_path = image_path.parent / f"{new_file_name}{image_path.suffix}"
        image_path.rename(new_image_path)
        return new_image_path

    def resize_image(self, image_path: Path, target_width: int, target_height: int) -> Path:
        """
        Resize the image to the specified dimensions while maintaining aspect ratio.
        """
        with Image.open(image_path) as img:
            original_ratio = img.width / img.height
            target_ratio = target_width / target_height

            if original_ratio > target_ratio:
                new_height = target_height
                new_width = int(target_height * original_ratio)
            else:
                new_width = target_width
                new_height = int(target_width / original_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = left + target_width
            bottom = top + target_height

            img = img.crop((left, top, right, bottom))

            resized_image_path = image_path.parent / f"resized_{image_path.name}"
            img.save(resized_image_path)

        return resized_image_path

    async def upload_image_to_wordpress(self, image_path: Path, file_name: str, alt_text: str) -> Optional[int]:
        """
        Upload the image to WordPress and return its ID.
        """
        try:
            image_id = await self.wordpress_service.upload_image(str(image_path), file_name, alt_text=alt_text)
            return image_id
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None

    def cleanup_local_images(self):
        """
        Clean up locally stored images.
        """
        for image_file in self.image_dir.glob('*'):
            image_file.unlink()
