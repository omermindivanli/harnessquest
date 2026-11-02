# Provider Guides

Complete setup and usage guides for each supported LLM provider.

## Quick Comparison

| Provider | Cost | Privacy | Speed | Best For | Setup Difficulty |
|----------|------|---------|-------|----------|------------------|
| **Ollama** | Free | 🔒 Local | Medium | Learning, privacy, offline | Easy |
| **OpenAI** | Pay-per-token | ☁️ Cloud | Fast | Production, best models | Easy |
| **Anthropic** | Pay-per-token | ☁️ Cloud | Fast | Coding, reasoning | Easy |
| **NVIDIA NIM** | Pay-per-token | ☁️ Cloud | Fast (GPU) | Enterprise, specialized | Medium |
| **LiteLLM** | Varies | Varies | Varies | 100+ providers, fallback | Medium |

---

## Ollama (Local LLMs) — Recommended for Learning

### Why Ollama?
- **Free** — No API costs
- **Private** — Data never leaves your machine
- **Offline** — Works without internet
- **Educational** — Learn harness engineering without cloud dependencies

### Installation

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com
```

### Start Server & Pull Models

```bash
# Start server (run in background)
ollama serve

# Pull recommended models for HarnessQuest
ollama pull llama3.1:8b       # Fast, good quality (4.7GB)
ollama pull llama3.1:70b      # High quality (40GB) - needs 48GB+ RAM
ollama pull nemotron3:ultra   # NVIDIA's reasoning model
ollama pull codellama:13b     # Code-specialized
ollama pull deepseek-coder:33b # Code-specialized
```

### Configuration

```bash
# Optional: Customize in .env
OLLAMA_BASE_URL=http://localhost:11434
```

### Usage

```bash
# List available models
harnessquest --list-models --provider ollama

# Run quest with Ollama
harnessquest-quest 1 --provider ollama --model llama3.1:8b

# Direct CLI
harnessquest --prompt "List files" --provider ollama --model llama3.1:8b
```

### Model Recommendations by Quest Level

| Level | Recommended Model | Reason |
|-------|-------------------|--------|
| 1-5 | `llama3.1:8b` | Fast, sufficient for basics |
| 6-10 | `llama3.1:8b` or `nemotron3:ultra` | Better reasoning |
| 11-15 | `nemotron3:ultra` or `codellama:13b` | Code + reasoning |
| 16-20 | `llama3.1:70b` (if RAM) | Maximum capability |

### Troubleshooting

**Server not responding:**
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
pkill ollama && ollama serve
```

**Out of memory:**
```bash
# Use smaller model
ollama pull llama3.1:8b  # instead of 70b

# Or increase swap
sudo fallocate -l 16G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

**Model not found:**
```bash
harnessquest --list-models --provider ollama
# If empty, refresh:
python -c "from harnessquest.core.providers import get_provider, get_settings; p = get_provider('ollama', get_settings()); print(p.refresh_models())"
```

---

## OpenAI

### Setup

```bash
# 1. Get API key: https://platform.openai.com/api-keys
# 2. Add to .env
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Models

| Model | Context | Best For | Cost (per 1M tokens) |
|-------|---------|----------|---------------------|
| `gpt-4o` | 128K | Flagship reasoning | $5/$15 |
| `gpt-4o-mini` | 128K | Fast, cost-effective | $0.15/$0.60 |
| `gpt-4-turbo` | 128K | Previous gen | $10/$30 |
| `o1-preview` | 128K | Reasoning (no tools) | $15/$60 |
| `o1-mini` | 128K | Fast reasoning (no tools) | $3/$12 |

### Usage

```bash
harnessquest-quest 1 --provider openai --model gpt-4o-mini
harnessquest --prompt "Write a Python script" --provider openai --model gpt-4o
```

### Tips
- Use `gpt-4o-mini` for learning (cheap, fast)
- `o1-preview`/`o1-mini` don't support tools — use for reasoning-only tasks
- Set spending limits in OpenAI dashboard

---

## Anthropic

### Setup

```bash
# 1. Get API key: https://console.anthropic.com/
# 2. Add to .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### Models

| Model | Context | Best For | Cost (per 1M tokens) |
|-------|---------|----------|---------------------|
| `claude-3-5-sonnet-20241022` | 200K | Best for coding | $3/$15 |
| `claude-3-5-haiku-20241022` | 200K | Fast, efficient | $0.25/$1.25 |
| `claude-3-opus-20240229` | 200K | Most capable | $15/$75 |

### Usage

```bash
harnessquest-quest 1 --provider anthropic --model claude-3-5-haiku-20241022
harnessquest --prompt "Debug this code" --provider anthropic --model claude-3-5-sonnet-20241022
```

### Tips
- `claude-3-5-haiku` is excellent for learning (fast, cheap)
- `claude-3-5-sonnet` is best for complex coding tasks
- 200K context window great for large repos

---

## NVIDIA NIM

### Setup

```bash
# 1. Get API key: https://build.nvidia.com
# 2. Add to .env
echo "NVIDIA_API_KEY=nvapi-your-key-here" > .env
echo "NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1" >> .env
```

### Models

| Model | Context | Best For |
|-------|---------|----------|
| `nvidia/nemotron-3-ultra` | 128K | NVIDIA flagship reasoning |
| `nvidia/nemotron-4-340b` | 128K | Large reasoning |
| `meta/llama-3.1-405b-instruct` | 128K | Meta's largest |
| `meta/llama-3.1-70b-instruct` | 128K | Balanced |
| `meta/llama-3.1-8b-instruct` | 128K | Fast, efficient |
| `mistralai/mistral-large` | 128K | Mistral flagship |
| `mistralai/mixtral-8x22b` | 65K | MoE model |

### Usage

```bash
harnessquest-quest 1 --provider nim --model meta/llama-3.1-70b-instruct
harnessquest-quest 11 --provider nim --model nvidia/nemotron-3-ultra
```

### Tips
- Enterprise-grade: SLA, compliance, GPU-optimized
- OpenAI-compatible API
- Great for production deployments
- Nemotron 3 Ultra excels at reasoning tasks

---

## LiteLLM (Unified Gateway)

### Setup

```bash
# Option 1: Use provider-specific keys (already configured above)
# LiteLLM will route to the right provider based on model prefix

# Option 2: Run LiteLLM Proxy for unified access
docker run -d -p 4000:4000 ghcr.io/berriai/litellm:main-latest

# Then configure:
echo "LITELLM_BASE_URL=http://localhost:4000" >> .env
echo "LITELLM_MASTER_KEY=sk-your-master-key" >> .env
```

### Usage

```bash
# LiteLLM auto-routes based on model prefix
harnessquest --prompt "Test" --provider litellm --model gpt-4o-mini
harnessquest --prompt "Test" --provider litellm --model claude-3-5-haiku-20241022
harnessquest --prompt "Test" --provider litellm --model ollama/llama3.1:8b
```

### Supported Providers (100+)
- OpenAI, Anthropic, Azure, AWS Bedrock, Google Vertex
- HuggingFace, Replicate, Together, Anyscale
- Ollama, LM Studio, LocalAI
- And many more...

See: https://docs.litellm.ai/docs/providers

---

## Multi-Provider Strategies

### Fallback Routing (Level 9 Quest)

```python
async def run_with_fallback(prompt, providers=["openai", "anthropic", "ollama"]):
    for provider_name in providers:
        try:
            provider = get_provider(provider_name)
            runner = HarnessRunner(provider=provider_name, model=provider.get_default_model())
            result = await runner.run(prompt)
            if result["status"] == "success":
                return result
        except Exception as e:
            print(f"{provider_name} failed: {e}, trying next...")
    raise Exception("All providers failed")
```

### Cost Optimization

```python
# Route simple tasks to cheap models, complex to capable
def select_model(task_complexity: str):
    if task_complexity == "simple":
        return ("ollama", "llama3.1:8b")      # Free
    elif task_complexity == "medium":
        return ("openai", "gpt-4o-mini")      # $0.15/1M
    else:
        return ("anthropic", "claude-3.5-sonnet")  # Best coding
```

### Privacy-First (Local Only)

```python
# Force local-only for sensitive data
runner = HarnessRunner(
    provider="ollama",
    model="llama3.1:8b",
    # No cloud API calls possible
)
```

---

## Environment Variables Reference

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# NVIDIA NIM
NVIDIA_API_KEY=nvapi-...
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# LiteLLM Proxy
LITELLM_BASE_URL=http://localhost:4000
LITELLM_MASTER_KEY=sk-...

# Application
DEFAULT_PROVIDER=litellm
DEFAULT_MODEL=gpt-4o-mini
MAX_TURNS=10
DEFAULT_TEMPERATURE=0.1
```

---

## Next Steps

1. **Start with Ollama** — Free, private, great for learning
2. **Try each provider** — Compare outputs on same quest
3. **Build fallback logic** — Level 9 teaches multi-provider orchestration
4. **Optimize for cost/privacy** — Route based on task requirements