# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/operations/formatting_operations.py

"""
formatting_operations module.

Provides high‑level functions for applying cell formatting and conditional formatting
to spreadsheets via the SpreadsheetManager.
"""

from typing import Dict, Any, Optional
import logging

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def set_cell_format(
    sheet_name: str,
    cell: str,
    style_rules: Optional[Dict[str, Any]] = None,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Apply specific styling to a single cell in a sheet.

    Args:
        sheet_name (str): Target sheet name.
        cell (str): Cell reference to format (e.g., 'A1').
        style_rules (Optional[Dict[str, Any]]): Styling rules to apply.
            Example:
                {
                    "font": {"bold": True, "color": "FF0000"},
                    "fill": {"patternType": "solid", "fgColor": "FFFF00"},
                }
            If None, default safe styling is applied.
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name, cell, and style_rules.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if not cell:
        error_msg = "Parameter 'cell' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.set_cell_format(sheet_name, cell, style_rules)

        message = f"Cell format applied successfully to '{cell}' in sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "cell": cell,
                "style_rules": style_rules
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while setting cell format: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while setting cell format: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while setting cell format: {e}")
        return handle_error_response(f"Failed to set cell format: {e}")


def apply_conditional_formatting(
    sheet_name: str,
    formatting_rules: Optional[Dict[str, Any]] = None,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Add conditional formatting rules to a range within a sheet.

    Args:
        sheet_name (str): Target sheet name.
        formatting_rules (Optional[Dict[str, Any]]): Conditional formatting parameters.
            Example:
                {
                    "range": "A1:A10",
                    "type": "containsText",
                    "text": "Hello",
                    "font": {"color": "FF0000", "bold": True},
                    "fill": {"fgColor": "FFFF00"}
                }
            If None, a no‑op default is used.
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name and formatting_rules.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.apply_conditional_formatting(sheet_name, formatting_rules)

        message = f"Conditional formatting applied successfully to sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "formatting_rules": formatting_rules
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while applying conditional formatting: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while applying conditional formatting: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while applying conditional formatting: {e}")
        return handle_error_response(f"Failed to apply conditional formatting: {e}")
