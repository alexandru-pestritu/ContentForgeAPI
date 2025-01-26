import pytest
import json
from unittest.mock import MagicMock

from app.services.placeholder_service import PlaceholderService


class MockProduct:
    """Mock class for Product objects, used to test PlaceholderService without a real DB model."""
    def __init__(
        self,
        name="Test Product",
        full_name="Test Product Full Name",
        affiliate_urls=None,
        description="A great product.",
        specifications=None,
        seo_keyword="best-product",
        pros=None,
        cons=None,
        review="This is a review.",
        rating=4.5,
        images=None
    ):
        self.name = name
        self.full_name = full_name
        self.affiliate_urls = affiliate_urls or []
        self.description = description
        self.specifications = specifications or []
        self.seo_keyword = seo_keyword
        self.pros = pros or []
        self.cons = cons or []
        self.review = review
        self.rating = rating
        self.images = images or []


class MockArticle:
    """Mock class for Article objects, used to test PlaceholderService without a real DB model."""
    def __init__(
        self,
        title="Test Article",
        slug="test-article",
        content="Article content...",
        seo_keywords=None,
        meta_title="Meta Title",
        meta_description="Meta Description",
        main_image_url="http://image.com/main.jpg",
        buyers_guide_image_url="http://image.com/guide.jpg",
        products=None,
        introduction="Article introduction",
        buyers_guide="Buyer's guide content",
        faqs=None,
        conclusion="Article conclusion"
    ):
        self.title = title
        self.slug = slug
        self.content = content
        self.seo_keywords = seo_keywords or []
        self.meta_title = meta_title
        self.meta_description = meta_description
        self.main_image_url = main_image_url
        self.buyers_guide_image_url = buyers_guide_image_url
        self.products = products or []
        self.introduction = introduction
        self.buyers_guide = buyers_guide
        self.faqs = faqs or []
        self.conclusion = conclusion


class MockStore:
    """Mock class for Store objects, used to test PlaceholderService without a real DB model."""
    def __init__(self, name="Test Store", base_url="http://teststore.com"):
        self.name = name
        self.base_url = base_url


def test_replace_placeholders_basic():
    service = PlaceholderService()
    template = "Hello, {username}! Welcome to {app_name}."
    replacements = {"username": "John", "app_name": "ContentForge"}

    result = service.replace_placeholders(template, replacements)
    assert result == "Hello, John! Welcome to ContentForge."


def test_replace_placeholders_missing_keys():
    service = PlaceholderService()
    template = "Hello, {username}. Today is {day}."
    replacements = {"username": "Alice"}

    result = service.replace_placeholders(template, replacements)
    assert result == "Hello, Alice. Today is {day}."


def test_replace_placeholders_escape_curly_braces():
    """
    Verifies how the method handles '{{' and '}}'. 
    The code performs replace("{{", "{") and replace("}}", "}").
    """
    service = PlaceholderService()
    template = "This is an example with {{curly}} braces"
    replacements = {}

    result = service.replace_placeholders(template, replacements)
    assert result == "This is an example with {curly} braces"


def test_get_replacements_for_product_basic():
    service = PlaceholderService()
    product = MockProduct(
        name="Mouse",
        full_name="Super Mouse v2",
        affiliate_urls=[
            MagicMock(url="http://affiliate1.com"), 
            MagicMock(url="http://affiliate2.com")
        ],
        description="This is a mouse",
        specifications=[
            MagicMock(spec_key="Color", spec_value="Black"), 
            MagicMock(spec_key="Weight", spec_value="100g")
        ],
        seo_keyword="mouse-best",
        pros=[MagicMock(text="Lightweight"), MagicMock(text="Affordable")],
        cons=[MagicMock(text="No wireless")],
        review="Great for office use",
        rating=4.0,
        images=[MagicMock(image_url="http://images.com/mouse1.jpg")]
    )

    replacements = service.get_replacements_for_product(product)
    assert replacements["name"] == "Mouse"
    assert replacements["full_name"] == "Super Mouse v2"
    assert replacements["affiliate_urls"] == "http://affiliate1.com, http://affiliate2.com"
    assert replacements["description"] == "This is a mouse"
    assert replacements["specifications"] == "Color: Black, Weight: 100g"
    assert replacements["seo_keyword"] == "mouse-best"
    assert replacements["pros"] == "Lightweight, Affordable"
    assert replacements["cons"] == "No wireless"
    assert replacements["review"] == "Great for office use"
    assert replacements["rating"] == "4.0"
    assert replacements["image_urls"] == "http://images.com/mouse1.jpg"


def test_get_replacements_for_product_with_output_json():
    service = PlaceholderService()
    product = MockProduct(name="Laptop")
    output_data = {"ai": "generated text"}

    replacements = service.get_replacements_for_product(product, output_json=output_data)
    assert "output" in replacements

    parsed_output = json.loads(replacements["output"])
    assert parsed_output == output_data


def test_get_replacements_for_article_basic():
    service = PlaceholderService()

    mock_keywords = [MagicMock(keyword="keyword1"), MagicMock(keyword="keyword2")]
    mock_products = [
        MockProduct(name="Product1", seo_keyword="kw1"),
        MockProduct(name="Product2", seo_keyword="kw2")
    ]
    mock_faqs = [
        MagicMock(question="Question1?", answer="Answer1"),
        MagicMock(question="Question2?", answer="Answer2")
    ]

    article = MockArticle(
        seo_keywords=mock_keywords,
        products=mock_products,
        faqs=mock_faqs
    )

    replacements = service.get_replacements_for_article(article)
    assert replacements["title"] == "Test Article"
    assert replacements["slug"] == "test-article"
    assert replacements["content"] == "Article content..."
    assert replacements["seo_keywords"] == "keyword1, keyword2"
    assert replacements["products_id_list"] == "Product1 - kw1, Product2 - kw2"
    assert "faqs" in replacements

    faqs_data = json.loads(replacements["faqs"])
    assert len(faqs_data) == 2
    assert faqs_data[0]["title"] == "Question1?"
    assert faqs_data[0]["description"] == "Answer1"


def test_get_replacements_for_store():
    service = PlaceholderService()
    store = MockStore(name="MegaStore", base_url="http://megastore.com")

    replacements = service.get_replacements_for_store(store)
    assert replacements["name"] == "MegaStore"
    assert replacements["base_url"] == "http://megastore.com"


@pytest.mark.parametrize("placeholder_type, expected_placeholders", [
    ("Store", [
        "{name}",
        "{base_url}"
    ]),
    ("Product", [
        "{name}", "{full_name}", "{affiliate_urls}", "{description}",
        "{specifications}", "{seo_keyword}", "{pros}", "{cons}", "{review}", "{rating}",
        "{image_urls}", "{output}"
    ]),
    ("Article", [
        "{title}", "{slug}", "{content}", "{seo_keywords}", "{meta_title}", "{meta_description}",
        "{main_image_url}", "{buyers_guide_image_url}", "{products_id_list}",
        "{introduction}", "{buyers_guide}", "{faqs}", "{conclusion}", "{output}"
    ]),
    ("Unknown", [])
])
def test_get_placeholders_for_type(placeholder_type, expected_placeholders):
    service = PlaceholderService()
    placeholders = service.get_placeholders_for_type(placeholder_type)
    assert placeholders == expected_placeholders
