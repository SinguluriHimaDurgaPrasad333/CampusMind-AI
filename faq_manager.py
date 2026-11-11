"""
CampusAI - FAQ Management Module
================================
Loads, filters, and searches university FAQs from structured CSV data.
Supports category filtering and keyword search with full provenance citations.
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional
from config import FAQS_FILE


def load_all_faqs(csv_path: Optional[Path] = None) -> List[Dict[str, str]]:
    """Loads FAQs from CSV file, returning a list of FAQ dictionaries."""
    target_path = csv_path or FAQS_FILE
    faqs = []

    if not target_path.exists():
        return faqs

    try:
        with open(target_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Sanitize fields
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                faqs.append(clean_row)
    except Exception as e:
        print(f"Error loading FAQs from {target_path}: {e}")

    return faqs


def get_faq_categories(faqs: Optional[List[Dict[str, str]]] = None) -> List[str]:
    """Returns a sorted list of unique categories found in the FAQ dataset."""
    faq_list = faqs if faqs is not None else load_all_faqs()
    categories = {item.get("category", "General") for item in faq_list if item.get("category")}
    return sorted(list(categories))


def search_faqs(
    query: str = "",
    category: Optional[str] = None,
    faqs: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """
    Filters FAQs by optional category and text search query.
    Matches queries against both the question and answer text.
    """
    faq_list = faqs if faqs is not None else load_all_faqs()
    results = []
    clean_query = query.strip().lower()

    for item in faq_list:
        # Category filter
        item_cat = item.get("category", "")
        if category and category != "All" and item_cat.lower() != category.lower():
            continue

        # Keyword query search
        if clean_query:
            q_text = item.get("question", "").lower()
            a_text = item.get("answer", "").lower()
            if clean_query not in q_text and clean_query not in a_text:
                continue

        results.append(item)

    return results
