from fastapi import FastAPI, Depends, HTTPException
from models.pydantic_models import URLInput, APIResponse, BrandContext
from services.scraper import ShopifyScraper
from services.competitor import fetch_competitors
from sqlalchemy.orm import Session
from database.db import get_db, Base, engine
from models.sqlalchemy_models import Brand, Product, HeroProduct, FAQ, SocialHandle, ContactDetail, ImportantLink
from typing import Optional

app = FastAPI(title="Shopify Insights Fetcher")

# Create database tables
Base.metadata.create_all(bind=engine)

def save_to_db(db: Session, brand_context: BrandContext):
    brand = Brand(
        store_url=str(brand_context.store_url),
        brand_description=brand_context.brand_description,
        privacy_policy=brand_context.privacy_policy,
        return_policy=brand_context.return_policy
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)

    for product in brand_context.product_catalog:
        db.add(Product(
            brand_id=brand.id,
            title=product.title,
            price=product.price,
            description=product.description,
            url=str(product.url) if product.url else None
        ))
    
    for product in brand_context.hero_products:
        db.add(HeroProduct(
            brand_id=brand.id,
            title=product.title,
            price=product.price,
            description=product.description,
            url=str(product.url) if product.url else None
        ))
    
    for faq in brand_context.faqs:
        db.add(FAQ(brand_id=brand.id, question=faq.question, answer=faq.answer))
    
    for handle in brand_context.social_handles:
        db.add(SocialHandle(brand_id=brand.id, platform=handle.platform, url=str(handle.url)))
    
    for email in brand_context.contact_details.emails:
        db.add(ContactDetail(brand_id=brand.id, email=email))
    
    for phone in brand_context.contact_details.phone_numbers:
        db.add(ContactDetail(brand_id=brand.id, phone_number=phone))
    
    for name, url in brand_context.important_links.items():
        db.add(ImportantLink(brand_id=brand.id, name=name, url=str(url)))
    
    db.commit()

@app.post("/fetch-insights", response_model=APIResponse)
async def fetch_insights(input: URLInput, db: Session = Depends(get_db)):
    try:
        scraper = ShopifyScraper(input.website_url)
        soup = scraper.fetch_page(input.website_url)
        if not soup:
            raise HTTPException(status_code=401, detail="Website not found")
        
        brand_context = scraper.scrape()
        
        # Save to database (bonus)
        save_to_db(db, brand_context)
        
        # Competitor analysis (bonus)
        brand_name = input.website_url.host.split(".")[0]
        competitors = await fetch_competitors(brand_name, input.website_url)
        for competitor in competitors:
            save_to_db(db, competitor)
        
        return APIResponse(status="success", data=brand_context)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")