# FILE: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/exceptions/spreadsheet_exceptions.py

"""
spreadsheet_exceptions module.

Defines custom exceptions for spreadsheet operations:
- SpreadsheetError: base class for all spreadsheet-related errors.
- OperationNotSupportedError: for unsupported operations.
- SpreadsheetFileNotFoundError: when a spreadsheet file cannot be found.
- InvalidSpreadsheetFileError: when a spreadsheet file is invalid.
"""

class SpreadsheetError(Exception):
    """
    Base class for all spreadsheet-related errors.

    Args:
        message (str): Description of the error.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class OperationNotSupportedError(SpreadsheetError):
    """
    Exception raised when a requested operation is not supported.

    Args:
        operation (str): Name of the unsupported operation.
    """
    def __init__(self, operation: str):
        message = f"Operation '{operation}' is not supported."
        super().__init__(message)


class SpreadsheetFileNotFoundError(SpreadsheetError):
    """
    Exception raised when the specified spreadsheet file is not found.

    Args:
        file_path (str): Path to the spreadsheet that was not found.
    """
    def __init__(self, file_path: str):
        message = f"Spreadsheet file '{file_path}' not found."
        super().__init__(message)


class InvalidSpreadsheetFileError(SpreadsheetError):
    """
    Exception raised when the provided spreadsheet file is invalid.

    Args:
        file_path (str): Path to the invalid spreadsheet file.
    """
    def __init__(self, file_path: str):
        message = f"Invalid spreadsheet file '{file_path}'. Must be a .xlsx file."
        super().__init__(message)
