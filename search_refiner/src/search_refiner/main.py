"""
Search Context Refiner - 2-Agent FlatAgent Workflow

Demonstrates:
1. Running Exa web search via MCP tools
2. Orchestrating multiple FlatAgents in sequence
3. Passing results between agents
4. Token-constrained output refinement

Workflow:
1. Search Agent: Searches the web via Exa MCP
2. Refiner Agent: Refines results to <= 500 tokens based on relevance
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from flatagents import FlatAgent, AgentResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AISuiteMCPProvider:
    """
    MCPToolProvider implementation using aisuite's MCPClient.

    Handles connection to MCP servers and tool execution.
    """

    def __init__(self):
        self._clients: Dict[str, Any] = {}

    def connect(self, server_name: str, config: Dict[str, Any]) -> None:
        """Connect to an MCP server."""
        if server_name in self._clients:
            return  # Already connected

        from aisuite.mcp import MCPClient

        # Expand environment variables in config
        expanded_config = self._expand_env_vars(config)

        # Build MCPClient config
        if 'command' in expanded_config:
            # Stdio transport
            client = MCPClient(
                command=expanded_config['command'],
                args=expanded_config.get('args', []),
                env=expanded_config.get('env'),
                name=server_name
            )
        elif 'server_url' in expanded_config:
            # HTTP transport
            client = MCPClient(
                server_url=expanded_config['server_url'],
                headers=expanded_config.get('headers'),
                timeout=expanded_config.get('timeout', 30.0),
                name=server_name
            )
        else:
            raise ValueError(f"Invalid MCP config for {server_name}: need 'command' or 'server_url'")

        self._clients[server_name] = client
        logger.info(f"Connected to MCP server: {server_name}")

    def _expand_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Expand ${VAR} patterns in config values."""
        result = {}
        for key, value in config.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                result[key] = os.environ.get(env_var, '')
            elif isinstance(value, dict):
                result[key] = self._expand_env_vars(value)
            elif isinstance(value, list):
                result[key] = [
                    os.environ.get(v[2:-1], '') if isinstance(v, str) and v.startswith('${') else v
                    for v in value
                ]
            else:
                result[key] = value
        return result

    def get_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """Get available tools from an MCP server."""
        if server_name not in self._clients:
            raise RuntimeError(f"Not connected to server: {server_name}")
        return self._clients[server_name].list_tools()

    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool call."""
        if server_name not in self._clients:
            raise RuntimeError(f"Not connected to server: {server_name}")
        return self._clients[server_name].call_tool(tool_name, arguments)

    def close(self) -> None:
        """Close all MCP connections."""
        for name, client in self._clients.items():
            try:
                client.close()
                logger.info(f"Closed MCP server: {name}")
            except Exception as e:
                logger.warning(f"Error closing {name}: {e}")
        self._clients.clear()


async def run_search_agent(
    search_agent: FlatAgent,
    provider: AISuiteMCPProvider,
    query: str
) -> str:
    """
    Run the search agent with tool orchestration.

    The search agent will execute web searches via Exa MCP and return results.
    """
    logger.info(f"Starting search agent for query: {query}")

    # Start with user message
    messages = [{"role": "user", "content": f"Search for: {query}"}]
    max_iterations = 5

    for i in range(max_iterations):
        result: AgentResponse = await search_agent.call(
            tool_provider=provider,
            messages=messages
        )

        # If no tool calls, we're done
        if not result.tool_calls:
            logger.info("Search agent completed (no tool calls)")
            return result.content or ""

        # Process tool calls
        logger.info(f"Iteration {i + 1}: {len(result.tool_calls)} tool call(s)")

        # Add assistant message with tool calls to history
        import json
        assistant_msg = {
            "role": "assistant",
            "content": result.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.tool,
                        "arguments": json.dumps(tc.arguments)
                    }
                }
                for tc in result.tool_calls
            ]
        }
        messages.append(assistant_msg)

        # Execute each tool call
        for tc in result.tool_calls:
            logger.info(f"Calling {tc.server}:{tc.tool}")

            try:
                tool_result = provider.call_tool(tc.server, tc.tool, tc.arguments)
                # Truncate display
                display = str(tool_result)[:150] + "..." if len(str(tool_result)) > 150 else str(tool_result)
                logger.info(f"Tool result: {display}")
            except Exception as e:
                tool_result = f"Error: {e}"
                logger.error(f"Tool error: {e}")

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(tool_result)
            })

    return result.content or "Max iterations reached"


async def run_refiner_agent(
    refiner_agent: FlatAgent,
    query: str,
    search_results: str
) -> str:
    """
    Run the refiner agent to condense search results.

    Takes the raw search results and refines them down to max 500 tokens.
    """
    logger.info("Starting refiner agent")

    result: AgentResponse = await refiner_agent.call(
        query=query,
        search_results=search_results
    )

    logger.info("Refiner agent completed")
    return result.content or ""


async def run(query: str):
    """Main function to run the search refiner demo."""
    print("=== Search Context Refiner ===\n")

    # Check for API keys
    if not os.environ.get("EXA_API_KEY"):
        print("ERROR: EXA_API_KEY environment variable not set")
        print("   Get an API key at https://exa.ai")
        return

    if not os.environ.get("CEREBRAS_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: No LLM API key found (CEREBRAS_API_KEY, OPENAI_API_KEY).")
        return

    # Load agent configs
    config_dir = Path(__file__).parent.parent.parent / 'config'
    search_agent = FlatAgent(config_file=str(config_dir / 'search.yml'))
    refiner_agent = FlatAgent(config_file=str(config_dir / 'refiner.yml'))

    print(f"Search Agent: {search_agent.agent_name}")
    print(f"Refiner Agent: {refiner_agent.agent_name}")
    print(f"Model: {search_agent.model}\n")

    # Create MCP provider
    provider = AISuiteMCPProvider()

    try:
        print(f"Query: {query}\n")

        # Step 1: Run search agent
        print("--- Step 1: Web Search ---")
        search_results = await run_search_agent(search_agent, provider, query)

        print("\n--- Raw Search Results ---")
        # Truncate for display
        display_results = search_results[:500] + "..." if len(search_results) > 500 else search_results
        print(display_results)

        # Step 2: Run refiner agent
        print("\n--- Step 2: Refining Results ---")
        refined_results = await run_refiner_agent(refiner_agent, query, search_results)

        print("\n--- Refined Results (≤500 tokens) ---")
        print(refined_results)

        # Statistics
        print("\n--- Execution Statistics ---")
        total_cost = search_agent.total_cost + refiner_agent.total_cost
        total_calls = search_agent.total_api_calls + refiner_agent.total_api_calls
        print(f"Total Cost: ${total_cost:.4f}")
        print(f"Total API Calls: {total_calls}")
        print(f"Search Agent Cost: ${search_agent.total_cost:.4f} ({search_agent.total_api_calls} calls)")
        print(f"Refiner Agent Cost: ${refiner_agent.total_cost:.4f} ({refiner_agent.total_api_calls} calls)")

    finally:
        provider.close()


def main():
    """Synchronous entry point."""
    import sys
    if len(sys.argv) < 2:
        print("Usage: search-refiner <query>")
        print("Example: search-refiner 'latest AI agent developments'")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    asyncio.run(run(query))


if __name__ == "__main__":
    main()
