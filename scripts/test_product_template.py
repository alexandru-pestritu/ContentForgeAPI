import asyncio
from sqlalchemy.orm import Session
from app.services.wordpress_service import WordPressService
from app.services.templates.product_template import ProductTemplate
from app.crud.crud_product import get_product_by_id
from app.database import SessionLocal
from app.database import get_db

async def setup(product_id: int):
    db = SessionLocal()

    wp_service = WordPressService()

    product = get_product_by_id(db, product_id)
    
    if product is None:
        print(f"Product with id {product_id} not found!")
        return None

    product_template = ProductTemplate(product=product, db=db, wp_service=wp_service, position=1)

    return product_template


async def test_product_template(product_id: int):
    product_template = await setup(product_id)

    if product_template is None:
        return

    rendered_template = await product_template.render()

    print(rendered_template)

if __name__ == "__main__":
    product_id = 10 # Change this to the product id you want to test
    asyncio.run(test_product_template(product_id))
