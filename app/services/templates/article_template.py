from datetime import datetime
import re
from app.models.gutenberg_blocks.default_blocks import SpacerBlock, ParagraphBlock, HeadingBlock, ImageBlock
from app.models.gutenberg_blocks.custom_blocks import AccordionBlock, ComparisonItemBlock, ComparisonTableBlock
from app.schemas.article import ArticleResponse
from app.crud.crud_product import get_product_by_id
from app.services.wordpress_service import WordPressService
from app.services.templates.product_template import ProductTemplate
from sqlalchemy.orm import Session

class ArticleTemplate:
    def __init__(self, article: ArticleResponse, db: Session, wp_service: WordPressService):
        self.article = article
        self.db = db
        self.wp_service = wp_service
        self.current_year = datetime.now().year


    def _get_first_keyword(self):
        if self.article.seo_keywords:
            return self.article.seo_keywords[0].capitalize()
        return ""
    

    async def _get_products(self):
        """
        Retrieves all products associated with the article and their first images.
        """
        products = []
        for product_id in self.article.products_id_list:
            product = get_product_by_id(self.db, product_id)
            if product:
                image_data = None
                if product.image_ids:
                    image_id = product.image_ids[0]
                    image_data = await self.wp_service.get_image_by_id(image_id)
                products.append((product, image_data))
        return products
    

    async def _get_products_templates(self, products):
        """
        Generates ProductTemplate blocks for each product.
        """
        product_templates = []
        for idx, (product, _) in enumerate(products, start=1):
            product_template = ProductTemplate(product, self.db, self.wp_service, position=idx)
            product_templates.append(await product_template.render())
        return "\n".join(product_templates)
    

    async def _render_buyers_guide_image(self):
        if self.article.buyers_guide_image_wp_id:
            image_data = await self.wp_service.get_image_by_id(self.article.buyers_guide_image_wp_id)
            if image_data:
                image_block = ImageBlock(image_id=image_data.id, image_url=image_data.url, alt_text=image_data.alt_text)
                return image_block.render()
        return ""


    def _split_content_to_blocks(self, content: str):
        """
        Splits the content of the buyer's guide into appropriate Gutenberg blocks.
        """
        blocks = []
        parts = re.findall(r'(<h4>.*?</h4>|<p>.*?</p>)', content, re.DOTALL)

        for part in parts:
            if part.startswith('<h4>'):
                heading_content = re.sub(r'<\/?h4>', '', part).strip() 
                blocks.append(HeadingBlock(level=3, content=heading_content).render())
            elif part.startswith('<p>'):
                paragraph_content = re.sub(r'<\/?p>', '', part).strip() 
                blocks.append(ParagraphBlock(content=paragraph_content).render())

        return blocks
    

    def round_rating(self, value: float, step: float = 0.5) -> float:
        """
        Rounds the rating to the nearest step (default step is 0.5).
        """
        return round(value * (1/step)) * step
    

    async def render_comparison_table(self, products):
        """
        Generates the comparison table for the products.
        """
        comparison_items = []
        for idx, (product, image_data) in enumerate(products, start=1):
            if not image_data:
                continue
            
            rounded_rating = self.round_rating(product.rating)

            specifications = product.specifications or {}
            bottom_text = "<br><br>".join([f"<strong>{key}</strong><br>{value}" for key, value in specifications.items()])

            comparison_item = ComparisonItemBlock(
                badge_color="#bf000a",
                product_image={
                    "id": image_data.id,
                    "url": str(image_data.url),
                    "alt": image_data.alt_text,
                    "width": image_data.width,
                    "height": image_data.height
                },
                product_title=product.name,
                product_subtitle=product.seo_keyword.capitalize(),
                number_value=idx,
                starRating=rounded_rating,  
                bottom_text=bottom_text,    
                pros_text="<br>".join([f"<i class='vertmiddle mr10 rhicon rhi-check greencolor font130'></i>{pro}" for pro in product.pros]),
                cons_text="<br>".join([f"<i class='vertmiddle mr10 rhicon rhi-minus redcolor font130'></i>{con}" for con in product.cons]),
                spec_text="",  
                button_url=str(product.affiliate_urls[0]) if product.affiliate_urls else "#",
                button_text="VERIFICĂ PREȚ",
                button_target=True,
                button_color="#bf000a",
                enable_badge=True,
                enable_numbers=True,
                enable_list_title=False,
                bottom_title="Specificații",
                pros_title="Pro",
                cons_title="Contra"
            )
            comparison_items.append(comparison_item)

        comparison_table = ComparisonTableBlock(
            enable_numbers=True,
            enable_list_title=False,
            bottom_title="Specificații",
            pros_title="Pro",
            cons_title="Contra",
            align="wide",
            items=comparison_items
        )
        
        return comparison_table.render()
    

    async def render_introduction(self, products):
        """
        Renders the introduction section with comparison table.
        """
        blocks = []
        blocks.append(SpacerBlock(height="15px").render())

        intro_blocks = self._split_content_to_blocks(self.article.introduction)
        blocks.extend(intro_blocks)

        blocks.append(SpacerBlock(height="5px").render())

        first_keyword = self._get_first_keyword()
        heading_text = f"TOP {len(self.article.products_id_list)} - {first_keyword} în {self.current_year}"
        blocks.append(HeadingBlock(level=2, content=heading_text, font_size="30px", line_height="1.3").render())

        blocks.append(await self.render_comparison_table(products))
        
        blocks.append(SpacerBlock(height="50px").render())

        return "\n".join(blocks)
    

    async def render_buyers_guide(self):
        """
        Renders the buyer's guide section.
        """
        blocks = []

        first_keyword = self._get_first_keyword()
        heading_text = f"Ghidul cumpărătorului pentru {first_keyword} în {self.current_year}"
        blocks.append(HeadingBlock(level=2, content=heading_text).render())

        blocks.append(await self._render_buyers_guide_image())

        guide_blocks = self._split_content_to_blocks(self.article.buyers_guide)
        blocks.extend(guide_blocks)

        blocks.append(SpacerBlock(height="15px").render())
        faq_heading = f"Întrebări frecvente despre {first_keyword.lower()}"
        blocks.append(HeadingBlock(level=3, content=faq_heading).render())

        if self.article.faqs:
            tabs = [{"title": faq["title"], "content": faq["description"]} for faq in self.article.faqs]
            blocks.append(AccordionBlock(tabs=tabs).render())

        blocks.append(HeadingBlock(level=2, content="Concluzie").render())

        conclusion_blocks = self._split_content_to_blocks(self.article.conclusion)
        blocks.extend(conclusion_blocks)

        return "\n".join(blocks) 


    async def render(self) -> str:
        """
        Renders the full article template.
        """
        products = await self._get_products()

        blocks = [
            await self.render_introduction(products),
            await self._get_products_templates(products),
            await self.render_buyers_guide()
        ]
        return "\n".join(blocks)
