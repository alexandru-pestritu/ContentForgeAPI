import os
import aiohttp
import httpx
import base64
from dotenv import load_dotenv
from typing import Optional
import mimetypes

from app.models.image import Image
from app.schemas.article import ArticleResponse

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
        }

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Read the image file
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Use aiohttp to handle the multipart/form-data request
        data = aiohttp.FormData()
        data.add_field(
            'file',
            image_data,
            filename=file_name,
            content_type=mime_type
        )

        if alt_text:
            data.add_field('alt_text', alt_text)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status != 201:
                        print(f"Error uploading image: {response.status}")
                        print(f"Response content: {await response.text()}")
                        return None
                    response_data = await response.json()
                    image_id = response_data.get('id')
                    return image_id
            except aiohttp.ClientError as e:
                print(f"Error uploading image: {e}")
                return None
            

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


    async def get_image_by_id(self, image_id: int) -> Optional[Image]:
        """
        Retrieve an image by its ID from WordPress and return an Image object.

        :param image_id: The ID of the image in WordPress.
        :return: An Image object or None if not found.
        """
        url = f"{self.base_url}/media/{image_id}"
        headers = {
            'Authorization': f'Basic {self.token}',
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                image_data = response.json()
                return Image(image_data)
        except httpx.HTTPStatusError as exc:
            print(f"Error fetching image with ID {image_id}: {exc}")
            return None
        
        
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
        Retrieve all categories from WordPress, handling pagination.
        """
        url = f"{self.base_url}/categories"
        headers = {
            'Authorization': f'Basic {self.token}',
        }

        all_categories = []
        page = 1

        async with httpx.AsyncClient() as client:
            while True:
                params = {
                    'per_page': 100,  
                    'page': page      
                }

                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                categories = response.json()
                if not categories:
                    break  

                all_categories.extend(categories)
                page += 1 

        return all_categories

        
    async def get_post_by_id(self, post_id: int) -> Optional[dict]:
        """
        Retrieve a post by its ID from WordPress.

        :param post_id: The ID of the post in WordPress.
        :return: A dictionary with the post data or None if not found.
        """
        url = f"{self.base_url}/posts/{post_id}"
        headers = {
            'Authorization': f'Basic {self.token}',
            'Content-Type': 'application/json',
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"Error fetching post with ID {post_id}: {exc}")
            return None

        
    async def add_article(self, article: ArticleResponse) -> Optional[int]:
        """
        Adds a new article to WordPress and returns its WP ID.
        """
        url = f"{self.base_url}/posts"
        headers = {
            'Authorization': f'Basic {self.token}',
            'Content-Type': 'application/json',
        }

        data = {
            'title': article.title,
            'slug': article.slug,
            'status': article.status,
            'categories': article.categories_id_list or [], 
            'featured_media': article.main_image_wp_id, 
            'content': article.content,
            'yoast_meta': {
            'yoast_wpseo_title': article.meta_title,
            'yoast_wpseo_metadesc': article.meta_description,
            'yoast_wpseo_focuskw': article.seo_keywords[0],
            'yoast_wpseo_metakeywords': article.seo_keywords[1:],
            }  
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                article_data = response.json()
                wp_id = article_data.get('id')
                return wp_id
        except httpx.HTTPStatusError as exc:
            print(f"Error adding article to WordPress: {exc}")
            return None
        

    async def update_article(self, article: ArticleResponse) -> Optional[int]:
        """
        Updates an existing article in WordPress using its WP ID.
        """
        if not article.wp_id:
            print("Error: WordPress ID is missing for article update.")
            return None
        
        url = f"{self.base_url}/posts/{article.wp_id}"
        headers = {
            'Authorization': f'Basic {self.token}',
            'Content-Type': 'application/json',
        }

        data = {
            'title': article.title,
            'slug': article.slug,
            'status': article.status,
            'categories': article.categories_id_list or [], 
            'featured_media': article.main_image_wp_id,  
            'content': article.content,
            'yoast_meta': {
            'yoast_wpseo_title': article.meta_title,
            'yoast_wpseo_metadesc': article.meta_description,
            'yoast_wpseo_focuskw': article.seo_keywords[0],
            'yoast_wpseo_metakeywords': article.seo_keywords[1:],
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                article_data = response.json()
                wp_id = article_data.get('id')
                return wp_id
        except httpx.HTTPStatusError as exc:
            print(f"Error updating article in WordPress: {exc}")
            return None