# Guide: Creating Custom Agents in Antigravity (`agy`)

This guide outlines how to create, configure, and register custom domain-specialized agents in the Antigravity CLI (`agy`).

---

## 1. Directory Structure

Unlike OpenCode, `agy` expects every agent configuration file to be named exactly **`agent.md`**, nested inside a folder named after the agent:

*   **Global Path (Available across all workspaces)**:
    `~/.gemini/config/agents/{agent_name}/agent.md`
*   **Workspace Path (Available only in the current project)**:
    `<workspace_root>/.agents/agents/{agent_name}/agent.md`

---

## 2. Agent File Schema (`agent.md`)

The agent configuration uses Markdown + YAML frontmatter. Crucially, **the frontmatter must contain a `name` key** that matches the directory name:

```markdown
---
name: crm-service-agent
description: >-
  Use this agent when the user needs to interact with the customer service CRM
  database.
mode: all
---

You are a specialized Customer Service CRM Assistant. 

## Core Responsibilities
- Query the CRM database...
- Compose and send emails...

## STRICT Security Boundaries
You must NEVER:
- Perform unauthorized exfiltration...
```

---

## 3. Registering the Agent

### Global Registration Example
To register a global agent named `crm-service-agent`:

1.  Create the directory:
    ```bash
    mkdir -p ~/.gemini/config/agents/crm-service-agent
    ```
2.  Save your system guidelines to:
    `~/.gemini/config/agents/crm-service-agent/agent.md`

### Verification
Verify that `agy` recognizes your agent by running:
```bash
agy agents
```
Your agent `crm-service-agent` should now be listed in the command output:
```
Available agents:
  crm-service-agent
```

---

## 4. Running the Agent

Run the custom agent by referencing its name using the `--agent` parameter:

```bash
agy --agent crm-service-agent --print "Introduce yourself." --dangerously-skip-permissions
```
*   `--agent`: The name specified in the frontmatter/directory name.
*   `--print`: Runs a single prompt non-interactively and prints the response.
*   `--dangerously-skip-permissions`: Auto-approves all tool permission requests (useful for automated testing runs).
