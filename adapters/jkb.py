from adapters.generic import GenericAdapter


class JKBAdapter(GenericAdapter):
    """Adapter for Jammu & Kashmir Bank statements."""

    # ── Hook overrides ─────────────────────────────────────────────────

    def junk_patterns(self):
        return [
            # JKB disclaimer block (appears on every page)
            "unless the constituent notifies the bank",
            "immediately of any discrepancy found",
            "by him in this statement of account",
            "it will be taken that he has found",
            "the account correct",
            # Page header / account metadata
            "printed by",
            "statement of account",
            "interest rate",
            "ckyc id",
            "no nomination available",
            "ifsc code",
            "micr code",
            "jammu and kashmir bank",
            "phone code",
            "general current account",
            "a/c no:",
            "boulevard road",
            "funds in clearing",
            "date stamp",
            # Address / recipient block (repeated on every page)
            "to:",
            "m/s.",
            "dalgate",
            "srinagar",
            # Column headers & summary lines
            "date particulars",
            "withdrawals deposits balance",
            "chq.no./ref.no.",
            "effective available amount",
            "total available amount",
            "ffd contribution",
            # Misc
            "end of statement",
        ]

    def is_pincode_line(self, clean_line):
        """Check if line is just a standalone pincode (6 digits)."""
        return clean_line.strip().isdigit() and len(clean_line.strip()) == 6

    def is_opening_balance(self, line_upper):
        return any(m in line_upper for m in ["B/F", "BROUGHT FORWARD"])

    # ── Context ────────────────────────────────────────────────────────

    def build_context(self, pdf_path):
        context = super().build_context(pdf_path)
        context["bank"] = "JKB"
        context["confidence"]["bank"] = 1.0
        return context
