# FILE: flexiai/credentials/credentials.py

"""
Credential management module.

Defines a strategy pattern for validating credentials and constructing AI clients
for various providers (OpenAI, Azure OpenAI, DeepSeek, Qwen, GitHub Azure Inference).
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Any
from flexiai.config.client_settings import config

logger = logging.getLogger(__name__)


class CredentialStrategy(ABC):
    """Abstract base class for provider-specific credential strategies."""

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present and valid."""
        ...

    @abstractmethod
    def get_client(self) -> Any:
        """Construct and return a configured client for the provider."""
        ...


class OpenAICredentialStrategy(CredentialStrategy):
    """Credential strategy for OpenAI's API (async)."""

    def validate_credentials(self) -> bool:
        if not config.provider.OPENAI_API_KEY:
            logger.error("[OpenAICredentialStrategy] OPENAI_API_KEY missing")
            return False
        return True

    def get_client(self) -> Any:
        """Instantiate and return an `AsyncOpenAI` client."""
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            api_key=config.provider.OPENAI_API_KEY,
            organization=config.provider.OPENAI_ORGANIZATION_ID,
            project=config.provider.OPENAI_PROJECT_ID,
            default_headers={
                "OpenAI-Beta": f"assistants={config.provider.OPENAI_ASSISTANT_VERSION}"
            }
        )


class AzureOpenAICredentialStrategy(CredentialStrategy):
    """Credential strategy for Azure OpenAI (async)."""

    def validate_credentials(self) -> bool:
        missing = []
        if not config.provider.AZURE_OPENAI_API_KEY:
            missing.append("AZURE_OPENAI_API_KEY")
        if not config.provider.AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not config.provider.AZURE_OPENAI_API_VERSION:
            missing.append("AZURE_OPENAI_API_VERSION")

        if missing:
            logger.error(f"[AzureOpenAICredentialStrategy] Missing settings: {', '.join(missing)}")
            return False
        return True

    def get_client(self) -> Any:
        """Instantiate and return an `AsyncAzureOpenAI` client."""
        from openai import AsyncAzureOpenAI
        return AsyncAzureOpenAI(
            api_key=config.provider.AZURE_OPENAI_API_KEY,
            api_version=config.provider.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.provider.AZURE_OPENAI_ENDPOINT
        )


class DeepSeekCredentialStrategy(CredentialStrategy):
    """Credential strategy for the DeepSeek API (async via OpenAI compatibility)."""

    def validate_credentials(self) -> bool:
        missing = []
        if not config.provider.DEEPSEEK_API_KEY:
            missing.append("DEEPSEEK_API_KEY")
        if not config.provider.DEEPSEEK_BASE_URL:
            missing.append("DEEPSEEK_BASE_URL")

        if missing:
            logger.error(f"[DeepSeekCredentialStrategy] Missing settings: {', '.join(missing)}")
            return False
        return True

    def get_client(self) -> Any:
        """Instantiate and return an `AsyncOpenAI` client pointing at DeepSeek."""
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            base_url=config.provider.DEEPSEEK_BASE_URL,
            api_key=config.provider.DEEPSEEK_API_KEY,
            default_headers={
                "X-Deepseek-Version": config.provider.DEEPSEEK_API_VERSION
            }
        )


class QwenCredentialStrategy(CredentialStrategy):
    """Credential strategy for the Qwen-compatible API (async via OpenAI compatibility)."""

    def validate_credentials(self) -> bool:
        missing = []
        if not config.provider.QWEN_API_KEY:
            missing.append("QWEN_API_KEY")
        if not config.provider.QWEN_BASE_URL:
            missing.append("QWEN_BASE_URL")

        if missing:
            logger.error(f"[QwenCredentialStrategy] Missing settings: {', '.join(missing)}")
            return False
        return True

    def get_client(self) -> Any:
        """Instantiate and return an `AsyncOpenAI` client pointing at Qwen."""
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            base_url=config.provider.QWEN_BASE_URL,
            api_key=config.provider.QWEN_API_KEY,
            default_headers={
                "X-DashScope-Version": config.provider.QWEN_API_VERSION
            }
        )


class GitHubAzureInferenceStrategy(CredentialStrategy):
    """Credential strategy for GitHub Azure Inference (Azure AI, async)."""

    def validate_credentials(self) -> bool:
        if not config.provider.GITHUB_TOKEN:
            logger.error("[GitHubAzureInferenceStrategy] GITHUB_TOKEN missing")
            return False
        return True

    def get_client(self) -> Any:
        """
        Instantiate and return an async Azure AI client:
        Uses the aio flavor of the SDK so calls can be awaited.
        """
        from azure.ai.inference.aio import ChatCompletionsClient
        from azure.core.credentials import AzureKeyCredential
        return ChatCompletionsClient(
            endpoint=config.provider.GITHUB_AZURE_INFERENCE_ENDPOINT,
            credential=AzureKeyCredential(config.provider.GITHUB_TOKEN)
        )


class CredentialManager:
    """Factory for selecting and executing a credential strategy to build an AI client."""

    _STRATEGY_MAP = {
        'openai': OpenAICredentialStrategy,
        'azure': AzureOpenAICredentialStrategy,
        'deepseek': DeepSeekCredentialStrategy,
        'qwen': QwenCredentialStrategy,
        'github_models': GitHubAzureInferenceStrategy
    }

    def __init__(self):
        cred_type = config.general.CREDENTIAL_TYPE.lower()
        if cred_type not in self._STRATEGY_MAP:
            raise ValueError(f"[CredentialManager] Unsupported CREDENTIAL_TYPE: '{cred_type}'")

        self.strategy = self._STRATEGY_MAP[cred_type]()
        if not self.strategy.validate_credentials():
            raise ValueError(
                f"[CredentialManager] Missing required credentials for provider '{config.general.CREDENTIAL_TYPE}'"
            )

        self.client = self.strategy.get_client()
        logger.info(f"[CredentialManager] Initialized client for provider '{config.general.CREDENTIAL_TYPE}'")

    def get_client(self) -> Any:
        """Return the configured AI client."""
        return self.client


def get_client() -> Any:
    """Synchronous entrypoint (returns an async-capable client)."""
    manager = CredentialManager()
    return manager.get_client()


async def get_client_async() -> Any:
    """Asynchronous entrypoint to obtain the configured AI client."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_client)
