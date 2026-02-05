import streamlit as st
import os
import shutil
import zipfile
from io import BytesIO

# Import your existing modules
from parser.context_builder import build_statement_context
from parser.account_holder import extract_account_holder_name
from parser.bank_detector import detect_bank
from adapters import get_adapter
from accounting.classifier import classify_transaction
from accounting.journal_builder import build_journal_entry
from writers.journal_pdf import generate_journal_pdf
from writers.tally_excel import generate_tally_excel

# --- CONFIGURATION ---
INPUT_DIR = "temp_input"
OUTPUT_DIR = "temp_output"

def reset_folders():
    """Clears folders for a fresh run"""
    if os.path.exists(INPUT_DIR):
        shutil.rmtree(INPUT_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(INPUT_DIR)
    os.makedirs(OUTPUT_DIR)

def process_file(pdf_path, filename):
    """Core logic extracted from your main.py"""
    try:
        # 1. Detect Bank & Build Context
        bank = detect_bank(pdf_path)
        adapter = get_adapter(bank)
        context = adapter.build_context(pdf_path)
        
        # 2. Get Account Holder
        account_holder = extract_account_holder_name(pdf_path)

        # 3. Process Transactions
        entries = []
        for txn in context["transactions"]:
            if txn["date"] == "OPENING":
                continue
            ttype = classify_transaction(txn)
            entries.append(build_journal_entry(txn, ttype))

        if not entries:
            return None, "No transactions found."

        # 4. Generate Outputs
        stem = os.path.splitext(filename)[0]
        journal_name = f"{stem} Journal.pdf"
        tally_name = f"{stem} Tally.xlsx"
        
        journal_path = os.path.join(OUTPUT_DIR, journal_name)
        tally_path = os.path.join(OUTPUT_DIR, tally_name)

        generate_journal_pdf(entries, journal_path, account_holder)
        generate_tally_excel(entries, tally_path)
        
        return {
            "bank": bank,
            "holder": account_holder,
            "journal": journal_path,
            "tally": tally_path,
            "journal_name": journal_name,
            "tally_name": tally_name
        }, None

    except Exception as e:
        return None, str(e)

# --- WEBSITE UI ---
st.set_page_config(page_title="Bank Statement Processor", layout="centered")

st.title("🏦 Bank Statement to Tally/Journal")
st.markdown("Upload your **JKB, HDFC, or SBI** PDF statements to generate accounting journals.")

# File Uploader
uploaded_files = st.file_uploader("Upload Statements (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Files"):
        reset_folders()
        
        results = []
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Save uploaded file to disk (required for pdfplumber)
            file_path = os.path.join(INPUT_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process
            data, error = process_file(file_path, uploaded_file.name)
            
            if error:
                st.error(f"Error processing {uploaded_file.name}: {error}")
            else:
                results.append(data)
                st.success(f"✅ Processed: {uploaded_file.name} ({data['bank']} - {data['holder']})")
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- DOWNLOAD SECTION ---
        if results:
            st.divider()
            st.subheader("📥 Downloads")
            
            # 1. Zip All Option
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for res in results:
                    zf.write(res["journal"], res["journal_name"])
                    zf.write(res["tally"], res["tally_name"])
            
            st.download_button(
                label="📦 Download All Files (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="Processed_Statements.zip",
                mime="application/zip",
                type="primary"
            )
            
            # 2. Individual Files
            st.write("---")
            for res in results:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{res['holder']}** ({res['bank']})")
                with col2:
                    with open(res["journal"], "rb") as f:
                        st.download_button("📄 Journal PDF", f, file_name=res["journal_name"])
                with col3:
                    with open(res["tally"], "rb") as f:
                        st.download_button("📊 Tally Excel", f, file_name=res["tally_name"])