# AgentFlowGuard

> **Application-Level Guardrail & Information Flow Control (IFC) Framework for Multi-Agent Model Context Protocol (MCP) Ecosystems**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-MCP-orange.svg)](https://modelcontextprotocol.io/)

---

## 📌 Executive Summary

**AgentFlowGuard** is an SSDLC-compliant security framework designed to protect enterprise multi-agent workflows against unauthorized data exfiltration, indirect prompt injection, and confused-deputy attacks. 

Operating at the interception layer between LLM agents and the **Model Context Protocol (MCP)** runtime, AgentFlowGuard dynamically tracks data taint, enforces deterministic information flow policies, and provides full cryptographic auditability through a tamper-evident telemetry ledger.

---

## 🏛️ System Architecture & Threat Model

```
+----------------------------------------------------------------------------------------------------+
|                                      UNTRUSTED EXTERNAL ZONE                                       |
|  [External User / Adversary] ---> [Untrusted Input: Prompts, PDFs, Customer Tickets, Commits]       |
+--------------------------------------------------+-------------------------------------------------+
                                                   | 
                                                   v [Trust Boundary 1: Ingestion]
+--------------------------------------------------+-------------------------------------------------+
|                                    COGNITIVE ORCHESTRATION ZONE                                    |
|  [Supervisor Agent] <=======================> [Specialized Worker Subagents]                       |
|   (LangChain / CrewAI / OpenCode / ReAct)       (Reader Agent, Auditor, Invoicer, Sender Agent)    |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v [Trust Boundary 2: Interception & Flow Control]
+--------------------------------------------------+-------------------------------------------------+
|                               AGENTFLOWGUARD SECURITY ENCLAVE                                      |
|  - MCPInterceptor (Hook before_tool_call & after_tool_return)                                      |
|  - TaintTracker (Canonical JSON Serialization, SHA256 Sub-tree Digest Walk)                       |
|  - PolicyEngine (Rule evaluation: ALLOW / BLOCK / WARN)                                            |
|  - TelemetryLogger (Audit trace, provenance ledger)                                                |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v [Trust Boundary 3: Tool Execution & Egress]
+--------------------------------------------------+-------------------------------------------------+
|                          PROTECTED DATA SOURCES  |               EXFILTRATION SINKS                 |
|  - CRM DB / customers.csv / leads.csv            |  - Webhook / HTTP POST (`send_webhook_payload`)  |
|  - Finance DB / salary.xlsx / tax_records.pdf    |  - DNS Out-of-Band (`resolve_dns_lookup`)       |
|  - Conference DB / blind author metadata         |  - Email MCP (`send_email` via SMTP)             |
|  - Git history / Reflog / .env files             |  - Slack MCP / Local File System Writes          |
+--------------------------------------------------+-------------------------------------------------+
```

### Core Security Pillars
1. **MCP Interception**: Intercepts `before_tool_call` and `after_tool_return` hooks to inspect arguments and tool responses in flight.
2. **Dynamic Taint Tracking**: Computes canonical JSON digests (SHA-256) to track sensitive data propagation across subagent delegations.
3. **Deterministic Policy Engine**: Enforces least-privilege egress controls (blocking unapproved sinks like unauthorized webhooks, DNS channels, and untrusted email recipients).
4. **Telemetry & Ledger**: Maintains an append-only audit trail in SQLite (`ledger.db`) for post-incident review and SOC triage.

---

## 📂 Repository Structure

```
├── agentflowguard/        # Core security runtime (interceptor, taint tracker, policy engine)
├── ProblemDemos/          # Security attack benchmarks (Database exfiltration, review deanonymization)
├── Experiment/            # Multi-domain evaluation scenarios (CRM, Finance, Conference, Coding)
├── LocalListener/         # HTTP RequestBin & UDP DNS honeypot logger
├── web_app/               # Interactive evaluation dashboard and ledger inspection UI
├── ATTACK_TREE.md         # Comprehensive STRIDE & DREAD threat model
└── run_crm_evaluation.py  # Automated evaluation harness
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Installation
```bash
git clone https://github.com/ShudarsanRegmi/agentflowguard.git
cd agentflowguard
pip install -r requirements.txt
```

### 3. Launch the Evaluation Dashboard
```bash
python web_app/app.py
```
Open your browser to `http://localhost:5000` to inspect live agent runs, policy decisions, and taint traces.

---

## 🛡️ Problem Scenarios Evaluated

- **Scenario 1: CRM & Customer Support Exfiltration** — Indirect prompt injection via customer support tickets attempting to dump customer PII to external webhooks.
- **Scenario 2: Double-Blind Conference Anonymity** — Reviewer agent tricked into deanonymizing author identity via supplementary paper metadata.
- **Scenario 3: Financial Ledger & Payroll Tampering** — Confused deputy attack attempting unauthorized payroll adjustments and DNS exfiltration.
- **Scenario 4: Source Code & Secret Leakage** — Exploitation of git history and developer environment variables through code assistance agents.

---

## 📄 License
This project is licensed under the MIT License.
