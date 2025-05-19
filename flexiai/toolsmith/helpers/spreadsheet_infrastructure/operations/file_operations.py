# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/operations/file_operations.py

"""
file_operations module.

Provides high‑level functions for creating and deleting spreadsheet workbooks
via the SpreadsheetManager.
"""

import os
import logging
from typing import Dict, Any

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import get_full_path
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def create_workbook(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Create a new workbook file at the specified location.

    Args:
        path (str, optional): Directory in which to save the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file to create.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]:
            {
                "status": bool,
                "message": str,
                "result": {
                    "file_path": str
                }
            }
    """
    try:
        full_path = get_full_path(path, file_name)

        # Ensure directory exists
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Created directory '{path}' as it did not exist.")

        # Create workbook without loading existing file
        manager = SpreadsheetManager(file_path=full_path, load_workbook=False)
        manager.create_workbook()

        message = f"Workbook '{file_name}' created successfully at '{path}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"file_path": full_path}
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in create_workbook: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in create_workbook: {e}")
        return handle_error_response(f"Failed to create workbook '{file_name}': {e}")


def delete_workbook(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Delete an existing workbook file from disk.

    Args:
        path (str, optional): Directory containing the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file to delete.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]:
            {
                "status": bool,
                "message": str,
                "result": {
                    "file_path": str
                }
            }
    """
    try:
        full_path = get_full_path(path, file_name)

        manager = SpreadsheetManager(file_path=full_path)
        manager.delete_workbook()

        message = f"Workbook '{file_name}' deleted successfully from '{path}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"file_path": full_path}
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in delete_workbook: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in delete_workbook: {e}")
        return handle_error_response(f"Failed to delete workbook '{file_name}': {e}")
