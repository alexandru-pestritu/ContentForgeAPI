import csv
import io
import json
from typing import Optional, Dict, Callable
from sqlalchemy.orm import Session
from app.models.store import Store
from app.models.product import Product
from app.models.article import Article
from app.models.prompt import Prompt
from sqlalchemy.orm import Query
from io import StringIO

def apply_filters_sorting_pagination(query: Query, model, skip: int, limit: int, sort_field: Optional[str], sort_order: Optional[int], filter: Optional[str]) -> Query:
    if filter:
        filter_pattern = f"%{filter}%"
        pass

    if sort_field:
        sort_attr = getattr(model, sort_field, None)
        if sort_attr:
            if sort_order == -1:
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())

    query = query.offset(skip).limit(limit)
    return query

def export_stores(db: Session, skip: int, limit: int, sort_field: Optional[str], sort_order: Optional[int], filter: Optional[str]) -> str:
    query = db.query(Store)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Store.name.ilike(filter_pattern) |
            Store.base_url.ilike(filter_pattern)
        )
    
    query = apply_filters_sorting_pagination(query, Store, skip, limit, sort_field, sort_order, None)
    stores = query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "base_url", "favicon_image_id", "favicon_url"])
    for store in stores:
        writer.writerow([store.id, store.name, store.base_url, store.favicon_image_id, store.favicon_url])
    return output.getvalue()

def export_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> str:
    query = db.query(Product)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Product.name.ilike(filter_pattern) |
            Product.seo_keyword.ilike(filter_pattern)
        )

    query = apply_filters_sorting_pagination(query, Product, skip, limit, sort_field, sort_order, None)
    products = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "store_ids", "name", "full_name", "affiliate_urls", "in_stock",
        "description", "specifications", "seo_keyword", "pros", "cons", "review",
        "rating", "image_urls", "image_ids", "last_checked"
    ])
    for product in products:
        store_ids_str = ",".join(map(str, product.get_store_ids())) if product.get_store_ids() else ""
        affiliate_urls_str = ",".join(product.get_affiliate_urls()) if product.get_affiliate_urls() else ""
        pros_str = ",".join(product.get_pros()) if product.get_pros() else ""
        cons_str = ",".join(product.get_cons()) if product.get_cons() else ""
        image_urls_str = ",".join(product.get_image_urls()) if product.get_image_urls() else ""
        image_ids_str = ",".join(map(str, product.get_image_ids())) if product.get_image_ids() else ""

        specifications_json = json.dumps(product.get_specifications()) if product.get_specifications() else ""

        writer.writerow([
            product.id,
            store_ids_str,
            product.name,
            product.full_name or "",
            affiliate_urls_str,
            product.in_stock,
            product.description or "",
            specifications_json,
            product.seo_keyword or "",
            pros_str,
            cons_str,
            product.review or "",
            product.rating,
            image_urls_str,
            image_ids_str,
            product.last_checked
        ])

    return output.getvalue()


def export_articles(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> str:
    query = db.query(Article)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Article.title.ilike(filter_pattern) |
            Article.slug.ilike(filter_pattern) |
            Article.status.ilike(filter_pattern)
        )

    query = apply_filters_sorting_pagination(query, Article, skip, limit, sort_field, sort_order, None)
    articles = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "wp_id", "categories_id_list", "title", "slug", "author_id", "status",
        "seo_keywords", "meta_title", "meta_description", "main_image_url", "main_image_wp_id",
        "buyers_guide_image_url", "buyers_guide_image_wp_id", "products_id_list",
        "introduction", "buyers_guide", "faqs", "conclusion"
    ])
    for article in articles:
        categories_id_str = ",".join(map(str, article.get_categories_id_list())) if article.get_categories_id_list() else ""
        seo_keywords_str = ",".join(article.get_seo_keywords()) if article.get_seo_keywords() else ""
        products_id_list_str = ",".join(map(str, article.get_products_id_list())) if article.get_products_id_list() else ""

        # faqs este o listă de dict-uri, o păstrăm ca JSON pentru că nu este ușor să o reprezentăm ca CSV
        faqs_json = json.dumps(article.get_faqs()) if article.get_faqs() else ""

        writer.writerow([
            article.id,
            article.wp_id,
            categories_id_str,
            article.title,
            article.slug,
            article.author_id,
            article.status,
            seo_keywords_str,
            article.meta_title or "",
            article.meta_description or "",
            article.main_image_url or "",
            article.main_image_wp_id,
            article.buyers_guide_image_url or "",
            article.buyers_guide_image_wp_id,
            products_id_list_str,
            article.introduction or "",
            article.buyers_guide or "",
            faqs_json,
            article.conclusion or ""
        ])

    return output.getvalue()

def export_prompts(
    db: Session,
    skip: int,
    limit: int,
    sort_field: Optional[str],
    sort_order: Optional[int],
    filter: Optional[str]
) -> str:
    query = db.query(Prompt)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Prompt.name.ilike(filter_pattern) |
            Prompt.type.ilike(filter_pattern) |
            Prompt.subtype.ilike(filter_pattern) |
            Prompt.text.ilike(filter_pattern)
        )

    query = apply_filters_sorting_pagination(query, Prompt, skip, limit, sort_field, sort_order, None)
    prompts = query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "type", "subtype", "text"])
    for prompt in prompts:
        writer.writerow([prompt.id, prompt.name, prompt.type, prompt.subtype, prompt.text])

    return output.getvalue()

EXPORTERS: Dict[str, Callable[..., str]] = {
    "store": export_stores,
    "product": export_products,
    "article": export_articles,
    "prompt": export_prompts,
}
