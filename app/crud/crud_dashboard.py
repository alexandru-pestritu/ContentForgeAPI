from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product
from app.schemas.dashboard import DashboardStatsResponse

def get_dashboard_stats(db: Session, blog_id : int) -> DashboardStatsResponse:
    """
    Retrieve statistics for the dashboard:
    - number of published articles
    - number of draft articles
    - total number of products
    - number of out of stock products
    """
    published_articles_count = db.query(Article).filter(Article.blog_id == blog_id, Article.status == "publish").count()
    
    draft_articles_count = db.query(Article).filter(Article.blog_id == blog_id, Article.status == "draft").count()

    total_products_count = db.query(Product).filter(Product.blog_id == blog_id).count()

    out_of_stock_products_count = db.query(Product).filter(Product.blog_id == blog_id, Product.in_stock == False).count()

    return DashboardStatsResponse(
        published_articles_count=published_articles_count,
        draft_articles_count=draft_articles_count,
        total_products_count=total_products_count,
        out_of_stock_products_count=out_of_stock_products_count
    )
