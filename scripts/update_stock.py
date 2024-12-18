import time
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.stock_check_log import StockCheckLog
from app.scrapers.scraper_factory import scraper_factory
from app.database import SessionLocal

CHECK_INTERVAL_DAYS = 14

def check_and_update_product_stock(db: Session, product: Product) -> bool:
    """
    Checks the stock status of a product and updates its details if necessary.
    Returns True if the product is in stock, False otherwise.
    If an error occurs during scraping, the product is skipped.
    """
    try:
        affiliate_urls = product.get_affiliate_urls()
        scraper = scraper_factory(affiliate_urls[0])
        scraped_data = scraper.scrape_product_data()

        in_stock = scraped_data.get('in_stock')

        if product.in_stock != in_stock:
            product.in_stock = in_stock
            product.description = scraped_data.get('description')
            product.full_name = scraped_data.get('full_name')
            product.set_specifications(scraped_data.get('specifications', {}))
            product.set_image_urls(scraped_data.get('image_urls', []))

        product.last_checked = datetime.now(timezone.utc)
        db.commit()

        return in_stock
    except Exception as e:
        print(f"Error while checking product {product.id}: {e}")
        return product.in_stock


def update_product_stocks(db: Session, manual_run: bool = False):
    """
    Updates the stock status of products that haven't been checked within the specified number of days,
    or all products if this is a manual run. Logs the duration of the stock check and the number of in-stock 
    and out-of-stock products.
    """
    start_time = time.time()

    now = datetime.now(timezone.utc)

    if manual_run:
        products_to_check = db.query(Product).all()
    else:
        threshold_time = now - timedelta(days=CHECK_INTERVAL_DAYS)
        products_to_check = db.query(Product).filter(
            (Product.last_checked == None) | 
            (Product.last_checked < threshold_time)
        ).all()

    total_products = db.query(Product).count()
    out_of_stock_count = 0

    for product in products_to_check:
        in_stock = check_and_update_product_stock(db, product)
        if not in_stock:
            out_of_stock_count += 1

    in_stock_count = total_products - out_of_stock_count

    duration = time.time() - start_time

    stock_check_log = StockCheckLog(
        duration=duration,
        in_stock_count=in_stock_count,
        out_of_stock_count=out_of_stock_count
    )
    db.add(stock_check_log)
    db.commit()

    print(f"Stock check complete. Duration: {duration:.2f} seconds. In stock: {in_stock_count}, Out of stock: {out_of_stock_count}.")


def scheduled_stock_update():
    """
    Runs the stock update job as scheduled by APScheduler.
    """
    db: Session = SessionLocal()
    try:
        update_product_stocks(db)
    finally:
        db.close()
