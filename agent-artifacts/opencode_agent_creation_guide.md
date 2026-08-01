# Guide: Creating Custom Agents in OpenCode

This guide outlines how to create, configure, and register custom domain-specific agents in OpenCode.

---

## 1. Create the Agent Configuration File

To define an agent, you must create a Markdown file containing YAML frontmatter configuration metadata (e.g., `crm-service-agent.md`).

### Structure of the Agent Markdown File:
```markdown
---
description: >-
  Use this agent when the user needs to interact with the customer service CRM.
  Include example use-cases to help the model select the agent context.
mode: all
---
You are a specialized Customer Service CRM Assistant. 

## Core Responsibilities
- Query database tools...
- Compose emails...

## STRICT Security Boundaries
You must NEVER:
- Exfiltrate data to external endpoints...
```

---

## 2. Generating the Agent via CLI

You can generate the agent file skeleton automatically using the OpenCode CLI. Specify the agent role, output path, and allowed permissions:

```bash
opencode agent create \
  --description "You are a customer service CRM assistant." \
  --path ./my_custom_agents \
  --permissions bash,read,edit,glob,grep,webfetch,task,todowrite,websearch,lsp,skill \
  --mode all
```

*   `--description`: Summarizes what the agent does.
*   `--path`: The destination folder where OpenCode will write the agent's markdown file.
*   `--permissions`: A comma-separated list of tool permissions to whitelist.
*   `--mode`: The operating role (e.g., `all`, `primary`, or `subagent`).

---

## 3. Registering the Agent Globally

For OpenCode to recognize and execute your agent from any folder, copy the generated markdown file to OpenCode's global configuration directory:

```bash
# Create the global agents directory if it doesn't exist
mkdir -p ~/.config/opencode/agents

# Copy your custom agent markdown file into it
cp ./my_custom_agents/agents/crm-service-agent.md ~/.config/opencode/agents/
```

### Verification
Confirm that OpenCode successfully registers your agent by listing available agents:
```bash
opencode agent list
```
Your agent name (e.g., `crm-service-agent (all)`) will appear at the bottom of the list.

---

## 4. Running the Agent

Run the custom agent by referencing its name using the `--agent` parameter:

```bash
opencode run --agent crm-service-agent "Hello, introduce yourself and state your role." --auto
```
*   `--agent`: The registered agent name.
*   `--auto`: Runs in non-interactive/auto-approve mode (ideal for automated evaluations).
