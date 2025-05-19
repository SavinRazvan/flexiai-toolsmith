# FILE: flexiai/toolsmith/helpers/spreadsheet_infrastructure/utils/error_handler.py

"""
error_handler module.

Defines OperationResponse for standardized success/error messaging and a helper
to generate error responses for spreadsheet operations.
"""

import logging
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OperationResponse(BaseModel):
    """
    Standardized response model for spreadsheet operations.

    Attributes:
        status (bool): True on success, False on failure.
        message (str): Description of the result or error.
        result (Optional[Any]): Operation data or None if not applicable.
    """
    status: bool = Field(..., description="Indicates success (`True`) or failure (`False`).")
    message: str = Field(..., description="Brief explanation of the operation result or error.")
    result: Optional[Any] = Field(None, description="Data returned from the operation, or `None` if not applicable.")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the OperationResponse model into a plain dictionary.

        Returns:
            Dict[str, Any]: The response as a dictionary.
        """
        return self.model_dump()


def handle_error_response(message: str) -> Dict[str, Any]:
    """
    Generate a standardized error response dictionary.

    Args:
        message (str): Error message to include in the response.

    Returns:
        Dict[str, Any]: A dict with status=False, the error message, and result=None.
    """
    logger.error(message)
    response = OperationResponse(
        status=False,
        message=message,
        result=None
    )
    return response.to_dict()
