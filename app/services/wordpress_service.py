import aiohttp
import httpx
import base64
import mimetypes
from typing import Optional, List, Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urljoin

from app.models.blog import Blog
from app.models.image import Image
from app.schemas.article import ArticleResponse

class WordPressService:
    """
    A service class for interacting with a specific WordPress instance, determined by blog_id.
    """

    def __init__(self, blog_id: int, db: Session):
        """
        Initializes the WordPressService with credentials based on the given blog_id.
        
        :param blog_id: The ID of the blog from which to retrieve WordPress credentials.
        :param db: The database session used to query the blogs table.
        :raises HTTPException: If no blog with the given ID is found.
        """
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(status_code=404, detail=f"Blog with id={blog_id} not found.")
        base_url = blog.base_url.rstrip("/")
        if not base_url.endswith("wp-json/wp/v2"):
            base_url = f"{base_url}/wp-json/wp/v2"
        self.base_url = base_url
        self.username = blog.username
        self.api_key = blog.api_key
        self.token = self._generate_token()

    def _generate_token(self) -> str:
        """
        Generates a Basic Auth token using the username and API key.

        :return: A Base64-encoded string for Authorization header.
        """
        wp_connection = f"{self.username}:{self.api_key}"
        token = base64.b64encode(wp_connection.encode()).decode('utf-8')
        return token

    async def upload_image(self, image_path: str, file_name: str, alt_text: Optional[str] = None) -> Optional[int]:
        """
        Uploads an image to WordPress and returns its ID. Optionally sets the alt text.

        :param image_path: The local file path of the image to upload.
        :param file_name: The name of the file to be stored in WordPress.
        :param alt_text: Optional alt text for the image.
        :return: The WordPress media ID of the uploaded image, or None if the upload fails.
        """
        url = f"{self.base_url}/media"

        headers = {
            'Authorization': f'Basic {self.token}',
        }

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        extension = mimetypes.guess_extension(mime_type) or ".jpg"
        if not file_name.endswith(extension):
            file_name += extension

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
        except OSError as e:
            print(f"Error reading file {image_path}: {e}")
            return None

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
                        print(f"Error uploading image: status={response.status}")
                        print(f"Response content: {await response.text()}")
                        return None
                    response_data = await response.json()
                    image_id = response_data.get('id')
                    return image_id
            except aiohttp.ClientError as e:
                print(f"Error uploading image: {e}")
                return None

    async def set_alt_text(self, image_id: int, alt_text: str) -> None:
        """
        Sets the alt text for an existing image in WordPress.

        :param image_id: The WordPress media ID.
        :param alt_text: The alt text to set.
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
        Retrieves an image by its ID from WordPress and returns an Image object.

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

    async def get_users(self) -> List[Dict]:
        """
        Retrieves a list of users from WordPress.

        :return: A list of user dictionaries.
        """
        url = f"{self.base_url}/users"
        headers = {
            'Authorization': f'Basic {self.token}',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_categories(self) -> List[Dict]:
        """
        Retrieves all categories from WordPress, handling pagination if necessary.

        :return: A list of category dictionaries.
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
        Retrieves a post by its ID from WordPress.

        :param post_id: The ID of the post in WordPress.
        :return: A dictionary of post data, or None if not found.
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

        :param article: The ArticleResponse object containing article details.
        :return: The newly created article's ID in WordPress, or None if the request fails.
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
                'yoast_wpseo_focuskw': article.seo_keywords[0] if article.seo_keywords else "",
                'yoast_wpseo_metakeywords': article.seo_keywords[1:] if article.seo_keywords else [],
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                article_data = response.json()
                return article_data.get('id')
        except httpx.HTTPStatusError as exc:
            print(f"Error adding article to WordPress: {exc}")
            return None

    async def update_article(self, article: ArticleResponse) -> Optional[int]:
        """
        Updates an existing article in WordPress using its WP ID.

        :param article: The ArticleResponse containing updated article details.
        :return: The updated article's ID in WordPress, or None if the request fails or WP ID is missing.
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
                'yoast_wpseo_focuskw': article.seo_keywords[0] if article.seo_keywords else "",
                'yoast_wpseo_metakeywords': article.seo_keywords[1:] if article.seo_keywords else [],
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                article_data = response.json()
                return article_data.get('id')
        except httpx.HTTPStatusError as exc:
            print(f"Error updating article in WordPress: {exc}")
            return None
