from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Optional, Dict

class FAQ(BaseModel):
    question: str
    answer: str

class SocialHandle(BaseModel):
    platform: str
    url: HttpUrl

class ContactDetail(BaseModel):
    emails: List[EmailStr] = []
    phone_numbers: List[str] = []

class Product(BaseModel):
    id: Optional[str] = None
    title: str
    price: Optional[str] = None
    description: Optional[str] = None
    url: Optional[HttpUrl] = None

class BrandContext(BaseModel):
    store_url: HttpUrl
    product_catalog: List[Product]
    hero_products: List[Product]
    privacy_policy: Optional[str] = None
    return_policy: Optional[str] = None
    faqs: List[FAQ] = []
    social_handles: List[SocialHandle] = []
    contact_details: ContactDetail
    brand_description: Optional[str] = None
    important_links: Dict[str, HttpUrl] = {}

class APIResponse(BaseModel):
    status: str
    data: Optional[BrandContext] = None
    error: Optional[str] = None
    error_code: Optional[int] = None

class URLInput(BaseModel):
    website_url: HttpUrl