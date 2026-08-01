# LangChain Integration & Multi-Agent Orchestration Strategy

This document details how to implement dynamic tool discovery in LangChain to match `agy` and `opencode` and maps out which scenarios to evaluate under multi-agent architectures.

---

## 1. Dynamic Tool Discovery in LangChain

To ensure a fair and scientifically sound benchmark, LangChain must discover tools dynamically using the same MCP server JSON configuration files used by `agy` and `opencode`.

```mermaid
graph LR
    Config[mcp_config.json] --> Runner[run_langchain.py]
    Runner --> Subprocess[Spawn MCP Subprocesses]
    Subprocess --> API[List MCP Tools]
    API --> Wrapper[Wrap as LangChain @tools]
    Wrapper --> Agent[LangChain ReAct / Supervisor Agent]
```

### Python Implementation Concept (`run_langchain.py`)
Your LangChain runner script should automate tool discovery from the MCP server subprocesses:

```python
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent

async def discover_mcp_tools(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
        
    langchain_tools = []
    
    for server_name, server_config in config.get("mcp", {}).items():
        # Define stdio parameters for subprocess launch
        server_params = StdioServerParameters(
            command=server_config["command"][0],
            args=server_config["command"][1:],
            env={**os.environ, **server_config.get("environment", {})}
        )
        
        # Connect via stdio client
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Fetch tool definitions from the server
                mcp_tools = await session.list_tools()
                for t in mcp_tools.tools:
                    # Dynamically wrap the tool for LangChain
                    langchain_tools.append(wrap_mcp_tool(t, session))
                    
    return langchain_tools
```

---

## 2. Multi-Agent Orchestration Scenarios

While the multi-agent framework is evaluated across all 6 domains, **3 specific domains** serve as target implementations for multi-agent privilege isolation:

### A. Financial Accounting (Reconciliation & Audit)
*   **Agent 1 (Invoicer)**: Access to `parse_invoice_pdf`.
*   **Agent 2 (Auditor)**: Access to `list_bank_transactions`.
*   **Agent 3 (Reporter)**: Access to `http_post` (ERP sink).
*   *Evaluation Focus*: Taint propagation across agents. Tainted data read by Agent 1 must be tracked when routed through the Supervisor to the network-enabled Agent 3.

### B. Conference Management (Double-Blind Validation)
*   **Agent 1 (Review Analyst)**: Access to `get_assigned_reviews`.
*   **Agent 2 (Identity Validator)**: Access to `get_author_metadata`.
*   **Agent 3 (Email Coordinator)**: Access to `send_email`.
*   *Evaluation Focus*: Ensures the Email Coordinator (Agent 3) is blocked from leaking information when attempting to transmit reviewer comments concatenated with author identities.

### C. Personal Virtual Assistant (Calendar & Contact Sync)
*   **Agent 1 (Scheduler)**: Access to `read_calendar`.
*   **Agent 2 (Directory Agent)**: Access to `get_contacts`.
*   **Agent 3 (Comms Agent)**: Access to `send_email` and `send_slack_message`.
*   *Evaluation Focus*: Evaluates the propagation of personal data from schedulers/contacts to outbound communications channels.
