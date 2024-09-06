from typing import Dict, Any
import json

from requests import Session

from app.models.prompt import Prompt

class AIResponseProcessingService:
    
    def clean_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Clean the AI response by removing any text before '{' and after '}'.
        This ensures the returned content is a valid JSON string.
        """
        try:
            start = ai_response.find('{')
            end = ai_response.rfind('}')
            
            if start != -1 and end != -1:
                cleaned_response = ai_response[start:end+1]
                return json.loads(cleaned_response)
            else:
                raise ValueError("Invalid AI response, missing JSON structure.")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Error cleaning and parsing AI response: {str(e)}")

    def process_response(self, db: Session, ai_response: str, prompt_id: int, obj_to_update: Any):
        """
        Process the AI response based on the prompt type and subtype retrieved from the database.
        
        :param db: The database session.
        :param ai_response: The raw AI response as a string.
        :param prompt_id: The ID of the prompt to retrieve type and subtype information.
        :param obj_to_update: The object (Product or Article) to update based on the processed AI response.
        """
        cleaned_json = self.clean_ai_response(ai_response)
        
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise ValueError(f"Prompt with ID {prompt_id} not found.")

        prompt_type = prompt.type
        prompt_subtype = prompt.subtype

        if prompt_type == "Product":
            if prompt_subtype == "Review":
                self.process_product_review(cleaned_json, obj_to_update)
            elif prompt_subtype == "Pros & Cons":
                self.process_product_pros_cons(cleaned_json, obj_to_update)
        elif prompt_type == "Article":
            if prompt_subtype == "Introduction":
                self.process_article_introduction(cleaned_json, obj_to_update)
            elif prompt_subtype == "Buyer's Guide":
                self.process_article_buyers_guide(cleaned_json, obj_to_update)
            elif prompt_subtype == "FAQs":
                self.process_article_faqs(cleaned_json, obj_to_update)
            elif prompt_subtype == "Conclusion":
                self.process_article_conclusion(cleaned_json, obj_to_update)
        else:
            raise ValueError(f"Unsupported prompt type: {prompt_type} or subtype: {prompt_subtype}")


    def process_product_review(self, ai_json: Dict[str, Any], product: Any):
        """
        Process the AI response for a product review and update the product object accordingly.
        Converts each paragraph into HTML <p> tags.
        Expected JSON structure:
        {
            "review": [
                "Paragraph 1...",
                "Paragraph 2...",
                ...
            ]
        }
        """
        if "review" in ai_json:
            product.review = "".join([f"<p>{paragraph}</p>" for paragraph in ai_json["review"]])
        else:
            raise ValueError("Expected 'review' key in AI response for Product Review.")

    def process_product_pros_cons(self, ai_json: Dict[str, Any], product: Any):
        """
        Process the AI response for product pros and cons and update the product object.
        Expected JSON structure:
        {
            "pros": ["Pro 1...", "Pro 2..."],
            "cons": ["Con 1...", "Con 2..."]
        }
        """
        if "pros" in ai_json and "cons" in ai_json:
            product.set_pros(ai_json["pros"])
            product.set_cons(ai_json["cons"])
        else:
            raise ValueError("Expected 'pros' and 'cons' keys in AI response for Product Pros & Cons.")

    def process_article_introduction(self, ai_json: Dict[str, Any], article: Any):
        """
        Process the AI response for an article introduction and update the article object.
        Converts each paragraph into HTML <p> tags.
        Expected JSON structure:
        {
            "introduction": [
                "Paragraph 1...",
                "Paragraph 2...",
                ...
            ]
        }
        """
        if "introduction" in ai_json:
            article.introduction = "".join([f"<p>{paragraph}</p>" for paragraph in ai_json["introduction"]])
        else:
            raise ValueError("Expected 'introduction' key in AI response for Article Introduction.")

    def process_article_buyers_guide(self, ai_json: Dict[str, Any], article: Any):
        """
        Process the AI response for a buyer's guide and update the article object.
        Converts titles into <h4> and paragraphs into <p> tags.
        Expected JSON structure:
        {
            "buyers_guide": [
                {
                    "title": "Section Title",
                    "paragraphs": [
                        "Paragraph 1...",
                        "Paragraph 2...",
                        ...
                    ]
                },
                ...
            ]
        }
        """
        if "buyers_guide" in ai_json:
            guide_html = ""
            for section in ai_json["buyers_guide"]:
                guide_html += f"<h4>{section['title']}</h4>"
                guide_html += "".join([f"<p>{para}</p>" for para in section['paragraphs']])
            article.buyers_guide = guide_html
        else:
            raise ValueError("Expected 'buyers_guide' key in AI response for Article Buyer's Guide.")

    def process_article_faqs(self, ai_json: Dict[str, Any], article: Any):
        """
        Process the AI response for an article FAQs and update the article object.
        Expected JSON structure:
        {
            "faqs": [
                {
                    "question": "Question 1?",
                    "answer": "Answer 1"
                },
                ...
            ]
        }
        """
        if "faqs" in ai_json:
            article.set_faqs(ai_json["faqs"])
        else:
            raise ValueError("Expected 'faqs' key in AI response for Article FAQs.")

    def process_article_conclusion(self, ai_json: Dict[str, Any], article: Any):
        """
        Process the AI response for an article conclusion and update the article object.
        Wraps the conclusion in a <p> tag.
        Expected JSON structure:
        {
            "conclusion": "Conclusion text here."
        }
        """
        if "conclusion" in ai_json:
            article.conclusion = f"<p>{ai_json['conclusion']}</p>"
        else:
            raise ValueError("Expected 'conclusion' key in AI response for Article Conclusion.")
