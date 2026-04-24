import json
import re

from bs4 import BeautifulSoup

from schema import UnifiedDocument

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.


def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    # ------------------------------------------

    def _clean_price(value):
        text = value.strip()
        if not text or text.upper() == "N/A":
            return None

        if not re.search(r"\d", text):
            return None

        numeric_text = re.sub(r"[^0-9.\-]", "", text)
        if not numeric_text:
            return None

        try:
            return float(numeric_text)
        except ValueError:
            return None

    table = soup.find("table", id="main-catalog")
    if table is None:
        return []

    documents = []
    rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")
    for row in rows:
        cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
        if len(cells) != 6:
            continue

        product_id, product_name, category, raw_price, raw_stock, raw_rating = cells
        cleaned_price = _clean_price(raw_price)

        try:
            stock_quantity = int(raw_stock)
        except ValueError:
            stock_quantity = None

        rating = None if "kh" in raw_rating.lower() and "gi" in raw_rating.lower() else raw_rating
        price_text = "price unavailable" if cleaned_price is None else f"listed at {cleaned_price} VND"
        stock_text = "unknown stock" if stock_quantity is None else f"{stock_quantity} units in stock"
        rating_text = "without rating data" if rating is None else f"rated {rating}"
        content = (
            f"Product {product_id}: {product_name} in category {category} is {price_text}, "
            f"has {stock_text}, and is {rating_text}."
        )

        document = UnifiedDocument(
            document_id=f"html-product-{product_id}",
            content=content,
            source_type="HTML",
            author="VinShop",
            source_metadata={
                "original_file": file_path,
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price": cleaned_price,
                "currency": "VND",
                "stock_quantity": stock_quantity,
                "rating": rating,
            },
        )

        if hasattr(document, "model_dump"):
            documents.append(document.model_dump(mode="json"))
        else:
            documents.append(json.loads(document.json()))

    return documents
