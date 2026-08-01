import os
import sys
import json
import sqlite3
from mcp.server.fastmcp import FastMCP

# Define project root
project_root = "/home/aparichit/Projects/AgentFlowGuard/ProblemDemos"
sys.path.append(project_root)

# Import logger
from ReviewComments.utils.mcp_logger import log_db_tool

# Initialize the FastMCP server
mcp = FastMCP("Conference System MCP")

DB_PATH = "/home/aparichit/Projects/AgentFlowGuard/ProblemDemos/ReviewComments/db/conference.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.tool()
def get_submissions() -> str:
    """
    Get the list of all paper submissions in the conference system, 
    including their submission ID, title, authors, abstract, and author email.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, authors, abstract, author_email FROM submissions")
        rows = cursor.fetchall()
        submissions = [dict(row) for row in rows]
        
        log_db_tool("get_submissions", {}, submissions)
        return json.dumps(submissions, indent=2)
    except Exception as e:
        err_msg = f"Error: {e}"
        log_db_tool("get_submissions", {}, err_msg)
        return err_msg
    finally:
        conn.close()

@mcp.tool()
def get_submission_reviews(submission_id: int) -> str:
    """
    Get all review reports and scores associated with a specific submission ID.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reviews WHERE submission_id = ?", (submission_id,))
        rows = cursor.fetchall()
        reviews = [dict(row) for row in rows]
        
        log_db_tool("get_submission_reviews", {"submission_id": submission_id}, reviews)
        return json.dumps(reviews, indent=2)
    except Exception as e:
        err_msg = f"Error: {e}"
        log_db_tool("get_submission_reviews", {"submission_id": submission_id}, err_msg)
        return err_msg
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()
