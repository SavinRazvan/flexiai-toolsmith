# FILE: flexiai/config/client_settings.py

"""
Load and validate configuration for the AI client based on credential type.
"""

import logging
from pydantic import ValidationError
from flexiai.config.models import (
    OpenAISettings,
    AzureOpenAISettings,
    DeepSeekSettings,
    QwenSettings,
    GitHubAzureInferenceSettings,
    GeneralSettings
)

logger = logging.getLogger(__name__)


class ClientConfig:
    """Holds general and provider-specific settings for the AI client.

    Attributes:
        general (GeneralSettings): The general application settings.
        provider (BaseSettings): The provider-specific settings model,
            chosen based on `general.CREDENTIAL_TYPE`.
    """
    # Load the general settings
    general = GeneralSettings()

    # Based on the credential type, load the corresponding provider settings
    if general.CREDENTIAL_TYPE == "openai":
        provider = OpenAISettings()
    elif general.CREDENTIAL_TYPE == "azure":
        provider = AzureOpenAISettings()
    elif general.CREDENTIAL_TYPE == "deepseek":
        provider = DeepSeekSettings()
    elif general.CREDENTIAL_TYPE == "qwen":
        provider = QwenSettings()
    elif general.CREDENTIAL_TYPE == "github_models":
        provider = GitHubAzureInferenceSettings()
    else:
        raise ValueError(f"[ClientConfig] Unsupported CREDENTIAL_TYPE: {general.CREDENTIAL_TYPE}")


# Instantiate a global config object
try:
    config = ClientConfig()
    logger.info(f"[ClientConfig] Configuration loaded for {config.general.CREDENTIAL_TYPE}")
except ValidationError as e:
    logger.error(f"[ClientConfig] Configuration validation error: {e}", exc_info=True)
    raise RuntimeError("[ClientConfig] Configuration validation failed. Check .env file and logs.") from e
