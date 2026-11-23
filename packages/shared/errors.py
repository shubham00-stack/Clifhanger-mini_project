"""Domain-specific exceptions for Cliffhanger Strength Analyzer."""


class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TenancyError(AppError):
    """Raised when an asset or analysis does not belong to the requested project."""
    def __init__(self, message: str = "Access denied: resource outside project tenancy boundary"):
        super().__init__(message=message, status_code=403)


class ModelProviderError(AppError):
    """Raised when NVIDIA NIM or external model provider fails."""
    def __init__(self, message: str = "Model inference failed", status_code: int = 502):
        super().__init__(message=message, status_code=status_code)


class RateLimitError(ModelProviderError):
    """Raised when upstream rate limits (429) are encountered."""
    def __init__(self, message: str = "Upstream provider rate limit exceeded"):
        super().__init__(message=message, status_code=429)


class ValidationError(AppError):
    """Raised when input validation or schema constraints fail."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, status_code=422)


class IngestionError(AppError):
    """Raised when file parsing or normalization fails."""
    def __init__(self, message: str = "Failed to ingest document"):
        super().__init__(message=message, status_code=400)
