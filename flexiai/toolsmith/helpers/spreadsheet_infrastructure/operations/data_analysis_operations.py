# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/operations/data_analysis_operations.py

"""
data_analysis_operations module.

Provides high‑level functions for generating summaries, validating structure,
and creating pivot tables in spreadsheet workbooks via the SpreadsheetManager.
"""

import logging
from typing import Dict, Any, Optional, List

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def generate_spreadsheet_summary(
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Generate a summary report of a workbook's sheets.

    Args:
        path (str, optional): Directory containing the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': { sheet_name: {'rows': int, 'columns': int}, ... }
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        summary = manager.generate_spreadsheet_summary()
        return {
            "status": True,
            "message": f"Spreadsheet summary generated successfully for '{file_name}'.",
            "result": summary
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in generate_spreadsheet_summary: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in generate_spreadsheet_summary: {e}")
        return handle_error_response(f"Failed to generate summary: {e}")


def retrieve_multiple_sheets_summary(
    files_list: List[Dict[str, str]],
    default_path: str,
    default_file_name: str
) -> Dict[str, Any]:
    """
    Generate summaries for multiple workbooks.

    Args:
        files_list (List[Dict[str, str]]): Each dict with optional 'path' and 'file_name'.
        default_path (str): Fallback directory if 'path' missing.
        default_file_name (str): Fallback file name if 'file_name' missing.

    Returns:
        Dict[str, Any]: {
            file_name: {
                'status': bool,
                'message': str,
                'summary': Optional[Dict[str, Any]]
            }, ...
        }
    """
    summaries: Dict[str, Any] = {}
    for file in files_list:
        path = file.get('path', default_path)
        file_name = file.get('file_name', default_file_name)
        full_path = get_full_path(path, file_name)
        try:
            check_file_exists(path, file_name)
            manager = SpreadsheetManager(file_path=full_path)
            summary = manager.generate_spreadsheet_summary()
            summaries[file_name] = {
                "status": True,
                "message": f"Summary generated successfully for '{file_name}'.",
                "summary": summary
            }
        except SpreadsheetError as e:
            logger.error(f"SpreadsheetError for {file_name}: {e}")
            summaries[file_name] = {
                "status": False,
                "message": str(e),
                "summary": None
            }
        except Exception as e:
            logger.exception(f"Unexpected error for {file_name}: {e}")
            summaries[file_name] = {
                "status": False,
                "message": f"Failed to generate summary for '{file_name}': {e}",
                "summary": None
            }
    logger.info("Retrieved multiple sheets summaries.")
    return summaries


def validate_spreadsheet_structure(
    required_sheets: List[str],
    required_headers: Dict[str, List[str]],
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Validate that a workbook contains specified sheets and headers.

    Args:
        required_sheets (List[str]): Sheet names that must exist.
        required_headers (Dict[str, List[str]]): Map of sheet_name to its header list.
        path (str, optional): Directory of the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': bool
            }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        valid = manager.validate_spreadsheet_structure(
            required_sheets=required_sheets,
            required_headers=required_headers
        )
        message = "Spreadsheet structure is valid." if valid else "Spreadsheet structure is invalid."
        return {
            "status": valid,
            "message": message,
            "result": valid
        }
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in validate_spreadsheet_structure: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError in validate_spreadsheet_structure: Missing {e}")
        return handle_error_response(f"Missing required parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error in validate_spreadsheet_structure: {e}")
        return handle_error_response(f"Failed to validate spreadsheet structure: {e}")


def create_pivot_table(
    sheet_name: str,
    pivot_table_config: Dict[str, Any],
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Create and insert a pivot table based on configuration.

    Args:
        sheet_name (str): Sheet to source and place pivot table.
        pivot_table_config (Dict[str, Any]): {
            'source_data': str,
            'destination': str,
            'rows': Optional[List[str]],
            'columns': Optional[List[str]],
            'values': Optional[List[Dict[str,str]]],
            'filters': Optional[List[str]],
            'page_fields': Optional[List[str]],
            'report_name': Optional[str]
        }
        path (str, optional): Directory of the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]:
            {
                'status': bool,
                'message': str,
                'result': Optional[Dict[str,str]]
            }
    """
    # ensure minimum config
    for required in ("source_data", "destination"):
        if required not in pivot_table_config:
            return handle_error_response(f"'{required}' is required in pivot_table_config.")

    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)

        resp = manager.create_pivot_table(
            sheet_name=sheet_name,
            source_data=pivot_table_config["source_data"],
            destination=pivot_table_config["destination"],
            rows=pivot_table_config.get("rows"),
            columns=pivot_table_config.get("columns"),
            values=pivot_table_config.get("values"),
            filters=pivot_table_config.get("filters"),
            page_fields=pivot_table_config.get("page_fields"),
            report_name=pivot_table_config.get("report_name")
        )

        if resp.get("status"):
            return {
                "status": True,
                "message": f"Pivot table '{resp.get('report_name')}' created at '{resp.get('pivot_table_location')}'.",
                "result": {
                    "pivot_table_location": resp.get("pivot_table_location"),
                    "report_name": resp.get("report_name"),
                    "sheet_name": resp.get("sheet_name")
                }
            }
        else:
            return handle_error_response("Pivot table creation failed.")
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError in create_pivot_table: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error in create_pivot_table: {e}")
        return handle_error_response(f"Failed to create pivot table: {e}")
