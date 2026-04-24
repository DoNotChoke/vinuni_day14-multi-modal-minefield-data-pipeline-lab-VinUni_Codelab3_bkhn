import json
import re
from datetime import datetime

import pandas as pd

from schema import UnifiedDocument

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Process sales records, handling type traps and duplicates.


def process_sales_csv(file_path):
    # --- FILE READING (Handled for students) ---
    df = pd.read_csv(file_path)
    # ------------------------------------------

    def _clean_price(value):
        if pd.isna(value):
            return None

        text = str(value).strip()
        if not text or text.upper() in {"N/A", "NULL"}:
            return None

        normalized_text = text.lower()
        word_to_number = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        if normalized_text in word_to_number:
            return float(word_to_number[normalized_text])

        word_match = re.search(
            r"\b(" + "|".join(word_to_number.keys()) + r")\b",
            normalized_text,
        )
        if word_match:
            return float(word_to_number[word_match.group(1)])

        if not re.search(r"\d", text):
            return None

        numeric_text = re.sub(r"[^0-9.\-]", "", text)
        if numeric_text in {"", "-", ".", "-."}:
            return None

        try:
            return float(numeric_text)
        except ValueError:
            return None

    def _normalize_date(value):
        if pd.isna(value):
            return None

        cleaned = re.sub(
            r"(\d+)(st|nd|rd|th)",
            r"\1",
            str(value).strip(),
            flags=re.IGNORECASE,
        )
        date_formats = (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%B %d %Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d %b %Y",
            "%b %d %Y",
        )

        for date_format in date_formats:
            try:
                return datetime.strptime(cleaned, date_format).strftime("%Y-%m-%d")
            except ValueError:
                continue

        parsed = pd.to_datetime(cleaned, errors="coerce", dayfirst=True)
        if pd.isna(parsed):
            return None
        return parsed.strftime("%Y-%m-%d")

    df = df.drop_duplicates(subset=["id"], keep="first").copy()
    df["price"] = df["price"].apply(_clean_price)
    df["date_of_sale"] = df["date_of_sale"].apply(_normalize_date)

    documents = []
    for row in df.to_dict(orient="records"):
        normalized_date = row["date_of_sale"]
        cleaned_price = None if pd.isna(row.get("price")) else float(row["price"])
        price_text = (
            f"{cleaned_price} {row['currency']}"
            if cleaned_price is not None
            else f"unavailable {row['currency']}"
        )
        content = (
            f"Sale record {row['id']}: {row['product_name']} in category {row['category']} "
            f"was sold for {price_text} on {normalized_date}."
        )

        stock_quantity = None if pd.isna(row.get("stock_quantity")) else int(row["stock_quantity"])
        document = UnifiedDocument(
            document_id=f"csv-sale-{row['id']}",
            content=content,
            source_type="CSV",
            author=row.get("seller_id") or "Unknown",
            timestamp=f"{normalized_date}T00:00:00" if normalized_date else None,
            source_metadata={
                "original_file": file_path,
                "sale_id": row["id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "price": cleaned_price,
                "currency": row["currency"],
                "date_of_sale": normalized_date,
                "seller_id": row.get("seller_id"),
                "stock_quantity": stock_quantity,
            },
        )

        if hasattr(document, "model_dump"):
            documents.append(document.model_dump(mode="json"))
        else:
            documents.append(json.loads(document.json()))

    return documents
