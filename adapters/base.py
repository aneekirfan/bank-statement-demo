import re


class BaseAdapter:
    """
    Base adapter that all bank-specific adapters inherit from.
    Subclasses override hook methods to handle bank-specific parsing.
    """

    # ── Hook methods (override in subclasses) ──────────────────────────

    def junk_patterns(self):
        """
        Return a list of lowercase substrings.  Any extracted line whose
        lowercased form contains one of these is silently skipped.
        """
        return []

    def is_opening_balance(self, line_upper):
        """
        Return True if *line_upper* (already uppercased) represents an
        opening-balance row.  Default detects common markers.
        """
        markers = ["B/F", "BROUGHT FORWARD", "BALANCE AS ON", "OPENING BALANCE"]
        return any(m in line_upper for m in markers)

    def parse_date_and_text(self, clean_line):
        """
        Given a cleaned line that starts with a date, return (date, text).
        Default: first 10 characters → date, rest → text.
        """
        return clean_line.split()[0], clean_line[10:].strip()

    def clean_raw_text(self, text):
        """
        Post-process the concatenated raw text of a single transaction
        before it is handed to the normaliser.
        """
        return text

    # ── Core interface ─────────────────────────────────────────────────

    def build_context(self, pdf_path):
        """
        Must return a StatementContext dict:
        {
          bank,
          account_holder,
          transactions,
          confidence
        }
        """
        raise NotImplementedError
