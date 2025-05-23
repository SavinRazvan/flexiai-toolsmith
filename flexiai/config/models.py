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
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_API_VERSION: str = Field("2023-11-22", env="OPENAI_API_VERSION")
    OPENAI_ORGANIZATION_ID: Optional[str] = Field(None, env="OPENAI_ORGANIZATION_ID")
    OPENAI_PROJECT_ID: Optional[str] = Field(None, env="OPENAI_PROJECT_ID")
    OPENAI_ASSISTANT_VERSION: str = Field("v2", env="OPENAI_ASSISTANT_VERSION")

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
    AZURE_OPENAI_API_KEY: str = Field(..., env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str = Field("2024-05-01-preview", env="AZURE_OPENAI_API_VERSION")

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
    DEEPSEEK_API_KEY: str = Field(..., env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field("https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")
    DEEPSEEK_API_VERSION: str = Field("2023-11-22", env="DEEPSEEK_API_VERSION")

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
    QWEN_API_KEY: str = Field(..., env="QWEN_API_KEY")
    QWEN_BASE_URL: str = Field(
        "https://dashscope.aliyuncs.com/compatible-mode/v1", env="QWEN_BASE_URL"
    )
    QWEN_API_VERSION: str = Field("2023-11-22", env="QWEN_API_VERSION")

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
    GITHUB_TOKEN: str = Field(..., env="GITHUB_TOKEN")
    GITHUB_AZURE_INFERENCE_ENDPOINT: str = Field(
        "https://models.inference.ai.azure.com", env="GITHUB_AZURE_INFERENCE_ENDPOINT"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


class GeneralSettings(BaseSettings):
    """General application settings.

    Attributes:
        CREDENTIAL_TYPE (str): Which AI provider to use ('openai', 'azure', etc.).
        USER_PROJECT_ROOT_DIR (str): Root directory of the user's project.
        ACTIVE_CHANNELS (str): Comma-separated list of channels to enable (e.g., 'cli,quart').
    """
    CREDENTIAL_TYPE: str = Field("openai", env="CREDENTIAL_TYPE")
    USER_PROJECT_ROOT_DIR: str = Field("", env="USER_PROJECT_ROOT_DIR")
    ACTIVE_CHANNELS: str = Field("cli", env="ACTIVE_CHANNELS")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )
