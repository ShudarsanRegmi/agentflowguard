import os
import sys
import socket
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load env variables from the root .env file
project_root = "/home/aparichit/Projects/AgentFlowGuard/ProblemDemos"
env_path = os.path.join(project_root, ".env")
print(f"[*] Loading environment from: {env_path}")
load_dotenv(env_path)

# Configurations
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = os.environ.get("SMTP_PORT", "465")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")

print(f"[*] Configuration Loaded:")
print(f"    - Host: {SMTP_HOST}")
print(f"    - Port: {SMTP_PORT}")
print(f"    - User: {SMTP_USER}")
print(f"    - Sender: {SENDER_EMAIL}")
print(f"    - Password Length: {len(SMTP_PASSWORD) if SMTP_PASSWORD else 0} chars")

recipient = "shudarsanregmi.work@gmail.com"
subject = "SMTP Standalone Test Email"
body = "This is a direct SMTP test email to verify credentials and network connectivity."

if not SMTP_USER or not SMTP_PASSWORD:
    print("[!] ERROR: SMTP_USER or SMTP_PASSWORD is not set in the .env file.")
    sys.exit(1)

try:
    port = int(SMTP_PORT)
except ValueError:
    print(f"[!] Invalid port in configuration: {SMTP_PORT}. Defaulting to 465.")
    port = 465

print(f"\n[*] Step 1: Resolving and testing low-level connection to {SMTP_HOST}:{port}...")
try:
    addrinfo = socket.getaddrinfo(SMTP_HOST, port)
    print(f"    - Resolved IPs: {[info[4][0] for info in addrinfo]}")
    
    # Try connecting to port using a socket
    print("    - Initiating socket test...")
    s = socket.create_connection((SMTP_HOST, port), timeout=5)
    print("    - Socket connection established successfully!")
    s.close()
except Exception as sock_err:
    print(f"[!] Socket connection test failed: {sock_err}")
    print("[!] This usually indicates a firewall, ISP port block, or offline DNS resolution.")
    print("="*60)
    traceback.print_exc()
    print("="*60)
    sys.exit(1)

print("\n[*] Step 2: Initiating SMTP Connection...")
try:
    if port == 465:
        print(f"    - Connecting to {SMTP_HOST}:{port} via SSL...")
        server = smtplib.SMTP_SSL(SMTP_HOST, port, timeout=30)
    else:
        print(f"    - Connecting to {SMTP_HOST}:{port} via standard protocol...")
        server = smtplib.SMTP(SMTP_HOST, port, timeout=30)
        print("    - Sending EHLO...")
        server.ehlo()
        try:
            print("    - Upgrading connection to TLS (STARTTLS)...")
            server.starttls()
            print("    - Sending EHLO post-TLS...")
            server.ehlo()
        except Exception as tls_err:
            print(f"    - Warning: STARTTLS failed (proceeding without TLS): {tls_err}")

    print("\n[*] Step 3: Authenticating...")
    print(f"    - Logging in as {SMTP_USER}...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("    - Authentication successful!")

    print("\n[*] Step 4: Building and sending message...")
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL if SENDER_EMAIL else SMTP_USER
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    print(f"    - Sending mail from {msg['From']} to {recipient}...")
    server.sendmail(msg['From'], recipient, msg.as_string())
    print("    - Email sent successfully!")

    print("\n[*] Step 5: Closing connection...")
    server.close()
    print("[*] Completed successfully.")
    
except Exception as e:
    print("\n[!] SMTP Operation failed during execution:")
    print("="*60)
    traceback.print_exc()
    print("="*60)
    sys.exit(1)
