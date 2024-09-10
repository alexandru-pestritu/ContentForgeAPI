import uuid
from app.models.gutenberg_blocks.gutenberg_block import GutenbergBlock

class ReviewHeadingBlock(GutenbergBlock):
    def __init__(self, position: int, title: str, subtitle: str, image: dict = None):
        unicode_title = self.escape_to_unicode(title)
        escaped_subtitle = self.escape_to_unicode(subtitle)

        self.attrs = {
            "position": position,
            "title": unicode_title,
            "subtitle": escaped_subtitle,
            "image": image if image else {"id": "", "url": "", "width": "", "height": "", "alt": ""}
        }

    def attrs_to_string(self) -> str:
        """Manually convert attributes to a string in the expected format."""
        image = self.attrs["image"]
        return (f'{{"position":"{self.attrs["position"]}",'
                f'"title":"{self.attrs["title"]}",'
                f'"subtitle":"{self.attrs["subtitle"]}",'
                f'"image":{{"id":"{image["id"]}","url":"{image["url"]}","width":"{image["width"]}","height":"{image["height"]}","alt":"{image["alt"]}"}}}}')

    def render(self) -> str:
        """Render the block with manual JSON-like format for attributes."""
        attrs_str = self.attrs_to_string()
        return f'<!-- wp:rehub/review-heading {attrs_str} --><div id="{self.attrs["position"]}-{self.attrs["subtitle"].replace(" ", "-").lower()}" class="wp-block-rehub-review-heading"></div><!-- /wp:rehub/review-heading -->'

class SliderBlock(GutenbergBlock):
    def __init__(self, slides: list):
        """
        :param slides: List of slides, each being a dictionary containing image details.
        """
        formatted_slides = [{"image": slide} for slide in slides]
        attrs = {"slides": formatted_slides}
        super().__init__(block_type="rehub/slider", attrs=attrs)

    def render(self) -> str:
        slides_html = ','.join([f'{{"image":{{"id":{slide["image"]["id"]},"url":"{slide["image"]["url"]}","width":{slide["image"]["width"]},"height":{slide["image"]["height"]},"alt":"{slide["image"]["alt"]}"}}}}' for slide in self.attrs["slides"]])
        return f'<!-- wp:rehub/slider {self.attrs_to_string()} /-->'


class PromoBoxBlock(GutenbergBlock):
    def __init__(self, title: str, content: str, background_color: str, show_border: bool, highlight_color: str, button_text: str, button_link: str):
        """
        :param title: The title of the promo box.
        :param content: The content of the promo box (HTML).
        :param background_color: Background color of the box.
        :param show_border: Whether to show a border or not.
        :param highlight_color: Highlight color for the box.
        :param button_text: Text for the button.
        :param button_link: URL link for the button.
        """
        escaped_content = self.escape_to_unicode(content)
        escaped_title = self.escape_to_unicode(title)

        attrs = {
            "title": escaped_title,
            "content": escaped_content,
            "backgroundColor": background_color,
            "showBorder": show_border,
            "highlightColor": highlight_color,
            "buttonText": button_text,
            "buttonLink": button_link
        }
        super().__init__(block_type="rehub/promo-box", attrs=attrs)

    def attrs_to_string(self) -> str:
        """Manually convert attributes to a string in the expected format."""
        return (f'{{"title":"{self.attrs["title"]}",'
                f'"content":"{self.attrs["content"]}",'
                f'"backgroundColor":"{self.attrs["backgroundColor"]}",'
                f'"showBorder":{str(self.attrs["showBorder"]).lower()},'
                f'"highlightColor":"{self.attrs["highlightColor"]}",'
                f'"buttonText":"{self.attrs["buttonText"]}",'
                f'"buttonLink":"{self.attrs["buttonLink"]}"}}')

    def render(self) -> str:
        """Render the block with manual JSON-like format for attributes."""
        return f'<!-- wp:rehub/promo-box {self.attrs_to_string()} /-->'


class ProsConsBlock(GutenbergBlock):
    def __init__(self, pros_items: list, cons_items: list, pros_title: str, cons_title: str, pros_bg_color: str, pros_icon_color: str, cons_bg_color: str, cons_icon_color: str):
        """
        :param pros_items: List of pros (advantages).
        :param cons_items: List of cons (disadvantages).
        :param pros_title: Title for the pros section.
        :param cons_title: Title for the cons section.
        :param pros_bg_color: Background color for the pros section.
        :param pros_icon_color: Icon color for the pros section.
        :param cons_bg_color: Background color for the cons section.
        :param cons_icon_color: Icon color for the cons section.
        """
        unique_id = uuid.uuid4().hex[:6]  
        block_id = str(uuid.uuid4()) 
        
        attrs = {
            "uniqueId": unique_id,
            "block_id": block_id,
            "boxShadow": {
                "openShadow": 0,
                "inset": 0,
                "horizontal": 0,
                "vertical": 8,
                "blur": 35,
                "spread": 0,
                "color": "rgba(0,0,0,0.10)"
            },
            "listTextItems": pros_items,
            "listTextItemsTwo": cons_items,
            "propsTitle": pros_title,
            "consTitle": cons_title,
            "propsBgColor": pros_bg_color,
            "propsIconColor": pros_icon_color,
            "consBgColor": cons_bg_color,
            "consIconColor": cons_icon_color
        }
        super().__init__(block_type="affiliate-booster/propsandcons", attrs=attrs)
        self.unique_id = unique_id
        self.block_id = block_id

    def render(self) -> str:
        return (
            f'<!-- wp:affiliate-booster/propsandcons {self.attrs_to_string()} -->'
            f'<div id="affiliate-style-{self.block_id}" class="wp-block-affiliate-booster-propsandcons affiliate-block-{self.unique_id} affiliate-wrapper">'
            f'<div class="affiliate-d-table affiliate-procon-inner">'
            f'<div class="affiliate-block-advanced-list affiliate-props-list affiliate-alignment-left">'
            f'<p class="affiliate-props-title affiliate-propcon-title"> {self.attrs["propsTitle"]} </p>'
            f'<ul class="affiliate-list affiliate-list-type-unordered affiliate-list-bullet-check-circle">'
            + ''.join([f'<li>{pro}</li>' for pro in self.attrs["listTextItems"]]) +
            f'</ul></div>'
            f'<div class="affiliate-block-advanced-list affiliate-cons-list affiliate-alignment-left">'
            f'<p class="affiliate-const-title affiliate-propcon-title"> {self.attrs["consTitle"]} </p>'
            f'<ul class="affiliate-list affiliate-list-type-unordered affiliate-list-bullet-times-circle">'
            + ''.join([f'<li>{con}</li>' for con in self.attrs["listTextItemsTwo"]]) +
            f'</ul></div></div></div>'
            f'<!-- /wp:affiliate-booster/propsandcons -->'
        )


class AffiliateButtonBlock(GutenbergBlock):
    def __init__(self, affiliate_link: str, button_text: str, image_url: str, image_alt: str, image_width: int = 16, image_height: int = 16, affiliate_text: str = ""):
        """
        :param affiliate_link: The affiliate URL link.
        :param button_text: The text displayed on the button.
        :param image_url: The URL of the image displayed in the affiliate tag.
        :param image_alt: The alt text for the image.
        :param image_width: The width of the image (default is 16).
        :param image_height: The height of the image (default is 16).
        :param affiliate_text: The text next to the affiliate image (e.g., "emag.ro").
        """
        self.affiliate_link = affiliate_link
        self.button_text = button_text
        self.image_url = image_url
        self.image_alt = image_alt
        self.image_width = image_width
        self.image_height = image_height
        self.affiliate_text = affiliate_text
        super().__init__(block_type="html", attrs={})

    def render(self) -> str:
        """
        Render the block as a Gutenberg HTML block.
        """
        return f"""
        <!-- wp:html -->
        <div class="buttons_col mb25 rh_big_btn_inline">
            <div class="priced_block clearfix">
                <a class="re_track_btn btn_offer_block" href="{self.affiliate_link}" target="_blank" rel="nofollow sponsored noopener">{self.button_text}</a>
                <span class="aff_tag">
                    <img decoding="async" src="{self.image_url}" height="{self.image_height}" width="{self.image_width}" alt="{self.image_alt}"> {self.affiliate_text}
                </span>	               
            </div>
        </div>
        <br><br>
        <!-- /wp:html -->
        """


class AccordionBlock(GutenbergBlock):
    def __init__(self, tabs: list[dict]):
        """
        :param tabs: A list of dictionaries where each dictionary contains the 'title' and 'content' for a tab.
        Example:
        [
            {"title": "What are the advantages of wireless headphones?", "content": "Wireless headphones..."},
            {"title": "How does active noise cancellation work?", "content": "Active noise cancellation..."}
        ]
        """
        self.tabs = tabs
        super().__init__(block_type="rehub/accordion", attrs={})

    def render(self) -> str:
        """
        Render the accordion block as a Gutenberg-compatible HTML block.
        """
        tabs_json = []
        for tab in self.tabs:
            title = tab.get("title", "")
            content = tab.get("content", "")
            tabs_json.append(f'{{"title":"{title}","content":"{content}"}}')

        tabs_content = ','.join(tabs_json)
        return f'<!-- wp:rehub/accordion {{"tabs":[{tabs_content}]}} /-->'


class ComparisonItemBlock:
    def __init__(self, badge_color: str, product_image: dict, product_title: str, product_subtitle: str, number_value: int, 
                 bottom_text: str, pros_text: str, cons_text: str, spec_text: str, button_url: str, button_text: str, 
                 button_target: bool, button_color: str, enable_badge: bool, enable_numbers: bool, enable_list_title: bool, 
                 bottom_title: str, pros_title: str, cons_title: str):
        """
        :param badge_color: Hex code for the badge color.
        :param product_image: Dictionary containing all the image properties including 'id', 'url', 'width', 'height', etc.
        :param product_title: Title of the product.
        :param product_subtitle: Subtitle of the product.
        :param number_value: The rank or number value for the product in the comparison.
        :param bottom_text: The bottom text, typically specifications.
        :param pros_text: Text detailing the pros of the product.
        :param cons_text: Text detailing the cons of the product.
        :param spec_text: Text detailing the specifications of the product.
        :param button_url: The URL for the "Check Price" button.
        :param button_text: Text for the button.
        :param button_target: Whether the button opens in a new tab (True/False).
        :param button_color: Hex code for the button color.
        :param enable_badge: Whether to display a badge (True/False).
        :param enable_numbers: Whether to display numbers (True/False).
        :param enable_list_title: Whether to enable a list title (True/False).
        :param bottom_title: Title for the bottom section, typically "Specifications".
        :param pros_title: Title for the pros section, typically "Pros".
        :param cons_title: Title for the cons section, typically "Cons".
        """
        self.badge_color = badge_color
        self.product_image = product_image
        self.product_title = product_title
        self.product_subtitle = product_subtitle
        self.number_value = number_value
        self.bottom_text = bottom_text
        self.pros_text = pros_text
        self.cons_text = cons_text
        self.spec_text = spec_text
        self.button_url = button_url
        self.button_text = button_text
        self.button_target = button_target
        self.button_color = button_color
        self.enable_badge = enable_badge
        self.enable_numbers = enable_numbers
        self.enable_list_title = enable_list_title
        self.bottom_title = bottom_title
        self.pros_title = pros_title
        self.cons_title = cons_title

    def render(self) -> str:
        """
        Render the ComparisonItemBlock as a valid Gutenberg block.
        """
        return (f'<!-- wp:rehub/comparison-item {{"badgeColor":"{self.badge_color}","productImage":{self.product_image},'
                f'"productTitle":"{self.product_title}","productSubtitle":"{self.product_subtitle}","numberValue":"{self.number_value}",'
                f'"bottomText":"{self.bottom_text}","prosText":"{self.pros_text}","consText":"{self.cons_text}",'
                f'"specText":"{self.spec_text}","buttonUrl":"{self.button_url}","buttonText":"{self.button_text}",'
                f'"buttonTarget":{str(self.button_target).lower()},"buttonColor":"{self.button_color}","enableBadge":{str(self.enable_badge).lower()},'
                f'"enableNumbers":{str(self.enable_numbers).lower()},"enableListTitle":{str(self.enable_list_title).lower()},'
                f'"bottomTitle":"{self.bottom_title}","prosTitle":"{self.pros_title}","consTitle":"{self.cons_title}"}} /-->')


class ComparisonTableBlock:
    def __init__(self, enable_numbers: bool, enable_list_title: bool, bottom_title: str, pros_title: str, cons_title: str, 
                 align: str, items: list[ComparisonItemBlock]):
        """
        :param enable_numbers: Whether to display item numbers in the comparison table (True/False).
        :param enable_list_title: Whether to enable the list title (True/False).
        :param bottom_title: Title for the bottom section, typically "Specifications".
        :param pros_title: Title for the pros section, typically "Pros".
        :param cons_title: Title for the cons section, typically "Cons".
        :param align: Alignment of the table (e.g., 'wide').
        :param items: List of ComparisonItemBlock instances for each item/product in the table.
        """
        self.enable_numbers = enable_numbers
        self.enable_list_title = enable_list_title
        self.bottom_title = bottom_title
        self.pros_title = pros_title
        self.cons_title = cons_title
        self.align = align
        self.items = items

    def render(self) -> str:
        """
        Render the ComparisonTableBlock along with its inner items.
        """
        items_content = '\n'.join([item.render() for item in self.items])
        return (f'<!-- wp:rehub/comparison-table {{"enableNumbers":{str(self.enable_numbers).lower()},"enableListTitle":'
                f'{str(self.enable_list_title).lower()},"bottomTitle":"{self.bottom_title}","prosTitle":"{self.pros_title}",'
                f'"consTitle":"{self.cons_title}","align":"{self.align}"}} -->\n'
                f'{items_content}\n<!-- /wp:rehub/comparison-table -->')
