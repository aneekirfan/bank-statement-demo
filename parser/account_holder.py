import pdfplumber
import re

def extract_account_holder_name(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        # Scan first 2 pages for the header info
        for i in range(min(2, len(pdf.pages))):
            text += "\n" + (pdf.pages[i].extract_text() or "")

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for i, line in enumerate(lines):
        # 1. Catch "Account Name : M/S..." (SBI style)
        if "ACCOUNT NAME" in line.upper():
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1 and len(parts[1].strip()) > 3:
                    name_part = parts[1].strip()
                    # Remove brackets like (ASIM FAZILI) if needed
                    return name_part.split(",")[0].strip()
            if i + 1 < len(lines):
                return lines[i + 1].strip()

        # 2. Catch "M/S. TAWAKKAL..." (HDFC style) at start of line
        if re.match(r"^(M/S\.?|MS\.{1,2})\s+[A-Z]", line, re.IGNORECASE):
             clean_name = re.sub(r"^(M/S\.?|MS\.{1,2})\.?\s*", "", line, flags=re.IGNORECASE)
             return clean_name.strip()

        # 3. Catch "TO: ... MS.. JI INDUSTRIES" (JKB style)
        if line.upper() == "TO:":
            if i + 1 < len(lines):
                name_line = lines[i + 1]
                clean_name = re.sub(r"^(MS\.\.|M/S\.?|MR\.|MRS\.)\s*", "", name_line, flags=re.IGNORECASE)
                return clean_name.strip()

    return "Unknown Account Holder"