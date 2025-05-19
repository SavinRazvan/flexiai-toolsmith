# FILE: flexiai/toolsmith/helpers/csv_infrastructure/utils/mixed_helpers.py

import json
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)

def serialize_datetimes(data: Any) -> Any:
    """
    Recursively serialize non-JSON-native types to JSON-compatible formats.

    Supported types: datetime, date, Decimal, set, tuple, bytes.

    Args:
        data (Any): The input data structure.

    Returns:
        Any: Data with all values converted to JSON-serializable types.
    """
    if isinstance(data, list):
        return [serialize_datetimes(item) for item in data]
    if isinstance(data, dict):
        return {key: serialize_datetimes(value) for key, value in data.items()}
    if isinstance(data, (datetime, date)):
        iso = data.isoformat()
        logger.debug(f"Serialized {data!r} to '{iso}'")
        return iso
    if isinstance(data, Decimal):
        s = str(data)
        logger.debug(f"Serialized Decimal {data!r} to '{s}'")
        return s
    if isinstance(data, set):
        lst = list(data)
        logger.debug(f"Serialized set {data!r} to list {lst!r}")
        return [serialize_datetimes(item) for item in lst]
    if isinstance(data, tuple):
        lst = list(data)
        logger.debug(f"Serialized tuple {data!r} to list {lst!r}")
        return [serialize_datetimes(item) for item in lst]
    if isinstance(data, bytes):
        try:
            s = data.decode('utf-8')
            logger.debug(f"Serialized bytes {data!r} to '{s}'")
            return s
        except UnicodeDecodeError as e:
            logger.error(f"Cannot decode bytes {data!r}: {e}")
            raise TypeError(f"Cannot decode bytes: {e}") from e
    return data

def prepare_tool_output(output_message: dict) -> dict:
    """
    Prepare a message for output by serializing any non-serializable objects.

    Args:
        output_message (dict): The raw output data.

    Returns:
        dict: A dict containing a JSON string under the 'output' key.
    """
    try:
        serialized = serialize_datetimes(output_message)
        json_str = json.dumps(serialized)
        logger.debug(f"Prepared tool output: {json_str}")
        return {"output": json_str}
    except Exception as e:
        logger.error(f"Error preparing tool output: {e}")
        raise
