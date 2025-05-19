# FILE: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/operations/data_entry_operations.py

"""
data_entry_operations module.

Provides high‑level functions for adding rows, writing headers, deleting rows,
and updating columns in spreadsheet workbooks via the SpreadsheetManager.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def add_row(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: str = "",
    data: List[Any] = None
) -> Dict[str, Any]:
    """
    Add a single row of data to a sheet.

    Args:
        path (str, optional): Directory path to the workbook.
        file_name (str, optional): Name of the workbook file.
        sheet_name (str): Name of the sheet to which the row will be added.
        data (List[Any]): List of values for the new row.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'sheet_name': str,
                    'row_data': List[Any]
                }
            }

    Raises:
        None: All exceptions are caught and returned in standardized response.
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.add_row(sheet_name, data)
        message = f"Row added successfully to sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "row_data": data
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in add_row: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in add_row: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in add_row: {e}")
        return handle_error_response(f"Failed to add row: {e}")


def add_rows(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: str = "",
    rows: List[List[Any]] = None
) -> Dict[str, Any]:
    """
    Add multiple rows of data to a sheet.

    Args:
        path (str, optional): Directory path to the workbook.
        file_name (str, optional): Name of the workbook file.
        sheet_name (str): Name of the sheet to which rows will be added.
        rows (List[List[Any]]): List of rows, each a list of values.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'sheet_name': str,
                    'rows_added': int
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.add_rows(sheet_name, rows)
        count = len(rows or [])
        message = f"{count} rows added successfully to sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "rows_added": count
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in add_rows: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in add_rows: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in add_rows: {e}")
        return handle_error_response(f"Failed to add rows: {e}")


def write_headers(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: str = "",
    headers: List[str] = None
) -> Dict[str, Any]:
    """
    Write a header row to a sheet.

    Args:
        path (str, optional): Directory path to the workbook.
        file_name (str, optional): Name of the workbook file.
        sheet_name (str): Name of the sheet where headers will be written.
        headers (List[str]): List of header labels.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'headers': List[str]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.write_headers(sheet_name, headers)
        message = f"Headers written successfully to sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "headers": headers
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in write_headers: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in write_headers: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in write_headers: {e}")
        return handle_error_response(f"Failed to write headers: {e}")


def delete_row(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: str = "",
    row_id: str = ""
) -> Dict[str, Any]:
    """
    Delete a specific row from a sheet.

    Args:
        path (str, optional): Directory path to the workbook.
        file_name (str, optional): Name of the workbook file.
        sheet_name (str): Name of the sheet from which to delete.
        row_id (str): 1-based index of the row to delete.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'row_id': str
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.delete_row(sheet_name, row_id)
        message = f"Row '{row_id}' deleted successfully from sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "row_id": row_id
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in delete_row: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in delete_row: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except ValueError as e:
        logger.error(f"ValueError in delete_row: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in delete_row: {e}")
        return handle_error_response(f"Failed to delete row '{row_id}': {e}")


def update_column(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: str = "",
    column_identifier: Union[str, int] = "",
    new_data: List[Any] = None,
    skip_header: bool = True,
    has_headers: bool = True
) -> Dict[str, Any]:
    """
    Update values in a specific column of a sheet.

    Args:
        path (str, optional): Directory path to the workbook.
        file_name (str, optional): Name of the workbook file.
        sheet_name (str): Name of the sheet to update.
        column_identifier (Union[str,int]): Column letter (e.g. 'C'), 1-based index, or header name.
        new_data (List[Any]): List of values to write down the column.
        skip_header (bool, optional): If True, start writing at row 2. Defaults to True.
        has_headers (bool, optional): If True, treat row 1 as header. Defaults to True.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'sheet_name': str,
                    'column_identifier': Union[str,int],
                    'rows_updated': int
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        count = manager.update_column(
            sheet_name=sheet_name,
            column_identifier=column_identifier,
            new_data=new_data,
            skip_header=skip_header,
            has_headers=has_headers
        )
        message = (
            f"Column '{column_identifier}' updated successfully in sheet '{sheet_name}'. "
            f"Rows updated: {count}."
        )
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "column_identifier": column_identifier,
                "rows_updated": count
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in update_column: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in update_column: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in update_column: {e}")
        return handle_error_response(f"Failed to update column '{column_identifier}': {e}")
