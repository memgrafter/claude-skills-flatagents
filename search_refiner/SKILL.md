---
name: search-refiner
description: Search the web and refine results to key findings. Use when the user asks to search and summarize, find and refine web results, or wants concise research summaries.
---

# Search Refiner

A 2-agent FlatAgent workflow using Cerebras + Exa MCP that searches the web and refines results to key findings.

## Usage

```bash
/Users/trentrobbins/code/claude-skills-flatagents/search_refiner/run.sh "your query"
```

## Setup

- **Auto setup**: First run automatically creates a virtualenv in `.claude/skills/search-refiner/.venv` and installs dependencies
- **Auto update**: Reinstalls automatically when `pyproject.toml` changes
- **Force reinstall**: `run.sh --setup` to manually trigger setup

Uses `uv` if available (faster), falls back to `pip` otherwise.

## Requirements

- `CEREBRAS_API_KEY` or `OPENAI_API_KEY` environment variable
- `EXA_API_KEY` environment variable
- Python 3.10+

## Workflow

1. **search-agent**: Uses Cerebras model with Exa web search tool
2. **refiner-agent**: Condenses results to ~500 tokens of key findings

## Output Format

- **Key findings** (2-3 points)
- **Supporting details**
- **Sources**
