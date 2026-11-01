from bs4 import BeautifulSoup


def extract_products(html: str) -> list[dict]:
    """Return every product card on the page with name, price, description and review count."""
    soup = BeautifulSoup(html, "lxml")
    products = []

    for card in soup.select("div.card.thumbnail"):
        link = card.select_one("a.title")
        price = card.select_one("h4.price span[itemprop='price']")
        description = card.select_one("p.description")
        reviews = card.select_one("span[itemprop='reviewCount']")

        # The visible link text is truncated ("Asus VivoBook..."), so use the title attribute.
        name = link.get("title") if link and link.get("title") else (
            link.get_text(strip=True) if link else None
        )

        products.append(
            {
                "name": name,
                "price": price.get_text(strip=True) if price else None,
                "description": description.get_text(strip=True) if description else None,
                "reviews": int(reviews.get_text(strip=True)) if reviews else None,
            }
        )

    return products
