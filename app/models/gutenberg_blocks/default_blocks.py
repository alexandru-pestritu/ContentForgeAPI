from app.models.gutenberg_blocks.gutenberg_block import GutenbergBlock


class SpacerBlock(GutenbergBlock):
    def __init__(self, height: str):
        attrs = {"height": height}
        super().__init__(block_type="spacer", attrs=attrs)

    def render(self) -> str:
        return f'<!-- wp:spacer {self.attrs_to_string()} --><div style="height:{self.attrs["height"]}" aria-hidden="true" class="wp-block-spacer"></div><!-- /wp:spacer -->'


class ParagraphBlock(GutenbergBlock):
    def __init__(self, content: str):
        super().__init__(block_type="paragraph", inner_content=f"<p>{content}</p>")


class HeadingBlock(GutenbergBlock):
    def __init__(self, level: int, content: str):
        attrs = {"level": level}
        super().__init__(block_type="heading", attrs=attrs, inner_content=content)

    def render(self) -> str:
        return f'<!-- wp:heading {self.attrs_to_string()} --><h{self.attrs["level"]}>{self.inner_content}</h{self.attrs["level"]}><!-- /wp:heading -->'


class ImageBlock(GutenbergBlock):
    def __init__(self, image_id: int, image_url: str, alt_text: str = "", size_slug: str = "large", link_destination: str = "none"):
        attrs = {
            "id": image_id,
            "sizeSlug": size_slug,
            "linkDestination": link_destination
        }
        super().__init__(block_type="image", attrs=attrs, inner_content=f'<figure class="wp-block-image size-{size_slug}"><img src="{image_url}" alt="{alt_text}" class="wp-image-{image_id}"/></figure>')


class HTMLBlock(GutenbergBlock):
    def __init__(self, html_content: str):
        """
        :param html_content: The raw HTML content to be rendered inside the Gutenberg block.
        """
        self.html_content = html_content
        super().__init__(block_type="html", attrs={})

    def render(self) -> str:
        """
        Render the block as Gutenberg-compatible HTML content.
        """
        return f'<!-- wp:html -->\n{self.html_content}\n<!-- /wp:html -->'
