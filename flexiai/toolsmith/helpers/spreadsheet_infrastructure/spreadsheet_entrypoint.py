# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/spreadsheet_entrypoint.py

import logging
from typing import Dict, Any, List, Optional

from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.error_handler import handle_error_response
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.utils.file_handler import check_file_exists

# ------------------------------------------------------------------------------
# Import the actual implementations from the 'operations' folder.
# ------------------------------------------------------------------------------

# 1) FileManagement operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.file_operations import (
    create_workbook,
    delete_workbook
)

# 2) SheetManagement operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.sheet_operations import (
    create_sheet,
    rename_sheet,
    delete_sheet
)

# 3) DataEntry operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.data_entry_operations import (
    add_row,
    add_rows,
    write_headers,
    delete_row,
    update_column
)

# 4) DataRetrieval operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.data_retrieval_operations import (
    retrieve_cell,
    retrieve_row,
    retrieve_column,
    filter_rows,
    retrieve_rows
)

# 5) DataAnalysis operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.data_analysis_operations import (
    generate_spreadsheet_summary,
    validate_spreadsheet_structure,
    create_pivot_table,
    retrieve_multiple_sheets_summary
)

# 6) FormulaOperations operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.formula_operations import (
    insert_formula,
    apply_formula_to_column,
    evaluate_formula,
    remove_formula,
    define_named_range
)

# 7) Formatting operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.formatting_operations import (
    set_cell_format,
    apply_conditional_formatting
)

# 8) DataValidation operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.data_validation_operations import (
    set_data_validation,
    remove_data_validation
)

# 9) DataTransformation operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.data_transformation_operations import (
    transpose_data,
    unpivot_data
)

# 10. Chart and Graphics operations
from flexiai.toolsmith.helpers.spreadsheet_infrastructure.operations.chart_operations import (
    create_chart,
    update_chart,
    remove_chart
)


logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# 1. FileManagement dispatcher (file_operations)
# ------------------------------------------------------------------------------
def file_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx"
) -> Dict[str, Any]:
    """
    Performs file-level workbook operations such as creating or deleting .xlsx files.

    Args:
        operation (str): The file-level operation to perform ("create_workbook" or "delete_workbook").
        path (str, optional): Directory to save or find the workbook. Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file. Defaults to 'example_spreadsheet.xlsx'.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "create_workbook":
        return create_workbook(path=path, file_name=file_name)
    elif operation == "delete_workbook":
        return delete_workbook(path=path, file_name=file_name)
    else:
        message = f"Unsupported file operation: {operation}"
        logger.warning(message)
        return {
            "status": False,
            "message": message,
            "result": None
        }


# ------------------------------------------------------------------------------
# 2. SheetManagement dispatcher (sheet_operations)
# ------------------------------------------------------------------------------
def sheet_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    new_sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manages sheet-level operations such as creating, renaming, or deleting sheets in a .xlsx file.

    Args:
        operation (str): The sheet-level operation to perform ("create_sheet", "rename_sheet", "delete_sheet").
        path (str, optional): Directory where the workbook resides. Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file. Defaults to 'example_spreadsheet.xlsx'.
        sheet_name (str, optional): Current or target sheet name (required for create, rename, delete).
        new_sheet_name (str, optional): New name for the sheet (required for rename_sheet).

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "create_sheet":
        if not sheet_name:
            return handle_error_response("Parameter 'sheet_name' is required for 'create_sheet' operation.")
        return create_sheet(sheet_name=sheet_name, path=path, file_name=file_name)
    elif operation == "rename_sheet":
        if not sheet_name or not new_sheet_name:
            return handle_error_response("Parameters 'sheet_name' and 'new_sheet_name' are required for 'rename_sheet' operation.")
        return rename_sheet(sheet_name=sheet_name, new_sheet_name=new_sheet_name, path=path, file_name=file_name)
    elif operation == "delete_sheet":
        if not sheet_name:
            return handle_error_response("Parameter 'sheet_name' is required for 'delete_sheet' operation.")
        return delete_sheet(sheet_name=sheet_name, path=path, file_name=file_name)
    else:
        return {
            "status": False,
            "message": f"Unsupported sheet operation: {operation}",
            "result": None
        }


# ------------------------------------------------------------------------------
# 3. DataEntry dispatcher (data_entry_operations)
# ------------------------------------------------------------------------------
def data_entry_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    data: Optional[List[str]] = None,
    rows: Optional[List[List[str]]] = None,
    headers: Optional[List[str]] = None,
    row_id: Optional[str] = None,
    column_name: Optional[str] = None,  # We keep it for backward compatibility
    new_data: Optional[List[str]] = None,
    skip_header: bool = True,
    has_headers: bool = True  # <-- (Optional) new param if you want to expose it
) -> Dict[str, Any]:
    """
    Handles data-entry operations such as adding rows, writing headers,
    deleting rows, and updating columns.

    Args:
        operation (str): e.g. "add_row", "add_rows", "write_headers", "delete_row", "update_column".
        path (str): Directory path.
        file_name (str): Name of the workbook file.
        sheet_name (str): Target sheet for the operation.
        data (List[str]): Row data for add_row.
        rows (List[List[str]]): Multiple rows for add_rows.
        headers (List[str]): Headers for write_headers.
        row_id (str): Row identifier for delete_row.
        column_name (str): Column to update for update_column (could be letter/index/header).
        new_data (List[str]): New values for update_column.
        skip_header (bool): Whether to skip the header row (for update_column).
        has_headers (bool): If True, we can interpret column_name as a header.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "add_row":
        if not sheet_name or not data:
            return handle_error_response("Parameters 'sheet_name' and 'data' are required for 'add_row' operation.")
        return add_row(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            data=data
        )

    elif operation == "add_rows":
        if not sheet_name or not rows:
            return handle_error_response("Parameters 'sheet_name' and 'rows' are required for 'add_rows' operation.")
        return add_rows(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            rows=rows
        )

    elif operation == "write_headers":
        if not sheet_name or not headers:
            return handle_error_response("Parameters 'sheet_name' and 'headers' are required for 'write_headers' operation.")
        return write_headers(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            headers=headers
        )

    elif operation == "delete_row":
        if not sheet_name or not row_id:
            return handle_error_response("Parameters 'sheet_name' and 'row_id' are required for 'delete_row' operation.")
        return delete_row(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            row_id=row_id
        )

    elif operation == "update_column":
        if not sheet_name or not column_name or not new_data:
            return handle_error_response("Parameters 'sheet_name', 'column_name', and 'new_data' are required for 'update_column' operation.")
        
        # We pass column_name to 'column_identifier' so that the new manager method 
        # can interpret it as letter, 1-based index, or a header if has_headers=True.
        return update_column(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            # The new manager supports "column_identifier" - we reuse 'column_name':
            column_identifier=column_name,  
            new_data=new_data,
            skip_header=skip_header,
            has_headers=has_headers
        )

    else:
        return {
            "status": False,
            "message": f"Unsupported data entry operation: {operation}",
            "result": None
        }


# ------------------------------------------------------------------------------
# 4. DataRetrieval dispatcher (data_retrieval_operations)
# ------------------------------------------------------------------------------
def data_retrieval_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    cell: Optional[str] = None,
    row_id: Optional[str] = None,
    column_name: Optional[str] = None,  # or 'column_identifier'
    condition_type: Optional[str] = None,
    condition_value: Optional[str] = None,
    start_row: int = 1,
    max_rows: int = 20,
    include_headers: bool = False,   # Original param (some folks prefer 'skip_header')
    skip_header: bool = True,        # Possibly we want both? Or unify them.
    has_headers: bool = True         # <-- new param if you want to interpret column_name as a header
) -> Dict[str, Any]:
    """
    Performs data-retrieval operations such as retrieving cells, rows, columns,
    filtering, and paginated retrieval.
    """
    if operation == "retrieve_cell":
        if not sheet_name or not cell:
            return handle_error_response("Parameters 'sheet_name' and 'cell' are required for 'retrieve_cell' operation.")
        return retrieve_cell(
            sheet_name=sheet_name,
            cell=cell,
            path=path,
            file_name=file_name
        )

    elif operation == "retrieve_row":
        if not sheet_name or not row_id:
            return handle_error_response("Parameters 'sheet_name' and 'row_id' are required for 'retrieve_row' operation.")
        # If row_id is provided as a string, you might convert to int if needed:
        row_num = int(row_id)
        return retrieve_row(
            sheet_name=sheet_name,
            row_id=row_num,
            skip_header=skip_header,
            path=path,
            file_name=file_name
        )

    elif operation == "retrieve_column":
        if not sheet_name or not column_name:
            return handle_error_response("Parameters 'sheet_name' and 'column_name' are required for 'retrieve_column' operation.")
        # Here we pass column_name to the new `column_identifier` param
        return retrieve_column(
            sheet_name=sheet_name,
            column_identifier=column_name,
            skip_header=False,   # or skip_header if you want to allow skipping first row
            has_headers=has_headers,
            path=path,
            file_name=file_name
        )

    elif operation == "filter_rows":
        if not sheet_name or not column_name or not condition_type or not condition_value:
            return handle_error_response(
                "Parameters 'sheet_name', 'column_name', 'condition_type', and 'condition_value' are required for 'filter_rows' operation."
            )
        return filter_rows(
            sheet_name=sheet_name,
            column_identifier=column_name,  # We rename for manager
            condition_type=condition_type,
            condition_value=condition_value,
            skip_header=skip_header,        # Could be True or False
            has_headers=has_headers,        # If you want to interpret col as a header name
            path=path,
            file_name=file_name
        )

    elif operation == "retrieve_rows":
        if not sheet_name:
            return handle_error_response("Parameter 'sheet_name' is required for 'retrieve_rows' operation.")
        # We might unify 'include_headers' & 'skip_header' into a single policy. 
        # For now, we show how you can pass them as needed:
        return retrieve_rows(
            sheet_name=sheet_name,
            start_row=start_row,
            max_rows=max_rows,
            # For example, some people prefer skip_header = not include_headers
            # or we pass them both. We'll assume retrieve_rows manager uses skip_header:
            skip_header=not include_headers,  
            path=path,
            file_name=file_name
        )
    else:
        message = f"Unsupported data retrieval operation: {operation}"
        logger.warning(message)
        return {
            "status": False,
            "message": message,
            "result": None
        }


# ------------------------------------------------------------------------------
# 5. DataAnalysis dispatcher (data_analysis_operations)
# ------------------------------------------------------------------------------
def data_analysis_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    required_sheets: Optional[List[str]] = None,
    required_headers: Optional[Dict[str, List[str]]] = None,
    sheet_name: Optional[str] = None,
    pivot_table_config: Optional[Dict[str, Any]] = None,
    files_list: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Performs data-analysis operations such as generating spreadsheet summaries,
    validating structure, creating pivot tables, or retrieving multiple sheets summaries.

    Args:
        operation (str): The data-analysis operation to perform ("generate_spreadsheet_summary", "validate_spreadsheet_structure", "create_pivot_table", "retrieve_multiple_sheets_summary").
        path (str, optional): Default directory path to the workbook. Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Default name of the workbook file. Defaults to 'example_spreadsheet.xlsx'.
        required_sheets (List[str], optional): Expected sheet names for `validate_spreadsheet_structure`.
        required_headers (Dict[str, List[str]], optional): Expected headers per sheet for `validate_spreadsheet_structure`.
        sheet_name (str, optional): Target sheet for `create_pivot_table`.
        pivot_table_config (Dict[str, Any], optional): Configuration details for `create_pivot_table`.
        files_list (List[Dict[str, str]], optional): List of file references for `retrieve_multiple_sheets_summary`. Each dict can contain 'path' and 'file_name'.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "generate_spreadsheet_summary":
        return generate_spreadsheet_summary(
            path=path,
            file_name=file_name
        )
    elif operation == "validate_spreadsheet_structure":
        if not required_sheets or not required_headers:
            return handle_error_response("Parameters 'required_sheets' and 'required_headers' are required for 'validate_spreadsheet_structure' operation.")
        return validate_spreadsheet_structure(
            required_sheets=required_sheets,
            required_headers=required_headers,
            path=path,
            file_name=file_name
        )
    elif operation == "create_pivot_table":
        if not sheet_name or not pivot_table_config:
            return handle_error_response("Parameters 'sheet_name' and 'pivot_table_config' are required for 'create_pivot_table' operation.")
        return create_pivot_table(
            sheet_name=sheet_name,
            pivot_table_config=pivot_table_config,
            path=path,
            file_name=file_name
        )
    elif operation == "retrieve_multiple_sheets_summary":
        if not files_list:
            return handle_error_response("Parameter 'files_list' is required for 'retrieve_multiple_sheets_summary' operation.")
        # Here, 'path' and 'file_name' serve as defaults for entries missing them in 'files_list'
        return retrieve_multiple_sheets_summary(
            files_list=files_list,
            default_path=path,
            default_file_name=file_name
        )
    else:
        return handle_error_response(f"Unsupported data analysis operation: {operation}")


# ------------------------------------------------------------------------------
# 6. FormulaOperations dispatcher (formula_operations)
# ------------------------------------------------------------------------------
def formula_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    cell: Optional[str] = None,
    formula: Optional[str] = None,
    column_name: Optional[str] = None,
    formula_template: Optional[str] = None,
    start_row: int = 1,
    range_name: Optional[str] = None,
    cell_range: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handles formula-related operations such as inserting formulas, applying
    formulas to columns, evaluating formulas in cells, removing formulas, 
    and defining named ranges.

    Args:
        operation (str): The formula operation to perform 
                         ("insert_formula", "apply_formula_to_column", 
                          "evaluate_formula", "remove_formula", "define_named_range").
        path (str, optional): Directory path to the workbook. 
                              Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file. 
                                   Defaults to 'example_spreadsheet.xlsx'.
        sheet_name (str, optional): Target sheet name.
        cell (str, optional): Cell reference (required for 
                               'insert_formula', 'evaluate_formula', 'remove_formula').
        formula (str, optional): Formula to insert into a cell 
                                  (for 'insert_formula').
        column_name (str, optional): Target column for 
                                     'apply_formula_to_column'.
        formula_template (str, optional): Template formula for 
                                          'apply_formula_to_column' 
                                          (e.g., '=A{row}+B{row}').
        start_row (int, optional): Starting row for 
                                   'apply_formula_to_column'. 
                                   Defaults to 1.
        range_name (str, optional): Name of the range to define 
                                    (for 'define_named_range').
        cell_range (str, optional): Cell range for the named range 
                                    (e.g., 'A1:B10') 
                                    (for 'define_named_range').

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "insert_formula":
        if not sheet_name or not cell or not formula:
            return handle_error_response(
                "Parameters 'sheet_name', 'cell', and 'formula' are required for 'insert_formula' operation."
            )
        return insert_formula(
            sheet_name=sheet_name,
            cell=cell,
            formula=formula,
            path=path,
            file_name=file_name
        )
    
    elif operation == "apply_formula_to_column":
        if not sheet_name or not column_name or not formula_template:
            return handle_error_response(
                "Parameters 'sheet_name', 'column_name', and 'formula_template' are required for 'apply_formula_to_column' operation."
            )
        return apply_formula_to_column(
            sheet_name=sheet_name,
            column_name=column_name,
            formula_template=formula_template,
            path=path,
            file_name=file_name,
            start_row=start_row
        )
    
    elif operation == "evaluate_formula":
        if not sheet_name or not cell:
            return handle_error_response(
                "Parameters 'sheet_name' and 'cell' are required for 'evaluate_formula' operation."
            )
        return evaluate_formula(
            sheet_name=sheet_name,
            cell=cell,
            path=path,
            file_name=file_name
        )
    
    elif operation == "remove_formula":
        if not sheet_name or not cell:
            return handle_error_response(
                "Parameters 'sheet_name' and 'cell' are required for 'remove_formula' operation."
            )
        return remove_formula(
            sheet_name=sheet_name,
            cell=cell,
            path=path,
            file_name=file_name
        )
    
    elif operation == "define_named_range":
        if not sheet_name or not range_name or not cell_range:
            return handle_error_response(
                "Parameters 'sheet_name', 'range_name', and 'cell_range' are required for 'define_named_range' operation."
            )
        return define_named_range(
            sheet_name=sheet_name,
            range_name=range_name,
            cell_range=cell_range,
            path=path,
            file_name=file_name
        )
    
    else:
        message = f"Unsupported formula operation: {operation}"
        logger.warning(message)
        return {
            "status": False,
            "message": message,
            "result": None
        }


# ------------------------------------------------------------------------------
# 7. Formatting dispatcher (formatting_operations)
# ------------------------------------------------------------------------------
def formatting_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    cell: Optional[str] = None,
    style_rules: Optional[Dict[str, Any]] = None,
    formatting_rules: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Applies formatting rules to cells, such as specific styles or conditional
    formatting.

    Args:
        operation (str): The formatting operation to perform ("set_cell_format", "apply_conditional_formatting").
        path (str, optional): Directory path to the workbook. Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file. Defaults to 'example_spreadsheet.xlsx'.
        sheet_name (str, optional): Target sheet to format.
        cell (str, optional): Target cell reference for 'set_cell_format' (e.g., 'A1'). 
        style_rules (Dict[str, Any], optional): Styling rules dict used by 'set_cell_format'.
        formatting_rules (Dict[str, Any], optional): Rules dict used by 'apply_conditional_formatting'.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "set_cell_format":
        if not sheet_name or not cell or not style_rules:
            return handle_error_response("Parameters 'sheet_name', 'cell', and 'style_rules' are required for 'set_cell_format' operation.")
        return set_cell_format(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            cell=cell,
            style_rules=style_rules
        )
    elif operation == "apply_conditional_formatting":
        if not sheet_name or not formatting_rules:
            return handle_error_response("Parameters 'sheet_name' and 'formatting_rules' are required for 'apply_conditional_formatting' operation.")
        return apply_conditional_formatting(
            path=path,
            file_name=file_name,
            sheet_name=sheet_name,
            formatting_rules=formatting_rules
        )
    else:
        message = f"Unsupported formatting operation: {operation}"
        logger.warning(message)
        return {
            "status": False,
            "message": message,
            "result": None
        }


# ------------------------------------------------------------------------------
# 8. DataValidation dispatcher (data_validation_operations)
# ------------------------------------------------------------------------------
def data_validation_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    validation_rules: Optional[Dict[str, Any]] = None,
    range_to_remove: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sets or removes data validation rules from cells in a .xlsx file.

    Args:
        operation (str): The data validation operation to perform ("set_data_validation", "remove_data_validation").
        path (str, optional): Directory path to the workbook. Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file. Defaults to 'example_spreadsheet.xlsx'.
        sheet_name (str, optional): Target sheet for data validation.
        validation_rules (Dict[str, Any], optional): Validation rules to apply for `set_data_validation`.
        range_to_remove (str, optional): Specific range to remove validations from (e.g., "A1:A10") for `remove_data_validation`.

    Returns:
        Dict[str, Any]: Standardized response with status, message, and result.
    """
    if operation == "set_data_validation":
        if not sheet_name or not validation_rules:
            return handle_error_response("Parameters 'sheet_name' and 'validation_rules' are required for 'set_data_validation' operation.")
        
        # Check if the file exists
        if not check_file_exists(path, file_name):
            return handle_error_response(f"Workbook '{file_name}' does not exist in path '{path}'.")
        
        return set_data_validation(
            sheet_name=sheet_name,
            validation_rules=validation_rules,
            path=path,
            file_name=file_name
        )
    elif operation == "remove_data_validation":
        if not sheet_name:
            return handle_error_response("Parameter 'sheet_name' is required for 'remove_data_validation' operation.")
        
        # Check if the file exists
        if not check_file_exists(path, file_name):
            return handle_error_response(f"Workbook '{file_name}' does not exist in path '{path}'.")
        
        return remove_data_validation(
            sheet_name=sheet_name,
            path=path,
            file_name=file_name,
            range_to_remove=range_to_remove  # Pass the new parameter
        )
    else:
        message = f"Unsupported data validation operation: {operation}"
        logger.warning(message)
        return {
            "status": False,
            "message": message,
            "result": None
        }


# ------------------------------------------------------------------------------
# 9. DataTransformation dispatcher (data_transformation_operations)
# ------------------------------------------------------------------------------
def data_transformation_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    source_range: Optional[str] = None,
    destination_range: Optional[str] = None
) -> Dict[str, Any]:
    logger.info(f"Starting data transformation operation: '{operation}' on file '{file_name}' at path '{path}'.")

    # Validate file existence
    try:
        check_file_exists(path, file_name)
    except Exception as e:
        error_message = f"File '{file_name}' not found at path '{path}'."
        logger.error(error_message)
        return handle_error_response(error_message)

    if operation == "transpose_data":
        if not source_range or not destination_range:
            error_message = "Parameters 'source_range' and 'destination_range' are required for 'transpose_data' operation."
            logger.error(error_message)
            return handle_error_response(error_message)
        
        logger.debug(f"Transposing data from '{source_range}' to '{destination_range}'.")
        result = transpose_data(
            source_range=source_range,
            destination_range=destination_range,
            path=path,
            file_name=file_name
        )
        logger.info(f"Transpose operation completed with status: {result.get('status')}.")
        return result

    elif operation == "unpivot_data":
        if not sheet_name:
            error_message = "Parameter 'sheet_name' is required for 'unpivot_data' operation."
            logger.error(error_message)
            return handle_error_response(error_message)
        
        logger.debug(f"Unpivoting data in sheet '{sheet_name}'.")
        result = unpivot_data(
            sheet_name=sheet_name,
            path=path,
            file_name=file_name
        )
        logger.info(f"Unpivot operation completed with status: {result.get('status')}.")
        return result

    else:
        error_message = f"Unsupported data transformation operation: {operation}"
        logger.error(error_message)
        return {
            "status": False,
            "message": error_message,
            "result": None
        }


# ------------------------------------------------------------------------------
# 10. Chart and Graphics dispatcher (chart_operations)
# ------------------------------------------------------------------------------
def chart_operations(
    operation: str,
    path: str = "flexiai.toolsmith/data/spreadsheets",
    file_name: str = "example_spreadsheet.xlsx",
    sheet_name: Optional[str] = None,
    # For create_chart
    chart_type: Optional[str] = None,
    data_range: Optional[str] = None,
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
    # For update_chart
    chart_title: Optional[str] = None,
    new_data_range: Optional[str] = None,
    new_categories_range: Optional[str] = None,
    new_title: Optional[str] = None,
    new_x_title: Optional[str] = None,
    new_y_title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dispatches chart-related operations such as creating, updating, or removing charts.
    
    Args:
        operation (str): The chart-related operation to perform 
                         ("create_chart", "update_chart", or "remove_chart").
        path (str, optional): Directory path to the workbook. Defaults to 'flexiai.toolsmith/data/spreadsheets'.
        file_name (str, optional): Name of the workbook file. Defaults to 'example_spreadsheet.xlsx'.
        sheet_name (str, optional): Name of the sheet where chart operations occur.
        
        -- create_chart parameters --
        chart_type (str, optional): Type of chart (e.g., "bar", "line", etc.). Required for 'create_chart'.
        data_range (str, optional): Range for numeric data (e.g., "B2:D10"). 
        categories_range (str, optional): Range for category labels (e.g., "A2:A10").
        destination_cell (str, optional): Cell where chart is placed (e.g., "A10").
        title (str, optional): Main chart title.
        x_title (str, optional): X-axis title.
        y_title (str, optional): Y-axis title.
        legend_position (str, optional): Legend position ("r", "b", etc.). Defaults to "r".
        style (int, optional): Built-in openpyxl chart style index. Defaults to 2.
        show_data_labels (bool, optional): Whether to show data labels. Defaults to False.
        overlap (int, optional): Overlap percentage for bar charts. E.g., 0 means side-by-side.
        grouping (str, optional): Grouping for bar/column charts (e.g. "clustered", "stacked").
        series_names (List[str], optional): Custom names for multiple series.

        -- update_chart parameters --
        chart_title (str, optional): Current chart.title used to locate the chart to update.
        new_data_range (str, optional): Updates data range if provided.
        new_categories_range (str, optional): Updates category labels if provided.
        new_title (str, optional): Updates chart's main title if provided.
        new_x_title (str, optional): Updates chart's X-axis title if provided.
        new_y_title (str, optional): Updates chart's Y-axis title if provided.
        
    Returns:
        Dict[str, Any]: Standardized response dict with status, message, and result.
    """
    # 1) create_chart
    if operation == "create_chart":
        # Validate required parameters
        if not sheet_name or not chart_type or not data_range:
            return handle_error_response(
                "Parameters 'sheet_name', 'chart_type', and 'data_range' are required for 'create_chart' operation."
            )

        return create_chart(
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
            series_names=series_names,
            path=path,
            file_name=file_name
        )

    # 2) update_chart
    elif operation == "update_chart":
        # Validate required parameters
        if not sheet_name or not chart_title:
            return handle_error_response(
                "Parameters 'sheet_name' and 'chart_title' are required for 'update_chart' operation."
            )
        
        return update_chart(
            sheet_name=sheet_name,
            chart_title=chart_title,
            new_data_range=new_data_range,
            new_categories_range=new_categories_range,
            new_title=new_title,
            new_x_title=new_x_title,
            new_y_title=new_y_title,
            path=path,
            file_name=file_name
        )

    # 3) remove_chart
    elif operation == "remove_chart":
        # Validate required parameters
        if not sheet_name or not chart_title:
            return handle_error_response(
                "Parameters 'sheet_name' and 'chart_title' are required for 'remove_chart' operation."
            )
        
        return remove_chart(
            sheet_name=sheet_name,
            chart_title=chart_title,
            path=path,
            file_name=file_name
        )

    else:
        message = f"Unsupported chart operation: {operation}"
        logger.warning(message)
        return {
            "status": False,
            "message": message,
            "result": None
        }

