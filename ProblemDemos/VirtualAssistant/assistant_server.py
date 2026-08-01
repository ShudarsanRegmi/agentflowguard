import os
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Virtual Assistant MCP")

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CALENDAR_PATH = os.path.join(DATA_DIR, "calendar.json")
CONTACTS_PATH = os.path.join(DATA_DIR, "contacts.json")

@mcp.tool()
def read_calendar() -> str:
    """Read all upcoming calendar events, including meetings, descriptions, and attendee emails."""
    try:
        with open(CALENDAR_PATH, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_contacts() -> str:
    """Get the contact list including names, roles, phone numbers, and email addresses."""
    try:
        with open(CONTACTS_PATH, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run()
