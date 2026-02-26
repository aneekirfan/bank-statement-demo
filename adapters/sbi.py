import re

from adapters.generic import GenericAdapter

# SBI lines start with two dates: "DD/MM/YYYY DD/MM/YYYY ..."
_DOUBLE_DATE_RE = re.compile(
    r"^(\d{2}/\d{2}/\d{4})\s+\d{2}/\d{2}/\d{4}\s+"
)


class SBIAdapter(GenericAdapter):
    """Adapter for State Bank of India statements."""

    # ── Hook overrides ─────────────────────────────────────────────────

    def junk_patterns(self):
        return [
            # Column headers (repeated on every page)
            "txn date",
            "value date description",
            "ref no./cheque",
            "branch debit credit balance",
            "no. code",
            # Account metadata / header
            "account name",
            "account number",
            "account description",
            "account statement from",
            "drawing power",
            "interest rate",
            "mod balance",
            "cif no",
            "ifs code",
            "micr code",
            "pending statement link",
            "request id",
            # SBI footer
            "computer generated statement",
            "does not require a signature",
            # (cid:X) tab-character artefacts that appear alone
            "date :(cid:",
            "address ",
        ]

    def is_opening_balance(self, line_upper):
        return "BALANCE AS ON" in line_upper

    def parse_date_and_text(self, clean_line):
        """
        SBI lines look like:
            01/04/2024 01/04/2024 TO TRANSFER- ...
        We take the first date as the transaction date and skip
        both dates to reach the description text.
        """
        m = _DOUBLE_DATE_RE.match(clean_line)
        if m:
            return m.group(1), clean_line[m.end():].strip()
        # Fallback to default (single date)
        return super().parse_date_and_text(clean_line)

    def clean_raw_text(self, text):
        """Strip stray (cid:N) artefacts from SBI text."""
        text = re.sub(r"\(cid:\d+\)", "", text)
        # Remove trailing SBI footer that may get concatenated
        text = re.sub(
            r"\s*\*?\*?This is a computer generated statement.*$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        return text.strip()

    # ── Context ────────────────────────────────────────────────────────

    def build_context(self, pdf_path):
        context = super().build_context(pdf_path)
        context["bank"] = "SBI"
        context["confidence"]["bank"] = 1.0
        # Clean (cid:N) artefacts from account holder name
        holder = context.get("account_holder", "")
        holder = re.sub(r"\(cid:\d+\)", "", holder).strip()
        context["account_holder"] = holder
        return context
