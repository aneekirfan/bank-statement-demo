"""
context_builder
~~~~~~~~~~~~~~~
Backward-compatible helper.  The canonical way to build a statement
context is now via the adapter pipeline (see adapters/).
"""

from parser.account_holder import extract_account_holder_name
from parser.bank_detector import detect_bank
from adapters import get_adapter


def build_statement_context(pdf_path):
    """Detect the bank and delegate to the appropriate adapter."""
    bank = detect_bank(pdf_path)
    adapter = get_adapter(bank)
    return adapter.build_context(pdf_path)
