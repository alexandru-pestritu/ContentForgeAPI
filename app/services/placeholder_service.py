import json
from typing import Dict, List, Optional

class PlaceholderService:
    def replace_placeholders(self, template: str, replacements: Dict[str, str]) -> str:
        """
        Replace placeholders in a template with actual values from replacements dict.
        """
        for placeholder, value in replacements.items():
            template = template.replace(f"{{{placeholder}}}", value)
            
        template = template.replace("{{", "{").replace("}}", "}")
        return template

    def get_replacements_for_product(self, product: object, output_json: Optional[dict] = None) -> Dict[str, str]:
        """
        Generate replacements for product-related placeholders.
        """
        replacements = {
            "name": product.name or "",
            "full_name": product.full_name or "",
            "affiliate_urls": ", ".join([aff.url for aff in product.affiliate_urls]),
            "description": product.description or "",
            "specifications": ", ".join([f"{spec.spec_key}: {spec.spec_value}" for spec in product.specifications]),
            "seo_keyword": product.seo_keyword or "",
            "pros": ", ".join([pro.text for pro in product.pros]),
            "cons": ", ".join([con.text for con in product.cons]),
            "review": product.review or "",
            "rating": str(product.rating) if product.rating else "",
            "image_urls": ", ".join([img.image_url for img in product.images]),
        }

        if output_json:
            replacements["output"] = json.dumps(output_json, indent=2)

        return replacements

    def get_replacements_for_article(self, article: object, output_json: Optional[dict] = None) -> Dict[str, str]:
        """
        Generate replacements for article-related placeholders.
        """
        seo_keywords = ", ".join([kw.keyword for kw in article.seo_keywords])
        products = article.products
        product_info = [f"{product.name} - {product.seo_keyword}" for product in products]
        faqs = [
            {"title": faq.question, "description": faq.answer}
            for faq in article.faqs
        ] if article.faqs else []

        replacements = {
            "title": article.title or "",
            "slug": article.slug or "",
            "content": article.content or "",
            "seo_keywords": seo_keywords,
            "meta_title": article.meta_title or "",
            "meta_description": article.meta_description or "",
            "main_image_url": article.main_image_url or "",
            "buyers_guide_image_url": article.buyers_guide_image_url or "",
            "products_id_list": ", ".join(product_info),
            "introduction": article.introduction or "",
            "buyers_guide": article.buyers_guide or "",
            "faqs": json.dumps(faqs, indent=2),
            "conclusion": article.conclusion or "",
        }

        if output_json:
            replacements["output"] = json.dumps(output_json, indent=2)

        return replacements

    def get_replacements_for_store(self, store: object) -> Dict[str, str]:
        """
        Generate replacements for store-related placeholders.
        """
        return {
            "name": store.name or "",
            "base_url": store.base_url or ""
        }

    @staticmethod
    def get_placeholders_for_type(type: str) -> List[str]:
        """
        Return available placeholders for a given type (product or article).
        """
        placeholders = {
            "Store": [
                "{name}", "{base_url}"
            ],
            "Product": [
                "{name}", "{full_name}", "{affiliate_urls}", "{description}",
                "{specifications}", "{seo_keyword}", "{pros}", "{cons}", "{review}", "{rating}",
                "{image_urls}", "{output}"
            ],
            "Article": [
                "{title}", "{slug}", "{content}", "{seo_keywords}", "{meta_title}", "{meta_description}", 
                "{main_image_url}", "{buyers_guide_image_url}", "{products_id_list}", 
                "{introduction}", "{buyers_guide}", "{faqs}", "{conclusion}", "{output}"
            ]
        }
        return placeholders.get(type, [])