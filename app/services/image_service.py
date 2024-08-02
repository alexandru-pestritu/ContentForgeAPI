from pathlib import Path
from typing import Optional
import httpx
from app.services.wordpress_service import WordPressService
from app.services.image_metadata_service import ImageMetadataService
import mimetypes

class ImageService:
    def __init__(self, wordpress_service: WordPressService):
        self.wordpress_service = wordpress_service
        self.metadata_service = ImageMetadataService()
        self.image_dir = Path('images')  
        self.image_dir.mkdir(exist_ok=True)

    async def download_image(self, image_url: str) -> Path:
        """
        Download an image from the web and save it locally with the correct extension.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(image_url)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            extension = mimetypes.guess_extension(content_type)
            if not extension:
               extension = ".jpg"  
            temp_image_path = self.image_dir / f"temp_image{extension}"
            with open(temp_image_path, 'wb') as image_file:
                image_file.write(response.content)

        return temp_image_path

    def set_image_metadata(self, image_path: Path, new_file_name: str) -> Path:
        """
        Rename the file with the given name, preserving the extension.
        """
        file_extension = image_path.suffix
        new_image_path = self.image_dir / f"{new_file_name}{file_extension}"
        image_path.rename(new_image_path)
        return new_image_path

    async def upload_image_to_wordpress(self, image_path: Path, file_name: str, alt_text: str) -> Optional[int]:
        """
        Upload the image to WordPress and return its ID.
        """
        image_id = await self.wordpress_service.upload_image(str(image_path), file_name, alt_text=alt_text)
        if image_id:
            self.cleanup_local_images()
        return image_id

    async def process_store_image(self, store_name: str, favicon_url: str) -> Optional[int]:
        """
        Download, process, and upload store image to WordPress.
        """
        try:
            image_filename, alt_text = self.metadata_service.generate_store_metadata(store_name)
            image_path = await self.download_image(favicon_url)
            
            processed_image_path = self.set_image_metadata(image_path, new_file_name=image_filename)
            return await self.upload_image_to_wordpress(processed_image_path, f"{image_filename}.png", alt_text)
        except Exception as e:
            print(f"Error processing store image: {e}")
            return None
        finally:
            self.cleanup_local_images()


    async def process_product_images(self, name: str, seo_keyword: str, full_name: str, image_urls: list) -> list:
        """
        Download, process, and upload product images to WordPress.
        """
        image_ids = []
        try:
            for index, image_url in enumerate(image_urls, start=1):
                image_filename, alt_text = self.metadata_service.generate_product_metadata(name, seo_keyword, full_name, index)
                image_path = await self.download_image(image_url)
                
                processed_image_path = self.set_image_metadata(image_path, new_file_name=image_filename)

                image_id = await self.upload_image_to_wordpress(processed_image_path, image_filename, alt_text)
                if image_id:
                    image_ids.append(image_id)
        except Exception as e:
            print(f"Error processing product images: {e}")
        finally:
            self.cleanup_local_images()

        return image_ids


    def cleanup_local_images(self):
        """
        Clean up locally stored images.
        """
        for image_file in self.image_dir.glob('*'):
            image_file.unlink()