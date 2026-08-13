import os
import sys
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load env variables from the root .env file
project_root = "/home/aparichit/Projects/AgentFlowGuard/ProblemDemos/DatabaseExfiltration"
load_dotenv(os.path.join(project_root, ".env"))

# Add root directory to python path for logger imports
sys.path.append(project_root)
from utils.mcp_logger import log_email_tool

# Initialize logging for the email server
log_dir = os.path.join(project_root, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "email_server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stderr)  # Log to stderr so it doesn't break JSON-RPC over stdout
    ]
)

logging.info("Email MCP Server starting...")

# Initialize the FastMCP server
mcp = FastMCP("Email MCP")

# Environment variables configuration for real SMTP
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.mailtrap.io")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "2525"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "agent@nexustech.com")

logging.info(f"Loaded config: SMTP_HOST={SMTP_HOST}, SMTP_PORT={SMTP_PORT}, SMTP_USER={SMTP_USER}, SENDER_EMAIL={SENDER_EMAIL}")

@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email to a recipient with a subject and body using the configured SMTP server."""
    logging.info(f"send_email called for recipient={recipient}, subject={subject}")
    
    # Reload environment variables in case they were updated in the .env file after startup
    load_dotenv(os.path.join(project_root, ".env"), override=True)
    smtp_host = os.environ.get("SMTP_HOST", "smtp.mailtrap.io")
    try:
        smtp_port = int(os.environ.get("SMTP_PORT", "2525"))
    except ValueError:
        smtp_port = 2525
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    sender_email = os.environ.get("SENDER_EMAIL", "agent@nexustech.com")
    
    # Check if SMTP user/password is missing
    if not smtp_user or not smtp_password:
        mock_msg = (
            f"=== MOCK EMAIL SENT ===\n"
            f"Recipient: {recipient}\n"
            f"Subject  : {subject}\n"
            f"Body     :\n{body}\n"
            f"========================\n"
            f"Note: To send actual emails, configure SMTP_HOST, SMTP_PORT, SMTP_USER, and SMTP_PASSWORD in .env."
        )
        logging.warning("SMTP credentials not fully configured. Running in MOCK mode.")
        logging.info(mock_msg)
        log_email_tool(recipient, subject)
        return f"Mock email sent to {recipient} (SMTP credentials not configured)."

    try:
        logging.info(f"Preparing email message container (From: {sender_email}, To: {recipient})")
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        # Detect HTML content
        is_html = body.strip().startswith("<") or "<html>" in body.lower()
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
        # Connect to SMTP server
        if smtp_port == 465:
            logging.info(f"Connecting to SMTP server at {smtp_host}:{smtp_port} using SSL...")
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            logging.info(f"Connecting to SMTP server at {smtp_host}:{smtp_port} using standard connection...")
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
            logging.info("Sending EHLO...")
            server.ehlo()
            try:
                logging.info("Starting TLS...")
                server.starttls()
                logging.info("Sending EHLO post-TLS...")
                server.ehlo()
            except Exception as tls_err:
                logging.warning(f"STARTTLS failed (proceeding without TLS): {tls_err}")
        
        # Authenticate
        logging.info(f"Authenticating as user: {smtp_user}...")
        server.login(smtp_user, smtp_password)
        logging.info("Authentication successful.")
        
        # Send mail
        logging.info(f"Sending mail from {sender_email} to {recipient}...")
        server.sendmail(sender_email, recipient, msg.as_string())
        logging.info("Mail sent successfully.")
        
        server.close()
        logging.info("SMTP connection closed.")
        
        # Log email tool execution
        log_email_tool(recipient, subject)
        return f"Email successfully sent to {recipient}."
    except Exception as e:
        err_msg = f"Failed to send email to {recipient}: {e}"
        logging.error(err_msg, exc_info=True)
        return err_msg

if __name__ == "__main__":
    mcp.run()
