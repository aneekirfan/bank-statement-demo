import pandas as pd
import os


def generate_tally_excel(entries, output_path):
    rows = []

    for e in entries:
        date = e["date"]
        debit_ledger = e["debit"]
        credit_ledger = e["credit"]
        amount = round(float(e["amount"]), 2)
        narration = e.get("narration", "")

        # Debit row (with date)
        rows.append({
            "Date": date,
            "Ledger Name": debit_ledger,
            "Debit Amount": amount,
            "Credit Amount": "",
            "Narration": narration
        })

        # Credit row (NO date)
        rows.append({
            "Date": "",
            "Ledger Name": credit_ledger,
            "Debit Amount": "",
            "Credit Amount": amount,
            "Narration": narration
        })

    df = pd.DataFrame(rows, columns=[
        "Date",
        "Ledger Name",
        "Debit Amount",
        "Credit Amount",
        "Narration"
    ])

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Safe overwrite
    if os.path.exists(output_path):
        os.remove(output_path)

    df.to_excel(output_path, index=False)
