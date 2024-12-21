from abc import ABC, abstractmethod
import os
from bs4 import BeautifulSoup
import requests

from app.services.settings_service import SettingsService

class BaseScraper(ABC):
    def __init__(self, product_url: str):
        self.product_url = product_url

    @abstractmethod
    def get_full_name(self) -> str:
        pass

    @abstractmethod
    def get_in_stock(self) -> bool:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_specifications(self) -> dict:
        pass

    @abstractmethod
    def get_image_urls(self) -> list:
        pass

    def scrape_product_data(self) -> dict:
        """
        Aggregate all the product data by calling the specific methods.
        """
        return {
            "in_stock": self.get_in_stock(),
            "description": self.get_description(),
            "specifications": self.get_specifications(),
            "image_urls": self.get_image_urls(),
            "full_name": self.get_full_name(),
        }

    def _fetch_page_content(self) -> BeautifulSoup:
        """
        Fetch the page content using Crawlbase with fallback for JavaScript API key.
        """
        crawlbase_api_key = SettingsService.get_setting_value("crawlbase_api_key")
        scrapingfish_api_key = SettingsService.get_setting_value("scrapingfish_api_key")

        if not crawlbase_api_key:
            raise ValueError("CRAWLBASE_API_KEY is not set in the environment variables")

        crawlbase_url = f"https://api.crawlbase.com/?token={crawlbase_api_key}&url={self.product_url}"
        response = requests.get(crawlbase_url)

        if response.status_code != 200:
            if not scrapingfish_api_key:
                raise ValueError("SCRAPINGFISH_API_KEY is not set in the environment variables")
            
            scrapingfish_url = f"https://scraping.narf.ai/api/v1/?api_key={scrapingfish_api_key}&url={self.product_url}"
            response = requests.get(scrapingfish_url)
            
        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch page content after fallback. Status Code: {response.status_code}")
        
        return BeautifulSoup(response.content, "html.parser")
