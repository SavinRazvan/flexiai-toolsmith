# FILE: flexiai/toolsmith/helpers/csv_infrastructure/utils/file_handler.py

import os
from flexiai.toolsmith.helpers.csv_infrastructure.exceptions.csv_exceptions import (
    CSVFileNotFoundError,
    InvalidCSVFileError,
)

def validate_path(path: str) -> bool:
    """
    Validates that the given directory path exists.

    Args:
        path (str): Directory path to validate.

    Returns:
        bool: True if the path exists.

    Raises:
        CSVFileNotFoundError: If the directory does not exist.
    """
    if not os.path.isdir(path):
        raise CSVFileNotFoundError(file_path=path)
    return True

def get_full_path(path: str, file_name: str) -> str:
    """
    Constructs the absolute path to the CSV file.

    Args:
        path (str): Directory path.
        file_name (str): CSV file name.

    Returns:
        str: Full filesystem path to the CSV file.
    """
    return os.path.join(path, file_name)

def check_file_exists(path: str, file_name: str) -> bool:
    """
    Checks that a CSV file exists and has the correct '.csv' extension.

    Args:
        path (str): Directory path where the file should reside.
        file_name (str): Name of the CSV file.

    Returns:
        bool: True if the file exists and is a valid CSV file.

    Raises:
        CSVFileNotFoundError: If the directory or file is not found.
        InvalidCSVFileError: If the file does not end with '.csv'.
    """
    # Ensure the directory itself exists
    validate_path(path)

    full_path = get_full_path(path, file_name)
    if not os.path.isfile(full_path):
        raise CSVFileNotFoundError(file_path=full_path)
    if not file_name.lower().endswith('.csv'):
        raise InvalidCSVFileError(file_path=full_path)
    return True
