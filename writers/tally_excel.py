import os
import pandas as pd

from accounting.narration import limited_narration
from accounting.tally_voucher import detect_voucher_type, party_ledger_name

BANK_LEDGER_BY_CODE = {
    "HDFC": "HDFC Bank",
    "SBI": "SBI Bank",
    "JKB": "J&K Bank",
}

TRANSFER_NARRATION_KEYWORDS = ["mtfr", "neft", "rtgs", "upi", "imps", "trf", "mbill", "ebil"]


def _has_transfer_keyword(description, narration):
    text = f"{description or ''} {narration or ''}".lower()

    # Explicit exception requested by client: treat "by cash" as Contra-only behavior.
    if "by cash" in text:
        return False

    return any(k in text for k in TRANSFER_NARRATION_KEYWORDS)


def _build_ledger_lines(voucher_type, txn, txn_type, amount, bank_ledger, narration):
    party_ledger = party_ledger_name(txn["description"])
    direction = txn.get("direction")
    has_transfer_keyword = _has_transfer_keyword(txn.get("description", ""), narration)

    if voucher_type == "Receipt":
        credit_ledger = "SALE" if has_transfer_keyword else party_ledger
        return [
            (credit_ledger, amount, "Cr"),
            (bank_ledger, amount, "Dr"),
        ]

    if voucher_type == "Payment":
        debit_ledger = party_ledger
        if txn_type == "bank_charges":
            debit_ledger = "Bank Charges"
        elif has_transfer_keyword:
            debit_ledger = "Purchase"

        return [
            (debit_ledger, amount, "Dr"),
            (bank_ledger, amount, "Cr"),
        ]

    if voucher_type == "Purchase":
        return [
            (party_ledger, amount, "Cr"),
            ("Purchase", amount, "Dr"),
        ]

    if voucher_type == "Sales":
        return [
            (party_ledger, amount, "Dr"),
            ("Sales", amount, "Cr"),
        ]

    if voucher_type == "Contra":
        if direction == "credit":
            return [
                (bank_ledger, amount, "Dr"),
                ("Cash", amount, "Cr"),
            ]

        return [
            ("Cash", amount, "Dr"),
            (bank_ledger, amount, "Cr"),
        ]

    if voucher_type == "Miscellaneous Expenses":
        return [
            ("Miscellaneous Expenses", amount, "Dr"),
            (bank_ledger, amount, "Cr"),
        ]

    return [
        (party_ledger, amount, "Dr"),
        (bank_ledger, amount, "Cr"),
    ]


def generate_tally_excel(transactions_with_type, output_path, bank_code=None):
    rows = []
    voucher_number = 1
    bank_ledger = BANK_LEDGER_BY_CODE.get(bank_code, "Bank A/c")

    for item in transactions_with_type:
        txn = item["txn"]
        txn_type = item["txn_type"]
        date = txn["date"]
        amount = round(float(txn["amount"]), 2)

        voucher_type = detect_voucher_type(txn, txn_type)
        narration = limited_narration(txn["description"])
        ledger_lines = _build_ledger_lines(voucher_type, txn, txn_type, amount, bank_ledger, narration)

        for idx, (ledger_name, ledger_amount, dr_cr) in enumerate(ledger_lines):
            rows.append({
                "Voucher Date": date if idx == 0 else "",
                "Voucher Type Name": voucher_type if idx == 0 else "",
                "Voucher Number": voucher_number if idx == 0 else "",
                "Ledger Name": ledger_name,
                "Ledger Amount": ledger_amount,
                "Ledger Amount Dr/Cr": dr_cr,
                "Narration": narration,
            })

        voucher_number += 1

    df = pd.DataFrame(rows, columns=[
        "Voucher Date",
        "Voucher Type Name",
        "Voucher Number",
        "Ledger Name",
        "Ledger Amount",
        "Ledger Amount Dr/Cr",
        "Narration",
    ])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        os.remove(output_path)

    df.to_excel(output_path, index=False)
