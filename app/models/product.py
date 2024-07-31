from sqlalchemy import Column, Integer, String, Text, Float, Boolean
from app.database import Base
import json

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_ids = Column(Text, nullable=True)  
    name = Column(String, index=True, nullable=False)
    affiliate_urls = Column(Text, nullable=True) 
    in_stock = Column(Boolean, nullable=True)
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    seo_keyword = Column(String, nullable=True)
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    review = Column(Text, nullable=True)
    rating = Column(Float, nullable=True) 
    image_ids = Column(Text, nullable=True) 

    def set_store_ids(self, store_ids):
        """Accepts a list of store IDs and stores them as JSON."""
        self.store_ids = json.dumps(store_ids)

    def get_store_ids(self):
        """Returns the list of store IDs stored as JSON."""
        if self.store_ids:
            return json.loads(self.store_ids)
        return []

    def set_affiliate_urls(self, affiliate_urls):
        """Accepts a list of affiliate URLs and stores them as JSON."""
        self.affiliate_urls = json.dumps(affiliate_urls)

    def get_affiliate_urls(self):
        """Returns the list of affiliate URLs stored as JSON."""
        if self.affiliate_urls:
            return json.loads(self.affiliate_urls)
        return []

    def set_image_ids(self, image_ids):
        """Accepts a list of image IDs and stores them as JSON."""
        self.image_ids = json.dumps(image_ids)

    def get_image_ids(self):
        """Returns the list of image IDs stored as JSON."""
        if self.image_ids:
            return json.loads(self.image_ids)
        return []
