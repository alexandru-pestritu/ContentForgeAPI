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
    image_urls = Column(Text, nullable=True)
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

    def set_specifications(self, specifications):
        """Accepts a dictionary of specifications and stores them as JSON."""
        self.specifications = json.dumps(specifications)

    def get_specifications(self):
        """Returns the dictionary of specifications stored as JSON."""
        if self.specifications:
            return json.loads(self.specifications)
        return {}
    
    def set_pros(self, pros):
        """Accepts a list of pros and stores them as JSON."""
        self.pros = json.dumps(pros)


    def get_pros(self):
        """Returns the list of pros stored as JSON."""
        if self.pros:
            return json.loads(self.pros)
        return []
    
    def set_cons(self, cons):
        """Accepts a list of cons and stores them as JSON."""
        self.cons = json.dumps(cons)

    def get_cons(self):
        """Returns the list of cons stored as JSON."""
        if self.cons:
            return json.loads(self.cons)
        return []
    
    def set_image_urls(self, image_urls):
        """Accepts a list of image URLs and stores them as JSON."""
        self.image_urls = json.dumps(image_urls)

    def get_image_urls(self):
        """Returns the list of image URLs stored as JSON."""
        if self.image_urls:
            return json.loads(self.image_urls)
        return []