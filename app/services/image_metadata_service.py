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

    def generate_featured_image_metadata(self, article_title: str, seo_keywords: list) -> Tuple[str, str]:
        """
        Generate a filename and alt text for the featured image of an article.
        """
        image_filename = article_title.lower().replace(' ', '-').replace(',', '-').replace('.', '-')

        if len(seo_keywords) >= 1:
            alt_text = " ".join(seo_keywords)
        else:
            alt_text = article_title

        return image_filename, alt_text

    def generate_buyers_guide_image_metadata(self, article_title: str, seo_keywords: list) -> Tuple[str, str]:
        """
        Generate a filename and alt text for the buyers guide image of an article.
        """

        if(seo_keywords[0]):
            image_filename = f"cum aleg {seo_keywords[0]} ghidul cumparatorului".replace(' ', '-').replace(',', '-').replace('.', '-')
        else:
            image_filename = article_title.lower().replace(' ', '-').replace(',', '-').replace('.', '-')

        if len(seo_keywords) >= 2:
            alt_text = f"ghidul cumparatorului pentru {seo_keywords[0]} cum alegi {seo_keywords[1]}"
        else:
            alt_text = article_title

        return image_filename, alt_text