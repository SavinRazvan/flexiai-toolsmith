# FILE: flexiai/toolsmith/tools_infrastructure/csv_infrastructure/utils/error_handler.py

import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class OperationResponse(BaseModel):
    """
    Standard response model for CSV operations.
    """
    status: bool = Field(..., description="True if operation succeeded, False otherwise.")
    message: str = Field(..., description="Description of the result or error.")
    result: Optional[Any] = Field(None, description="Data returned by the operation, if any.")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response model to a plain dict.

        Returns:
            Dict[str, Any]: The response as a dictionary.
        """
        return self.model_dump()

def handle_error_response(message: str) -> Dict[str, Any]:
    """
    Build a standardized error response.

    Args:
        message (str): Error message.

    Returns:
        Dict[str, Any]: A dict with status=False, the error message, and result=None.
    """
    logger.error(message)
    response = OperationResponse(status=False, message=message, result=None)
    return response.to_dict()
