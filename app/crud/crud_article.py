import json
from sqlalchemy.orm import Session
from app.models.article import Article
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

    new_article.set_seo_keywords(article.seo_keywords)
    new_article.set_products_id_list(article.products_id_list)
    new_article.set_categories_id_list(article.categories_id_list)


    if image_service:
        if new_article.main_image_url:
            main_image_id = await image_service.process_featured_image(
                article_title=article.title,
                seo_keywords=article.seo_keywords,
                image_url=new_article.main_image_url,
                target_width=1400,
                target_height=960
            )
            new_article.main_image_wp_id = main_image_id

        if new_article.buyers_guide_image_url:
            buyers_guide_image_id = await image_service.process_buyers_guide_image(
                article_title=article.title,
                seo_keywords=article.seo_keywords,
                image_url=new_article.buyers_guide_image_url,
                target_width=1400,
                target_height=960
            )
            new_article.buyers_guide_image_wp_id = buyers_guide_image_id

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
    limit: int = 10
    ) -> List[ArticleResponse]:
    """
    Retrieve a list of articles, with pagination support.
    """
    articles = db.query(Article).offset(skip).limit(limit).all()
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

    if 'seo_keywords' in update_data:
        article.set_seo_keywords(update_data['seo_keywords'])
    if 'products_id_list' in update_data:
        article.set_products_id_list(update_data['products_id_list'])
    if 'categories_id_list' in update_data:
        article.set_categories_id_list(update_data['categories_id_list'])
    if 'faqs' in update_data:
        article.set_faqs(update_data['faqs'])

    if 'main_image_url' in update_data:
        update_data['main_image_url'] = str(update_data['main_image_url'])
    if 'buyers_guide_image_url' in update_data:
        update_data['buyers_guide_image_url'] = str(update_data['buyers_guide_image_url'])

    if image_service:
        if 'main_image_url' in update_data and update_data['main_image_url']:
            main_image_id = await image_service.process_featured_image(
                article_title=article.title,
                seo_keywords=update_data.get('seo_keywords', []),
                image_url=update_data['main_image_url'],
                target_width=1400,
                target_height=960
            )
            article.main_image_wp_id = main_image_id

        if 'buyers_guide_image_url' in update_data and update_data['buyers_guide_image_url']:
            buyers_guide_image_id = await image_service.process_buyers_guide_image(
                article_title=article.title,
                seo_keywords=update_data.get('seo_keywords', []),
                image_url=update_data['buyers_guide_image_url'],
                target_width=1400,
                target_height=960
            )
            article.buyers_guide_image_wp_id = buyers_guide_image_id

    for key, value in update_data.items():
        if key not in ('seo_keywords', 'products_id_list', 'categories_id_list', 'faqs'):
            setattr(article, key, value)

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
