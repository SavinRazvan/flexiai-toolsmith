# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/operations/data_retrieval_operations.py

"""
data_retrieval_operations module.

Provides high‑level functions for retrieving cell values, rows, columns,
and filtering rows in spreadsheet workbooks via the SpreadsheetManager.
"""

import logging
from typing import Dict, Any, Union, List

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def retrieve_cell(
    sheet_name: str,
    cell: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Retrieve the value of a single cell.

    Args:
        sheet_name (str): Name of the sheet.
        cell (str): Cell reference to retrieve (e.g. 'A1').
        path (str, optional): Directory containing the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'cell': str,
                    'value': Any
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        value = manager.retrieve_cell(sheet_name, cell)
        message = f"Value retrieved from cell '{cell}' in sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "cell": cell,
                "value": value
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in retrieve_cell: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in retrieve_cell: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in retrieve_cell: {e}")
        return handle_error_response(f"Failed to retrieve cell '{cell}': {e}")


def retrieve_row(
    sheet_name: str,
    row_id: int,
    skip_header: bool = False,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Retrieve all values from a single row.

    Args:
        sheet_name (str): Name of the sheet.
        row_id (int): 1-based row index.
        skip_header (bool, optional): If True and row_id == 1, treats row 1 as header.
        path (str, optional): Directory containing the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'row_id': int,
                    'row_data': List[Any]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        row_data = manager.retrieve_row(sheet_name, row_id, skip_header=skip_header)
        message = f"Data retrieved from row '{row_id}' in sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "row_id": row_id,
                "row_data": row_data
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in retrieve_row: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in retrieve_row: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in retrieve_row: {e}")
        return handle_error_response(f"Failed to retrieve row '{row_id}': {e}")


def retrieve_column(
    sheet_name: str,
    column_identifier: Union[str, int],
    skip_header: bool = False,
    has_headers: bool = True,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Retrieve all values from a column.

    Args:
        sheet_name (str): Name of the sheet.
        column_identifier (Union[str,int]): Column letter, 1-based index, or header name.
        skip_header (bool, optional): If True, skip the first row. Defaults to False.
        has_headers (bool, optional): If True, allows header-based identification. Defaults to True.
        path (str, optional): Directory containing the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'column_identifier': Union[str,int],
                    'column_data': List[Any]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        column_data = manager.retrieve_column(
            sheet_name,
            column_identifier,
            skip_header=skip_header,
            has_headers=has_headers
        )
        message = f"Data retrieved from column '{column_identifier}' in sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "column_identifier": column_identifier,
                "column_data": column_data
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in retrieve_column: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in retrieve_column: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in retrieve_column: {e}")
        return handle_error_response(f"Failed to retrieve column '{column_identifier}': {e}")


def filter_rows(
    sheet_name: str,
    column_identifier: Union[str, int],
    condition_type: str,
    condition_value: str,
    skip_header: bool = True,
    has_headers: bool = True,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Filter rows based on a condition applied to a column.

    Args:
        sheet_name (str): Name of the sheet.
        column_identifier (Union[str,int]): Column letter, 1-based index, or header name.
        condition_type (str): Condition type ('equals', 'greater_than', etc.).
        condition_value (str): Value to compare against.
        skip_header (bool, optional): If True, skip the first row. Defaults to True.
        has_headers (bool, optional): If True, allows header-based identification. Defaults to True.
        path (str, optional): Directory containing the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'filtered_rows': List[List[Any]]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        filtered = manager.filter_rows(
            sheet_name,
            column_identifier,
            condition_type,
            condition_value,
            skip_header=skip_header,
            has_headers=has_headers
        )
        message = f"Rows filtered in sheet '{sheet_name}' by '{condition_type}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "filtered_rows": filtered
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in filter_rows: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in filter_rows: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in filter_rows: {e}")
        return handle_error_response(f"Failed to filter rows: {e}")


def retrieve_rows(
    sheet_name: str,
    start_row: int = 1,
    max_rows: int = 20,
    skip_header: bool = False,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Retrieve a block of rows with pagination.

    Args:
        sheet_name (str): Name of the sheet.
        start_row (int, optional): 1-based starting row. Defaults to 1.
        max_rows (int, optional): Maximum number of rows to retrieve. Defaults to 20.
        skip_header (bool, optional): If True and start_row <= 1, treat row 1 as header. Defaults to False.
        path (str, optional): Directory containing the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': {
                    'rows': List[List[Any]]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        rows_data = manager.retrieve_rows(
            sheet_name=sheet_name,
            start_row=start_row,
            max_rows=max_rows,
            skip_header=skip_header
        )
        message = f"Rows retrieved from sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "rows": rows_data
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in retrieve_rows: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in retrieve_rows: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in retrieve_rows: {e}")
        return handle_error_response(f"Failed to retrieve rows: {e}")
