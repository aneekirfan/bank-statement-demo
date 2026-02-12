import os
from accounting.classifier import classify_transaction
from accounting.journal_builder import build_journal_entry
from writers.journal_pdf import generate_journal_pdf
from writers.tally_excel import generate_tally_excel
from parser.account_holder import extract_account_holder_name
from parser.bank_detector import detect_bank
from adapters import get_adapter

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def process_all_files():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all PDF files
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    
    if not files:
        print(f"No PDF files found in '{INPUT_DIR}/'")
        return

    print(f"Found {len(files)} statements to process.\n")

    for filename in files:
        print(f"--- Processing: {filename} ---")
        pdf_path = os.path.join(INPUT_DIR, filename)

        try:
            # 1. Detect Bank & Build Context
            bank = detect_bank(pdf_path)
            print(f"  Detected Bank: {bank}")
            
            adapter = get_adapter(bank)
            context = adapter.build_context(pdf_path)
            
            # 2. Get Account Holder
            account_holder = extract_account_holder_name(pdf_path)
            print(f"  Account Holder: {account_holder}")

            # 3. Process Transactions
            entries = []
            tally_transactions = []
            for txn in context["transactions"]:
                # SKIP the special 'OPENING' row for Journal/Tally
                # (It was only used internally to calculate the first balance)
                if txn["date"] == "OPENING":
                    continue

                ttype = classify_transaction(txn)
                entries.append(build_journal_entry(txn, ttype))
                tally_transactions.append({"txn": txn, "txn_type": ttype})

            if not entries:
                print("  WARNING: No transactions found. Skipping output generation.")
                continue

            # 4. Generate Outputs with Dynamic Names
            # Example: "sbi.pdf" -> "sbi Journal.pdf"
            stem = os.path.splitext(filename)[0]
            
            journal_path = os.path.join(OUTPUT_DIR, f"{stem} Journal.pdf")
            tally_path = os.path.join(OUTPUT_DIR, f"{stem} Tally.xlsx")

            generate_journal_pdf(entries, journal_path, account_holder)
            generate_tally_excel(tally_transactions, tally_path, bank)
            
            print(f"  Success! Output saved to: {journal_path}")

        except Exception as e:
            print(f"  ERROR processing {filename}: {e}")
        
        print("\n")

if __name__ == "__main__":
    process_all_files()