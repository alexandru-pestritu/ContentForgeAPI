from app.models.gutenberg_blocks.custom_blocks import AffiliateButtonBlock, PromoBoxBlock, ProsConsBlock, ReviewHeadingBlock, SliderBlock
from app.models.gutenberg_blocks.default_blocks import HeadingBlock, ParagraphBlock
from app.models.image import Image
from app.schemas.product import ProductResponse
from app.services.wordpress_service import WordPressService
from app.crud.crud_store import get_store_by_id
from app.models.product import Product
from app.models.store import Store
from app.schemas.stores import StoreResponse
from sqlalchemy.orm import Session

class ProductTemplate:
    def __init__(self, product: ProductResponse, db: Session, wp_service: WordPressService, position: int = 1):
        self.product = product
        self.db = db
        self.wp_service = wp_service
        self.position = position
        self.store = self._get_store()  
        self.images = []  

    def _get_store(self):
        store_id = self.product.store_ids[0]
        store = get_store_by_id(self.db, store_id)
        return store

    async def _get_image(self, image_id: int):
        return await self.wp_service.get_image_by_id(image_id)

    async def _get_images(self):
        image_ids = self.product.image_ids
        images = []
        for image_id in image_ids:
            image = await self._get_image(image_id)
            if image: 
                images.append(image)
        return images

    async def render_review_heading(self) -> str:
        title = f'<a href="{self.product.affiliate_urls[0]}">{self.product.name}</a>'
        subtitle = self.product.seo_keyword
        return ReviewHeadingBlock(position=self.position, title=title, subtitle=subtitle).render()

    async def render_slider(self) -> str:
        """
        Renders the slider block.
        """
        if not self.images:
            self.images = await self._get_images()

        slides = []
        for image in self.images:
            slides.append({
                "id": image.id,
                "url": image.url,
                "width": image.width,
                "height": image.height,
                "alt": image.alt_text
            })
        return SliderBlock(slides=slides).render()

    async def render_promobox(self) -> str:
        specifications = self.product.specifications
        content = " | ".join([f"<strong>{key}</strong>: {value}" for key, value in specifications.items()])
        return PromoBoxBlock(
            title="",
            content=f'<p style="font-size:16px; text-align:justify;">{content}</p>',
            background_color="#f5f5f5",
            show_border=True,
            highlight_color="#bf000a",
            button_text="Verifică preț",
            button_link=self.product.affiliate_urls[0]
        ).render()

    async def render_pros_cons(self) -> str:
        pros = self.product.pros
        cons = self.product.cons
        return ProsConsBlock(
            pros_items=pros,
            cons_items=cons,
            pros_title="Pro",
            cons_title="Contra",
            pros_bg_color="#339900",
            pros_icon_color="#339900",
            cons_bg_color="#bf000a",
            cons_icon_color="#bf000a"
        ).render()

    async def render_review(self) -> str:
        paragraphs = self.product.review.split("<p>")
        review_blocks = []
        review_blocks.append(HeadingBlock(level=4, content="Recenzie").render())
        for paragraph in paragraphs[:-1]:
            cleaned_paragraph = paragraph.replace("</p>", "")
            review_blocks.append(ParagraphBlock(content=cleaned_paragraph).render())
        review_blocks.append(HeadingBlock(level=4, content="Verdict").render())
        final_paragraph = paragraphs[-1].replace("</p>", "")
        review_blocks.append(ParagraphBlock(content=final_paragraph).render())
        return "\n".join(review_blocks)


    async def render_affiliate_button(self) -> str:
        affiliate_url = self.product.affiliate_urls[0]
        if self.store and self.store.favicon_image_id:
            image = await self.wp_service.get_image_by_id(self.store.favicon_image_id)
        else:
            image = Image({
                "id": 0,
                "source_url": "",
                "mime_type": "",
                "title": {"rendered": ""},
                "alt_text": "",
                "media_details": {"width": 0, "height": 0, "sizes": {}},
                "author": 0,
                "modified": "",
                "post": 0
            })

        return AffiliateButtonBlock(
            affiliate_link=affiliate_url,
            button_text="Verifică preț",
            image_url=image.url,
            image_alt=image.alt_text,
            image_width=image.width,
            image_height=image.height,
            affiliate_text=self.store.name if self.store else ""
        ).render()


    async def render(self) -> str:
        """
        Renders the full product template.
        """

        blocks = [
            await self.render_review_heading(),
            await self.render_slider(),
            await self.render_promobox(),
            await self.render_pros_cons(),
            await self.render_review(),
            await self.render_affiliate_button(),
        ]
        return "\n".join(blocks)

