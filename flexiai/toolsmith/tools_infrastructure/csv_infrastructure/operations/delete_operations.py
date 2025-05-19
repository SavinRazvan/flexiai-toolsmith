# FILE: flexiai/toolsmith/tools_infrastructure/csv_infrastructure/operations/delete_operations.py

import logging
from typing import Any, Dict

from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.managers.csv_manager import CSVManager
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.exceptions.csv_exceptions import CSVError
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.file_handler import (
    get_full_path,
    check_file_exists,
)
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.error_handler import handle_error_response

logger = logging.getLogger(__name__)


def delete_csv(
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Deletes an entire CSV file from disk.

    Args:
        path (str, optional): Directory path where the CSV resides.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file to delete (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"file_path": str}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path, load_csv=False)
        manager.delete_csv()
        message = f"CSV file '{file_name}' deleted successfully from '{path}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"file_path": full_path}
        }
    except CSVError as e:
        logger.error(f"CSVError while deleting CSV: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while deleting CSV '{file_name}': {e}")
        return handle_error_response(f"Failed to delete CSV '{file_name}': {e}")


def delete_row(
    row_index: int,
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Deletes a single row from a CSV by its zero-based index.

    Args:
        row_index (int): Zero-based index of the row to delete.
        path (str, optional): Directory path where the CSV resides.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"row_index": int}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        manager.delete_row(row_index)
        message = f"Row at index {row_index} deleted successfully from '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"row_index": row_index}
        }
    except CSVError as e:
        logger.error(f"CSVError while deleting row: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while deleting row {row_index} from '{file_name}': {e}")
        return handle_error_response(f"Failed to delete row {row_index} from '{file_name}': {e}")
