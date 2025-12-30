import asyncio
import json
import os
import sys
from pathlib import Path

from flatagents import FlatAgent, AgentResponse


class MCPProvider:
    """Connects to MCP servers and executes tool calls."""

    def __init__(self):
        self._clients = {}

    def connect(self, server_name: str, config: dict):
        if server_name in self._clients:
            return

        from aisuite.mcp import MCPClient

        # Expand ${VAR} env references in config
        config = {
            k: os.environ.get(v[2:-1], '') if isinstance(v, str) and v.startswith('${') else v
            for k, v in config.items()
        }

        if 'command' in config:
            self._clients[server_name] = MCPClient(
                command=config['command'],
                args=config.get('args', []),
                env=config.get('env'),
                name=server_name
            )
        else:
            self._clients[server_name] = MCPClient(
                server_url=config['server_url'],
                name=server_name
            )

    def get_tools(self, server_name: str):
        return self._clients[server_name].list_tools()

    def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        return self._clients[server_name].call_tool(tool_name, arguments)

    def close(self):
        for client in self._clients.values():
            client.close()


async def search(agent: FlatAgent, provider: MCPProvider, query: str) -> str:
    """Run search agent with tool loop."""
    messages = [{"role": "user", "content": f"Search for: {query}"}]

    for _ in range(5):
        result: AgentResponse = await agent.call(tool_provider=provider, messages=messages)

        if not result.tool_calls:
            return result.content or ""

        # Add assistant message with tool calls
        messages.append({
            "role": "assistant",
            "content": result.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.tool, "arguments": json.dumps(tc.arguments)}
                }
                for tc in result.tool_calls
            ]
        })

        # Execute tool calls and add results
        for tc in result.tool_calls:
            try:
                tool_result = provider.call_tool(tc.server, tc.tool, tc.arguments)
            except Exception as e:
                tool_result = f"Error: {e}"

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(tool_result)
            })

    return result.content or ""


async def run(query: str):
    """Search web and refine results to key findings."""
    config_dir = Path(__file__).parent.parent.parent / 'config'
    search_agent = FlatAgent(config_file=str(config_dir / 'search.yml'))
    refiner_agent = FlatAgent(config_file=str(config_dir / 'refiner.yml'))

    provider = MCPProvider()

    try:
        search_results = await search(search_agent, provider, query)
        result: AgentResponse = await refiner_agent.call(query=query, search_results=search_results)
        print(result.content or "")
    finally:
        provider.close()


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "latest developments in AI agents"
    asyncio.run(run(query))
