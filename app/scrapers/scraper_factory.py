from app.scrapers.base_scraper import BaseScraper
from app.scrapers.emag_scraper import EmagScraper

def scraper_factory(product_url: str) -> BaseScraper:
    """
    Factory function to create the appropriate scraper based on the product URL.
    """
    if "emag.ro" in product_url:
        return EmagScraper(product_url)
    
    else:
        raise ValueError(f"No scraper available for the provided URL: {product_url}")
