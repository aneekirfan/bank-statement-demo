from config import LEDGER_MAP
from accounting.narration import limited_narration

def build_journal_entry(txn, txn_type):
    amount = txn["amount"]
    date = txn["date"]
    narration = limited_narration(txn["description"])

    # Default Variables
    debit = ""
    credit = ""

    # 1. SALES (Money In) -> Debit Bank, Credit Sales
    if txn_type == "sales":
        debit = LEDGER_MAP["bank"]
        credit = LEDGER_MAP["sales"]
    
    # 2. PURCHASE (Money Out) -> Debit Purchase, Credit Bank
    elif txn_type == "purchase":
        debit = LEDGER_MAP["purchase"]
        credit = LEDGER_MAP["bank"]

    # 3. SPECIFIC CHARGES (Money Out) -> Debit Expense, Credit Bank
    # This handles GST, Interest, Loan, Bank Charges, etc.
    elif txn_type in LEDGER_MAP:
        debit = LEDGER_MAP[txn_type]
        credit = LEDGER_MAP["bank"]
    
    # Fallback (Treat as Purchase)
    else:
        debit = LEDGER_MAP["purchase"]
        credit = LEDGER_MAP["bank"]

    return {
        "date": date,
        "debit": debit,
        "credit": credit,
        "amount": amount,
        "narration": narration
    }