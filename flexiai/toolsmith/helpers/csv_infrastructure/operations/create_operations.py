# FILE: flexiai/toolsmith/helpers/csv_infrastructure/operations/create_operations.py

import os
import logging
from typing import Any, Dict, List, Optional

from flexiai.toolsmith.helpers.csv_infrastructure.managers.csv_manager import CSVManager
from flexiai.toolsmith.helpers.csv_infrastructure.exceptions.csv_exceptions import CSVError
from flexiai.toolsmith.helpers.csv_infrastructure.utils.file_handler import get_full_path
from flexiai.toolsmith.helpers.csv_infrastructure.utils.error_handler import handle_error_response

logger = logging.getLogger(__name__)


def create_csv(
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = "",
    headers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Creates a new CSV file with optional headers.

    Args:
        path (str, optional): Directory path to save the CSV. Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file to create (including '.csv').
        headers (List[str], optional): List of column names for the new CSV. Defaults to None.

    Returns:
        Dict[str, Any]: Standardized response dict with:
            - status (bool): True on success, False on error.
            - message (str): Success or error message.
            - result (dict): {
                  "file_path": full path of the created CSV,
                  "headers": the headers written (or None)
              } on success, or None on failure.
    """
    if not file_name:
        error_msg = "Parameter 'file_name' is required."
        logger.error(error_msg)
        return handle_error_response(error_msg)

    full_path = get_full_path(path, file_name)
    try:
        # Ensure the directory exists
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created directory '{path}' as it did not exist.")

        # Initialize manager without loading an existing CSV
        manager = CSVManager(file_path=full_path, load_csv=False)
        manager.create_csv(headers=headers)

        message = f"CSV file '{file_name}' created successfully at '{path}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "file_path": full_path,
                "headers": headers
            }
        }
    except CSVError as e:
        logger.error(f"CSVError while creating CSV: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while creating CSV '{file_name}': {e}")
        return handle_error_response(f"Failed to create CSV '{file_name}': {str(e)}")
