import pytesseract
from PIL import Image
import pdfplumber

def extract_text_with_ocr(pdf_path):
    text_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            image = page.to_image(resolution=300).original
            text = pytesseract.image_to_string(image)
            text_lines.extend(text.split("\n"))

    return text_lines
