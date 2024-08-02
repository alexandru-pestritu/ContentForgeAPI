from typing import Tuple

class ImageMetadataService:
    """
    Service for generating image filenames and alt text optimized for SEO.
    """

    def generate_store_metadata(self, store_name: str) -> Tuple[str, str]:
        """
        Generate a filename and alt text for a store based on the store name.
        """
        image_filename = store_name.lower().replace(' ', '-').replace(',', '-').replace('.', '-')
        alt_text = f"favicon magazin online {store_name}"

        return image_filename, alt_text

    def generate_product_metadata(self, name: str, seo_keyword: str, full_name: str, index: int) -> Tuple[str, str]:
        """
        Generate a filename and alt text for a product based on the product name, SEO keyword, and full name.
        """
        image_filename = f"{name.lower().replace(' ', '-').replace(',', '')}-{seo_keyword.lower().replace(' ', '-').replace(',', '')}-{str(index).zfill(2)}.jpg"
        alt_text = full_name

        return image_filename, alt_text
