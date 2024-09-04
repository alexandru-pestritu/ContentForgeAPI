import markdown
import html2text

class MarkdownService:
    def __init__(self):
        """
        Initializes the MarkdownService with a HTML to Markdown converter.
        """
        self.html2md_converter = html2text.HTML2Text()
        self.html2md_converter.ignore_links = False 
        self.html2md_converter.ignore_images = False  

    def markdown_to_html(self, markdown_text: str) -> str:
        """
        Converts Markdown text to HTML.

        :param markdown_text: The Markdown text to convert.
        :return: Converted HTML from Markdown.
        """
        return markdown.markdown(markdown_text)

    def html_to_markdown(self, html_text: str) -> str:
        """
        Converts HTML text to Markdown.

        :param html_text: The HTML text to convert.
        :return: Converted Markdown from HTML.
        """
        return self.html2md_converter.handle(html_text)
