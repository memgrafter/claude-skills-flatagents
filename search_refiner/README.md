# Search Context Refiner

A 2-agent FlatAgent workflow that demonstrates web search orchestration and intelligent content refinement.

## Overview

This example shows how to:

1. **Chain multiple FlatAgents together** - Run agents sequentially and pass results between them
2. **Integrate MCP tools** - Use Exa MCP server for web search capabilities
3. **Refine context** - Intelligently summarize large search results into a token-limited context window
4. **Manage costs** - Track execution metrics across multi-agent workflows

## Architecture

### Agent 1: Search Agent
- **Purpose**: Perform web searches via Exa
- **Input**: User query
- **Output**: Raw search results with sources
- **Tools**: Exa web search via MCP

### Agent 2: Refiner Agent
- **Purpose**: Condense search results to most relevant information
- **Input**: Original query + raw search results
- **Output**: Refined results (≤500 tokens)
- **Constraint**: Must stay within 500 token limit

## Requirements

- Python 3.8+
- `CEREBRAS_API_KEY` or `OPENAI_API_KEY` for LLM calls
- `EXA_API_KEY` for web search access

## Installation

```bash
# From the flatagents repo root
cd sdk/python/examples/search_refiner

# Install in development mode
pip install -e .
```

## Usage

### Command Line

```bash
search-refiner
```

Or directly:

```bash
python -m search_refiner.main
```

### Python Script

```python
import asyncio
from search_refiner.main import run

asyncio.run(run())
```

## Configuration

Both agents use Cerebras + zai-glm-4.6 model (configurable in YAML):

- **search.yml**: Web search agent configuration
- **refiner.yml**: Content refinement agent configuration

Modify `config/search.yml` and `config/refiner.yml` to adjust:
- Temperature (creativity vs. consistency)
- Max tokens
- System prompts
- Input templates

## Example Output

```
=== Search Context Refiner ===

Query: latest developments in AI agents December 2024

--- Step 1: Web Search ---
Iteration 1: 1 tool call(s)
Calling exa:web_search_exa
Tool result: Found 15 relevant articles...

--- Raw Search Results ---
[Raw results from Exa search...]

--- Step 2: Refining Results ---

--- Refined Results (≤500 tokens) ---
Key findings:
1. Major advancement in multi-agent systems...
2. New benchmarks released for agent evaluation...
3. Industry adoption increasing...

Supporting details:
[Concise summary of findings with sources]

--- Execution Statistics ---
Total Cost: $0.0042
Total API Calls: 2
Search Agent Cost: $0.0035 (1 calls)
Refiner Agent Cost: $0.0007 (1 calls)
```

## Key Concepts

### Multi-Agent Orchestration
The workflow demonstrates explicit agent composition:
1. Load both agent configs
2. Run search agent with MCP tool provider
3. Extract search results
4. Run refiner agent with those results
5. Return refined output

### MCP Tool Integration
- Exa MCP server provides web search
- MCPToolProvider handles tool discovery and execution
- Tool calls are executed in an orchestration loop

### Token Management
The refiner agent:
- Receives original query for context
- Takes raw search results as input
- Constrains output to 500 tokens max
- Prioritizes relevance to original query

## Extending the Demo

Try these modifications:

1. **Add more agents**: Create a third agent for fact-checking
2. **Tool discovery**: Print available tools before running agents
3. **Iterative refinement**: Run refiner multiple times with feedback
4. **Different queries**: Test with various search topics
5. **Cost optimization**: Compare temperatures and model choices

## Files

- `config/search.yml` - Search agent configuration
- `config/refiner.yml` - Refiner agent configuration
- `src/search_refiner/main.py` - Main orchestration logic
- `pyproject.toml` - Package configuration

## See Also

- [MCP Exa Example](../mcp_exa/) - Detailed MCP tool integration
- [HelloWorld Example](../helloworld/) - Simple agent loop example
- [Writer-Critic Example](../writer_critic/) - Iterative refinement pattern
