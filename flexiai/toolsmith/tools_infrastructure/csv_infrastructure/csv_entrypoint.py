# FILE: flexiai/toolsmith/tools_infrastructure/csv_infrastructure/csv_entrypoint.py

import logging
from typing import Any, Dict, List, Optional, Union

from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.file_handler import check_file_exists
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.exceptions.csv_exceptions import CSVError

from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.operations.create_operations import create_csv
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.operations.delete_operations import delete_csv, delete_row
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.operations.read_operations import (
    read_csv, read_row, read_column, generate_csv_summary,
)
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.operations.update_operations import (
    append_row, append_rows, update_cell,
)
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.operations.filter_operations import filter_rows
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.operations.data_validation_operations import (
    validate_csv_structure,
)

logger = logging.getLogger(__name__)


def csv_entrypoint(
    operation: str,
    path: str = "flexiai/toolsmith/data/csv",
    file_name: str = "",
    index: Optional[int] = None,
    column: Optional[Union[str, int]] = None,
    row: Optional[Dict[str, Any]] = None,
    rows: Optional[List[Dict[str, Any]]] = None,
    value: Optional[Any] = None,
    condition_type: Optional[str] = None,
    condition_value: Optional[Any] = None,
    headers: Optional[List[str]] = None,
    required_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Entrypoint for CSV operations.
    Supported operations:
      - create, delete, read, read_row, read_column, summary,
        append_row, append_rows, update_cell, delete_row,
        filter_rows, validate
    """
    try:
        # For anything except creation, file_name must be provided and exist
        if operation != "create":
            if not file_name:
                raise CSVError("Parameter 'file_name' is required.")
            check_file_exists(path, file_name)

        # 1. CREATE
        if operation == "create":
            if not file_name:
                raise CSVError("Parameter 'file_name' is required for 'create'.")
            return create_csv(path=path, file_name=file_name, headers=headers)

        # 2. DELETE WHOLE FILE
        if operation == "delete":
            return delete_csv(path=path, file_name=file_name)

        # 3. READ ALL ROWS
        if operation == "read":
            return read_csv(path=path, file_name=file_name)

        # 4. READ SINGLE ROW
        if operation == "read_row":
            if index is None:
                raise CSVError("Parameter 'index' is required for 'read_row'.")
            return read_row(index=index, path=path, file_name=file_name)

        # 5. READ A COLUMN
        if operation == "read_column":
            if column is None:
                raise CSVError("Parameter 'column' is required for 'read_column'.")
            return read_column(column=column, path=path, file_name=file_name)

        # 6. SUMMARY
        if operation == "summary":
            return generate_csv_summary(path=path, file_name=file_name)

        # 7. APPEND ONE ROW
        if operation == "append_row":
            if row is None:
                raise CSVError("Parameter 'row' is required for 'append_row'.")
            return append_row(row=row, path=path, file_name=file_name)

        # 8. APPEND MULTIPLE ROWS
        if operation == "append_rows":
            if rows is None:
                raise CSVError("Parameter 'rows' is required for 'append_rows'.")
            return append_rows(rows=rows, path=path, file_name=file_name)

        # 9. UPDATE ONE CELL
        if operation == "update_cell":
            if index is None or column is None or value is None:
                raise CSVError("Parameters 'index', 'column', and 'value' are required for 'update_cell'.")
            return update_cell(
                row_index=index,
                column=column,
                value=value,
                path=path,
                file_name=file_name
            )

        # 10. DELETE A ROW
        if operation == "delete_row":
            if index is None:
                raise CSVError("Parameter 'index' is required for 'delete_row'.")
            return delete_row(row_index=index, path=path, file_name=file_name)

        # 11. FILTER ROWS
        if operation == "filter_rows":
            if column is None or condition_type is None or condition_value is None:
                raise CSVError(
                    "Parameters 'column', 'condition_type', and 'condition_value' are required for 'filter_rows'."
                )
            return filter_rows(
                column=column,
                condition_type=condition_type,
                condition_value=condition_value,
                path=path,
                file_name=file_name
            )

        # 12. VALIDATE STRUCTURE
        if operation == "validate":
            if required_columns is None:
                raise CSVError("Parameter 'required_columns' is required for 'validate'.")
            return validate_csv_structure(
                required_columns=required_columns,
                path=path,
                file_name=file_name
            )

        # UNKNOWN OPERATION
        raise CSVError(f"Unsupported CSV operation: '{operation}'")

    except CSVError as e:
        logger.error(f"[csv_entrypoint][{operation}] {e}")
        return handle_error_response(str(e))

    except Exception as e:
        logger.exception(f"[csv_entrypoint][{operation}] unexpected")
        return handle_error_response(f"Unexpected error in '{operation}': {e}")
