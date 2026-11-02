"""Provider abstraction layer for HarnessQuest.

Supports multiple LLM providers through a unified interface:
- OpenAI (via LiteLLM)
- Anthropic (via LiteLLM)
- NVIDIA NIM (NVIDIA Inference Microservices)
- Ollama (local LLMs)
- LiteLLM (unified gateway to 100+ providers)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional
import litellm
from litellm import acompletion

from harnessquest.core.config import Settings, get_settings


@dataclass
class ModelInfo:
    """Information about an available model."""
    id: str
    name: str
    provider: str
    context_window: int
    supports_streaming: bool = True
    supports_tools: bool = True
    description: str = ""


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""
    name: str
    api_key_env: str
    base_url_env: Optional[str] = None
    default_model: str = ""
    models: Optional[List[ModelInfo]] = None
    
    def __post_init__(self):
        if self.models is None:
            self.models = []


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: ProviderConfig, settings: Settings):
        self.config = config
        self.settings = settings
        self._api_key: Optional[str] = None
        self._base_url: Optional[str] = None
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier."""
        pass
    
    @property
    def api_key(self) -> Optional[str]:
        """Get API key from settings."""
        if self._api_key is None:
            self._api_key = getattr(self.settings, self.config.api_key_env.lower(), None)
        return self._api_key
    
    @property
    def base_url(self) -> Optional[str]:
        """Get base URL from settings."""
        if self._base_url is None and self.config.base_url_env:
            self._base_url = getattr(self.settings, self.config.base_url_env.lower(), None)
        return self._base_url
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        """Execute a completion request."""
        pass
    
    @abstractmethod
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ):
        """Execute a streaming completion request."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models for this provider."""
        pass
    
    @abstractmethod
    def validate_config(self) -> tuple[bool, str]:
        """Validate provider configuration. Returns (is_valid, error_message)."""
        pass
    
    def get_default_model(self) -> str:
        """Get default model for this provider."""
        return self.config.default_model


class LiteLLMProvider(LLMProvider):
    """LiteLLM unified provider - supports 100+ providers through one interface."""
    
    @property
    def provider_name(self) -> str:
        return "litellm"
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        """Execute completion via LiteLLM."""
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        # Set API key if available
        if self.api_key:
            litellm.api_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        return await acompletion(**params)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ):
        """Execute streaming completion via LiteLLM."""
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.api_key:
            litellm.api_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        # acompletion with stream=True returns an async iterator
        async for chunk in await acompletion(**params):
            yield chunk
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get models from LiteLLM's known model list."""
        # Return common models - in practice, users configure their own
        return [
            ModelInfo("gpt-4o", "GPT-4o", "openai", 128000, True, True, "OpenAI flagship model"),
            ModelInfo("gpt-4o-mini", "GPT-4o Mini", "openai", 128000, True, True, "Fast, cost-effective"),
            ModelInfo("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet", "anthropic", 200000, True, True, "Anthropic's best"),
            ModelInfo("claude-3-5-haiku-20241022", "Claude 3.5 Haiku", "anthropic", 200000, True, True, "Fast, efficient"),
        ]
    
    def validate_config(self) -> tuple[bool, str]:
        """LiteLLM always works as fallback."""
        return True, "LiteLLM provider ready (configure specific provider for best experience)"


class OpenAIProvider(LLMProvider):
    """OpenAI provider via LiteLLM."""
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        params = {
            "model": f"openai/{model}" if not model.startswith("openai/") else model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.api_key:
            litellm.openai_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        return await acompletion(**params)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ):
        """Execute streaming completion via LiteLLM."""
        params = {
            "model": f"openai/{model}" if not model.startswith("openai/") else model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.api_key:
            litellm.openai_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        async for chunk in await acompletion(**params):
            yield chunk
    
    def get_available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo("gpt-4o", "GPT-4o", "openai", 128000, True, True, "Flagship reasoning model"),
            ModelInfo("gpt-4o-mini", "GPT-4o Mini", "openai", 128000, True, True, "Fast, cost-effective"),
            ModelInfo("gpt-4-turbo", "GPT-4 Turbo", "openai", 128000, True, True, "Previous generation"),
            ModelInfo("o1-preview", "o1 Preview", "openai", 128000, True, False, "Reasoning model (no tools)"),
            ModelInfo("o1-mini", "o1 Mini", "openai", 128000, True, False, "Fast reasoning (no tools)"),
        ]
    
    def validate_config(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "OPENAI_API_KEY not set. Add to .env or environment."
        return True, "OpenAI provider configured"


class AnthropicProvider(LLMProvider):
    """Anthropic provider via LiteLLM."""
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        params = {
            "model": f"anthropic/{model}" if not model.startswith("anthropic/") else model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.api_key:
            litellm.anthropic_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        return await acompletion(**params)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ):
        """Execute streaming completion via LiteLLM."""
        params = {
            "model": f"anthropic/{model}" if not model.startswith("anthropic/") else model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.api_key:
            litellm.anthropic_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        async for chunk in await acompletion(**params):
            yield chunk
    
    def get_available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet", "anthropic", 200000, True, True, "Best for coding"),
            ModelInfo("claude-3-5-haiku-20241022", "Claude 3.5 Haiku", "anthropic", 200000, True, True, "Fast, efficient"),
            ModelInfo("claude-3-opus-20240229", "Claude 3 Opus", "anthropic", 200000, True, True, "Most capable"),
        ]
    
    def validate_config(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "ANTHROPIC_API_KEY not set. Add to .env or environment."
        return True, "Anthropic provider configured"


class NVIDIANIMProvider(LLMProvider):
    """NVIDIA NIM (Inference Microservices) provider."""
    
    @property
    def provider_name(self) -> str:
        return "nim"
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        # NIM uses OpenAI-compatible API
        params = {
            "model": f"openai/{model}" if not model.startswith("openai/") else model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        # NIM uses NVIDIA_API_KEY and custom base URL
        if self.api_key:
            litellm.openai_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        return await acompletion(**params)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ):
        """Execute streaming completion via LiteLLM."""
        params = {
            "model": f"openai/{model}" if not model.startswith("openai/") else model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.api_key:
            litellm.openai_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url
        
        async for chunk in await acompletion(**params):
            yield chunk
    
    def get_available_models(self) -> List[ModelInfo]:
        return [
            ModelInfo("nvidia/nemotron-3-ultra", "Nemotron 3 Ultra", "nim", 128000, True, True, "NVIDIA flagship"),
            ModelInfo("nvidia/nemotron-4-340b", "Nemotron 4 340B", "nim", 128000, True, True, "Large reasoning"),
            ModelInfo("meta/llama-3.1-405b-instruct", "Llama 3.1 405B", "nim", 128000, True, True, "Meta's largest"),
            ModelInfo("meta/llama-3.1-70b-instruct", "Llama 3.1 70B", "nim", 128000, True, True, "Balanced"),
            ModelInfo("meta/llama-3.1-8b-instruct", "Llama 3.1 8B", "nim", 128000, True, True, "Fast, efficient"),
            ModelInfo("mistralai/mistral-large", "Mistral Large", "nim", 128000, True, True, "Mistral flagship"),
            ModelInfo("mistralai/mixtral-8x22b", "Mixtral 8x22B", "nim", 65536, True, True, "MoE model"),
        ]
    
    def validate_config(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "NVIDIA_API_KEY not set. Get from https://build.nvidia.com"
        if not self.base_url:
            return False, "NVIDIA_NIM_BASE_URL not set (e.g., https://integrate.api.nvidia.com/v1)"
        return True, "NVIDIA NIM provider configured"


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: ProviderConfig, settings: Settings):
        super().__init__(config, settings)
        self._cached_models: Optional[List[ModelInfo]] = None
    
    @property
    def provider_name(self) -> str:
        return "ollama"
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        params = {
            "model": f"ollama/{model}" if not model.startswith("ollama/") else model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.base_url:
            litellm.api_base = self.base_url
        
        return await acompletion(**params)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ):
        """Execute streaming completion via LiteLLM."""
        params = {
            "model": f"ollama/{model}" if not model.startswith("ollama/") else model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        if self.base_url:
            litellm.api_base = self.base_url
        
        async for chunk in await acompletion(**params):
            yield chunk
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get models from local Ollama instance."""
        if self._cached_models:
            return self._cached_models
        
        # Default common models - will be refreshed by refresh_models()
        default_models = [
            ModelInfo("llama3.1:8b", "Llama 3.1 8B", "ollama", 128000, True, True, "Fast local model"),
            ModelInfo("llama3.1:70b", "Llama 3.1 70B", "ollama", 128000, True, True, "High quality local"),
            ModelInfo("nemotron3:ultra", "Nemotron 3 Ultra", "ollama", 128000, True, True, "NVIDIA model locally"),
            ModelInfo("qwen2.5:7b", "Qwen 2.5 7B", "ollama", 32768, True, True, "Multilingual"),
            ModelInfo("codellama:13b", "CodeLlama 13B", "ollama", 16384, True, True, "Code specialized"),
            ModelInfo("deepseek-coder:33b", "DeepSeek Coder 33B", "ollama", 16384, True, True, "Code specialized"),
        ]
        self._cached_models = default_models
        return default_models
    
    def refresh_models(self) -> List[ModelInfo]:
        """Refresh model list from local Ollama."""
        import subprocess
        try:
            result = subprocess.run(
                ["ollama", "list", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                import json
                models_data = json.loads(result.stdout)
                self._cached_models = [
                    ModelInfo(
                        id=m["name"],
                        name=m["name"],
                        provider="ollama",
                        context_window=128000,  # Default, varies by model
                        supports_streaming=True,
                        supports_tools=True,
                        description=f"Local model ({m.get('size', 'unknown size')})"
                    )
                    for m in models_data
                ]
        except Exception:
            pass  # Fall back to defaults
        return self._cached_models or self.get_available_models()
    
    def validate_config(self) -> tuple[bool, str]:
        import subprocess
        try:
            result = subprocess.run(
                ["ollama", "version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, "Ollama not installed. Install from https://ollama.com"
        except FileNotFoundError:
            return False, "Ollama not found in PATH. Install from https://ollama.com"
        
        # Check if Ollama server is running
        try:
            import requests
            base = self.base_url or "http://localhost:11434"
            resp = requests.get(f"{base}/api/tags", timeout=3)
            if resp.status_code != 200:
                return False, f"Ollama server not responding at {base}. Run 'ollama serve'"
        except Exception as e:
            return False, f"Cannot connect to Ollama: {e}"
        
        return True, "Ollama provider configured"


# Provider registry
PROVIDER_REGISTRY: Dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "nim": NVIDIANIMProvider,
    "ollama": OllamaProvider,
    "litellm": LiteLLMProvider,
}

PROVIDER_CONFIGS: Dict[str, ProviderConfig] = {
    "openai": ProviderConfig(
        name="OpenAI",
        api_key_env="OPENAI_API_KEY",
        default_model="gpt-4o-mini",
    ),
    "anthropic": ProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        default_model="claude-3-5-haiku-20241022",
    ),
    "nim": ProviderConfig(
        name="NVIDIA NIM",
        api_key_env="NVIDIA_API_KEY",
        base_url_env="NVIDIA_NIM_BASE_URL",
        default_model="meta/llama-3.1-70b-instruct",
    ),
    "ollama": ProviderConfig(
        name="Ollama (Local)",
        api_key_env="",  # No API key needed
        base_url_env="OLLAMA_BASE_URL",
        default_model="llama3.1:8b",
    ),
    "litellm": ProviderConfig(
        name="LiteLLM (Unified)",
        api_key_env="",  # Uses provider-specific keys
        default_model="gpt-4o-mini",
    ),
}


def get_provider(provider_name: str, settings: Optional[Settings] = None) -> LLMProvider:
    """Factory function to get a provider instance."""
    if settings is None:
        settings = get_settings()
    
    provider_name = provider_name.lower()
    if provider_name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDER_REGISTRY.keys())}")
    
    config = PROVIDER_CONFIGS[provider_name]
    provider_class = PROVIDER_REGISTRY[provider_name]
    return provider_class(config, settings)


def list_providers() -> Dict[str, Dict[str, Any]]:
    """List all available providers with their info."""
    return {
        name: {
            "name": config.name,
            "default_model": config.default_model,
            "requires_api_key": bool(config.api_key_env),
            "requires_base_url": bool(config.base_url_env),
            "api_key_env": config.api_key_env,
            "base_url_env": config.base_url_env,
        }
        for name, config in PROVIDER_CONFIGS.items()
    }


def get_all_models() -> Dict[str, List[ModelInfo]]:
    """Get all models grouped by provider."""
    settings = get_settings()
    result = {}
    for name, provider_class in PROVIDER_REGISTRY.items():
        config = PROVIDER_CONFIGS[name]
        provider = provider_class(config, settings)
        result[name] = provider.get_available_models()
    return result