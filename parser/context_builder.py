from parser.pdf_text_parser import extract_transactions
from parser.row_normalizer import normalize_transactions
from parser.account_holder import extract_account_holder_name
from parser.bank_detector import detect_bank


def build_statement_context(pdf_path):
    raw_txns = extract_transactions(pdf_path)
    transactions = normalize_transactions(raw_txns)

    account_holder = extract_account_holder_name(pdf_path)

    bank = detect_bank(pdf_path)
    context = {
        "bank": bank,
        "account_holder": account_holder,
        "transactions": transactions,
        "confidence": {
            "bank": 1.0 if bank != "UNKNOWN" else 0.3,
            "account_holder": 0.7 if account_holder != "Account Holder" else 0.3,
            "transactions": 1.0 if transactions else 0.0
        }
    }

    return context
