---
title: Installation
---

# Installation

## Requirements

- Python 3.11 or higher
- An API key for at least one AI provider

## Install with pip

```bash
pip install noxaudit
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install noxaudit
```

## Optional Extras

Noxaudit supports multiple AI providers. Install the extras for the providers you want to use:

```bash tab="Anthropic (default)"
pip install noxaudit
```

```bash tab="OpenAI"
pip install 'noxaudit[openai]'
```

```bash tab="Google Gemini"
pip install 'noxaudit[google]'
```

```bash tab="MCP Server"
pip install 'noxaudit[mcp]'
```

```bash tab="All providers"
pip install 'noxaudit[openai,google,mcp]'
```

## API Key Setup

Set the API key for your chosen provider as an environment variable:

```bash
# Anthropic (default)
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# Google Gemini
export GOOGLE_API_KEY=...
```

> [!TIP]
> Add your API key to a `.env` file in your project root and load it with `export $(grep -v '^#' .env | xargs)`. Make sure `.env` is in your `.gitignore`.

## Verify Installation

```bash
noxaudit --version
noxaudit --help
```

## Next Steps

- [Quick Start](/docs/getting-started/quickstart) — run your first audit in under a minute
- [Configuration](/docs/guides/configuration) — set up `noxaudit.yml` for your project
