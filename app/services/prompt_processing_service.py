from sqlalchemy.orm import Session
from typing import Optional
from app.models.product import Product
from app.models.article import Article
from app.models.store import Store
from app.models.prompt import Prompt
from app.services.placeholder_service import PlaceholderService
from app.services.markdown_service import MarkdownService

class PromptProcessingService:
    def __init__(self):
        self.placeholder_service = PlaceholderService()

    def get_output_for_product(self, subtype: str) -> dict:
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

    def get_output_for_article(self, subtype: str) -> dict:
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
                        "title": "Question 1?",
                        "description": "Detailed answer for question 1."
                    },
                    {
                        "title": "Question 2?",
                        "description": "Detailed answer for question 2."
                    }
                ]
            }
        elif subtype == "Conclusion":
            return {"conclusion": "Conclusion text here."}
        return {}

    def replace_placeholders_for_product(self, db: Session, text: str, product_id: int, subtype: Optional[str] = None) -> str:
        """
        Replace placeholders in the text with actual product data.
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return text

        output_json = self.get_output_for_product(subtype) if subtype else None
        replacements = self.placeholder_service.get_replacements_for_product(product, output_json)
        return self.placeholder_service.replace_placeholders(text, replacements)
    

    def replace_placeholders_for_article(self, db: Session, text: str, article_id: int, subtype: Optional[str] = None) -> str:
        """
        Replace placeholders in the text with actual article data.
        """
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return text

        output_json = self.get_output_for_article(subtype) if subtype else None
        replacements = self.placeholder_service.get_replacements_for_article(article, output_json)
        return self.placeholder_service.replace_placeholders(text, replacements)
    

    def prepare_product_prompt_for_ai(self, db: Session, prompt_id: int, product_id: int) -> Optional[str]:
        """
        Prepare a product-related prompt for AI by replacing placeholders.
        """
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return None

        replaced_text = self.replace_placeholders_for_product(db, prompt.text, product_id, prompt.subtype)
        markdown_service = MarkdownService()
        return markdown_service.html_to_markdown(replaced_text)
    

    def prepare_article_prompt_for_ai(self, db: Session, prompt_id: int, article_id: int) -> Optional[str]:
        """
        Prepare an article-related prompt for AI by replacing placeholders.
        """
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return None

        replaced_text = self.replace_placeholders_for_article(db, prompt.text, article_id, prompt.subtype)
        markdown_service = MarkdownService()
        return markdown_service.html_to_markdown(replaced_text)
