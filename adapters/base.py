class BaseAdapter:
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
