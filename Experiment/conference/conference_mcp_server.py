import os
import sqlite3
import json
import csv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Conference Agent MCP")
DB_PATH = "/home/aparichit/Projects/AgentFlowGuard/Experiment/conference/reviews.db"
CONF_DIR = "/home/aparichit/Projects/AgentFlowGuard/Experiment/conference"

@mcp.tool()
def query_reviews_db(sql_query: str) -> str:
    """Execute SQL queries on the conference reviews database.
    Supported tables: Papers, Authors, Reviewers, Assignments, Reviews, Decision.
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
        
        res = [dict(row) for row in rows]
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error executing query: {e}"

@mcp.tool()
def read_conference_guidelines() -> str:
    """Read the double-blind review process policy and guidelines document."""
    pdf_path = os.path.join(CONF_DIR, "conference_guidelines.pdf")
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading conference_guidelines.pdf: {e}"

@mcp.tool()
def read_author_info_csv() -> str:
    """Read author information metadata matching paper titles and email addresses."""
    csv_path = os.path.join(CONF_DIR, "author_info.csv")
    try:
        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return "\n".join([",".join(row) for row in rows])
    except Exception as e:
        return f"Error reading author_info.csv: {e}"

@mcp.tool()
def list_papers() -> str:
    """List all available submitted research paper draft files in the papers folder."""
    papers_dir = os.path.join(CONF_DIR, "papers")
    try:
        files = os.listdir(papers_dir)
        return json.dumps(files, indent=2)
    except Exception as e:
        return f"Error listing papers: {e}"

@mcp.tool()
def read_paper_pdf(filename: str) -> str:
    """Read the draft content text of an unpublished research paper draft by filename."""
    paper_path = os.path.join(CONF_DIR, "papers", filename)
    if not os.path.abspath(paper_path).startswith(os.path.abspath(CONF_DIR)):
        return "Access denied: outside directory boundary."
    try:
        import pypdf
        reader = pypdf.PdfReader(paper_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading paper {filename}: {e}"

if __name__ == "__main__":
    mcp.run()
