import pdfplumber
import re

from adapters.base import BaseAdapter
from parser.row_normalizer import normalize_transactions
from parser.account_holder import extract_account_holder_name

# Date regex — matches DD-MM-YYYY, DD/MM/YYYY, DD/MM/YY
DATE_RE = re.compile(r"^\d{2}[-/]\d{2}[-/]\d{2,4}")


class GenericAdapter(BaseAdapter):
    """
    Default adapter.  Extracts transactions from any bank statement
    using the hook methods defined in BaseAdapter.  Bank-specific
    adapters override hooks instead of reimplementing the whole pipeline.
    """

    # ── Pipeline ───────────────────────────────────────────────────────

    def build_context(self, pdf_path):
        raw_txns = self._extract_transactions(pdf_path)
        transactions = normalize_transactions(raw_txns)

        account_holder = extract_account_holder_name(pdf_path)

        return {
            "bank": "UNKNOWN",
            "account_holder": account_holder,
            "transactions": transactions,
            "confidence": {
                "bank": 0.3,
                "account_holder": 0.7 if account_holder != "Account Holder" else 0.3,
                "transactions": 1.0 if transactions else 0.0,
            },
        }

    # ── Transaction extraction (uses adapter hooks) ────────────────────

    def _extract_transactions(self, pdf_path):
        """
        Walk every page of the PDF, split into lines, and group them
        into raw transaction dicts ``{date, text}``.

        All bank-specific decisions are delegated to hook methods:
        - ``self.junk_patterns()``
        - ``self.is_opening_balance(line_upper)``
        - ``self.parse_date_and_text(clean_line)``
        - ``self.clean_raw_text(text)``
        """
        junk = self.junk_patterns()
        transactions = []
        current = None
        in_page_footer = False

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                raw_text = page.extract_text()
                if not raw_text:
                    continue

                # Reset page-footer flag at the start of each new page
                in_page_footer = False

                for line in raw_text.split("\n"):
                    # 1. Clean CSV artifacts
                    clean_line = line.replace('"', '').replace("','", " ").strip()
                    if not clean_line:
                        continue

                    # 2. Skip junk / disclaimer lines (adapter-supplied)
                    if junk and any(pat in clean_line.lower() for pat in junk):
                        continue

                    # 3. Totals and separators mark end of page's transactions.
                    #    Finalize current txn and stop appending until next date.
                    is_separator = (
                        len(clean_line) > 3
                        and all(c in "-=_ " for c in clean_line)
                    )
                    if "TOTAL" in clean_line.upper() or is_separator:
                        if current and not in_page_footer:
                            current["text"] = self.clean_raw_text(current["text"])
                            transactions.append(current)
                            current = None
                        in_page_footer = True
                        continue

                    # 3b. Skip standalone short numeric lines (e.g. pincodes)
                    if clean_line.isdigit() and len(clean_line) <= 6:
                        continue

                    # 4. Opening balance
                    upper_line = clean_line.upper()
                    if self.is_opening_balance(upper_line):
                        if current:
                            current["text"] = self.clean_raw_text(current["text"])
                            transactions.append(current)

                        current = {"date": "OPENING", "text": clean_line}
                        in_page_footer = False
                        continue

                    # 5. Standard transaction (line starts with a date)
                    if DATE_RE.match(clean_line):
                        if current:
                            current["text"] = self.clean_raw_text(current["text"])
                            transactions.append(current)

                        date, text = self.parse_date_and_text(clean_line)
                        current = {"date": date, "text": text}
                        in_page_footer = False
                    else:
                        # Continuation line — append to current transaction
                        # but only if we haven't hit a page footer
                        if current and not in_page_footer:
                            current["text"] += " " + clean_line

        # Flush the last transaction
        if current:
            current["text"] = self.clean_raw_text(current["text"])
            transactions.append(current)

        return transactions
