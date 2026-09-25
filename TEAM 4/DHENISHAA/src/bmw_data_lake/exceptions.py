"""Custom exceptions for the BMW data lake project."""


class BMWDataLakeError(Exception):
    """Base exception for project errors."""


class DataValidationError(BMWDataLakeError):
    """Raised when data validation fails."""


class InvalidSchemaError(BMWDataLakeError):
    """Raised when a schema is invalid or unexpected."""


class TransformationError(BMWDataLakeError):
    """Raised when transformation logic fails."""


class AWSConfigurationError(BMWDataLakeError):
    """Raised when AWS configuration is missing or invalid."""
