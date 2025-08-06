"""Source module exceptions."""


class RedirectAuthorize(Exception):
    """Custom class to signal a redirect to trigger OAuth autorization workflow for a specific source_name."""

    def __init__(self, url_name, source_name):
        """Init for RedirectAuthorize."""
        self.url_name = url_name
        self.source_name = source_name
        super().__init__()
