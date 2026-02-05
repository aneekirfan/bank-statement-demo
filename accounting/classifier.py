import re

def classify_transaction(txn):
    desc = txn["description"].lower()
    direction = txn.get("direction")

    # --- 1. SPECIFIC CHARGES (Highest Priority) ---
    if "gst" in desc:
        return "gst"
    if "loan" in desc:
        return "loan"
    if "printing" in desc or "statement pr" in desc:
        return "printing"

    # --- 2. BANK CHARGES (Priority over Transfers) ---
    # Fix: Check for "Charge/Fee" BEFORE checking for "NEFT/UPI"
    # Logic: "NEFT CHARGES" contains "NEFT", but it IS a charge.
    
    # List of strong charge keywords
    charge_keywords = ["sms", "cibil", "fee", "inspc", "commissio", "charge", "chrg"]
    
    if any(x in desc for x in charge_keywords):
        # EXCEPTION: "Recharge" (e.g. Jio Recharge) is NOT a bank charge, it's a Purchase
        if "recharge" in desc:
            pass  # Fall through to Purchase logic
        else:
            return "bank_charges"

    # --- 3. SAFEGUARDS ---
    # Now we check if it's a Transfer. 
    # Since we already handled "NEFT CHARGES" above, "NEFT" here means a real transfer.
    is_transfer = any(x in desc for x in ["mtfr", "neft", "rtgs", "upi", "imps", "trf", "by cash"])

    # Interest Check (Must not be a transfer)
    if not is_transfer:
        if re.search(r"\binterest\b", desc) or "int.coll" in desc or "i nt.coll" in desc:
            return "interest"

    # --- 4. DIRECTION-BASED (Standard Logic) ---
    if direction == "credit":
        return "sales"
    if direction == "debit":
        return "purchase"

    # --- 5. Fallback ---
    if is_transfer or "deposit" in desc:
        return "sales"

    return "purchase"