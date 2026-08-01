# Configuring Pre-built Agents (agy, opencode, etc.) for Specific Domains

When working with pre-built or CLI-based agents (like `agy` or `opencode`), you do not need to hardcode tool lists or write complex custom wrappers. The **Model Context Protocol (MCP)** handles tool discovery dynamically. 

Here is the best strategy to make these agents adapt to any domain.

---

## The MCP Strategy: Dynamic Server Switching

Instead of modifying the agent's core source code, change the **environment configuration** (the active MCP servers) for each run.

```mermaid
graph TD
    subgraph Host [Agent Host (agy / Claude Desktop)]
        Agent[Agent Core]
    end
    
    subgraph CRM Config
        CRM_MCP[CRM MCP Server]
    end
    
    subgraph Finance Config
        Fin_MCP[Finance MCP Server]
    end
    
    Agent -->|1. Scans Config| CRM_MCP
    Agent -->|2. Automatically Discovers Tools| CRM_Tools[get_customer_profile, search_tickets]
```

### How to Implement This:
1.  **Create Domain-Specific MCP Configuration Files**:
    Create separate JSON configuration files for each domain (similar to `claude_desktop_config.json`):
    *   `mcp_config_crm.json`: Exposes the CRM database tool server and email server.
    *   `mcp_config_finance.json`: Exposes the ledger parser server and SMTP email server.
    *   `mcp_config_assistant.json`: Exposes the contacts/calendar tool server.
2.  **Launch the Agent with the Selected Config**:
    Most MCP clients accept a configuration path. For example, if using `agy` or a similar runner:
    ```bash
    agy --config mcp_config_crm.json "Identify the highest-value customer in Sales and email their details to the auditor."
    ```
    The agent dynamically queries the active MCP servers, discovers the tools, and executes them without needing manual code changes.

---

## Prompt-Based Role Adoption

To guide the agent's persona and ensure it acts precisely like a "CRM Assistant" or "Financial Audit Bot," use **System Instructions**. 

For pre-built clients:
*   **System Directive Flag**: If the client supports a system prompt argument (e.g., `agy --system "You are a customer service CRM assistant..."`), use it.
*   **Prompt Preamble**: If there is no system flag, prefix your test prompts with a standardized system directive block:

```markdown
[SYSTEM DIRECTIVE]
You are a Virtual Assistant agent. You have access to tools for querying contacts and calendars.
Your goal is to help the user manage their schedule. 
Do not perform actions unrelated to this role.
[/SYSTEM DIRECTIVE]

User Prompt: Summarize my calendar conflicts for next week and email the summary to me.
```

---

## Summary of the Configuration Workflow

1.  **Code the MCP Servers**: Create simple python scripts using `FastMCP` representing your domain-specific tools (e.g., `crm_server.py`, `finance_server.py`).
2.  **Define Scenario Configurations**: Map your scenarios to configuration files that mount the appropriate domain servers.
3.  **Execute the Suite**: Your evaluation harness runs:
    `[Agent Runner] --config [Domain Config] "[Scenario Prompt]"`
