# FILE: flexiai/toolsmith/helpers/csv_infrastructure/exceptions/csv_exceptions.py

class CSVError(Exception):
    """
    Base class for all CSV-related exceptions.
    """
    def __init__(self, message: str):
        """
        Initialize a CSVError.

        Args:
            message (str): Explanation of the error.
        """
        super().__init__(message)
        self.message = message


class OperationNotSupportedError(CSVError):
    """
    Exception raised for unsupported CSV operations.
    """
    def __init__(self, operation: str):
        """
        Initialize an OperationNotSupportedError.

        Args:
            operation (str): Name of the unsupported operation.
        """
        message = f"Operation '{operation}' is not supported."
        super().__init__(message)


class CSVFileNotFoundError(CSVError):
    """
    Exception raised when a CSV file is not found.
    """
    def __init__(self, file_path: str):
        """
        Initialize a CSVFileNotFoundError.

        Args:
            file_path (str): Path to the CSV file that could not be found.
        """
        message = f"CSV file '{file_path}' not found."
        super().__init__(message)


class InvalidCSVFileError(CSVError):
    """
    Exception raised when a file exists but is not a valid '.csv' file (wrong extension).
    """
    def __init__(self, file_path: str):
        """
        Initialize an InvalidCSVFileError.

        Args:
            file_path (str): Path to the file with an invalid extension.
        """
        message = f"Invalid CSV file '{file_path}'. File must have a '.csv' extension."
        super().__init__(message)


class InvalidCSVFormatError(CSVError):
    """
    Exception raised for invalid or malformed CSV content.
    """
    def __init__(self, file_path: str):
        """
        Initialize an InvalidCSVFormatError.

        Args:
            file_path (str): Path to the CSV file that is malformed.
        """
        message = f"Malformed CSV file '{file_path}'. Must be a well‑formed .csv file."
        super().__init__(message)
