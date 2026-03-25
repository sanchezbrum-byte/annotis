"""Domain exception hierarchy.

All exceptions raised by Annotis derive from AnnotisError so callers
can catch the base class when they want to handle any application error.

Dependency rule: this module imports nothing outside the stdlib.
"""


class AnnotisError(Exception):
    """Base exception for all Annotis errors."""


class ImageLoadError(AnnotisError):
    """Raised when an image file cannot be opened or decoded."""


class UnsupportedFormatError(AnnotisError):
    """Raised when an image file extension is not in the supported set."""


class SessionNotFoundError(AnnotisError):
    """Raised when a session ID does not exist in the store."""


class ExportError(AnnotisError):
    """Raised when an export operation fails (IO, schema, empty dataset)."""


class InvalidAnnotationError(AnnotisError):
    """Raised when annotation data is structurally invalid."""
