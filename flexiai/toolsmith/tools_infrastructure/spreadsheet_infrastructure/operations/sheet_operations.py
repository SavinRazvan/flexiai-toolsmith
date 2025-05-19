# FILE: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/operations/sheet_operations.py

"""
sheet_operations module.

Provides high‑level functions to create, rename, and delete sheets
within an Excel workbook via SpreadsheetManager, returning standardized
response dictionaries for downstream handling.
"""

import logging
from typing import Dict, Any, Optional

from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def create_sheet(
    sheet_name: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Creates a new sheet within an existing workbook.

    Args:
        sheet_name (str): Name of the sheet to create.
        path (str, optional): Directory path where the workbook resides.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        manager = SpreadsheetManager(file_path=full_path)
        manager.create_sheet(sheet_name)
        message = f"Sheet '{sheet_name}' created successfully in '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while creating sheet: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while creating sheet '{sheet_name}': {e}")
        return handle_error_response(f"Failed to create sheet: {e}")


def rename_sheet(
    sheet_name: str,
    new_sheet_name: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Renames an existing sheet within a workbook.

    Args:
        sheet_name (str): Current name of the sheet.
        new_sheet_name (str): New name for the sheet.
        path (str, optional): Directory path where the workbook resides.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if not new_sheet_name:
        error_msg = "Parameter 'new_sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        manager = SpreadsheetManager(file_path=full_path)
        manager.rename_sheet(sheet_name, new_sheet_name)
        message = f"Sheet '{sheet_name}' renamed to '{new_sheet_name}' successfully in '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "old_sheet_name": sheet_name,
                "new_sheet_name": new_sheet_name
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while renaming sheet: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while renaming sheet '{sheet_name}': {e}")
        return handle_error_response(f"Failed to rename sheet: {e}")


def delete_sheet(
    sheet_name: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Deletes an existing sheet from a workbook.

    Args:
        sheet_name (str): Name of the sheet to delete.
        path (str, optional): Directory path where the workbook resides.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        manager = SpreadsheetManager(file_path=full_path)
        manager.delete_sheet(sheet_name)
        message = f"Sheet '{sheet_name}' deleted successfully from '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while deleting sheet: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while deleting sheet '{sheet_name}': {e}")
        return handle_error_response(f"Failed to delete sheet: {e}")
