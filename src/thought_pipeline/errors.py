"""Domain-specific exceptions with user-facing messages."""


class PipelineError(Exception):
    """Base exception for expected pipeline failures."""


class ConfigurationError(PipelineError):
    """Raised when required configuration is missing or inconsistent."""


class ContentNotFoundError(PipelineError):
    """Raised when an experiment ID or referenced file cannot be found."""


class GenerationError(PipelineError):
    """Raised when an external or offline generator cannot return a package."""


class QualityValidationError(PipelineError):
    """Raised when structurally valid output fails editorial rules."""
