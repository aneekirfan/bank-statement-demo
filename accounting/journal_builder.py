from config import LEDGER_MAP
from accounting.narration import limited_narration

def build_journal_entry(txn, txn_type):
    # Use 'amount' which is consistent across all normalized rows
    amount = txn["amount"]
    date = txn["date"]
    raw_description = txn["description"]
    narration = limited_narration(raw_description)

    debit = ""
    credit = ""

    # --- 1. GENERAL EXPENSES (New) ---
    # Matches the 'general_expense' tag from classifier.py
    if txn_type == "general_expense":
        debit = "General Expenses A/c"
        credit = LEDGER_MAP["bank"]

    # --- 2. SALES (Money In) ---
    elif txn_type == "sales":
        debit = LEDGER_MAP["bank"]
        credit = LEDGER_MAP["sales"]
    
    # --- 3. PURCHASE / PAYMENTS (Default Money Out) ---
    # This handles Credit Cards, Party Payments, etc.
    elif txn_type == "purchase":
        debit = LEDGER_MAP["purchase"]
        credit = LEDGER_MAP["bank"]

    # --- 4. SPECIFIC CHARGES ---
    # Handles gst, loan, printing, interest, bank_charges via config.py
    elif txn_type in LEDGER_MAP:
        debit = LEDGER_MAP[txn_type]
        credit = LEDGER_MAP["bank"]
    
    # --- 5. FALLBACK ---
    else:
        debit = LEDGER_MAP["purchase"]
        credit = LEDGER_MAP["bank"]

    # --- VOUCHER TYPE DETERMINATION ---
    # Priority: CDR keyword (Contra) > Sales (Receipt) > Everything else (Payment)
    if "cdr" in raw_description.lower():
        voucher_type = "Contra"
    elif txn_type == "sales":
        voucher_type = "Receipt"
    else:
        voucher_type = "Payment"

    return {
        "date": date,
        "debit": debit,
        "credit": credit,
        "amount": amount,
        "narration": narration,
        "raw_description": raw_description,
        "voucher_type": voucher_type
    }
