from app.scrapers.scraper_factory import scraper_factory

# Replace with a valid product URL from eMAG
product_url = "valid product url from eMAG"

scraper = scraper_factory(product_url)

in_stock = scraper.get_in_stock()
print(f"In Stock: {in_stock}")

description = scraper.get_description()
print(f"Description: {description}")

specifications = scraper.get_specifications()
print(f"Specifications: {specifications}")

image_urls = scraper.get_image_urls()
print(f"Image URLs: {image_urls}")
