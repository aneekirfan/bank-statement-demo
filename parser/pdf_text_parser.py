"""
pdf_text_parser
~~~~~~~~~~~~~~~
Low-level PDF text extraction utility.

Bank-specific transaction extraction logic lives in the adapter layer
(see adapters/generic.py and its subclasses).  This module is kept as
a thin helper for any code that only needs raw page text.
"""

import pdfplumber


def extract_page_texts(pdf_path):
    """Return a list of plain-text strings, one per PDF page."""
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    return texts