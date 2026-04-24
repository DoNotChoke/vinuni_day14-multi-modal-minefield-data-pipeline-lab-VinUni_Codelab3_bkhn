import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Clean the transcript text and extract key information.

def clean_transcript(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    cleaned_text = re.sub(r'\[Music\]|\[inaudible\]|\[Laughter\]', '', text)
    cleaned_text = re.sub(r'\[\d{1,2}:\d{2}(:\d{2})?\]', '', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    price_pattern = r'\b(\w+\s)+(đồng|nghìn|ngàn|triệu|tỷ)\b'
    price_match = re.search(price_pattern, cleaned_text, re.IGNORECASE)
    
    extracted_price = price_match.group(0) if price_match else "Not found"
    
    return {
        "original_source": file_path,
        "clean_content": cleaned_text,
        "metadata": {
            "extracted_price": extracted_price,
            "language": "vi",
            "status": "processed"
        }
    }