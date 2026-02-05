from adapters.generic import GenericAdapter


class JKBAdapter(GenericAdapter):
    def build_context(self, pdf_path):
        context = super().build_context(pdf_path)
        context["bank"] = "JKB"
        context["confidence"]["bank"] = 1.0
        return context
