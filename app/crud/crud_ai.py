from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.article import Article
from app.schemas.article import ArticleResponse
from app.schemas.product import ProductResponse
from app.services.edenai_service import EdenAIService
from app.services.prompt_processing_service import PromptProcessingService
from app.services.ai_response_processing_service import AIResponseProcessingService
from typing import Dict, Any, Optional

edenai_service = EdenAIService()
prompt_processing_service = PromptProcessingService()
ai_response_processor = AIResponseProcessingService()

async def get_providers_by_feature_and_subfeature(feature_name: str, subfeature_name: str) -> dict:
    """
    Fetch providers and available models for a specific feature and subfeature using EdenAI.

    :param feature_name: The name of the feature (e.g., 'text').
    :param subfeature_name: The name of the subfeature (e.g., 'chat').
    :return: A dictionary containing the providers, their models, and associated costs.
    """
    try:
        providers_data = await edenai_service.get_providers_and_models(feature_name, subfeature_name)
        return providers_data
    except Exception as e:
        raise ValueError(f"Error retrieving providers: {str(e)}")

async def generate_product_text(
    db: Session, 
    product_id: int, 
    prompt_id: int, 
    provider: str, 
    model: str
) -> Dict[str, Any]:
    """
    Generate text for a product using EdenAI and update the product based on the AI response.

    :param db: Database session.
    :param product_id: The ID of the product.
    :param prompt_id: The ID of the prompt.
    :param provider: The provider to use (e.g., 'openai').
    :param model: The model to use (e.g., 'gpt-4o').
    :return: A dictionary containing the updated product and the cost of the operation.
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found.")

        prompt_text = prompt_processing_service.prepare_product_prompt_for_ai(db, prompt_id, product_id)
        if not prompt_text:
            raise ValueError("Failed to prepare product prompt for AI.")

        if model=="default":
            provider_model = provider
        else:
            provider_model = f"{provider}/{model}"  
        providers = [provider_model]

        ai_response = await edenai_service.execute_chat_prompt(providers, prompt_text)
        if provider_model not in ai_response:
            raise ValueError(f"No response from provider {provider_model}.")

        ai_response_processor.process_response(db, ai_response[provider_model]['generated_text'], prompt_id, product)

        db.commit()

        return {
            "product": ProductResponse.from_orm(product),
            "cost": ai_response[provider_model]['cost']
        }

    except Exception as e:
        raise ValueError(f"Error generating product text: {str(e)}")

async def generate_article_text(
    db: Session, 
    article_id: int, 
    prompt_id: int, 
    provider: str, 
    model: str
) -> Dict[str, Any]:
    """
    Generate text for an article using EdenAI and update the article based on the AI response.

    :param db: Database session.
    :param article_id: The ID of the article.
    :param prompt_id: The ID of the prompt.
    :param provider: The provider to use (e.g., 'openai').
    :param model: The model to use (e.g., 'gpt-4o').
    :return: A dictionary containing the updated article and the cost of the operation.
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise ValueError(f"Article with ID {article_id} not found.")

        prompt_text = prompt_processing_service.prepare_article_prompt_for_ai(db, prompt_id, article_id)
        if not prompt_text:
            raise ValueError("Failed to prepare article prompt for AI.")

        if model=="default":
            provider_model = provider
        else:
            provider_model = f"{provider}/{model}"  
        providers = [provider_model]

        ai_response = await edenai_service.execute_chat_prompt(providers, prompt_text)
        if provider_model not in ai_response:
            raise ValueError(f"No response from provider {provider_model}.")

        ai_response_processor.process_response(db, ai_response[provider_model]['generated_text'], prompt_id, article)

        db.commit()

        return {
            "article": ArticleResponse.from_orm(article),
            "cost": ai_response[provider_model]['cost']
        }

    except Exception as e:
        raise ValueError(f"Error generating article text: {str(e)}")
