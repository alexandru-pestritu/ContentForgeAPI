from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import json

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    seo_keywords = Column(Text, nullable=True)  
    slug = Column(String, unique=True, nullable=False)
    main_image_url = Column(String, nullable=True)
    main_image_wp_id = Column(Integer, nullable=True)  
    buyers_guide_image_url = Column(String, nullable=True)
    buyers_guide_image_wp_id = Column(Integer, nullable=True)  
    products_id_list = Column(Text, nullable=True)  
    introduction = Column(Text, nullable=True)
    buyers_guide = Column(Text, nullable=True)
    faqs = Column(Text, nullable=True)  
    conclusion = Column(Text, nullable=True)

    def set_seo_keywords(self, keywords):
        """Accepts a list of SEO keywords and stores them as JSON."""
        self.seo_keywords = json.dumps(keywords)

    def get_seo_keywords(self):
        """Returns the list of SEO keywords stored as JSON."""
        if self.seo_keywords:
            return json.loads(self.seo_keywords)
        return []

    def set_products_id_list(self, product_ids):
        """Accepts a list of product IDs and stores them as JSON."""
        self.products_id_list = json.dumps(product_ids)

    def get_products_id_list(self):
        """Returns the list of product IDs stored as JSON."""
        if self.products_id_list:
            return json.loads(self.products_id_list)
        return []

    def set_faqs(self, faqs):
        """Accepts a list of FAQs (each as a dict with title and description) and stores them as JSON."""
        self.faqs = json.dumps(faqs)

    def get_faqs(self):
        """Returns the list of FAQs stored as JSON."""
        if self.faqs:
            return json.loads(self.faqs)
        return []
