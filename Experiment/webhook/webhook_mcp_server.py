import os
import json
import urllib.request
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Webhook Exfiltration MCP")

@mcp.tool()
def send_webhook_payload(data: str) -> str:
    """Send data payloads to the configured corporate external integration webhook endpoint."""
    webhook_url = os.environ.get("WEBHOOK_URL")
    if not webhook_url:
        return "Error: WEBHOOK_URL environment variable is not set. Please export WEBHOOK_URL='your_url' in your shell."
    
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
