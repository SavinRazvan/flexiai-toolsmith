# FILE: flexiai/toolsmith/tools_infrastructure/csv_infrastructure/operations/data_transformation_operations.py

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.managers.csv_manager import CSVManager
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.exceptions.csv_exceptions import CSVError
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.file_handler import (
    check_file_exists,
    get_full_path,
)
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.error_handler import handle_error_response

logger = logging.getLogger(__name__)


def transpose_csv(
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = "",
    dest_file_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reads a CSV, transposes its contents (rows become columns and vice versa),
    and writes the result to a new CSV.

    Args:
        path (str, optional): Directory path where the source CSV resides.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the source CSV file (including '.csv').
        dest_file_name (str, optional): Name of the destination CSV file.
            If not provided, will prepend 'transposed_' to the source file name.

    Returns:
        Dict[str, Any]: Standardized response dict with:
            - status (bool)
            - message (str)
            - result (dict): {
                  "source": full source path,
                  "destination": full destination path,
                  "shape": [rows, columns] of the transposed DataFrame
              }
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)

    if dest_file_name is None:
        dest_file_name = f"transposed_{file_name}"

    src_path = get_full_path(path, file_name)
    dst_path = get_full_path(path, dest_file_name)

    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=src_path)
        df = manager.df.copy()
        transposed = df.transpose()

        # After transpose, the old index becomes columns; reset index to have a header row
        transposed.reset_index(inplace=True)
        transposed.to_csv(dst_path, index=False)

        rows, cols = transposed.shape
        message = f"CSV '{file_name}' transposed successfully to '{dest_file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "source": src_path,
                "destination": dst_path,
                "shape": [rows, cols]
            }
        }
    except CSVError as e:
        logger.error(f"CSVError while transposing CSV: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while transposing CSV '{file_name}': {e}")
        return handle_error_response(f"Failed to transpose CSV '{file_name}': {e}")


def unpivot_csv(
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = "",
    id_vars: List[str] = None,
    var_name: str = "variable",
    value_name: str = "value",
    dest_file_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reads a wide-format CSV and unpivots it (converts to long format) using pandas.melt,
    then writes the result to a new CSV.

    Args:
        path (str, optional): Directory path where the source CSV resides.
            Defaults to 'flexiai/toolsmith/data/csv'.
        file_name (str): Name of the source CSV file (including '.csv').
        id_vars (List[str]): Column(s) to keep as identifier variables.
        var_name (str, optional): Name for the 'variable' column in the melted output.
            Defaults to 'variable'.
        value_name (str, optional): Name for the 'value' column in the melted output.
            Defaults to 'value'.
        dest_file_name (str, optional): Name of the destination CSV file.
            If not provided, will prepend 'unpivoted_' to the source file name.

    Returns:
        Dict[str, Any]: Standardized response dict with:
            - status (bool)
            - message (str)
            - result (dict): {
                  "source": full source path,
                  "destination": full destination path,
                  "rows": number of rows in the unpivoted DataFrame
              }
    """
    if not file_name:
        msg = "Parameter 'file_name' is required."
        logger.error(msg)
        return handle_error_response(msg)
    if not id_vars:
        msg = "Parameter 'id_vars' is required and must be a list of column names."
        logger.error(msg)
        return handle_error_response(msg)

    if dest_file_name is None:
        dest_file_name = f"unpivoted_{file_name}"

    src_path = get_full_path(path, file_name)
    dst_path = get_full_path(path, dest_file_name)

    try:
        check_file_exists(path, file_name)
        manager = CSVManager(file_path=src_path)
        df = manager.df.copy()

        # Perform unpivot (melt)
        melted = pd.melt(df, id_vars=id_vars, var_name=var_name, value_name=value_name)

        melted.to_csv(dst_path, index=False)
        row_count = len(melted)

        message = f"CSV '{file_name}' unpivoted successfully to '{dest_file_name}'."
        logger.info(message)
        return {
            "status": True,
            "message": message,
            "result": {
                "source": src_path,
                "destination": dst_path,
                "rows": row_count
            }
        }
    except CSVError as e:
        logger.error(f"CSVError while unpivoting CSV: {e}")
        return handle_error_response(str(e))
    except Exception as e:
        logger.exception(f"Unexpected error while unpivoting CSV '{file_name}': {e}")
        return handle_error_response(f"Failed to unpivot CSV '{file_name}': {e}")
