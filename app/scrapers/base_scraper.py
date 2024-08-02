from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()

CRAWLBASE_API_KEY = os.getenv("CRAWLBASE_API_KEY")

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
        Fetch the page content using Crawlbase.
        """
        if not CRAWLBASE_API_KEY:
            raise ValueError("CRAWLBASE_API_KEY is not set in the environment variables")
        
        crawlbase_url = f"https://api.crawlbase.com/?token={CRAWLBASE_API_KEY}&url={self.product_url}"

        response = requests.get(crawlbase_url)

        response.raise_for_status() 
        return BeautifulSoup(response.content, "html.parser")
