from app.database import SessionLocal
from app.schemas.settings import SettingCreate, SettingResponse
from app.crud.crud_settings import get_setting_by_key, create_setting
from typing import Any

class SettingsService:
    """
    Service class for managing settings.
    """

    @staticmethod
    def get_setting_value(key: str) -> Any:
        """
        Returns the value of a setting by its key.
        """
        with SessionLocal() as db:
            setting = get_setting_by_key(db, key)
            if not setting:
                raise ValueError(f"Setting with key '{key}' not found")

            if setting.type == "integer":
                return int(setting.value)
            elif setting.type == "float":
                return float(setting.value)
            elif setting.type == "boolean":
                return setting.value.lower() in ["true", "1", "yes"]
            elif setting.type == "string":
                return setting.value
            else:
                raise ValueError(f"Unsupported setting type: {setting.type}")

    @staticmethod
    def initialize_default_settings():
        """
        Initializes the default settings.
        """
        default_settings = [
            # Scraping
            {"key": "crawlbase_api_key", "value": "", "type": "string", "description": "API Key for Crawlbase scraping service."},
            {"key": "scrapingfish_api_key", "value": "", "type": "string", "description": "API Key for Scrapingfish fallback scraping service."},
            {"key": "stock_check_log_interval", "value": "14", "type": "integer", "description": "Interval in days for checking product stock availability."},
            {"key": "scrape_data_when_adding_product", "value": "true", "type": "boolean", "description": "Scrape data automatically when adding a product."},

            # AI Generation
            {"key": "edenai_api_key", "value": "", "type": "string", "description": "API Key for EdenAI content generation service."},
            {"key": "ai_default_provider", "value": "openai", "type": "string", "description": "Default AI provider for content generation."},
            {"key": "ai_default_model", "value": "gpt-4o", "type": "string", "description": "Default AI model for content generation."},
            {"key": "ai_temperature", "value": "0.1", "type": "float", "description": "Temperature for AI model."},
            {"key": "ai_max_tokens", "value": "4096", "type": "integer", "description": "Maximum tokens for AI model."},
            {"key": "ai_timeout", "value": "120", "type": "integer", "description": "Timeout for AI generation requests in seconds."},

            # Specifications Filtering
            {"key": "max_specs", "value": "10", "type": "integer", "description": "Maximum number of specifications to display in WordPress widget."},
            {"key": "specs_to_place_last", "value": "", "type": "string", "description": "Specifications to always place at the end of the list."},
            {"key": "spec_relevance_percentage", "value": "0.5", "type": "float", "description": "Relevance threshold for specifications order."},
            {"key": "spec_variability_percentage", "value": "0.5", "type": "float", "description": "Variability threshold for specifications order."},

            # Images - Store
            {"key": "store_image_width", "value": "16", "type": "integer", "description": "Store image width."},
            {"key": "store_image_height", "value": "16", "type": "integer", "description": "Store image height."},
            {"key": "store_image_file_name", "value": "", "type": "string", "description": "File name pattern for store images."},
            {"key": "store_image_alt_text", "value": "", "type": "string", "description": "Alt text pattern for store images"},

            # Images - Product
            {"key": "product_image_width", "value": "1080", "type": "integer", "description": "Product image width."},
            {"key": "product_image_height", "value": "1080", "type": "integer", "description": "Product image height."},
            {"key": "product_image_file_name", "value": "", "type": "string", "description": "File name pattern for product images."},
            {"key": "product_image_alt_text", "value": "", "type": "string", "description": "Alt text pattern for product images."},

            # Images - Article
            # Main image
            {"key": "article_main_image_width", "value": "1400", "type": "integer", "description": "Article main image width"},
            {"key": "article_main_image_height", "value": "960", "type": "integer", "description": "Article main image height"},
            {"key": "article_main_image_file_name", "": "main_image", "type": "string", "description": "File name pattern for main article images."},
            {"key": "article_main_image_alt_text", "": "Main article image", "type": "string", "description": "Alt text pattern for main article images."},
            
            # Buyer's Guide image
            {"key": "article_guide_image_width", "value": "1400", "type": "integer", "description": "Buyer's guide image width."},
            {"key": "article_guide_image_height", "value": "960", "type": "integer", "description": "Buyer's guide image height."},
            {"key": "article_guide_image_file_name", "": "guide_image", "type": "string", "description": "File name pattern for buyer's guide images."},
            {"key": "article_guide_image_alt_text", "": "Buyer's guide image", "type": "string", "description": "Alt text pattern for buyer's guide images."},
        ]

        with SessionLocal() as db:
            for default_setting in default_settings:
                existing = get_setting_by_key(db, default_setting["key"])
                if not existing:
                    create_setting(db, SettingCreate(**default_setting))
