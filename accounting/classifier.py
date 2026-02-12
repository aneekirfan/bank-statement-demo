import re

def classify_transaction(txn):
    # Normalize description for matching
    desc = txn["description"].lower()
    direction = txn.get("direction")

    # --- 1. SPECIFIC EXPENSES (Utilities / Recharges) ---
    # These are flagged as 'general_expense' (Debit: General Expenses A/c)
    # This separates them from normal 'Purchase' payments.
    expense_keywords = [
        "pdd", "jkpdd", "kpdcl", "electricity",   # Power
        "jio", "airtel", "bsnl", "vi ", "vodafone", # Telecom
        "recharge", "prepaid", "postpaid", "billpay" # Generic Bill words
    ]
    
    if any(k in desc for k in expense_keywords):
        return "general_expense"

    # --- 2. SPECIFIC LEDGER CHARGES ---
    if "gst" in desc:
        return "gst"
    if "loan" in desc:
        return "loan"
    if "printing" in desc or "statement pr" in desc:
        return "printing"

    # --- 3. BANK CHARGES ---
    # We check these BEFORE "transfers" because sometimes "NEFT CHARGES" 
    # has both words. We want it to be a Charge, not a Transfer.
    charge_keywords = ["sms", "cibil", "fee", "inspc", "commissio", "charge", "chrg", "recovery"]
    
    if any(x in desc for x in charge_keywords):
        # EXCEPTION: "Recharge" is already caught in Step 1.
        # But if it somehow slipped through, we ignore it here so it doesn't become "Bank Charges"
        if "recharge" in desc:
            pass 
        else:
            return "bank_charges"

    # --- 4. SAFEGUARDS (For Interest) ---
    # Define what a "Transfer" looks like
    is_transfer = any(x in desc for x in ["mtfr", "neft", "rtgs", "upi", "imps", "trf", "by cash", "mbill", "ebil"])

    # Interest Check: MUST NOT be a transfer
    # This prevents footer text like "Interest Rate 10%" from mislabeling a transfer.
    if not is_transfer:
        if re.search(r"\binterest\b", desc) or "int.coll" in desc or "i nt.coll" in desc:
            return "interest"

    # --- 5. DIRECTION-BASED (The Default Buckets) ---
    if direction == "credit":
        return "sales"
    
    if direction == "debit":
        # This catches "MBILL", "Credit Card", "Party Payments", and "eBIL" 
        # that didn't match the expense keywords in Step 1.
        return "purchase"

    # --- 6. Fallback (If direction is missing for some reason) ---
    if is_transfer or "deposit" in desc:
        return "sales"

    return "purchase"
