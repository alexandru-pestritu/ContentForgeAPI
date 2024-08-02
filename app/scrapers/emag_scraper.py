from bs4 import BeautifulSoup
from app.scrapers.base_scraper import BaseScraper

class EmagScraper(BaseScraper):
    def __init__(self, product_url: str):
        super().__init__(product_url)
        self.page_content = self._fetch_page_content() 

    def get_full_name(self) -> str:
        """
        Extract and return the full product name from the page content.
        """
        full_name_element = self.page_content.find('h1', class_='page-title')
        if full_name_element:
            return full_name_element.get_text(strip=True)
        return ""

    def get_in_stock(self) -> bool:
        """
        Extract and return whether the product is in stock from the page content.
        Returns True if the product is in stock or in limited quantity,
        Returns False if the product is out of stock.
        """
        stock_element = self.page_content.find('div', class_='stock-and-genius')
        
        if stock_element:
            stock_status = stock_element.find('span', class_='label')
            if stock_status:
                if 'label-in_stock' in stock_status.get('class', []):
                    return True
                elif 'label-limited_stock_qty' in stock_status.get('class', []):
                    return True
                elif 'label-out_of_stock' in stock_status.get('class', []):
                    return False
        return False

    def get_description(self) -> str:
        """
        Extract and return the product description from the page content,
        including text within <ul>, <ol>, and <li> elements.
        """
        description_element = self.page_content.find('div', class_='product-page-description-text')

        if description_element:
            description_text_parts = []
            for element in description_element.descendants:
                if element.name == 'p':
                    description_text_parts.append(element.get_text(strip=True))
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        description_text_parts.append(li.get_text(strip=True))
            
            return ' '.join(description_text_parts).strip()

        return ""

    def get_specifications(self) -> dict:
        """
        Extract and return the product specifications from the page content,
        with values separated by commas instead of newlines.
        """
        specs_tables = self.page_content.find_all('table', class_='table table-striped specifications-table')
        product_specs = {}
        for table in specs_tables:
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 2:
                    spec_name = columns[0].text.strip()
                    spec_value = columns[1].text.strip().replace('\n', ', ')
                    product_specs[spec_name] = spec_value
        return product_specs

    def get_image_urls(self) -> list:
        """
        Extract and return a list of image URLs from the page content.
        """
        image_elements = self.page_content.select('.product-gallery-inner .thumbnail-wrapper a[href]')
        image_urls = [img['href'] for img in image_elements[:5]]
        return image_urls

