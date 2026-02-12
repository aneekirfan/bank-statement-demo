import pdfplumber
import re

# FIX: Supports DD-MM-YYYY, DD/MM/YYYY, and DD/MM/YY
DATE_RE = re.compile(r"^\d{2}[-/]\d{2}[-/]\d{2,4}")

# Known footer/disclaimer text to ignore (e.g. JKB repeating disclaimer)
# The disclaimer is split across multiple lines by pdfplumber, so each fragment is listed.
JUNK_PATTERNS = [
    "unless the constituent notifies the bank",
    "immediately of any discrepancy found",
    "by him in this statement of account",
    "it will be taken that he has found",
    "the account correct",
]

def extract_transactions(pdf_path):
    transactions = []
    current = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw_text = page.extract_text()
            if not raw_text:
                continue
            
            lines = raw_text.split("\n")

            for line in lines:
                # 1. Clean CSV artifacts
                clean_line = line.replace('"', '').replace("','", " ").strip()
                if not clean_line:
                    continue

                # 1.5 Skip known junk/disclaimer lines
                if any(pat in clean_line.lower() for pat in JUNK_PATTERNS):
                    continue

                # 2. Skip Totals
                if "TOTAL" in clean_line.upper():
                    continue

                # 3. Start Opening Balance Block
                # Supports JKB "B/F" and SBI "Balance as on"
                upper_line = clean_line.upper()
                if any(x in upper_line for x in ["B/F", "BROUGHT FORWARD", "BALANCE AS ON", "OPENING BALANCE"]):
                    # Close previous transaction if any
                    if current:
                        transactions.append(current)
                    
                    # Start a special "OPENING" transaction. 
                    # Subsequent lines (like the amount) will be appended to this
                    # until the next Date line is found.
                    current = {
                        "date": "OPENING",
                        "text": clean_line
                    }
                    continue

                # 4. Process Standard Transactions
                if DATE_RE.match(clean_line):
                    if current:
                        transactions.append(current)

                    current = {
                        "date": clean_line.split()[0], # Safe extraction of date
                        "text": clean_line[10:].strip()
                    }
                else:
                    if current:
                        current["text"] += " " + clean_line

        if current:
            transactions.append(current)

    return transactions