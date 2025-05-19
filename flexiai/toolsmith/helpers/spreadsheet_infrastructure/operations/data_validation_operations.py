# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/operations/data_validation_operations.py

"""
data_validation_operations module.

Provides high‑level functions for applying and removing data validation rules
in spreadsheet workbooks via the SpreadsheetManager.
"""

import logging
from typing import Dict, Any, Optional

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def set_data_validation(
    sheet_name: str,
    validation_rules: Dict[str, Any],
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Apply data validation rules to a sheet.

    Args:
        sheet_name (str): Name of the target sheet.
        validation_rules (Dict[str, Any]): Dictionary of validation parameters.
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Workbook file name.
            Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]:
            {
                "status": bool,
                "message": str,
                "result": {
                    "sheet_name": str,
                    "validation_rules": Dict[str, Any]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.set_data_validation(sheet_name, validation_rules)
        message = f"Data validation set successfully for sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "sheet_name": sheet_name,
                "validation_rules": validation_rules
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in set_data_validation: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in set_data_validation: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in set_data_validation: {e}")
        return handle_error_response(f"Failed to set data validation: {e}")


def remove_data_validation(
    sheet_name: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    range_to_remove: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove data validation rules from a sheet or a specific range.

    Args:
        sheet_name (str): Name of the target sheet.
        path (str, optional): Directory path to the workbook.
            Defaults to 'flexiai/toolsmith/data/spreadsheets'.
        file_name (str, optional): Workbook file name.
            Defaults to 'example_spreadsheet.xlsx'.
        range_to_remove (str, optional): Specific cell range to clear validations from.
            If None, all validations in the sheet are removed.

    Returns:
        Dict[str, Any]:
            {
                "status": bool,
                "message": str,
                "result": {
                    "sheet_name": str,
                    "range_to_remove": Optional[str]
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.remove_data_validation(sheet_name, range_to_remove)

        if range_to_remove:
            message = f"Data validation removed from range '{range_to_remove}' in sheet '{sheet_name}'."
            result = {"sheet_name": sheet_name, "range_to_remove": range_to_remove}
        else:
            message = f"All data validations removed from sheet '{sheet_name}'."
            result = {"sheet_name": sheet_name, "range_to_remove": None}

        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": result
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in remove_data_validation: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in remove_data_validation: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in remove_data_validation: {e}")
        return handle_error_response(f"Failed to remove data validation: {e}")
