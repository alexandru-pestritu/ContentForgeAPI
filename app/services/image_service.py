from pathlib import Path
from typing import Optional
import uuid
import httpx
from app.services.wordpress_service import WordPressService
from app.services.image_metadata_service import ImageMetadataService
import mimetypes
from PIL import Image

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
            temp_filename = f"{uuid.uuid4()}{extension}"
            temp_image_path = self.image_dir / temp_filename
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

    def resize_image(self, image_path: Path, target_width: int, target_height: int) -> Path:
        """
        Resize the image to the specified dimensions while maintaining aspect ratio.
        The image will be scaled to fill the target dimensions completely, and any excess will be cropped.
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

    async def upload_resized_image_to_wordpress(self, image_url: str, file_name: str, alt_text: str, target_width: int, target_height: int) -> Optional[int]:
        """
        Download, resize, and upload an image to WordPress.
        """
        try:
            image_path = await self.download_image(image_url)
            resized_image_path = self.resize_image(image_path, target_width, target_height)
            image_id = await self.wordpress_service.upload_image(str(resized_image_path), file_name, alt_text=alt_text)
            return image_id
        
        except Exception as e:
            print(f"Error processing and uploading image: {e}")
            return None
        finally:
            self.cleanup_local_images()

    async def process_featured_image(self, article_title: str, seo_keywords: list, image_url: str, target_width: int, target_height: int) -> Optional[int]:
        """
        Download, process, and upload the featured image for an article to WordPress.
        """
        try:
            image_filename, alt_text = self.metadata_service.generate_featured_image_metadata(article_title, seo_keywords)
            image_id = await self.upload_resized_image_to_wordpress(image_url, f"{image_filename}.jpg", alt_text, target_width, target_height)
            return image_id
        except Exception as e:
            print(f"Error processing featured image: {e}")
            return None

    async def process_buyers_guide_image(self, article_title: str, seo_keywords: list, image_url: str, target_width: int, target_height: int) -> Optional[int]:
        """
        Download, process, and upload the buyers guide image for an article to WordPress.
        """
        try:
            image_filename, alt_text = self.metadata_service.generate_buyers_guide_image_metadata(article_title, seo_keywords)
            image_id = await self.upload_resized_image_to_wordpress(image_url, f"{image_filename}.jpg", alt_text, target_width, target_height)
            return image_id
        except Exception as e:
            print(f"Error processing buyers guide image: {e}")
            return None

    def cleanup_local_images(self):
        """
        Clean up locally stored images.
        """
        for image_file in self.image_dir.glob('*'):
            image_file.unlink()