import pandas as pd
import os


def generate_tally_excel(entries, output_path):
    rows = []
    # voucher_number = 1  # Commented out: not needed for simplified output

    for e in entries:
        date = e["date"]
        amount = round(float(e["amount"]), 2)
        narration = e.get("narration", "")
        debit_ledger = e.get("debit", "")

        # --- SIMPLIFIED OUTPUT: Only Date, Narration, Debit, Credit ---
        # Determine debit/credit amount based on direction
        debit_amount = ""
        credit_amount = ""

        # If Bank A/c is debited, money came IN → Credit column
        # If Bank A/c is credited, money went OUT → Debit column
        if debit_ledger == "Bank A/c":
            credit_amount = amount
        else:
            debit_amount = amount

        rows.append({
            "Date": date,
            "Narration": narration,
            "Debit": debit_amount,
            "Credit": credit_amount
        })

        # --- ORIGINAL TALLY FORMAT (commented out for future use) ---
        # debit_ledger = e["debit"]
        # credit_ledger = e["credit"]
        # voucher_type = e.get("voucher_type", "Payment")
        #
        # # --- Row ordering based on voucher type ---
        # # Receipt: Cr ledger first (Row 1), Dr ledger second (Row 2)
        # # Payment/Contra: Dr ledger first (Row 1), Cr ledger second (Row 2)
        #
        # if voucher_type == "Receipt":
        #     # Row 1: Credit ledger (with date, voucher info, narration)
        #     rows.append({
        #         "Voucher Date": date,
        #         "Voucher Type Name": voucher_type,
        #         "Voucher Number": voucher_number,
        #         "Ledger Name": credit_ledger,
        #         "Ledger Amount": amount,
        #         "Ledger Amount Dr/Cr": "Cr",
        #         "Narration": narration
        #     })
        #     # Row 2: Debit ledger (blank date/voucher/narration)
        #     rows.append({
        #         "Voucher Date": "",
        #         "Voucher Type Name": "",
        #         "Voucher Number": "",
        #         "Ledger Name": debit_ledger,
        #         "Ledger Amount": amount,
        #         "Ledger Amount Dr/Cr": "Dr",
        #         "Narration": ""
        #     })
        # else:
        #     # Payment or Contra
        #     # Row 1: Debit ledger (with date, voucher info, narration)
        #     rows.append({
        #         "Voucher Date": date,
        #         "Voucher Type Name": voucher_type,
        #         "Voucher Number": voucher_number,
        #         "Ledger Name": debit_ledger,
        #         "Ledger Amount": amount,
        #         "Ledger Amount Dr/Cr": "Dr",
        #         "Narration": narration
        #     })
        #     # Row 2: Credit ledger (blank date/voucher/narration)
        #     rows.append({
        #         "Voucher Date": "",
        #         "Voucher Type Name": "",
        #         "Voucher Number": "",
        #         "Ledger Name": credit_ledger,
        #         "Ledger Amount": amount,
        #         "Ledger Amount Dr/Cr": "Cr",
        #         "Narration": ""
        #     })
        #
        # voucher_number += 1

    # --- SIMPLIFIED COLUMNS ---
    df = pd.DataFrame(rows, columns=[
        "Date",
        "Narration",
        "Debit",
        "Credit"
    ])

    # --- ORIGINAL COLUMNS (commented out for future use) ---
    # df = pd.DataFrame(rows, columns=[
    #     "Voucher Date",
    #     "Voucher Type Name",
    #     "Voucher Number",
    #     "Ledger Name",
    #     "Ledger Amount",
    #     "Ledger Amount Dr/Cr",
    #     "Narration"
    # ])

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Safe overwrite
    if os.path.exists(output_path):
        os.remove(output_path)

    df.to_excel(output_path, index=False, sheet_name="Accounting Voucher")
