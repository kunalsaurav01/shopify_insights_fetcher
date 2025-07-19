from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    store_url = Column(String, unique=True, nullable=False)
    brand_description = Column(Text)
    privacy_policy = Column(Text)
    return_policy = Column(Text)
    products = relationship("Product", back_populates="brand")
    hero_products = relationship("HeroProduct", back_populates="brand")
    faqs = relationship("FAQ", back_populates="brand")
    social_handles = relationship("SocialHandle", back_populates="brand")
    contact_details = relationship("ContactDetail", back_populates="brand")
    important_links = relationship("ImportantLink", back_populates="brand")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    title = Column(String, nullable=False)
    price = Column(String)
    description = Column(Text)
    url = Column(String)
    brand = relationship("Brand", back_populates="products")

class HeroProduct(Base):
    __tablename__ = "hero_products"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    title = Column(String, nullable=False)
    price = Column(String)
    description = Column(Text)
    url = Column(String)
    brand = relationship("Brand", back_populates="hero_products")

class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    brand = relationship("Brand", back_populates="faqs")

class SocialHandle(Base):
    __tablename__ = "social_handles"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    platform = Column(String, nullable=False)
    url = Column(String, nullable=False)
    brand = relationship("Brand", back_populates="social_handles")

class ContactDetail(Base):
    __tablename__ = "contact_details"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    email = Column(String)
    phone_number = Column(String)
    brand = relationship("Brand", back_populates="contact_details")

class ImportantLink(Base):
    __tablename__ = "important_links"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    brand = relationship("Brand", back_populates="important_links")