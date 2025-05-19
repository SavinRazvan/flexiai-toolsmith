# FILE: flexiai/toolsmith/tools_infrastructure/spreadsheet_infrastructure/operations/data_transformation_operations.py

"""
data_transformation_operations module.

Provides high‑level functions for transposing and unpivoting data
in spreadsheet workbooks via the SpreadsheetManager.
"""

import logging
from typing import Dict, Any

from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.tools_infrastructure.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def transpose_data(
    source_range: str,
    destination_range: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Transpose a block of cells from rows to columns (or vice versa).

    Args:
        source_range (str): Range to transpose (e.g. 'Sheet1!A1:C3').
        destination_range (str): Top-left cell for transposed data (e.g. 'Sheet2!A1').
        path (str, optional): Directory containing the workbook. Defaults to standard path.
        file_name (str, optional): Workbook file name. Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]:
            {
                "status": bool,
                "message": str,
                "result": {
                    "source_range": str,
                    "destination_range": str
                }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        manager.transpose_data(source_range, destination_range)
        message = f"Data transposed from '{source_range}' to '{destination_range}' successfully."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "source_range": source_range,
                "destination_range": destination_range
            }
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in transpose_data: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in transpose_data: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in transpose_data: {e}")
        return handle_error_response(f"Failed to transpose data: {e}")


def unpivot_data(
    sheet_name: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Convert a wide-format sheet into a long-format list of records.

    Args:
        sheet_name (str): Name of the sheet to unpivot.
        path (str, optional): Directory containing the workbook. Defaults to standard path.
        file_name (str, optional): Workbook file name. Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]:
            {
                "status": bool,
                "message": str,
                "result": List[Dict[str, Any]]
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        long_format = manager.unpivot_data(sheet_name)
        message = f"Data unpivoted successfully in sheet '{sheet_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": long_format
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in unpivot_data: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in unpivot_data: missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in unpivot_data: {e}")
        return handle_error_response(f"Failed to unpivot data: {e}")
