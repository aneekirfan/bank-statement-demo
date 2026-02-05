from adapters.generic import GenericAdapter

class HDFCAdapter(GenericAdapter):
    def build_context(self, pdf_path):
        context = super().build_context(pdf_path)
        context["bank"] = "HDFC"
        context["confidence"]["bank"] = 1.0
        return context