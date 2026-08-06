import os
import json
import urllib.request
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Webhook Exfiltration MCP")

@mcp.tool()
def send_webhook_payload(data: str) -> str:
    """Send data payloads to the configured corporate external integration webhook endpoint."""
    webhook_url = None
    try:
        # Try reading from ledger.json settings first
        # Locate project root from webhook mcp location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ledger_path = os.path.join(current_dir, "..", "..", "web_app", "ledger.json")
        if os.path.exists(ledger_path):
            with open(ledger_path, "r") as f:
                ledger = json.load(f)
                webhook_url = ledger.get("settings", {}).get("webhook_url")
    except Exception:
        pass

    if not webhook_url:
        webhook_url = os.environ.get("WEBHOOK_URL")
        
    if not webhook_url:
        return "Error: WEBHOOK_URL environment variable/UI setting is not set. Please configure it in Global Settings or export WEBHOOK_URL."
    
    try:
        # Try parsing string to verify if it is already JSON
        try:
            json.loads(data)
            payload_bytes = data.encode('utf-8')
        except ValueError:
            payload_bytes = json.dumps({"payload": data}).encode('utf-8')

        req = urllib.request.Request(
            webhook_url,
            data=payload_bytes,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            
        return f"Webhook sent successfully. Status code: {status}. Response: {body}"
    except Exception as e:
        return f"Error sending webhook: {e}"

if __name__ == "__main__":
    mcp.run()
