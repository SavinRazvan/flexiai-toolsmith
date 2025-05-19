# FILE: flexiai/toolsmith/helpers/csv_infrastructure/operations/update_operations.py

import logging
from typing import Any, Dict, List, Union

from flexiai.toolsmith.helpers.csv_infrastructure.managers.csv_manager import CSVManager
from flexiai.toolsmith.helpers.csv_infrastructure.exceptions.csv_exceptions import CSVError
from flexiai.toolsmith.helpers.csv_infrastructure.utils.file_handler import (
    get_full_path,
    check_file_exists,
)
from flexiai.toolsmith.helpers.csv_infrastructure.utils.error_handler import handle_error_response

logger = logging.getLogger(__name__)


def append_row(
    row: Dict[str, Any],
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Appends a single row to a CSV file.

    Args:
        row (Dict[str, Any]): Mapping of column names (or indices) to values.
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"appended_row": Dict[str, Any]}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)
    full_path = get_full_path(path, file_name)

    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        manager.append_row(row)
        message = f"Appended one row to '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"appended_row": row}
        }
    except CSVError as e:
        logger.error(f"CSVError while appending row: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while appending row to '{file_name}': {e}")
        return handle_error_response(f"Failed to append row to '{file_name}': {e}")


def append_rows(
    rows: List[Dict[str, Any]],
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Appends multiple rows to a CSV file.

    Args:
        rows (List[Dict[str, Any]]): List of row mappings.
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"appended_count": int}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)
    full_path = get_full_path(path, file_name)

    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        manager.append_rows(rows)
        count = len(rows)
        message = f"Appended {count} rows to '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"appended_count": count}
        }
    except CSVError as e:
        logger.error(f"CSVError while appending rows: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while appending rows to '{file_name}': {e}")
        return handle_error_response(f"Failed to append rows to '{file_name}': {e}")


def update_cell(
    row_index: int,
    column: Union[str, int],
    value: Any,
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Updates a single cell in a CSV by row index and column.

    Args:
        row_index (int): Zero-based row index.
        column (str|int): Column name or zero-based index.
        value (Any): New value to set.
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"row_index": int, "column": Union[str,int], "new_value": Any}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)
    full_path = get_full_path(path, file_name)

    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        manager.update_cell(row_index, column, value)
        message = f"Updated cell at row {row_index}, column '{column}' in '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "row_index": row_index,
                "column": column,
                "new_value": value
            }
        }
    except CSVError as e:
        logger.error(f"CSVError while updating cell: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while updating cell in '{file_name}': {e}")
        return handle_error_response(f"Failed to update cell in '{file_name}': {e}")
