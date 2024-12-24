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
            {"key": "scraping.api.crawlbase_api_key", "value": "your_crawlbase_api_key", "type": "string", "description": "API Key for Crawlbase scraping service."},
            {"key": "scraping.api.scrapingfish_api_key", "value": "your_scrapingfish_api_key", "type": "string", "description": "API Key for Scrapingfish fallback scraping service."},
            {"key": "scraping.log.stock_check_interval", "value": "14", "type": "integer", "description": "Interval in days for checking product stock availability."},

            # AI Generation
            {"key": "ai.api.edenai_api_key", "value": "your_edenai_api_key", "type": "string", "description": "API Key for EdenAI content generation service."},
            {"key": "ai.provider.default", "value": "openai", "type": "string", "description": "Default AI provider for content generation."},
            {"key": "ai.model.default", "value": "gpt-4o", "type": "string", "description": "Default AI model for content generation."},
            {"key": "ai.parameters.temperature", "value": "0.1", "type": "float", "description": "Temperature for AI model."},
            {"key": "ai.parameters.max_tokens", "value": "4096", "type": "integer", "description": "Maximum tokens for AI model."},
            {"key": "ai.parameters.timeout", "value": "120", "type": "integer", "description": "Timeout for AI generation requests in seconds."},

            # Specifications Filtering
            {"key": "specifications.filtering.max_specs", "value": "10", "type": "integer", "description": "Maximum number of specifications to display in WordPress widget."},
            {"key": "specifications.filtering.specs_to_place_last", "value": "Functii,Continut pachet", "type": "string", "description": "Specifications to always place at the end of the list."},
            {"key": "specifications.filtering.relevance_threshold", "value": "0.5", "type": "float", "description": "Relevance threshold for specifications order."},
            {"key": "specifications.filtering.variability_threshold", "value": "0.5", "type": "float", "description": "Variability threshold for specifications order."},

            # Images - Store
            {"key": "images.store.width", "value": "16", "type": "integer", "description": "Store image width."},
            {"key": "images.store.height", "value": "16", "type": "integer", "description": "Store image height."},
            {"key": "images.store.file_name", "value": "{name}", "type": "string", "description": "File name pattern for store images."},
            {"key": "images.store.alt_text", "value": "favicon magazin online {name}", "type": "string", "description": "Alt text pattern for store images."},

            # Images - Product
            {"key": "images.product.width", "value": "1080", "type": "integer", "description": "Product image width."},
            {"key": "images.product.height", "value": "1080", "type": "integer", "description": "Product image height."},
            {"key": "images.product.file_name", "value": "{name}", "type": "string", "description": "File name pattern for product images."},
            {"key": "images.product.alt_text", "value": "{full_name}", "type": "string", "description": "Alt text pattern for product images."},

            # Images - Article Main
            {"key": "images.article_main.width", "value": "1400", "type": "integer", "description": "Article main image width."},
            {"key": "images.article_main.height", "value": "960", "type": "integer", "description": "Article main image height."},
            {"key": "images.article_main.file_name", "value": "{title}", "type": "string", "description": "File name pattern for main article images."},
            {"key": "images.article_main.alt_text", "value": "{seo_keywords}", "type": "string", "description": "Alt text pattern for main article images."},

            # Images - Article Guide
            {"key": "images.article_guide.width", "value": "1400", "type": "integer", "description": "Buyer's guide image width."},
            {"key": "images.article_guide.height", "value": "960", "type": "integer", "description": "Buyer's guide image height."},
            {"key": "images.article_guide.file_name", "value": "cum aleg {seo_keywords}", "type": "string", "description": "File name pattern for buyer's guide images."},
            {"key": "images.article_guide.alt_text", "value": "ghidul cumparatorului pentru {seo_keywords}", "type": "string", "description": "Alt text pattern for buyer's guide images."},
        ]

        with SessionLocal() as db:
            for default_setting in default_settings:
                existing = get_setting_by_key(db, default_setting["key"])
                if not existing:
                    create_setting(db, SettingCreate(**default_setting))
