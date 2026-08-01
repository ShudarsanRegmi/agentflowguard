import os
import sys
import json
import pymysql
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load env variables from the root .env file
project_root = "/home/aparichit/Projects/AgentFlowGuard/ProblemDemos/DatabaseExfiltration"
load_dotenv(os.path.join(project_root, ".env"))

# Add root directory to python path for logger imports
sys.path.append(project_root)
from utils.mcp_logger import log_db_tool

# Initialize the FastMCP server
mcp = FastMCP("Employee Database MCP")

DB_CONFIG = {
    'host': os.environ.get("DB_HOST", "localhost"),
    'port': int(os.environ.get("DB_PORT", "3306")),
    'user': os.environ.get("DB_USER", "aparichit"),
    'password': os.environ.get("DB_PASSWORD", "letmelogin"),
    'database': os.environ.get("DB_NAME", "company_db"),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@mcp.tool()
def get_employee(employee_id: int) -> str:
    """Get full details of a specific employee, including their profile and performance reviews."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get employee info
            cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
            employee = cursor.fetchone()
            if not employee:
                res = f"Employee with ID {employee_id} not found."
                log_db_tool("get_employee", {"employee_id": employee_id}, res)
                return res
            
            # Get performance reviews
            cursor.execute("SELECT * FROM performance_reviews WHERE employee_id = %s", (employee_id,))
            reviews = cursor.fetchall()
            employee['performance_reviews'] = reviews
            
            log_db_tool("get_employee", {"employee_id": employee_id}, employee)
            return json.dumps(employee, default=str, indent=2)
    except Exception as e:
        err_msg = f"Error: {e}"
        log_db_tool("get_employee", {"employee_id": employee_id}, err_msg)
        return err_msg
    finally:
        connection.close()

@mcp.tool()
def search_employees(department: str) -> str:
    """Search for employees working in a specific department."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT employee_id, name, email, department, salary FROM employees WHERE department = %s", (department,))
            results = cursor.fetchall()
            log_db_tool("search_employees", {"department": department}, results)
            return json.dumps(results, default=str, indent=2)
    except Exception as e:
        err_msg = f"Error: {e}"
        log_db_tool("search_employees", {"department": department}, err_msg)
        return err_msg
    finally:
        connection.close()

@mcp.tool()
def get_project_details(project_id: int) -> str:
    """Get details of a company project including budget and status."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM projects WHERE project_id = %s", (project_id,))
            project = cursor.fetchone()
            if not project:
                res = f"Project with ID {project_id} not found."
                log_db_tool("get_project_details", {"project_id": project_id}, res)
                return res
            
            log_db_tool("get_project_details", {"project_id": project_id}, project)
            return json.dumps(project, default=str, indent=2)
    except Exception as e:
        err_msg = f"Error: {e}"
        log_db_tool("get_project_details", {"project_id": project_id}, err_msg)
        return err_msg
    finally:
        connection.close()

@mcp.tool()
def generate_department_report(department: str) -> str:
    """Generate a high-level summary report for a department, including head count, budget metrics, and performance indicators."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 1. Get basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as headcount, 
                    SUM(salary) as total_budget, 
                    AVG(salary) as average_salary,
                    MIN(salary) as min_salary,
                    MAX(salary) as max_salary
                FROM employees 
                WHERE department = %s
            """, (department,))
            stats = cursor.fetchone()
            
            if not stats or stats['headcount'] == 0:
                res = f"No data found for department: {department}."
                log_db_tool("generate_department_report", {"department": department}, res)
                return res
            
            # 2. Get reviews rating distribution
            cursor.execute("""
                SELECT 
                    AVG(pr.rating) as average_rating,
                    COUNT(pr.review_id) as total_reviews
                FROM performance_reviews pr
                JOIN employees e ON pr.employee_id = e.employee_id
                WHERE e.department = %s
            """, (department,))
            review_stats = cursor.fetchone()
            
            # 3. Get list of employees in dept
            cursor.execute("""
                SELECT employee_id, name, email, salary 
                FROM employees 
                WHERE department = %s
                ORDER BY salary DESC
            """, (department,))
            employee_list = cursor.fetchall()
            
            report = {
                "department": department,
                "summary": {
                    "headcount": stats['headcount'],
                    "total_salary_budget": float(stats['total_budget']) if stats['total_budget'] else 0.0,
                    "average_salary": float(stats['average_salary']) if stats['average_salary'] else 0.0,
                    "min_salary": float(stats['min_salary']) if stats['min_salary'] else 0.0,
                    "max_salary": float(stats['max_salary']) if stats['max_salary'] else 0.0
                },
                "performance_summary": {
                    "average_review_rating": float(review_stats['average_rating']) if review_stats['average_rating'] else None,
                    "total_performance_reviews": review_stats['total_reviews']
                },
                "employees": employee_list
            }
            
            log_db_tool("generate_department_report", {"department": department}, report)
            return json.dumps(report, default=str, indent=2)
    except Exception as e:
        err_msg = f"Error: {e}"
        log_db_tool("generate_department_report", {"department": department}, err_msg)
        return err_msg
    finally:
        connection.close()

if __name__ == "__main__":
    mcp.run()
