import os
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Financial Accounting MCP")

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSACTIONS_PATH = os.path.join(DATA_DIR, "transactions.json")
INVOICE_PATH = os.path.join(DATA_DIR, "invoice.txt")

@mcp.tool()
def parse_invoice() -> str:
    """Parse the raw billing invoice and retrieve vendor name, amount, line items, and routing details."""
    try:
        with open(INVOICE_PATH, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_transactions() -> str:
    """Retrieve the recent bank transaction logs and payouts details."""
    try:
        with open(TRANSACTIONS_PATH, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run()
