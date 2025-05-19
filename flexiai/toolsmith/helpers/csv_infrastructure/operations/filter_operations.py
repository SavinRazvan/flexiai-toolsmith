# FILE: flexiai/toolsmith/helpers/csv_infrastructure/operations/filter_operations.py

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


def filter_rows(
    column: Union[str, int],
    condition_type: str,
    condition_value: Any,
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = ""
) -> Dict[str, Any]:
    """
    Filters rows in a CSV file based on a condition on one column.

    Args:
        column (Union[str, int]): Column name or zero-based index.
        condition_type (str): Condition to apply 
                              ('equals','greater_than','less_than',
                               'contains','startswith','endswith').
        condition_value (Any): Value to compare against.
        path (str, optional): Directory path to the CSV. Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the CSV file (including '.csv').

    Returns:
        Dict[str, Any]: Standardized response with:
            - status (bool)
            - message (str)
            - result: {"filtered_rows": List[Dict[str, Any]]}
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=full_path)
        filtered: List[Dict[str, Any]] = manager.filter_rows(
            column, condition_type, condition_value
        )
        message = (
            f"Filtered rows in '{file_name}' where column '{column}' "
            f"{condition_type} '{condition_value}' – {len(filtered)} matches found."
        )
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {"filtered_rows": filtered}
        }
    except CSVError as e:
        logger.error(f"CSVError while filtering rows: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while filtering rows in '{file_name}': {e}")
        return handle_error_response(f"Failed to filter rows in '{file_name}': {e}")
