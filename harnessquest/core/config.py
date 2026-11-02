"""Configuration management for HarnessQuest.

Uses Pydantic Settings for type-safe configuration loading from environment variables.
NEVER commits actual credentials - only .env.example template is committed.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # =========================================================================
    # LLM Provider API Keys
    # =========================================================================
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key from https://platform.openai.com/api-keys"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key from https://console.anthropic.com/"
    )
    nvidia_api_key: Optional[str] = Field(
        default=None,
        description="NVIDIA API key from https://build.nvidia.com (for NIM)"
    )
    nvidia_nim_base_url: Optional[str] = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="NVIDIA NIM API base URL"
    )
    ollama_base_url: Optional[str] = Field(
        default="http://localhost:11434",
        description="Ollama server base URL"
    )
    
    # =========================================================================
    # LiteLLM Configuration (for 100+ other providers)
    # =========================================================================
    litellm_master_key: Optional[str] = Field(
        default=None,
        description="LiteLLM master key for proxy mode"
    )
    litellm_base_url: Optional[str] = Field(
        default=None,
        description="LiteLLM proxy base URL"
    )
    
    # =========================================================================
    # Application Settings
    # =========================================================================
    default_provider: str = Field(
        default="litellm",
        description="Default LLM provider (openai, anthropic, nim, ollama, litellm)"
    )
    default_model: str = Field(
        default="gpt-4o-mini",
        description="Default model name"
    )
    max_turns: int = Field(
        default=10,
        description="Maximum turns per agent run"
    )
    default_temperature: float = Field(
        default=0.1,
        description="Default temperature for completions"
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout in seconds"
    )
    
    # =========================================================================
    # Gamification Settings
    # =========================================================================
    xp_storage_path: str = Field(
        default=".harnessquest_xp.json",
        description="Path to persistent XP storage"
    )
    enable_gamification: bool = Field(
        default=True,
        description="Enable gamification features"
    )
    
    # =========================================================================
    # Sandbox Settings
    # =========================================================================
    sandbox_workspace: str = Field(
        default=".",
        description="Sandbox workspace root directory"
    )
    command_timeout: int = Field(
        default=15,
        description="Command execution timeout in seconds"
    )
    
    # =========================================================================
    # Evaluation Settings
    # =========================================================================
    judge_model: str = Field(
        default="gpt-4o-mini",
        description="Model to use for LLM-as-judge evaluation"
    )
    judge_provider: str = Field(
        default="litellm",
        description="Provider for judge model"
    )
    
    # =========================================================================
    # Logging & Observability
    # =========================================================================
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    enable_telemetry: bool = Field(
        default=False,
        description="Enable OpenTelemetry tracing"
    )
    otel_endpoint: Optional[str] = Field(
        default=None,
        description="OpenTelemetry collector endpoint"
    )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings


def validate_provider_config(provider: str) -> tuple[bool, str]:
    """Validate that a provider has required configuration."""
    settings = get_settings()
    
    requirements = {
        "openai": ("openai_api_key", "OPENAI_API_KEY"),
        "anthropic": ("anthropic_api_key", "ANTHROPIC_API_KEY"),
        "nim": ("nvidia_api_key", "NVIDIA_API_KEY"),
        "ollama": (),  # No API key required
        "litellm": (),  # Uses provider-specific keys
    }
    
    if provider not in requirements:
        return False, f"Unknown provider: {provider}"
    
    for attr, env_var in requirements.get(provider, []):
        value = getattr(settings, attr, None)
        if not value:
            return False, f"{env_var} not set. Add to .env or environment variables."
    
    return True, f"{provider} configuration valid"


def get_provider_help(provider: str) -> str:
    """Get setup help for a specific provider."""
    help_texts = {
        "openai": """
OpenAI Setup:
1. Get API key: https://platform.openai.com/api-keys
2. Add to .env: OPENAI_API_KEY=sk-...
3. Models: gpt-4o, gpt-4o-mini, o1-preview, o1-mini
""",
        "anthropic": """
Anthropic Setup:
1. Get API key: https://console.anthropic.com/
2. Add to .env: ANTHROPIC_API_KEY=sk-ant-...
3. Models: claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022
""",
        "nim": """
NVIDIA NIM Setup:
1. Get API key: https://build.nvidia.com
2. Add to .env:
   NVIDIA_API_KEY=nvapi-...
   NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
3. Models: nemotron-3-ultra, llama-3.1-405b, mistral-large
""",
        "ollama": """
Ollama Setup (Local LLMs):
1. Install: https://ollama.com
2. Run server: ollama serve
3. Pull models: ollama pull llama3.1:8b
4. Optional .env: OLLAMA_BASE_URL=http://localhost:11434
5. Models: llama3.1:8b, llama3.1:70b, nemotron3:ultra, codellama:13b
""",
        "litellm": """
LiteLLM Setup (100+ Providers):
1. Uses provider-specific keys above
2. Or run LiteLLM proxy for unified access
3. See: https://docs.litellm.ai/docs/providers
""",
    }
    return help_texts.get(provider, "No help available for this provider.")