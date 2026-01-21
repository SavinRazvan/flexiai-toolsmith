# FILE: flexiai/config/models.py

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class OpenAISettings(BaseSettings):
    """Settings for OpenAI provider.

    Attributes:
        OPENAI_API_KEY (str): API key for OpenAI.
        OPENAI_API_VERSION (str): OpenAI API version.
        OPENAI_ORGANIZATION_ID (Optional[str]): Organization ID for billing/accounting.
        OPENAI_PROJECT_ID (Optional[str]): Project ID for assistant grouping.
        OPENAI_ASSISTANT_VERSION (str): Assistant version header for OpenAI Beta.
    """
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")  # type: ignore
    OPENAI_API_VERSION: str = Field(default="2023-11-22", env="OPENAI_API_VERSION")  # type: ignore
    OPENAI_ORGANIZATION_ID: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION_ID")  # type: ignore
    OPENAI_PROJECT_ID: Optional[str] = Field(default=None, env="OPENAI_PROJECT_ID")  # type: ignore
    OPENAI_ASSISTANT_VERSION: str = Field(default="v2", env="OPENAI_ASSISTANT_VERSION")  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


class AzureOpenAISettings(BaseSettings):
    """Settings for Azure OpenAI provider.

    Attributes:
        AZURE_OPENAI_API_KEY (str): API key for Azure OpenAI.
        AZURE_OPENAI_ENDPOINT (str): Endpoint URL for Azure OpenAI.
        AZURE_OPENAI_API_VERSION (str): Azure OpenAI API version.
    """
    AZURE_OPENAI_API_KEY: str = Field(env="AZURE_OPENAI_API_KEY")  # type: ignore
    AZURE_OPENAI_ENDPOINT: str = Field(env="AZURE_OPENAI_ENDPOINT")  # type: ignore
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-05-01-preview", env="AZURE_OPENAI_API_VERSION")  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


class DeepSeekSettings(BaseSettings):
    """Settings for DeepSeek API provider.

    Attributes:
        DEEPSEEK_API_KEY (str): API key for DeepSeek.
        DEEPSEEK_BASE_URL (str): Base URL for DeepSeek API.
        DEEPSEEK_API_VERSION (str): API version for DeepSeek.
    """
    DEEPSEEK_API_KEY: str = Field(env="DEEPSEEK_API_KEY")  # type: ignore
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")  # type: ignore
    DEEPSEEK_API_VERSION: str = Field(default="2023-11-22", env="DEEPSEEK_API_VERSION")  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


class QwenSettings(BaseSettings):
    """Settings for Qwen-compatible API provider.

    Attributes:
        QWEN_API_KEY (str): API key for Qwen.
        QWEN_BASE_URL (str): Base URL for Qwen API.
        QWEN_API_VERSION (str): API version for Qwen.
    """
    QWEN_API_KEY: str = Field(env="QWEN_API_KEY")  # type: ignore
    QWEN_BASE_URL: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1", env="QWEN_BASE_URL"
    )  # type: ignore
    QWEN_API_VERSION: str = Field(default="2023-11-22", env="QWEN_API_VERSION")  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


class GitHubAzureInferenceSettings(BaseSettings):
    """Settings for GitHub Azure Inference (Azure AI) provider.

    Attributes:
        GITHUB_TOKEN (str): Personal access token for GitHub/Azure inference.
        GITHUB_AZURE_INFERENCE_ENDPOINT (str): Endpoint URL for the inference service.
    """
    GITHUB_TOKEN: str = Field(env="GITHUB_TOKEN")  # type: ignore
    GITHUB_AZURE_INFERENCE_ENDPOINT: str = Field(
        default="https://models.inference.ai.azure.com", env="GITHUB_AZURE_INFERENCE_ENDPOINT"
    )  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


class GeneralSettings(BaseSettings):
    """General application settings."""

    CREDENTIAL_TYPE: str = Field(default="openai", env="CREDENTIAL_TYPE")  # type: ignore
    USER_PROJECT_ROOT_DIR: str = Field(default="", env="USER_PROJECT_ROOT_DIR")  # type: ignore
    ACTIVE_CHANNELS: str = Field(default="cli", env="ACTIVE_CHANNELS")  # type: ignore

    # always required
    ASSISTANT_ID: str = Field(env="ASSISTANT_ID")  # type: ignore
    USER_ID: str = Field(env="USER_ID")  # type: ignore

    # optional with defaults
    ASSISTANT_NAME: str = Field(default="Assistant", env="ASSISTANT_NAME")  # type: ignore
    USER_NAME: str = Field(default="User", env="USER_NAME")  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )
