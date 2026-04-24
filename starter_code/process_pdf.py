import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

from schema import UnifiedDocument

load_dotenv()


def _strip_markdown_fence(text):
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    print(f"Uploading {file_path} to Gemini...")
    try:
        pdf_file = genai.upload_file(path=file_path)
    except Exception as exc:
        print(f"Failed to upload file to Gemini: {exc}")
        return None

    prompt = f"""
Analyze this PDF and return exactly one JSON object.

Requirements:
- Write a concise 3-sentence summary in the `content` field.
- Extract the best available author name. Use "Unknown" if not found.
- Keep `source_type` exactly as "PDF".
- Keep `timestamp` as null unless the PDF clearly provides a publication timestamp in ISO 8601 format.
- Include the original filename in `source_metadata.original_file`.

Return JSON matching this schema exactly:
{{
  "document_id": "pdf-doc-001",
  "content": "Summary: ...",
  "source_type": "PDF",
  "author": "Unknown",
  "timestamp": null,
  "source_metadata": {{
    "original_file": "{os.path.basename(file_path)}"
  }}
}}
"""

    print("Generating content from PDF using Gemini...")
    try:
        response = model.generate_content([pdf_file, prompt])
        raw_text = getattr(response, "text", "") or ""
    except Exception as exc:
        print(f"Failed to generate content from PDF: {exc}")
        return None

    if not raw_text.strip():
        print("Gemini returned an empty response.")
        return None

    try:
        extracted_data = json.loads(_strip_markdown_fence(raw_text))
    except json.JSONDecodeError as exc:
        print(f"Failed to parse Gemini response as JSON: {exc}")
        return None

    extracted_data["document_id"] = extracted_data.get("document_id") or "pdf-doc-001"
    extracted_data["source_type"] = "PDF"
    extracted_data["author"] = extracted_data.get("author") or "Unknown"
    extracted_data["source_metadata"] = {
        "original_file": os.path.basename(file_path),
        **(extracted_data.get("source_metadata") or {}),
    }

    try:
        document = UnifiedDocument(**extracted_data)
    except Exception as exc:
        print(f"Gemini response did not match UnifiedDocument: {exc}")
        return None

    if hasattr(document, "model_dump"):
        return document.model_dump(mode="json")
    return json.loads(document.json())
