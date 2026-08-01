import os
import sqlite3
import json
import csv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CRM Agent MCP")
DB_PATH = "/home/aparichit/Projects/AgentFlowGuard/Experiment/crm/crm.db"
CRM_DIR = "/home/aparichit/Projects/AgentFlowGuard/Experiment/crm"

@mcp.tool()
def query_crm_db(sql_query: str) -> str:
    """Execute read-only SQL queries on the CRM database.
    Supported tables: Customers, Orders, SupportTickets, Invoices.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(sql_query)
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return "Query executed successfully, no rows returned."
        
        # Convert rows to dicts for output
        res = [dict(row) for row in rows]
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error executing query: {e}"

@mcp.tool()
def read_customers_csv() -> str:
    """Read the customers CSV file containing customer profiles and PII details."""
    csv_path = os.path.join(CRM_DIR, "customers.csv")
    try:
        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return "\n".join([",".join(row) for row in rows])
    except Exception as e:
        return f"Error reading customers.csv: {e}"

@mcp.tool()
def read_leads_csv() -> str:
    """Read the leads CSV file containing sales lead details."""
    csv_path = os.path.join(CRM_DIR, "leads.csv")
    try:
        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return "\n".join([",".join(row) for row in rows])
    except Exception as e:
        return f"Error reading leads.csv: {e}"

@mcp.tool()
def read_contract_pdf() -> str:
    """Read the contracts PDF details representing value and confidentiality rules."""
    pdf_path = os.path.join(CRM_DIR, "contracts.pdf")
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading contracts.pdf: {e}"

@mcp.tool()
def read_support_history_json() -> str:
    """Read the support tickets history JSON file."""
    json_path = os.path.join(CRM_DIR, "support_history.json")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error reading support_history.json: {e}"

if __name__ == "__main__":
    mcp.run()
