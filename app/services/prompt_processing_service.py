import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product
from app.models.prompt import Prompt
from app.services.markdown_service import MarkdownService

class PromptProcessingService:
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

    def replace_placeholders_for_product(self, db: Session, text: str, product_id: int, subtype: str) -> str:
        """
        Replace placeholders in the text with actual product data, including {output}.
        """
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return text

        output_json = self.get_output_for_product(subtype)

        replacements = {
            "{name}": product.name or "",
            "{full_name}": product.full_name or "",
            "{affiliate_urls}": ", ".join([aff.url for aff in product.affiliate_urls]),
            "{description}": product.description or "",
            "{specifications}": ", ".join([f"{spec.spec_key}: {spec.spec_value}" for spec in product.specifications]),
            "{seo_keyword}": product.seo_keyword or "",
            "{pros}": ", ".join([pro.text for pro in product.pros]),
            "{cons}": ", ".join([con.text for con in product.cons]),
            "{review}": product.review or "",
            "{rating}": str(product.rating) if product.rating else "",
            "{image_urls}": ", ".join([img.image_url for img in product.images]),
            "{output}": json.dumps(output_json, indent=2)
        }

        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)

        return text

    def replace_placeholders_for_article(self, db: Session, text: str, article_id: int, subtype: str) -> str:
        """
        Replace placeholders in the text with actual article data, including {output}.
        """
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            return text

        output_json = self.get_output_for_article(subtype)

        seo_keywords = ", ".join([kw.keyword for kw in article.seo_keywords])

        products = article.products
        product_info = [f"{product.name} - {product.seo_keyword}" for product in products]
        faqs = [
                {"title": faq.question, "description": faq.answer}
                for faq in article.faqs
            ] if article.faqs else []
        
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
            "{faqs}": json.dumps(faqs, indent=2),
            "{conclusion}": article.conclusion or "",
            "{output}": json.dumps(output_json, indent=2)
        }

        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)

        return text

    def prepare_product_prompt_for_ai(self, db: Session, prompt_id: int, product_id: int) -> Optional[str]:
        """
        Prepare a product-related prompt for AI consumption by replacing placeholders and converting to Markdown.
        """
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return None

        replaced_text = self.replace_placeholders_for_product(db, prompt.text, product_id, prompt.subtype)

        markdown_service = MarkdownService()
        markdown_text = markdown_service.html_to_markdown(replaced_text)

        return markdown_text

    def prepare_article_prompt_for_ai(self, db: Session, prompt_id: int, article_id: int) -> Optional[str]:
        """
        Prepare an article-related prompt for AI consumption by replacing placeholders and converting to Markdown.
        """
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return None

        replaced_text = self.replace_placeholders_for_article(db, prompt.text, article_id, prompt.subtype)

        markdown_service = MarkdownService()
        markdown_text = markdown_service.html_to_markdown(replaced_text)

        return markdown_text
