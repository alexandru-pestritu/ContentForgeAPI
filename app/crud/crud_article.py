import csv
import io
import json
from sqlalchemy.orm import Session
from app.models.article import Article, ArticleSEOKeyword, ArticleFAQ, Category
from app.models.product import Product
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from typing import List, Optional
from app.services.image_service import ImageService

async def create_article(
    db: Session, 
    article: ArticleCreate, 
    image_service: Optional[ImageService] = None
    ) -> ArticleResponse:
    """
    Create a new article record in the database.
    """
    new_article = Article(
        title=article.title,
        slug=article.slug,
        author_id=article.author_id,
        status=article.status,
        meta_title=article.meta_title,
        meta_description=article.meta_description,
        main_image_url=str(article.main_image_url) if article.main_image_url else None,
        buyers_guide_image_url=str(article.buyers_guide_image_url) if article.buyers_guide_image_url else None,
    )

    if article.seo_keywords is not None:
        new_article.seo_keywords = [ArticleSEOKeyword(keyword=k) for k in article.seo_keywords]

    if article.products_id_list is not None:
        products = db.query(Product).filter(Product.id.in_(article.products_id_list)).all()
        new_article.products = products

    if article.categories_id_list is not None:
        new_article.categories = [Category(wp_id=category_id) for category_id in article.categories_id_list]

    if image_service:
        if article.main_image_url:
            new_article.main_image_wp_id = await image_service.process_image(
                entity_type="article_main",
                entity=new_article,
                image_url=article.main_image_url
            )
        if article.buyers_guide_image_url:
            new_article.buyers_guide_image_wp_id = await image_service.process_image(
                entity_type="article_guide",
                entity=new_article,
                image_url=article.buyers_guide_image_url
            )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return ArticleResponse.from_orm(new_article)

def get_article_by_id(
    db: Session, 
    article_id: int
    ) -> Optional[ArticleResponse]:
    """
    Retrieve an article by its ID.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        return ArticleResponse.from_orm(article)
    return None

def get_articles(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> dict:
    """
    Retrieve a list of articles, with pagination support, sorting, filtering, and total records.
    """
    query = db.query(Article)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Article.title.ilike(filter_pattern) |
            Article.slug.ilike(filter_pattern) |
            Article.status.ilike(filter_pattern)
        )

    if sort_field:
        if sort_order == -1:
            query = query.order_by(getattr(Article, sort_field).desc())
        else:
            query = query.order_by(getattr(Article, sort_field).asc())

    total_records = query.count()
    articles = query.offset(skip).limit(limit).all()

    return {
        "articles": [ArticleResponse.from_orm(article) for article in articles],
        "total_records": total_records
    }


def get_latest_articles(db: Session, limit: int) -> List[ArticleResponse]:
    """
    Retrieve the latest articles based on the highest IDs (as IDs are assigned incrementally).
    """
    articles = db.query(Article).order_by(Article.id.desc()).limit(limit).all()
    return [ArticleResponse.from_orm(article) for article in articles]


async def update_article(
    db: Session, 
    article_id: int, 
    article_update: ArticleUpdate, 
    image_service: Optional[ImageService] = None
) -> Optional[ArticleResponse]:
    """
    Update an existing article record.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return None

    update_data = article_update.model_dump()

    if 'seo_keywords' in update_data and update_data['seo_keywords'] is not None:
        article.seo_keywords.clear()
        article.seo_keywords = [ArticleSEOKeyword(keyword=k) for k in update_data['seo_keywords']]

    if 'products_id_list' in update_data and update_data['products_id_list'] is not None:
        products = db.query(Product).filter(Product.id.in_(update_data['products_id_list'])).all()
        article.products.clear()
        article.products = products
        
    if 'categories_id_list' in update_data and update_data['categories_id_list'] is not None:
        article.categories.clear()
        article.categories = [Category(wp_id=category_id) for category_id in update_data['categories_id_list']]

    if 'faqs' in update_data and update_data['faqs'] is not None:
        article.faqs.clear()
        article.faqs = [ArticleFAQ(question=faq['title'], answer=faq['description']) for faq in update_data['faqs']]

    if 'main_image_url' in update_data:
        update_data['main_image_url'] = str(update_data['main_image_url'])
    if 'buyers_guide_image_url' in update_data:
        update_data['buyers_guide_image_url'] = str(update_data['buyers_guide_image_url'])

    for key, value in update_data.items():
        if key not in ('seo_keywords', 'products_id_list', 'categories_id_list', 'faqs'):
            setattr(article, key, value)

    if image_service:
        if 'main_image_url' in update_data:
            article.main_image_wp_id = await image_service.process_image(
                entity_type="article_main",
                entity=article,
                image_url=update_data['main_image_url']
            )
        if 'buyers_guide_image_url' in update_data:
            article.buyers_guide_image_wp_id = await image_service.process_image(
                entity_type="article_guide",
                entity=article,
                image_url=update_data['buyers_guide_image_url']
            )

    db.commit()
    db.refresh(article)
    return ArticleResponse.from_orm(article)

def delete_article(db: Session, article_id: int) -> Optional[ArticleResponse]:
    """
    Delete an article by its ID.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
        return ArticleResponse.from_orm(article)
    return None