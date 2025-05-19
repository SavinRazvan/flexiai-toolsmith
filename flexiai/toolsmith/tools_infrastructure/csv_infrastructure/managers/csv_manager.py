# FILE: flexiai/toolsmith/tools_infrastructure/csv_infrastructure/managers/csv_manager.py

import os
import logging
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable

from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.exceptions.csv_exceptions import CSVError
from flexiai.toolsmith.tools_infrastructure.csv_infrastructure.utils.file_handler import (
    get_full_path,
    check_file_exists
)

logger = logging.getLogger(__name__)


class CSVManager:
    """
    Manages CRUD and utility operations on CSV files using pandas.
    """

    def __init__(self, file_path: str, load_csv: bool = True):
        """
        Initialize the CSVManager.

        Args:
            file_path (str): Path to the CSV file.
            load_csv (bool): Whether to load the CSV into memory on init. Defaults to True.
        """
        self.file_path = file_path
        self.df: Optional[pd.DataFrame] = None
        logger.debug(f"Initialized CSVManager for '{self.file_path}'.")
        if load_csv:
            self._load_csv()

    def _load_csv(self) -> None:
        """
        Load the CSV from disk into a pandas DataFrame.

        Raises:
            CSVError: If the file cannot be loaded.
        """
        try:
            # Ensure the file exists before reading
            path, name = os.path.dirname(self.file_path), os.path.basename(self.file_path)
            check_file_exists(path, name)
            # Load all columns as strings, don't auto-convert blanks to NaN
            self.df = pd.read_csv(self.file_path, dtype=str, keep_default_na=False)
            # Clean up whitespace, convert empty strings to NaN, drop blank rows, etc.
            self._clean_and_validate()
            logger.info(f"CSV '{self.file_path}' loaded and cleaned successfully.")
        except Exception as e:
            logger.error(f"Failed to load CSV '{self.file_path}': {e}")
            raise CSVError(f"Failed to load CSV '{self.file_path}': {e}") from e

    def _clean_and_validate(self, required_columns: Optional[List[str]] = None) -> None:
        """
        Trim whitespace, convert empty strings to NaN, drop blank rows,
        and optionally ensure required_columns have no missing values.
        """
        # 1) Strip whitespace on all string columns
        for col in self.df.columns:
            self.df[col] = self.df[col].astype(str).str.strip()

        # 2) Convert empty strings (or whitespace-only) to actual NaN
        self.df.replace({"": pd.NA, r"^\s*$": pd.NA}, regex=True, inplace=True)

        # 3) Drop rows that are entirely blank (all NaN)
        before = len(self.df)
        self.df.dropna(how="all", inplace=True)
        after = len(self.df)
        if before != after:
            logger.warning(f"Dropped {before - after} fully blank rows from '{self.file_path}'.")

        # 4) If required_columns provided, ensure they exist and have no missing
        if required_columns:
            missing_cols = [c for c in required_columns if c not in self.df.columns]
            if missing_cols:
                raise CSVError(f"Missing required columns after load: {missing_cols}")

            nulls = {}
            for c in required_columns:
                cnt = int(self.df[c].isna().sum())
                if cnt:
                    nulls[c] = cnt
            if nulls:
                raise CSVError(f"Column(s) with missing values: {nulls}")

    def _ensure_loaded(self) -> None:
        """
        Ensure that the DataFrame is loaded into memory.
        """
        if self.df is None:
            self._load_csv()

    def _save_csv(self) -> None:
        """
        Save the in-memory DataFrame back to the CSV file.

        Raises:
            CSVError: If saving fails.
        """
        try:
            self.df.to_csv(self.file_path, index=False)
            logger.info(f"CSV '{self.file_path}' saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save CSV '{self.file_path}': {e}")
            raise CSVError(f"Failed to save CSV '{self.file_path}': {e}") from e

    def create_csv(self, headers: Optional[List[str]] = None) -> None:
        """
        Create a new CSV file. Fails if the file already exists.

        Args:
            headers (List[str], optional): Column names for the new CSV. Defaults to None.

        Raises:
            CSVError: If the file exists or creation fails.
        """
        full_path = get_full_path(os.path.dirname(self.file_path), os.path.basename(self.file_path))
        if os.path.exists(full_path):
            raise CSVError(f"Cannot create. File '{full_path}' already exists.")
        try:
            df = pd.DataFrame(columns=headers) if headers else pd.DataFrame()
            df.to_csv(full_path, index=False)
            self.df = df
            logger.info(f"CSV '{full_path}' created with headers={headers}.")
        except Exception as e:
            logger.error(f"Failed to create CSV '{full_path}': {e}")
            raise CSVError(f"Failed to create CSV '{full_path}': {e}") from e

    def delete_csv(self) -> None:
        """
        Delete the CSV file from disk.

        Raises:
            CSVError: If deletion fails.
        """
        try:
            self.df = None
            os.remove(self.file_path)
            logger.info(f"CSV '{self.file_path}' deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete CSV '{self.file_path}': {e}")
            raise CSVError(f"Failed to delete CSV '{self.file_path}': {e}") from e

    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read the entire CSV into a list of dicts.

        Returns:
            List[Dict[str, Any]]: All rows as dictionaries.

        Raises:
            CSVError: If reading fails.
        """
        self._ensure_loaded()
        try:
            records = self.df.to_dict(orient="records")
            logger.info(f"Read {len(records)} rows from '{self.file_path}'.")
            return records
        except Exception as e:
            logger.error(f"Failed to read all rows: {e}")
            raise CSVError(f"Failed to read all rows: {e}") from e

    def read_rows(self, start: int = 0, count: int = 20) -> List[Dict[str, Any]]:
        """
        Read a slice of rows with pagination.

        Args:
            start (int): Zero-based start index. Defaults to 0.
            count (int): Number of rows to read. Defaults to 20.

        Returns:
            List[Dict[str, Any]]: The requested slice of rows.

        Raises:
            CSVError: If reading fails.
        """
        self._ensure_loaded()
        try:
            slice_df = self.df.iloc[start:start + count]
            records = slice_df.to_dict(orient="records")
            logger.info(f"Read rows {start} to {start + count - 1} from '{self.file_path}'.")
            return records
        except Exception as e:
            logger.error(f"Failed to read rows: {e}")
            raise CSVError(f"Failed to read rows: {e}") from e

    def read_row(self, index: int) -> Dict[str, Any]:
        """
        Read a single row by integer index.

        Args:
            index (int): Zero-based row index.

        Returns:
            Dict[str, Any]: The row as a dict.

        Raises:
            CSVError: If index out of range or reading fails.
        """
        self._ensure_loaded()
        try:
            row = self.df.iloc[index]
            record = row.to_dict()
            logger.info(f"Read row {index} from '{self.file_path}'.")
            return record
        except Exception as e:
            logger.error(f"Failed to read row {index}: {e}")
            raise CSVError(f"Failed to read row {index}: {e}") from e

    def read_column(self, column: Union[str, int]) -> List[Any]:
        """
        Read an entire column by name or 0-based index.

        Args:
            column (Union[str,int]): Column name or zero-based index.

        Returns:
            List[Any]: All values in the column.

        Raises:
            CSVError: If column not found or reading fails.
        """
        self._ensure_loaded()
        try:
            if isinstance(column, int):
                col_name = self.df.columns[column]
            else:
                col_name = column
            values = self.df[col_name].tolist()
            logger.info(f"Read column '{col_name}' from '{self.file_path}'.")
            return values
        except Exception as e:
            logger.error(f"Failed to read column {column}: {e}")
            raise CSVError(f"Failed to read column {column}: {e}") from e

    def append_row(self, row: Dict[str, Any]) -> None:
        """
        Append a single row to the CSV.

        Args:
            row (Dict[str, Any]): Mapping of column to value.

        Raises:
            CSVError: If append or save fails.
        """
        self._ensure_loaded()
        try:
            self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
            self._save_csv()
            logger.info(f"Appended row to '{self.file_path}': {row}")
        except Exception as e:
            logger.error(f"Failed to append row: {e}")
            raise CSVError(f"Failed to append row: {e}") from e

    def append_rows(self, rows: List[Dict[str, Any]]) -> None:
        """
        Append multiple rows to the CSV.

        Args:
            rows (List[Dict[str, Any]]): List of row mappings.

        Raises:
            CSVError: If append or save fails.
        """
        self._ensure_loaded()
        try:
            self.df = pd.concat([self.df, pd.DataFrame(rows)], ignore_index=True)
            self._save_csv()
            logger.info(f"Appended {len(rows)} rows to '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to append rows: {e}")
            raise CSVError(f"Failed to append rows: {e}") from e

    def update_cell(
        self,
        row_index: int,
        column: Union[str, int],
        value: Any
    ) -> None:
        """
        Update a single cell.

        Args:
            row_index (int): Zero-based row index.
            column (Union[str,int]): Column name or zero-based index.
            value (Any): New cell value.

        Raises:
            CSVError: If update or save fails.
        """
        self._ensure_loaded()
        try:
            if isinstance(column, int):
                col_name = self.df.columns[column]
            else:
                col_name = column
            self.df.at[row_index, col_name] = value
            self._save_csv()
            logger.info(f"Updated cell ({row_index}, {col_name}) to '{value}'.")
        except Exception as e:
            logger.error(f"Failed to update cell: {e}")
            raise CSVError(f"Failed to update cell: {e}") from e

    def delete_row(self, row_index: int) -> None:
        """
        Delete a row by index.

        Args:
            row_index (int): Zero-based row index.

        Raises:
            CSVError: If deletion or save fails.
        """
        self._ensure_loaded()
        try:
            self.df = self.df.drop(self.df.index[row_index]).reset_index(drop=True)
            self._save_csv()
            logger.info(f"Deleted row {row_index} from '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to delete row {row_index}: {e}")
            raise CSVError(f"Failed to delete row {row_index}: {e}") from e

    def filter_rows(
        self,
        column: Union[str, int],
        condition_type: str,
        condition_value: Any
    ) -> List[Dict[str, Any]]:
        """
        Return rows matching a condition on a column.

        Args:
            column (Union[str,int]): Column name or zero-based index.
            condition_type (str): 'equals','greater_than','less_than','contains','startswith','endswith'.
            condition_value (Any): Value to compare against.

        Returns:
            List[Dict[str, Any]]: Matching rows as dicts.

        Raises:
            CSVError: If filter fails.
        """
        self._ensure_loaded()
        try:
            if isinstance(column, int):
                col_name = self.df.columns[column]
            else:
                col_name = column

            cond = self._build_condition_func(condition_type, condition_value)
            mask = self.df[col_name].apply(cond)
            result = self.df[mask].to_dict(orient="records")
            logger.info(f"Filtered rows on '{col_name}' {condition_type} '{condition_value}': {len(result)} found.")
            return result
        except Exception as e:
            logger.error(f"Failed to filter rows: {e}")
            raise CSVError(f"Failed to filter rows: {e}") from e

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate basic summary: row count, column count, and column names.

        Returns:
            Dict[str, Any]: {'rows': int, 'columns': int, 'column_names': List[str]}

        Raises:
            CSVError: If summary fails.
        """
        self._ensure_loaded()
        try:
            summary = {
                "rows": len(self.df),
                "columns": len(self.df.columns),
                "column_names": self.df.columns.tolist()
            }
            logger.info(f"Generated summary for '{self.file_path}': {summary}")
            return summary
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise CSVError(f"Failed to generate summary: {e}") from e

    def validate_structure(self, required_columns: List[str]) -> bool:
        """
        Validate that required columns exist.

        Args:
            required_columns (List[str]): Column names that must be present.

        Returns:
            bool: True if valid.

        Raises:
            CSVError: If any column is missing.
        """
        self._ensure_loaded()
        missing = [col for col in required_columns if col not in self.df.columns]
        if missing:
            message = f"Missing required columns: {missing}"
            logger.error(message)
            raise CSVError(message)
        logger.info(f"CSV '{self.file_path}' contains all required columns.")
        return True

    def _build_condition_func(self, condition: str, value: Any) -> Callable[[Any], bool]:
        """
        Internal: build a predicate for filtering.

        Args:
            condition (str): Condition type.
            value (Any): Comparison value.

        Returns:
            Callable[[Any], bool]: Predicate function.

        Raises:
            CSVError: On unsupported condition.
        """
        if condition == "equals":
            # compare trimmed strings
            val = "" if value is None else str(value).strip()
            return lambda x: str(x).strip() == val
        if condition == "greater_than":
            return lambda x: float(x) > float(value) if pd.notna(x) else False
        if condition == "less_than":
            return lambda x: float(x) < float(value) if pd.notna(x) else False
        if condition == "contains":
            return lambda x: value in str(x) if pd.notna(x) else False
        if condition == "startswith":
            return lambda x: str(x).startswith(value) if pd.notna(x) else False
        if condition == "endswith":
            return lambda x: str(x).endswith(value) if pd.notna(x) else False
        logger.error(f"Unsupported condition '{condition}'.")
        raise CSVError(f"Unsupported condition '{condition}'.")
