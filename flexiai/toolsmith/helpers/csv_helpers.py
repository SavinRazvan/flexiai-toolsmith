# File: flexiai/toolsmith/helpers/csv_helpers.py

import os
import pandas as pd
import logging


class CSVHelpers:
    """
    CSVHelpers provides utility methods for handling CSV operations.
    Includes dynamic operations for reading, writing, updating, and matching data.
    """

    def __init__(self):
        """
        Initializes the CSVHelpers instance with a logger.
        """
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def handle_csv(file_path: str, operation: str, **kwargs) -> dict:
        """
        Dispatcher method that delegates CSV operations to specific methods.

        Args:
            file_path (str): Path to the CSV file.
            operation (str): The operation to perform. Options: 'read', 'write', 'update'.
            **kwargs: Additional arguments required for the specific operation.

        Returns:
            dict: A dictionary with the status, message, and result (if applicable).
        """
        try:
            operations = {
                'read': CSVHelpers._read_csv,
                'write': CSVHelpers._write_csv,
                'update': CSVHelpers._update_csv
            }

            operation_method = operations.get(operation.lower())
            if not operation_method:
                return {"status": False, "message": f"Unsupported operation: {operation}.", "result": None}

            return operation_method(file_path, **kwargs)

        except Exception as e:
            return {"status": False, "message": f"An unexpected error occurred: {str(e)}", "result": None}

    @staticmethod
    def _read_csv(file_path: str, **kwargs) -> dict:
        """
        Reads a CSV file into a pandas DataFrame.

        Args:
            file_path (str): Path to the CSV file.
            **kwargs: Additional pandas read_csv parameters (e.g., encoding).

        Returns:
            dict: A dictionary with the status, message, and DataFrame result.
        """
        try:
            if not os.path.exists(file_path):
                return {"status": False, "message": f"File not found: {file_path}.", "result": None}

            df = pd.read_csv(file_path, dtype=str, **kwargs)
            return {"status": True, "message": "File read successfully.", "result": df}

        except pd.errors.EmptyDataError:
            return {"status": False, "message": "The CSV file is empty.", "result": None}
        except Exception as e:
            return {"status": False, "message": f"Error reading CSV file: {str(e)}", "result": None}

    @staticmethod
    def _write_csv(file_path: str, dataframe: pd.DataFrame, **kwargs) -> dict:
        """
        Writes a pandas DataFrame to a CSV file.

        Args:
            file_path (str): Path to the CSV file.
            dataframe (pd.DataFrame): DataFrame to write.
            **kwargs: Additional pandas to_csv parameters (e.g., encoding).

        Returns:
            dict: A dictionary with the status and message.
        """
        try:
            if not isinstance(dataframe, pd.DataFrame):
                return {"status": False, "message": "A valid DataFrame must be provided for writing.", "result": None}

            dataframe.to_csv(file_path, index=False, **kwargs)
            return {"status": True, "message": "File written successfully.", "result": None}

        except Exception as e:
            return {"status": False, "message": f"Error writing CSV file: {str(e)}", "result": None}

    @staticmethod
    def _update_csv(file_path: str, updates: dict, condition: callable, **kwargs) -> dict:
        """
        Updates specific records in a CSV file based on a condition.

        Args:
            file_path (str): Path to the CSV file.
            updates (dict): Dictionary of column-value pairs to update.
            condition (callable): A function that takes a DataFrame row and returns True if the row should be updated.
            **kwargs: Additional pandas read_csv parameters.

        Returns:
            dict: A dictionary with the status and message.
        """
        try:
            read_response = CSVHelpers._read_csv(file_path, **kwargs)
            if not read_response["status"]:
                return read_response

            df = read_response["result"]

            # Apply the condition to identify rows to update
            mask = df.apply(condition, axis=1)
            if not mask.any():
                return {"status": False, "message": "No records match the provided condition.", "result": None}

            # Update the DataFrame
            for key, value in updates.items():
                if key in df.columns:
                    df.loc[mask, key] = value
                else:
                    return {"status": False, "message": f"Column '{key}' does not exist in the CSV.", "result": None}

            # Write the updated DataFrame back to CSV
            write_response = CSVHelpers._write_csv(file_path, df, **kwargs)
            return write_response

        except Exception as e:
            return {"status": False, "message": f"Error updating CSV file: {str(e)}", "result": None}

    @staticmethod
    def clean_dataframe(df: pd.DataFrame, columns_to_lower: list = None, columns_to_strip: list = None) -> pd.DataFrame:
        """
        Cleans the DataFrame by stripping spaces and converting specified columns to lowercase.

        Args:
            df (pd.DataFrame): The DataFrame to clean.
            columns_to_lower (list, optional): Columns to convert to lowercase.
            columns_to_strip (list, optional): Columns to strip spaces.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        if columns_to_strip:
            for column in columns_to_strip:
                if column in df.columns:
                    df[column] = df[column].astype(str).str.strip()

        if columns_to_lower:
            for column in columns_to_lower:
                if column in df.columns:
                    df[column] = df[column].astype(str).str.lower()

        return df

    @staticmethod
    def find_matching_records(df: pd.DataFrame, search_criteria: dict, min_matches: int = 3) -> list:
        """
        Finds matching records in the DataFrame based on the search criteria.

        Args:
            df (pd.DataFrame): The cleaned DataFrame containing data.
            search_criteria (dict): Dictionary of search criteria where keys are column names and values are the values to match.
            min_matches (int): Minimum number of matching fields required.

        Returns:
            list of dict: List of matched records as dictionaries.
        """
        if not search_criteria:
            return []

        # Initialize a Series to count matches
        match_counts = pd.Series(0, index=df.index)

        # Iterate over each search criterion and update match_counts
        for key, value in search_criteria.items():
            if key in df.columns:
                if key == "date_of_birth":
                    # Exact match for date_of_birth
                    match = df[key] == value
                else:
                    # Case-insensitive match for other fields
                    match = df[key].str.lower() == value.lower()
                match_counts += match.astype(int)

        # Filter records with at least min_matches
        matched_indices = match_counts[match_counts >= min_matches].index
        matched_records = df.loc[matched_indices]

        # Convert matched records to list of dictionaries
        return matched_records.to_dict(orient='records')
