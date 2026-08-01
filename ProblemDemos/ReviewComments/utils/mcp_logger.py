import os
import json
from datetime import datetime, timezone

LOG_FILE = "/home/aparichit/Projects/AgentFlowGuard/ProblemDemos/ReviewComments/logs/mcp_actions.log"

def log_db_tool(tool_name, args, result):
    """
    Logs database tools execution.
    Format:
    {
      "timestamp": "...",
      "tool": "...",
      "args": {...},
      "result_size": 1200
    }
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Calculate result size by stringifying the output
    result_str = json.dumps(result, default=str)
    result_size = len(result_str)
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tool": tool_name,
        "args": args,
        "result_size": result_size
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_email_tool(recipient, subject):
    """
    Logs email sending tool execution.
    Format:
    {
      "timestamp": "...",
      "tool": "send_email",
      "recipient": "...",
      "subject": "..."
    }
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tool": "send_email",
        "recipient": recipient,
        "subject": subject
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
