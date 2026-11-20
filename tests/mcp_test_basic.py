import asyncio, sys, os, json
import anyio

from mcp import Client, ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_demo.mcp_client import server_params

# Reference for the code: 
# https://py.sdk.modelcontextprotocol.io/client/#whats-on-a-connected-client

# Deprecated
"""
# Note that StdioServerParameters can take either an actual URL or a command to run a local server script
# URL if transport layer is over HTTP/HTTPS and MCP server is running as a web service
# Example: mcp_server_params = StdioServerParameters(command="http://localhost:8000")
mcp_server_params = StdioServerParameters(command="uv", args=["run", "mcp_server.py"])
# Command if running a local server script
# Example: mcp_server_params = StdioServerParameters(command="uv", args=["run", "mcp_server.py"]) AKA "uv run mcp_server.py"
"""

# Simple test that runs a single tool call against the MCP server and backend server API (get_all_horses())
# Usage in terminal:
# uv run mcp_test_basic.py mcp_server.py
async def main() -> None:

    async with Client(server_params(sys.argv[1])) as client:

        # "get_horse_data" is content.name, and the dict is content.input containing the expected tool call arguments
        result = await client.call_tool("get_all_horses", {})
        #print(result)

        print(result.model_dump_json())

        #print(client.server_info)
        #print(client.server_capabilities)
        #print(client.protocol_version)
        #print(client.instructions)


if __name__ == "__main__":
    anyio.run(main)