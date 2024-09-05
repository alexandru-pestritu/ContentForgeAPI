import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product
from app.models.prompt import Prompt
from app.services.markdown_service import MarkdownService

class PromptProcessingService:
    def get_output_for_product(subtype: str) -> dict:
        """
        Returns the output JSON for product-related prompts based on the subtype.
        """
        if subtype == "Review":
            return {
                "review": [
                    "Paragraph 1...",
                    "Paragraph 2...",
                    "Paragraph 3...",
                ]
            }
        elif subtype == "Pros & Cons":
            return {
                "pros": ["Pro 1...", "Pro 2...", "..."],
                "cons": ["Con 1...", "Con 2...", "..."]
            }
        return {}

    def get_output_for_article(subtype: str) -> dict:
        """
        Returns the output JSON for article-related prompts based on the subtype.
        """
        if subtype == "Introduction":
            return {
                "introduction": [
                    "Paragraph 1...",
                    "Paragraph 2...",
                    "Paragraph 3...",
                    "Paragraph 4..."
                ]
            }
        elif subtype == "Buyer's Guide":
            return {
                "buyers_guide": [
                    {
                        "title": "Section Title",
                        "paragraphs": [
                            "Paragraph 1...",
                            "Paragraph 2...",
                        ]
                    }
                ]
            }
        elif subtype == "FAQs":
            return {
                "faqs": [
                    {
                        "question": "Question 1?",
                        "answer": "Detailed answer for question 1."
                    },
                    {
                        "question": "Question 2?",
                        "answer": "Detailed answer for question 2."
                    }
                ]
            }
        elif subtype == "Conclusion":
            return {"conclusion": "Conclusion text here."}
        return {}

    def replace_placeholders_for_product(db: Session, text: str, product_id: int, subtype: str) -> str:
        """
        Replace placeholders in the text with actual product data, including {output}.
        """
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return text

        output_json = PromptProcessingService.get_output_for_product(subtype)

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
            "{image_urls}": ", ".join(product.get_image_urls()),
            "{output}": json.dumps(output_json, indent=2)
        }

        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)

        return text

    def replace_placeholders_for_article(db: Session, text: str, article_id: int, subtype: str) -> str:
        """
        Replace placeholders in the text with actual article data, including {output}.
        """
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            return text

        output_json = PromptProcessingService.get_output_for_article(subtype)

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
            "{conclusion}": article.conclusion or "",
            "{output}": json.dumps(output_json, indent=2)
        }

        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)

        return text

    def prepare_product_prompt_for_ai(db: Session, prompt_id: int, product_id: int) -> Optional[str]:
        """
        Prepare a product-related prompt for AI consumption by replacing placeholders and converting to Markdown.
        """
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return None

        replaced_text = PromptProcessingService.replace_placeholders_for_product(db, prompt.text, product_id, prompt.subtype)

        markdown_service = MarkdownService()
        markdown_text = markdown_service.html_to_markdown(replaced_text)

        return markdown_text

    def prepare_article_prompt_for_ai(db: Session, prompt_id: int, article_id: int) -> Optional[str]:
        """
        Prepare an article-related prompt for AI consumption by replacing placeholders and converting to Markdown.
        """
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return None

        replaced_text = PromptProcessingService.replace_placeholders_for_article(db, prompt.text, article_id, prompt.subtype)

        markdown_service = MarkdownService()
        markdown_text = markdown_service.html_to_markdown(replaced_text)

        return markdown_text
