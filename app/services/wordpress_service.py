import os
import httpx
import base64
from dotenv import load_dotenv
from typing import Optional
import mimetypes

load_dotenv()

class WordPressService:
    def __init__(self):
        self.base_url = os.getenv("WORDPRESS_BASE_URL")
        self.username = os.getenv("WORDPRESS_USERNAME")
        self.api_key = os.getenv("WORDPRESS_API_KEY")
        self.token = self._generate_token()

    def _generate_token(self) -> str:
        """
        Generate the Basic Auth token using the username and API key.
        """
        wp_connection = f"{self.username}:{self.api_key}"
        token = base64.b64encode(wp_connection.encode()).decode('utf-8')
        return token

    async def upload_image(self, image_path: str, file_name: str, alt_text: Optional[str] = None) -> Optional[int]:
        """
        Upload an image to WordPress and return its ID. Optionally set the alt text.
        """
        url = f"{self.base_url}/media"
        headers = {
            'Authorization': f'Basic {self.token}',
            'Content-Disposition': f'attachment; filename={file_name}',
        }

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        with open(image_path, 'rb') as file:
            files = {'file': (file_name, file, mime_type)}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, files=files, timeout=60.0)
                response.raise_for_status()
                
                data = response.json()
                image_id = data.get('id')

                if alt_text and image_id:
                    await self.set_alt_text(image_id, alt_text)

                return image_id

    async def set_alt_text(self, image_id: int, alt_text: str):
        """
        Set the alt text for an image already uploaded to WordPress.
        """
        url = f"{self.base_url}/media/{image_id}"
        headers = {
            'Authorization': f'Basic {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'alt_text': alt_text
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()

    async def get_image_info(self, image_id: int) -> dict:
        """
        Retrieve information about an image from WordPress using its ID.
        """
        url = f"{self.base_url}/media/{image_id}"
        headers = {
            'Authorization': f'Basic {self.token}',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        
    async def get_users(self) -> list:
        """
        Retrieve a list of users from WordPress.
        """
        url = f"{self.base_url}/users"
        headers = {
            'Authorization': f'Basic {self.token}',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_categories(self) -> list:
        """
        Retrieve a list of categories from WordPress.
        """
        url = f"{self.base_url}/categories"
        headers = {
            'Authorization': f'Basic {self.token}',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()