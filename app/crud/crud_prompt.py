from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse
from typing import Dict, List, Optional
from app.services.markdown_service import MarkdownService

def create_prompt(db: Session, prompt: PromptCreate) -> PromptResponse:
    new_prompt = Prompt(**prompt.model_dump())
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return PromptResponse.model_validate(new_prompt)

def get_prompt_by_id(db: Session, prompt_id: int) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt:
        return PromptResponse.model_validate(prompt)
    return None

def get_prompts(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> dict:
    query = db.query(Prompt)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Prompt.name.ilike(filter_pattern) |
            Prompt.type.ilike(filter_pattern) |
            Prompt.subtype.ilike(filter_pattern) |
            Prompt.text.ilike(filter_pattern)
        )

    if sort_field:
        if sort_order == -1:
            query = query.order_by(getattr(Prompt, sort_field).desc())
        else:
            query = query.order_by(getattr(Prompt, sort_field).asc())

    total_records = query.count()
    prompts = query.offset(skip).limit(limit).all()

    return {
        "prompts": [PromptResponse.model_validate(prompt) for prompt in prompts],
        "total_records": total_records
    }

def update_prompt(db: Session, prompt_id: int, prompt_update: PromptUpdate) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt:
        update_data = prompt_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prompt, key, value)
        db.commit()
        db.refresh(prompt)
        return PromptResponse.model_validate(prompt)
    return None

def delete_prompt(db: Session, prompt_id: int) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt:
        db.delete(prompt)
        db.commit()
        return PromptResponse.model_validate(prompt)
    return None

def get_prompt_types_subtypes() -> Dict[str, List[str]]:
    """
    Return the available types and subtypes for prompts.
    """
    return {
        "Product": ["Review", "Pros & Cons"],
        "Article": ["Introduction", "Buyer's Guide", "FAQs", "Conclusion"]
    }


def get_placeholders_for_type(type: str) -> List[str]:
    """
    Return available placeholders for a given type (product or article).
    """
    placeholders = {
        "Product": [
            "{name}", "{full_name}", "{affiliate_urls}", "{description}",
            "{specifications}", "{seo_keyword}", "{pros}", "{cons}", "{review}", "{rating}",
            "{image_urls}"
        ],
        "Article": [
            "{title}", "{slug}", "{content}", "{seo_keywords}", "{meta_title}", "{meta_description}", 
            "{main_image_url}", "{buyers_guide_image_url}", "{products_id_list}", 
            "{introduction}", "{buyers_guide}", "{faqs}", "{conclusion}"
        ]
    }
    return placeholders.get(type, [])


def replace_placeholders_for_product(db: Session, text: str, product_id: int) -> str:
    """
    Replace placeholders in the text with actual product data.
    
    :param db: Database session.
    :param text: Text containing placeholders.
    :param product_id: ID of the product to retrieve data for.
    :return: Text with placeholders replaced.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return text
    
    replacements = {
        "{name}": product.name or "",
        "{full_name}": product.full_name or "",
        "{affiliate_urls}": ", ".join(product.get_affiliate_urls()),
        "{description}": product.description or "",
        "{specifications}": ", ".join([f"{k}: {v}" for k, v in product.get_specifications().items()]),
        "{seo_keyword}": product.seo_keyword or "",
        "{pros}": ", ".join(product.get_pros()),
        "{cons}": ", ".join(product.get_cons()),
        "{review}": product.review or "",
        "{rating}": str(product.rating) if product.rating else "",
        "{image_urls}": ", ".join(product.get_image_urls())
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text

def replace_placeholders_for_article(db: Session, text: str, article_id: int) -> str:
    """
    Replace placeholders in the text with actual article data.
    
    :param db: Database session.
    :param text: Text containing placeholders.
    :param article_id: ID of the article to retrieve data for.
    :return: Text with placeholders replaced.
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        return text

    seo_keywords = ", ".join(article.get_seo_keywords())
    
    product_info = []
    product_ids = article.get_products_id_list()
    if product_ids:
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        product_info = [f"{product.name} - {product.seo_keyword}" for product in products]
    
    replacements = {
        "{title}": article.title or "",
        "{slug}": article.slug or "",
        "{content}": article.content or "",
        "{seo_keywords}": seo_keywords,
        "{meta_title}": article.meta_title or "",
        "{meta_description}": article.meta_description or "",
        "{main_image_url}": article.main_image_url or "",
        "{buyers_guide_image_url}": article.buyers_guide_image_url or "",
        "{products_id_list}": ", ".join(product_info),
        "{introduction}": article.introduction or "",
        "{buyers_guide}": article.buyers_guide or "",
        "{faqs}": article.faqs or "",
        "{conclusion}": article.conclusion or ""
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text

def prepare_product_prompt_for_ai(db: Session, prompt_id: int, product_id: int) -> Optional[str]:
    """
    Prepare a product-related prompt for AI consumption by replacing placeholders and converting to Markdown.
    
    :param db: Database session.
    :param prompt_id: ID of the prompt to retrieve.
    :param product_id: ID of the product to use for placeholder replacements.
    :return: The prepared prompt text in Markdown format or None if the prompt or product is not found.
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return None
    
    replaced_text = replace_placeholders_for_product(db, prompt.text, product_id)
    
    markdown_service = MarkdownService()
    markdown_text = markdown_service.html_to_markdown(replaced_text)
    
    return markdown_text

def prepare_article_prompt_for_ai(db: Session, prompt_id: int, article_id: int) -> Optional[str]:
    """
    Prepare an article-related prompt for AI consumption by replacing placeholders and converting to Markdown.
    
    :param db: Database session.
    :param prompt_id: ID of the prompt to retrieve.
    :param article_id: ID of the article to use for placeholder replacements.
    :return: The prepared prompt text in Markdown format or None if the prompt or article is not found.
    """
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return None
    
    replaced_text = replace_placeholders_for_article(db, prompt.text, article_id)
    
    markdown_service = MarkdownService()
    markdown_text = markdown_service.html_to_markdown(replaced_text)
    
    return markdown_text