from accounting.narration import limited_narration


TRANSFER_KEYWORDS = ["mtfr", "neft", "rtgs", "upi", "imps", "trf"]
CASH_KEYWORDS = ["by cash", "cash deposit", "cash dep", "cash", "self"]
PURCHASE_HINTS = ["purchase", "pos", "debit card", "dr card", "ecom", "shopping"]
SALES_HINTS = ["sale", "sales", "invoice", "inv ", "inv-"]


def detect_voucher_type(txn, txn_type):
    """Map a classified transaction to a Tally voucher type."""
    desc = txn["description"].lower()
    direction = txn.get("direction")

    if txn_type == "bank_charges":
        return "Bank Charges"

    if txn_type == "general_expense":
        return "Miscellaneous Expenses"

    if "deposit" in desc or any(k in desc for k in CASH_KEYWORDS):
        return "Contra"

    if direction == "debit":
        if txn_type == "purchase" and any(k in desc for k in PURCHASE_HINTS):
            return "Purchase"
        return "Payment"

    if direction == "credit":
        if any(k in desc for k in SALES_HINTS):
            return "Sales"
        return "Receipt"

    if txn_type == "purchase":
        return "Payment"

    if txn_type == "sales":
        return "Receipt"

    if any(k in desc for k in TRANSFER_KEYWORDS):
        return "Contra"

    return "Payment"


def party_ledger_name(description):
    """Fallback ledger name when party is not separately parsed."""
    return limited_narration(description).title()
