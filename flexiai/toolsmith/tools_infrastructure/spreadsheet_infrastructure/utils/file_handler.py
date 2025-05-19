# FILE: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/utils/file_handler.py

"""
file_handler module.

Provides utilities to validate spreadsheet file paths and ensure that files exist
and are valid .xlsx workbooks, as well as constructing full file paths.
"""

import os
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import (
    SpreadsheetFileNotFoundError,
    InvalidSpreadsheetFileError
)


def validate_path(path: str) -> bool:
    """
    Validate that the given directory path exists.

    Args:
        path (str): Directory path to validate.

    Returns:
        bool: True if the directory exists.

    Raises:
        SpreadsheetFileNotFoundError: If the directory does not exist.
    """
    if not os.path.exists(path):
        raise SpreadsheetFileNotFoundError(file_path=path)
    return True


def check_file_exists(path: str, file_name: str) -> bool:
    """
    Check that the specified file exists and is a valid .xlsx workbook.

    Args:
        path (str): Directory path containing the file.
        file_name (str): Name of the file.

    Returns:
        bool: True if the file exists and has a .xlsx extension.

    Raises:
        SpreadsheetFileNotFoundError: If the file does not exist at the constructed path.
        InvalidSpreadsheetFileError: If the file does not have a .xlsx extension.
    """
    full_path = get_full_path(path, file_name)
    if not os.path.exists(full_path):
        raise SpreadsheetFileNotFoundError(file_path=full_path)
    if not file_name.lower().endswith('.xlsx'):
        raise InvalidSpreadsheetFileError(file_path=full_path)
    return True


def get_full_path(path: str, file_name: str) -> str:
    """
    Construct the absolute path to the spreadsheet file.

    Args:
        path (str): Directory path.
        file_name (str): File name.

    Returns:
        str: The full file path (path + file_name).
    """
    return os.path.join(path, file_name)
