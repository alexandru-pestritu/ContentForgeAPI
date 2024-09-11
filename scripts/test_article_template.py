import asyncio
from sqlalchemy.orm import Session
from app.services.wordpress_service import WordPressService
from app.services.templates.article_template import ArticleTemplate
from app.crud.crud_article import get_article_by_id
from app.database import SessionLocal

async def setup(article_id: int):
    db = SessionLocal()

    wp_service = WordPressService()

    article = get_article_by_id(db, article_id)

    if article is None:
        print(f"Article with id {article_id} not found!")
        return None

    article_template = ArticleTemplate(article=article, db=db, wp_service=wp_service)

    return article_template


async def test_article_template(article_id: int):
    article_template = await setup(article_id)

    if article_template is None:
        return

    rendered_template = await article_template.render()

    print(rendered_template)

if __name__ == "__main__":
    article_id = 5  # Change this to the article id you want to test
    asyncio.run(test_article_template(article_id))
