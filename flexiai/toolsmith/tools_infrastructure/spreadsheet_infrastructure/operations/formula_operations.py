# FILE: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/operations/formula_operations.py

"""
formula_operations module.

Provides high‑level functions to insert, apply, evaluate, and remove formulas,
as well as define named ranges in spreadsheets via SpreadsheetManager.
"""

import logging
from typing import Dict, Any

from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def insert_formula(
    sheet_name: str,
    cell: str,
    formula: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Insert a formula into a specific cell in a sheet.

    Args:
        sheet_name (str): Target sheet name.
        cell (str): Cell reference where to insert the formula (e.g., 'A1').
        formula (str): Formula string, must start with '=' (e.g., '=SUM(B1:B10)').
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name, cell, and formula.
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
    if not formula:
        error_msg = "Parameter 'formula' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.insert_formula(sheet_name, cell, formula)

        message = f"Formula '{formula}' inserted into '{cell}' on sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "cell": cell,
                "formula": formula
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while inserting formula: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while inserting formula: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while inserting formula: {e}")
        return handle_error_response(f"Failed to insert formula: {e}")


def apply_formula_to_column(
    sheet_name: str,
    column_name: str,
    formula_template: str,
    start_row: int = 1,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Apply a formula template down an entire column.

    Args:
        sheet_name (str): Target sheet name.
        column_name (str): Column letter (e.g., 'C') to apply the formula.
        formula_template (str): Formula with '{row}' placeholder (e.g., '=A{row}+B{row}').
        start_row (int, optional): 1‑based row number to start. Defaults to 1.
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name, column, formula_template, start_row, and rows_updated.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if not column_name:
        error_msg = "Parameter 'column_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if not formula_template:
        error_msg = "Parameter 'formula_template' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if start_row < 1:
        error_msg = "Parameter 'start_row' must be a positive integer."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        rows_updated = manager.apply_formula_to_column(sheet_name, column_name, formula_template, start_row)

        message = (
            f"Applied formula template '{formula_template}' to column '{column_name}' "
            f"on sheet '{sheet_name}' starting at row {start_row} ({rows_updated} rows updated)."
        )
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "column": column_name,
                "formula_template": formula_template,
                "start_row": start_row,
                "rows_updated": rows_updated
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while applying formula to column: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while applying formula to column: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while applying formula to column: {e}")
        return handle_error_response(f"Failed to apply formula to column '{column_name}': {e}")


def evaluate_formula(
    sheet_name: str,
    cell: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Retrieve the computed value of a cell if it contains a formula.

    Args:
        sheet_name (str): Target sheet name.
        cell (str): Cell reference to evaluate (e.g., 'A1').
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name, cell, and value.
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
        value = manager.evaluate_formula(sheet_name, cell)

        message = f"Evaluated formula in '{cell}' on sheet '{sheet_name}'. Value: {value}"
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "cell": cell,
                "value": value
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while evaluating formula: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while evaluating formula: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while evaluating formula: {e}")
        return handle_error_response(f"Failed to evaluate formula in cell '{cell}': {e}")


def remove_formula(
    sheet_name: str,
    cell: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Remove a formula from a specific cell.

    Args:
        sheet_name (str): Target sheet name.
        cell (str): Cell reference to clear (e.g., 'A1').
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name and cell.
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
        manager.remove_formula(sheet_name, cell)

        message = f"Removed formula from '{cell}' on sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "cell": cell
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while removing formula: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while removing formula: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while removing formula: {e}")
        return handle_error_response(f"Failed to remove formula from '{cell}': {e}")


def define_named_range(
    sheet_name: str,
    range_name: str,
    cell_range: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Define or overwrite a named range in a sheet.

    Args:
        sheet_name (str): Target sheet name.
        range_name (str): Name for the named range.
        cell_range (str): Cell range string (e.g., 'A1:B10').
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result (dict) containing sheet_name, range_name, and cell_range.
    """
    full_path = get_full_path(path, file_name)

    if not sheet_name:
        error_msg = "Parameter 'sheet_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if not range_name:
        error_msg = "Parameter 'range_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)
    if not cell_range:
        error_msg = "Parameter 'cell_range' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.define_named_range(sheet_name, range_name, cell_range)

        message = f"Named range '{range_name}' defined as '{cell_range}' on sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "range_name": range_name,
                "cell_range": cell_range
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while defining named range: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while defining named range: {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while defining named range: {e}")
        return handle_error_response(f"Failed to define named range '{range_name}': {e}")
