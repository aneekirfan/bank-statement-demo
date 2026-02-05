import re

# Standard Regex (Amount + Balance)
AMOUNT_RE = re.compile(r"([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*(Dr|Cr)?", re.IGNORECASE)

# Opening Balance Regex (Balance Only)
OPENING_RE = re.compile(r"([\d,]+\.\d{2})\s*(Dr|Cr)?", re.IGNORECASE)

def normalize_transactions(raw_txns):
    normalized = []
    previous_balance = None

    for txn in raw_txns:
        # --- PHASE 1: Handle Opening Balance Row ---
        if txn["date"] == "OPENING":
            match = OPENING_RE.search(txn["text"])
            if match:
                bal_str = match.group(1).replace(",", "")
                dr_cr = match.group(2).strip() if match.group(2) else ""
                
                val = float(bal_str)
                if "DR" in dr_cr.upper():
                    previous_balance = -val
                else:
                    previous_balance = val
            continue 

        # --- PHASE 2: Handle Normal Transactions ---
        matches = AMOUNT_RE.findall(txn["text"])
        if not matches:
            continue

        last_match = matches[-1]
        
        amount = float(last_match[0].replace(",", ""))
        balance_abs = float(last_match[1].replace(",", ""))
        dr_cr_tag = last_match[2].strip() if last_match[2] else ""

        if "DR" in dr_cr_tag.upper():
            current_balance = -balance_abs
        else:
            current_balance = balance_abs

        # Calculate Direction
        direction = None
        if previous_balance is not None:
            delta = current_balance - previous_balance
            if delta > 0.01:
                direction = "credit"  # Sales
            elif delta < -0.01:
                direction = "debit"   # Purchase

        # Clean Description
        clean_desc = txn["text"]
        for part in last_match[:2]:
            clean_desc = clean_desc.replace(part, "")
        if dr_cr_tag:
            clean_desc = clean_desc.replace(dr_cr_tag, "")
            
        clean_desc = clean_desc.replace('"', '').strip()

        normalized.append({
            "date": txn["date"],
            "description": clean_desc,
            "amount": amount,
            "balance": current_balance,
            "direction": direction
        })

        previous_balance = current_balance

    return normalized