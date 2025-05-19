# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/operations/chart_operations.py

"""
chart_operations module.

Provides high‑level functions for creating, updating, and removing charts
in spreadsheet workbooks via the SpreadsheetManager.
"""

import logging
from typing import Dict, Any, Optional, List

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.managers.spreadsheet_manager import SpreadsheetManager
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import check_file_exists, get_full_path
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.exceptions.spreadsheet_exceptions import SpreadsheetError

logger = logging.getLogger(__name__)


def create_chart(
    sheet_name: str,
    chart_type: str,
    data_range: str,
    categories_range: Optional[str] = None,
    destination_cell: str = "A10",
    title: Optional[str] = None,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    legend_position: str = "r",
    style: int = 2,
    show_data_labels: bool = False,
    overlap: Optional[int] = None,
    grouping: Optional[str] = None,
    series_names: Optional[List[str]] = None,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Create a chart in the specified sheet of a workbook.

    Args:
        sheet_name (str): Name of the sheet to place the chart.
        chart_type (str): One of 'bar', 'line', 'pie', 'scatter', 'area', 'bubble'.
        data_range (str): Cell range for the chart data (e.g. 'B2:D10').
        categories_range (str, optional): Range for category labels (e.g. 'A2:A10').
        destination_cell (str, optional): Top-left cell for the chart (default 'A10').
        title (str, optional): Chart title.
        x_title (str, optional): X-axis title.
        y_title (str, optional): Y-axis title.
        legend_position (str, optional): Legend position (e.g. 'r', 'b').
        style (int, optional): Openpyxl chart style index.
        show_data_labels (bool, optional): Whether to show data labels.
        overlap (int, optional): Overlap for bar/column charts.
        grouping (str, optional): Grouping for bar/column charts.
        series_names (List[str], optional): Series titles.
        path (str, optional): Directory of the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]: {
            'status': bool,
            'message': str,
            'pivot_table_location'/'result': Optional[dict]
        }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        result = manager.create_chart(
            sheet_name=sheet_name,
            chart_type=chart_type,
            data_range=data_range,
            categories_range=categories_range,
            destination_cell=destination_cell,
            title=title,
            x_title=x_title,
            y_title=y_title,
            legend_position=legend_position,
            style=style,
            show_data_labels=show_data_labels,
            overlap=overlap,
            grouping=grouping,
            series_names=series_names
        )
        logger.info(result.get("message"))
        return result
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while creating chart: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while creating chart: {e}")
        return handle_error_response(f"Missing parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while creating chart: {e}")
        return handle_error_response(f"Failed to create chart: {e}")


def update_chart(
    sheet_name: str,
    chart_title: str,
    new_data_range: Optional[str] = None,
    new_categories_range: Optional[str] = None,
    new_title: Optional[str] = None,
    new_x_title: Optional[str] = None,
    new_y_title: Optional[str] = None,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Update an existing chart in the workbook.

    Args:
        sheet_name (str): Sheet containing the chart.
        chart_title (str): Current title of the chart to update.
        new_data_range (str, optional): New data range (e.g. 'B2:D10').
        new_categories_range (str, optional): New categories range.
        new_title (str, optional): New chart title.
        new_x_title (str, optional): New X-axis title.
        new_y_title (str, optional): New Y-axis title.
        path (str, optional): Directory of the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]: {
            'status': bool,
            'message': str,
            'result': Optional[dict]
        }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        result = manager.update_chart(
            sheet_name=sheet_name,
            chart_title=chart_title,
            new_data_range=new_data_range,
            new_categories_range=new_categories_range,
            new_title=new_title,
            new_x_title=new_x_title,
            new_y_title=new_y_title
        )
        logger.info(result.get("message"))
        return result
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while updating chart: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while updating chart: {e}")
        return handle_error_response(f"Missing parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while updating chart: {e}")
        return handle_error_response(f"Failed to update chart '{chart_title}': {e}")


def remove_chart(
    sheet_name: str,
    chart_title: str,
    path: str = "flexiai/toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Remove a chart from the workbook.

    Args:
        sheet_name (str): Sheet containing the chart.
        chart_title (str): Title of the chart to remove.
        path (str, optional): Directory of the workbook.
        file_name (str, optional): Workbook file name.

    Returns:
        Dict[str, Any]: {
            'status': bool,
            'message': str,
            'result': Optional[dict]
        }
    """
    full_path = get_full_path(path, file_name)
    try:
        check_file_exists(path, file_name)
        manager = SpreadsheetManager(file_path=full_path)
        result = manager.remove_chart(sheet_name=sheet_name, chart_title=chart_title)
        logger.info(result.get("message"))
        return result
    except SpreadsheetError as e:
        logger.error(f"SpreadsheetError while removing chart: {e}")
        return handle_error_response(str(e))
    except KeyError as e:
        logger.error(f"KeyError while removing chart: {e}")
        return handle_error_response(f"Missing parameter: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while removing chart: {e}")
        return handle_error_response(f"Failed to remove chart '{chart_title}': {e}")
