from sqlalchemy.orm import Session
from app.models.article import Article
from app.schemas.article import ArticleResponse
from app.schemas.product import ProductResponse
from app.services.specifications_filtering_service import SpecificationsFilteringService
from app.services.wordpress_service import WordPressService
from app.services.templates.product_template import ProductTemplate
from app.services.templates.article_template import ArticleTemplate
from app.crud.crud_product import get_product_by_id
from app.crud.crud_article import get_article_by_id
from typing import Dict, Any, Optional

specifications_filter_service = SpecificationsFilteringService()

async def generate_product_widget(db: Session, blog_id: int, product_id: int) -> Dict[str, Any]:
    """
    Generate the product widget using ProductTemplate for a given product ID.

    :param db: Database session.
    :param product_id: The ID of the product.
    :return: A dictionary containing the product template content.
    """
    try:
        wp_service = WordPressService(blog_id=blog_id, db=db)
        product_response = get_product_by_id(db, blog_id=blog_id, product_id=product_id)
        if not product_response:
            raise ValueError(f"Product with ID {product_id} not found.")

        product_template = ProductTemplate(product_response, db, wp_service)
        generated_content = await product_template.render()

        return {
            "product_id": product_id,
            "content": generated_content
        }

    except Exception as e:
        raise ValueError(f"Error generating product widget: {str(e)}")


async def generate_article_widget(
    db: Session, 
    blog_id: int,
    article_id: int, 
    publish_to_wp: bool = False
) -> Dict[str, Any]:
    """
    Generate the article widget using ArticleTemplate for a given article ID, optionally publish or update to WordPress.

    :param db: Database session.
    :param article_id: The ID of the article.
    :param publish_to_wp: Boolean indicating if the article should be published or updated in WordPress.
    :return: A dictionary containing the article template content and WP ID if applicable.
    """
    try:
        wp_service = WordPressService(blog_id=blog_id, db=db)
        article_response = get_article_by_id(db, blog_id=blog_id, article_id=article_id)
        if not article_response:
            raise ValueError(f"Article with ID {article_id} not found.")

        article_template = ArticleTemplate(article_response, db, wp_service, specifications_filter_service)
        generated_content = await article_template.render()

        article = db.query(Article).filter(Article.id == article_id, Article.blog_id == blog_id).first()
        article.content = generated_content
        db.commit()
        article_response.content = generated_content

        wp_id = None

        if publish_to_wp:
            if article.wp_id:
                wp_id = await wp_service.update_article(article_response)
                if(wp_id==None):
                    wp_id = await wp_service.add_article(article_response)
            else:
                wp_id = await wp_service.add_article(article_response)

            if wp_id:
                article.wp_id = wp_id
                article.status = "publish"
                db.commit()

        return {
            "article_id": article_id,
            "content": generated_content,
            "wp_id": wp_id
        }

    except Exception as e:
        raise ValueError(f"Error generating article widget: {str(e)}")
