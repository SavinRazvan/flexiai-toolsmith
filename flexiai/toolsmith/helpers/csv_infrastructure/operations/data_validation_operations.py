# FILE: flexiai/toolsmith/helpers/csv_infrastructure/operations/data_validation_operations.py

import logging
from typing import Any, Dict, List

from flexiai.toolsmith.helpers.csv_infrastructure.managers.csv_manager import CSVManager
from flexiai.toolsmith.helpers.csv_infrastructure.exceptions.csv_exceptions import CSVError
from flexiai.toolsmith.helpers.csv_infrastructure.utils.file_handler import (
    check_file_exists,
    get_full_path,
)
from flexiai.toolsmith.helpers.csv_infrastructure.utils.error_handler import handle_error_response

logger = logging.getLogger(__name__)


def validate_csv_structure(
    required_columns: List[str],
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Validates that the CSV file contains all required columns.

    Args:
        required_columns (List[str]): List of column names that must be present.
        path (str, optional): Directory path where the CSV resides.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file to validate (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response dict with:
            - status (bool): True if all columns are present, False otherwise.
            - message (str): Success or error message.
            - result (bool): True if valid structure, False if invalid.
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        is_valid = manager.validate_structure(required_columns)
        message = "CSV structure is valid." if is_valid else "CSV structure is invalid."
        logger.info(message)
        return {
            "status": is_valid,
            "message": message,
            "result": is_valid
        }
    except CSVError as e:
        logger.error(f"CSVError while validating structure: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while validating CSV structure for '{file_name}': {e}")
        return handle_error_response(f"Failed to validate CSV structure: {e}")
