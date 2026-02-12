import streamlit as st
import os
import shutil
import zipfile
from io import BytesIO

# --- 1. SETUP PAGE & STYLING (HumbleBees Theme) ---
st.set_page_config(page_title="Journal & Tally Builder", layout="centered", page_icon="🏦")

# Hide Streamlit's default header/footer for a clean "Pro" look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    /* Button styling to match the theme */
    div.stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. IMPORTS (Project Modules) ---
# Note: specific imports from your project structure
from parser.account_holder import extract_account_holder_name
from parser.bank_detector import detect_bank
from adapters import get_adapter
from accounting.classifier import classify_transaction
from accounting.journal_builder import build_journal_entry

# FIXED: Importing from 'writers' folder as per our fix
from writers.journal_pdf import generate_journal_pdf
from writers.tally_excel import generate_tally_excel

# --- 3. CONFIGURATION ---
INPUT_DIR = "temp_input"
OUTPUT_DIR = "temp_output"

def reset_folders():
    """Clears folders for a fresh run to prevent mixing data."""
    if os.path.exists(INPUT_DIR):
        shutil.rmtree(INPUT_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(INPUT_DIR)
    os.makedirs(OUTPUT_DIR)

def process_file(pdf_path, filename):
    """
    The Core Logic:
    1. Detect Bank
    2. Parse PDF
    3. Classify Transactions (inc. Utility vs Credit Card logic)
    4. Generate PDF & Excel
    """
    try:
        # A. Detect Bank & Build Context
        bank = detect_bank(pdf_path)
        if not bank:
            return None, "Could not detect bank (Only JKB, HDFC, SBI supported)."
            
        adapter = get_adapter(bank)
        context = adapter.build_context(pdf_path)
        
        # B. Get Account Holder Name
        account_holder = extract_account_holder_name(pdf_path)

        # C. Process Transactions
        entries = []
        tally_transactions = []
        for txn in context["transactions"]:
            # Skip opening balance rows
            if txn["date"] == "OPENING":
                continue
            
            # Classify (Purchase vs General Expense vs Sales)
            ttype = classify_transaction(txn)
            
            # Build Journal Entry
            entry = build_journal_entry(txn, ttype)
            entries.append(entry)
            tally_transactions.append({"txn": txn, "txn_type": ttype})

        if not entries:
            return None, "No valid transactions found in statement."

        # D. Generate Outputs
        stem = os.path.splitext(filename)[0]
        journal_name = f"{stem} Journal.pdf"
        tally_name = f"{stem} Tally.xlsx"
        
        journal_path = os.path.join(OUTPUT_DIR, journal_name)
        tally_path = os.path.join(OUTPUT_DIR, tally_name)

        # Generate the files using your 'writers' scripts
        generate_journal_pdf(entries, journal_path, account_holder)
        generate_tally_excel(tally_transactions, tally_path, bank)
        
        return {
            "bank": bank,
            "holder": account_holder,
            "journal_path": journal_path,   # Full path for reading
            "tally_path": tally_path,       # Full path for reading
            "journal_name": journal_name,   # Filename for download
            "tally_name": tally_name        # Filename for download
        }, None

    except Exception as e:
        return None, str(e)

# --- 4. THE UI LAYOUT ---

# Top Navigation: Back to Google Site
col_nav, col_title = st.columns([1, 4])
with col_nav:
    # This button redirects users back to your main website
    st.link_button("⬅ Back to Home", "https://www.humblebees.in/home") 

with col_title:
    st.title("Journal/Tally Builder")

st.markdown("Upload your **JKB, HDFC, or SBI** PDF statements to automatically generate Accounting Journals and Tally Excel sheets.")

# File Uploader
uploaded_files = st.file_uploader("Upload Statements (PDF)", type="pdf", accept_multiple_files=True)

# Process Button
if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Statements"):
        reset_folders()
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file to disk temporarily
            file_path = os.path.join(INPUT_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Run the logic
            data, error = process_file(file_path, uploaded_file.name)
            
            if error:
                st.error(f"❌ Error in {uploaded_file.name}: {error}")
            else:
                results.append(data)
                # Success Message
                st.success(f"✅ {data['holder']} ({data['bank']}) - Processed Successfully")
            
            # Update Progress
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("Processing Complete!")

        # --- DOWNLOAD SECTION ---
        if results:
            st.divider()
            st.subheader("📥 Download Results")
            
            # OPTION 1: Download All as ZIP
            if len(results) > 1:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for res in results:
                        zf.write(res["journal_path"], res["journal_name"])
                        zf.write(res["tally_path"], res["tally_name"])
                
                st.download_button(
                    label="📦 Download All (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="Processed_Statements.zip",
                    mime="application/zip",
                    type="primary"
                )
                st.write("---")

            # OPTION 2: Individual Files
            for res in results:
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    st.write(f"**{res['holder']}**")
                with c2:
                    with open(res["journal_path"], "rb") as f:
                        st.download_button("📄 Journal PDF", f, file_name=res["journal_name"])
                with c3:
                    with open(res["tally_path"], "rb") as f:
                        st.download_button("📊 Tally Excel", f, file_name=res["tally_name"])

