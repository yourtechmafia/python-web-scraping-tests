"""List the tools ScrapingBee's MCP server offers (initialize + tools/list over HTTP)."""
import json
import os

import requests

URL = "https://mcp.scrapingbee.com/mcp"
H = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}", "Content-Type": "application/json",
     "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}


def call(method, params, i):
    r = requests.post(URL, headers=H, timeout=30, json={"jsonrpc": "2.0", "id": i, "method": method, "params": params})
    data = next(line[6:] for line in r.text.splitlines() if line.startswith("data: "))
    return json.loads(data)["result"]


info = call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0.1"}}, 1)
tools = call("tools/list", {}, 2)["tools"]
print(info["serverInfo"], len(tools), "tools")
print(sorted(t["name"] for t in tools))
