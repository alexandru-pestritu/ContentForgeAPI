import time
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.blog import Blog
from app.models.product import Product
from app.models.stock_check_log import StockCheckLog
from app.scrapers.scraper_factory import scraper_factory
from app.services.settings_service import SettingsService


def check_and_update_product_stock(db: Session, product: Product) -> bool:
    """
    Checks the stock status of a product and updates its details if necessary.
    Returns True if the product is in stock, False otherwise.
    If an error occurs during scraping, the product is skipped and its old in_stock value is returned.
    """
    try:
        affiliate_urls = product.affiliate_urls
        if not affiliate_urls:
            return product.in_stock

        scraper = scraper_factory(affiliate_urls[0].url)
        scraped_data = scraper.scrape_product_data()

        in_stock = scraped_data.get('in_stock')

        if product.in_stock != in_stock:
            product.in_stock = in_stock

        product.last_checked = datetime.now(timezone.utc)
        db.commit()

        return in_stock
    except Exception as e:
        print(f"Error while checking product {product.id}: {e}")
        return product.in_stock


def update_product_stocks(db: Session, manual_run: bool = False):
    """
    Updates the stock status of products per blog. For each blog:
      - Gets the list of products that need stock checking (based on last_checked or forced if manual_run).
      - Scrapes and updates stock info.
      - Logs the check result in StockCheckLog with the correct blog_id.

    :param db: The database session.
    :param manual_run: If True, updates stock for ALL products in each blog. Otherwise, only those past the interval.
    """
    check_interval_days = SettingsService.get_setting_value("scraping.log.stock_check_interval")
    now = datetime.now(timezone.utc)

    blogs = db.query(Blog).all()

    for blog in blogs:
        start_time = time.time()

        if manual_run:
            products_to_check = db.query(Product).filter(Product.blog_id == blog.id).all()
        else:
            threshold_time = now - timedelta(days=check_interval_days)
            products_to_check = db.query(Product).filter(
                Product.blog_id == blog.id,
                (Product.last_checked == None) | (Product.last_checked < threshold_time)
            ).all()

        total_products = db.query(Product).filter(Product.blog_id == blog.id).count()
        out_of_stock_count = 0

        for product in products_to_check:
            in_stock = check_and_update_product_stock(db, product)
            if not in_stock:
                out_of_stock_count += 1

        in_stock_count = total_products - out_of_stock_count
        duration = time.time() - start_time

        stock_check_log = StockCheckLog(
            blog_id=blog.id,
            duration=duration,
            in_stock_count=in_stock_count,
            out_of_stock_count=out_of_stock_count
        )
        db.add(stock_check_log)
        db.commit()

        print(f"[Blog ID={blog.id}] Stock check complete. "
              f"Duration: {duration:.2f} seconds. "
              f"In stock: {in_stock_count}, Out of stock: {out_of_stock_count}.")


def scheduled_stock_update():
    """
    Runs the stock update job as scheduled by APScheduler or a similar scheduler.
    """
    db: Session = SessionLocal()
    try:
        update_product_stocks(db)
    finally:
        db.close()
