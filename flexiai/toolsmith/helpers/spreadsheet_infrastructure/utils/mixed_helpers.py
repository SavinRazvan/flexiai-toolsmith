# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/utils/mixed_helpers.py

"""
mixed_helpers module.

Provides helper functions to serialize non-JSON-compatible Python objects (dates, decimals,
sets, tuples, bytes) into JSON-friendly formats, and prepare tool output messages by
serializing and JSON-encoding them.
"""

import json
import logging
from datetime import datetime, date
from typing import Any, Dict
from decimal import Decimal

logger = logging.getLogger(__name__)


def serialize_datetimes(data: Any) -> Any:
    """
    Recursively serialize non-JSON-native types to JSON-compatible representations.

    Supported conversions:
      - datetime, date -> ISO 8601 strings
      - Decimal -> string
      - set, tuple -> list
      - bytes -> UTF-8 decoded string (raises TypeError if decoding fails)

    Args:
        data (Any): The data structure to serialize.

    Returns:
        Any: The structure with all non-serializable values converted.

    Raises:
        TypeError: If a bytes object cannot be decoded as UTF-8.
    """
    if isinstance(data, list):
        return [serialize_datetimes(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_datetimes(value) for key, value in data.items()}
    elif isinstance(data, (datetime, date)):
        iso = data.isoformat()
        logger.debug(f"Serialized {type(data).__name__} {data} -> '{iso}'")
        return iso
    elif isinstance(data, Decimal):
        s = str(data)
        logger.debug(f"Serialized Decimal {data} -> '{s}'")
        return s
    elif isinstance(data, set):
        lst = list(data)
        logger.debug(f"Serialized set {data} -> {lst}")
        return lst
    elif isinstance(data, tuple):
        lst = list(data)
        logger.debug(f"Serialized tuple {data} -> {lst}")
        return lst
    elif isinstance(data, bytes):
        try:
            text = data.decode('utf-8')
            logger.debug(f"Serialized bytes {data} -> '{text}'")
            return text
        except UnicodeDecodeError as e:
            logger.error(f"Cannot decode bytes: {e}")
            raise TypeError(f"Cannot decode bytes object: {e}") from e
    else:
        return data


def prepare_tool_output(output_message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare a tool output message by serializing non-serializable objects and JSON-encoding.

    Args:
        output_message (Dict[str, Any]): Message dict that may contain dates, decimals, etc.

    Returns:
        Dict[str, Any]: A dict with key 'output' and value as a JSON string of the serialized message.

    Raises:
        TypeError: If serialization of contained objects fails.
        Exception: For any other unexpected error during preparation.
    """
    try:
        serialized = serialize_datetimes(output_message)
        json_str = json.dumps(serialized)
        logger.debug(f"Prepared tool output JSON: {json_str}")
        return {"output": json_str}
    except Exception as e:
        logger.error(f"Error preparing tool output: {e}")
        raise
