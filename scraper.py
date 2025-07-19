import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models.pydantic_models import BrandContext, Product, FAQ, SocialHandle, ContactDetail
from typing import Optional
import re
import json

class ShopifyScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException:
            return None

    def get_product_catalog(self) -> list[Product]:
        products = []
        url = f"{self.base_url}/products.json"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for item in data.get("products", []):
                products.append(Product(
                    id=str(item.get("id")),
                    title=item.get("title", ""),
                    price=str(item.get("variants", [{}])[0].get("price", "")),
                    description=item.get("body_html", ""),
                    url=f"{self.base_url}/products/{item.get('handle', '')}"
                ))
        except requests.RequestException:
            pass
        return products

    def get_hero_products(self) -> list[Product]:
        soup = self.fetch_page(self.base_url)
        products = []
        if soup:
            # Assuming hero products are in a carousel or featured section
            for product_div in soup.select(".product-card, .featured-product"):
                title = product_div.select_one(".product-title") or product_div.select_one("h3")
                price = product_div.select_one(".product-price") or product_div.select_one(".price")
                url = product_div.select_one("a[href*='/products/']")
                products.append(Product(
                    title=title.text.strip() if title else "",
                    price=price.text.strip() if price else "",
                    url=urljoin(self.base_url, url["href"]) if url else None
                ))
        return products

    def get_privacy_policy(self) -> Optional[str]:
        soup = self.fetch_page(f"{self.base_url}/policies/privacy-policy")
        if soup:
            content = soup.select_one(".policy-content, .main-content")
            return content.text.strip() if content else None
        return None

    def get_return_policy(self) -> Optional[str]:
        soup = self.fetch_page(f"{self.base_url}/policies/refunded-policy")
        if soup:
            content = soup.select_one(".policy-content, .main-content")
            return content.text.strip() if content else None
        return None

    def get_faqs(self) -> list[FAQ]:
        faqs = []
        soup = self.fetch_page(f"{self.base_url}/pages/faq")
        if soup:
            for faq_item in soup.select(".faq-item, .accordion"):
                question = faq_item.select_one(".faq-question, .accordion-title")
                answer = faq_item.select_one(".faq-answer, .accordion-content")
                if question and answer:
                    faqs.append(FAQ(
                        question=question.text.strip(),
                        answer=answer.text.strip()
                    ))
        return faqs

    def get_social_handles(self) -> list[SocialHandle]:
        soup = self.fetch_page(self.base_url)
        handles = []
        if soup:
            for link in soup.select("a[href*='instagram.com'], a[href*='facebook.com'], a[href*='tiktok.com']"):
                platform = "instagram" if "instagram.com" in link["href"] else "facebook" if "facebook Xcom" in link["href"] else "tiktok"
                handles.append(SocialHandle(platform=platform, url=link["href"]))
        return handles

    def get_contact_details(self) -> ContactDetail:
        soup = self.fetch_page(f"{self.base_url}/pages/contact")
        emails = []
        phone_numbers = []
        if soup:
            text = soup.get_text()
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
            phone_numbers = re.findall(r"\b\d{10}\b|\+\d{1,3}\s?\d{10}\b", text)
        return ContactDetail(emails=emails, phone_numbers=phone_numbers)

    def get_brand_description(self) -> Optional[str]:
        soup = self.fetch_page(f"{self.base_url}/pages/about")
        if soup:
            content = soup.select_one(".about-content, .main-content")
            return content.text.strip() if content else None
        return None

    def get_important_links(self) -> dict[str, str]:
        soup = self.fetch_page(self.base_url)
        links = {}
        if soup:
            for link in soup.select("a[href*='/pages/'], a[href*='track'], a[href*='contact'], a[href*='blog']"):
                name = link.text.strip().lower()
                if name in ["order tracking", "contact us", "blogs"]:
                    links[name] = urljoin(self.base_url, link["href"])
        return links

    def scrape(self) -> BrandContext:
        return BrandContext(
            store_url=self.base_url,
            product_catalog=self.get_product_catalog(),
            hero_products=self.get_hero_products(),
            privacy_policy=self.get_privacy_policy(),
            return_policy=self.get_return_policy(),
            faqs=self.get_faqs(),
            social_handles=self.get_social_handles(),
            contact_details=self.get_contact_details(),
            brand_description=self.get_brand_description(),
            important_links=self.get_important_links()
        )