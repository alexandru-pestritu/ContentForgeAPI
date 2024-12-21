import re
from typing import Tuple, Optional
from app.services.placeholder_service import PlaceholderService
from app.services.settings_service import SettingsService

class ImageMetadataService:
    def __init__(self, placeholder_service: PlaceholderService):
        self.placeholder_service = placeholder_service

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to ensure it is safe for use by removing special or invalid characters.
        """
        sanitized = re.sub(r'[^\w\-_]', '-', filename)
        sanitized = re.sub(r'-{2,}', '-', sanitized)
        sanitized = sanitized.strip('-')
        return sanitized

    def generate_metadata(self, entity_type: str, entity: object, output_json: Optional[dict] = None) -> Tuple[str, str]:
        """
        Generate file name and alt text metadata for a given entity type using settings and placeholders.
        """
        file_name_template = SettingsService.get_setting_value(f"{entity_type}_image_file_name")
        alt_text_template = SettingsService.get_setting_value(f"{entity_type}_image_alt_text")

        if entity_type == "product":
            replacements = self.placeholder_service.get_replacements_for_product(entity, output_json)
        elif entity_type in {"article_main", "article_guide"}:
            replacements = self.placeholder_service.get_replacements_for_article(entity, output_json)
        elif entity_type == "store":
            replacements = self.placeholder_service.get_replacements_for_store(entity)
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        file_name = self.placeholder_service.replace_placeholders(file_name_template, replacements)
        alt_text = self.placeholder_service.replace_placeholders(alt_text_template, replacements)

        file_name = self.sanitize_filename(file_name)
        
        return file_name, alt_text
