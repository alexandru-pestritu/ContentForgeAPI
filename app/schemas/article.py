from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.models.article import Article

class ArticleBase(BaseModel):
    title: str
    slug: str
    categories_id_list: Optional[List[int]]
    author_id: Optional[int]
    status: Optional[str] = "draft"
    seo_keywords: Optional[List[str]]
    meta_title: Optional[str]
    meta_description: Optional[str]
    main_image_url: Optional[HttpUrl]
    buyers_guide_image_url: Optional[HttpUrl]
    products_id_list: Optional[List[int]]

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(ArticleBase):
    wp_id: Optional[int]
    main_image_wp_id: Optional[int]
    buyers_guide_image_wp_id: Optional[int]
    content: Optional[str]
    introduction: Optional[str]
    buyers_guide: Optional[str]
    faqs: Optional[List[dict]]
    conclusion: Optional[str]

class ArticleResponse(ArticleBase):
    id: int
    blog_id: int
    wp_id: Optional[int]
    main_image_wp_id: Optional[int]
    buyers_guide_image_wp_id: Optional[int]
    content: Optional[str]
    introduction: Optional[str]
    buyers_guide: Optional[str]
    faqs: Optional[List[dict]]
    conclusion: Optional[str]

    @classmethod
    def from_orm(cls, article: Article):
        return cls(
            id=article.id,
            blog_id=article.blog_id,
            wp_id=article.wp_id,
            categories_id_list=[category.wp_id for category in article.categories],
            title=article.title,
            slug=article.slug,
            author_id=article.author_id,
            status=article.status,
            seo_keywords=[kw.keyword for kw in article.seo_keywords],
            meta_title=article.meta_title,
            meta_description=article.meta_description,
            main_image_url=HttpUrl(article.main_image_url),
            main_image_wp_id=article.main_image_wp_id,
            buyers_guide_image_url=HttpUrl(article.buyers_guide_image_url),
            buyers_guide_image_wp_id=article.buyers_guide_image_wp_id,
            products_id_list=[product.id for product in article.products],
            content=article.content,
            introduction=article.introduction,
            buyers_guide=article.buyers_guide,
            faqs=[{"title": faq.question, "description": faq.answer} for faq in article.faqs] if article.faqs else None,
            conclusion=article.conclusion,
        )

class Config:
    from_attributes = True

