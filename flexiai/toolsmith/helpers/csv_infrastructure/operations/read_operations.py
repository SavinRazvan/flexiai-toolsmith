# FILE: flexiai/toolsmith/helpers/csv_infrastructure/operations/read_operations.py

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


def read_csv(
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Reads all rows from a CSV file.

    Args:
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"rows": List[Dict[str, Any]]}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        records: List[Dict[str, Any]] = manager.read_all()
        message = f"Read {len(records)} rows from '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"rows": records}
        }
    except CSVError as e:
        logger.error(f"CSVError while reading CSV: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while reading CSV '{file_name}': {e}")
        return handle_error_response(f"Failed to read CSV '{file_name}': {e}")


def read_row(
    index: int,
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Reads a single row by zero-based index.

    Args:
        index (int): Zero-based row index.
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"row_index": int, "row_data": Dict[str, Any]}
    """
    if file_name == "":
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        row = manager.read_row(index)
        message = f"Read row {index} from '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"row_index": index, "row_data": row}
        }
    except CSVError as e:
        logger.error(f"CSVError while reading row: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while reading row {index} in '{file_name}': {e}")
        return handle_error_response(f"Failed to read row {index} in '{file_name}': {e}")


def read_column(
    column: Union[str, int],
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Reads an entire column by name or zero-based index.

    Args:
        column (str|int): Column name or zero-based index.
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"column": Union[str,int], "column_data": List[Any]}
    """
    if file_name == "":
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        values = manager.read_column(column)
        message = f"Read column '{column}' from '{file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"column": column, "column_data": values}
        }
    except CSVError as e:
        logger.error(f"CSVError while reading column: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while reading column '{column}' in '{file_name}': {e}")
        return handle_error_response(f"Failed to read column '{column}' in '{file_name}': {e}")


def generate_csv_summary(
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Generates a summary of the CSV: number of rows, columns, and column names.

    Args:
        path (str, optional): Directory path to the CSV file.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"rows": int, "columns": int, "column_names": List[str]}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        summary = manager.generate_summary()
        message = f"CSV summary for '{file_name}' generated successfully."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": summary
        }
    except CSVError as e:
        logger.error(f"CSVError while generating summary: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while generating summary for '{file_name}': {e}")
        return handle_error_response(f"Failed to generate summary for '{file_name}': {e}")
