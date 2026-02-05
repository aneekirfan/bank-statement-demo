import pdfplumber
from config import BANK_FINGERPRINTS


def detect_bank(pdf_path):
    import pdfplumber
    from config import BANK_FINGERPRINTS

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(min(2, len(pdf.pages))):
            page_text = pdf.pages[i].extract_text() or ""
            text += "\n" + page_text.upper()

    text = " ".join(text.split())  # normalize whitespace

    for bank, keywords in BANK_FINGERPRINTS.items():
        for kw in keywords:
            if kw in text:
                return bank

    return "UNKNOWN"

