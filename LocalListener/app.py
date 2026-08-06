import os
import sys
import json
import uuid
import socket
import struct
import threading
import uvicorn
import binascii
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="LocalListener - Request & DNS Query Bin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared memory log storage
captured_events = []
max_log_size = 500

class DNSRequestPayload(BaseModel):
    domain: str
    source_ip: str

# Helper to automatically decode common exfiltration formats (Hex, Base64)
def try_decode_payload(payload_str: str) -> dict:
    decodings = {}
    payload_str = payload_str.strip()
    if not payload_str:
        return decodings
        
    # 1. Hex decoding
    try:
        # Clean hex from possible subdomain formatting
        clean_hex = payload_str.replace(".", "").replace("-", "")
        decoded_bytes = bytes.fromhex(clean_hex)
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        if any(c.isalnum() for c in decoded_str): # Filter garbage binary data
            decodings["Hex Decoded"] = decoded_str
    except Exception:
        pass
        
    # 2. Base64 decoding
    try:
        # Clean base64 padding
        clean_b64 = payload_str.replace(" ", "+")
        missing_padding = len(clean_b64) % 4
        if missing_padding:
            clean_b64 += '=' * (4 - missing_padding)
        import base64
        decoded_bytes = base64.b64decode(clean_b64, validate=False)
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        if any(c.isalnum() for c in decoded_str):
            decodings["Base64 Decoded"] = decoded_str
    except Exception:
        pass

    return decodings

# --- DNS SERVER BACKGROUND THREAD ---
# Runs a lightweight local DNS server on UDP socket to listen to queries directly.
def start_dns_server(host="0.0.0.0", port=1053):
    print(f"[*] Starting local UDP DNS Listener on {host}:{port}...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.bind((host, port))
    except Exception as e:
        print(f"[!] Error binding UDP DNS socket on port {port}: {e}")
        print("[!] Note: Standard DNS port 53 requires admin/sudo privileges. Defaulting to port 1053.")
        return

    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            if not data:
                continue
                
            # Parse simple DNS Header to extract query domain
            # DNS Header is 12 bytes long
            if len(data) < 12:
                continue
                
            transaction_id = data[:2]
            flags = data[2:4]
            qdcount = struct.unpack("!H", data[4:6])[0] # Question Count
            
            # Domain parsing (RFC 1035 labels format)
            domain_parts = []
            idx = 12
            while idx < len(data):
                length = data[idx]
                if length == 0:
                    idx += 1
                    break
                idx += 1
                domain_parts.append(data[idx:idx+length].decode("utf-8", errors="ignore"))
                idx += length
                
            domain = ".".join(domain_parts)
            
            if domain:
                # Log DNS request event
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Try decoding subdomains for exfiltrated payloads
                subdomains_payload = ".".join(domain_parts[:-2]) if len(domain_parts) > 2 else domain
                decodings = try_decode_payload(subdomains_payload)
                
                event = {
                    "id": str(uuid.uuid4()),
                    "type": "DNS",
                    "timestamp": timestamp,
                    "source_ip": addr[0],
                    "target": domain,
                    "method": "UDP-RESOLVE",
                    "headers": {
                        "Transaction ID": binascii.hexlify(transaction_id).decode(),
                        "Flags": binascii.hexlify(flags).decode(),
                        "Port": str(addr[1])
                    },
                    "body": f"DNS Query resolved for hostname: {domain}",
                    "decodings": decodings
                }
                
                captured_events.insert(0, event)
                if len(captured_events) > max_log_size:
                    captured_events.pop()
                    
                # Send standard DNS mock A reply (127.0.0.1 loopback)
                # Reply contains: Header + Question + Answer Record
                # flags: 0x8180 (Standard query response, no error)
                response = transaction_id + b"\x81\x80" + data[4:6] + data[4:6] + b"\x00\x00\x00\x00"
                # Copy original question
                question_end = idx + 4 # includes QTYPE (2 bytes) + QCLASS (2 bytes)
                response += data[12:question_end]
                
                # Answer record: Name pointer to offset 12 (0xc00c), Type A (0x0001), Class IN (0x0001), TTL 60s (0x0000003c), Data length 4 (0x0004), IP 127.0.0.1 (0x7f000001)
                response += b"\xc0\x0c" + b"\x00\x01" + b"\x00\x01" + b"\x00\x00\x00\x3c" + b"\x00\x04" + b"\x7f\x00\x00\x01"
                udp_socket.sendto(response, addr)
                
        except Exception as e:
            print(f"[!] DNS server processing error: {e}")

# --- API ENDPOINTS ---

@app.get("/api/events")
def get_events():
    return captured_events

@app.post("/api/events/clear")
def clear_events():
    captured_events.clear()
    return {"status": "success", "message": "All events cleared."}

@app.post("/api/dns-query")
def receive_http_dns_forward(payload: DNSRequestPayload):
    """Fallback endpoint for tools that forward DNS queries via HTTP."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    decodings = try_decode_payload(payload.domain)
    
    event = {
        "id": str(uuid.uuid4()),
        "type": "DNS",
        "timestamp": timestamp,
        "source_ip": payload.source_ip,
        "target": payload.domain,
        "method": "HTTP-FORWARD",
        "headers": {"Content-Type": "application/json"},
        "body": f"DNS Exfiltration Target Host: {payload.domain}",
        "decodings": decodings
    }
    captured_events.insert(0, event)
    return {"status": "success"}

# Catch-all Webhook listener endpoints
@app.api_route("/webhook/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all_webhook(path: str, request: Request):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = (await request.body()).decode("utf-8", errors="ignore")
    headers = dict(request.headers)
    
    # Try decoding request body
    decodings = try_decode_payload(body)
    
    event = {
        "id": str(uuid.uuid4()),
        "type": "HTTP",
        "timestamp": timestamp,
        "source_ip": request.client.host if request.client else "127.0.0.1",
        "target": f"/webhook/{path}" + (f"?{request.url.query}" if request.url.query else ""),
        "method": request.method,
        "headers": headers,
        "body": body,
        "decodings": decodings
    }
    
    captured_events.insert(0, event)
    if len(captured_events) > max_log_size:
        captured_events.pop()
        
    return {"status": "success", "message": "Payload received by LocalListener RequestBin."}

# Serve modern Webhook.site alternative Dashboard UI
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalListener - Request & DNS Bin</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&family=Fira+Code&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --bg-tertiary: #1f2937;
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --accent-primary: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --success: #10b981;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        header {
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 70px;
            flex-shrink: 0;
        }

        .logo-group {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .logo-icon {
            background: linear-gradient(135deg, var(--accent-primary), #6366f1);
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #fff;
            font-family: 'Outfit', sans-serif;
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
        }

        .controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .btn {
            background-color: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn:hover {
            background-color: var(--accent-glow);
            border-color: var(--accent-primary);
        }

        .btn-danger:hover {
            background-color: rgba(239, 68, 68, 0.15);
            border-color: #ef4444;
        }

        .url-display {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px dashed var(--border-color);
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--accent-primary);
        }

        .main-layout {
            display: flex;
            flex: 1;
            overflow: hidden;
            align-items: stretch;
        }

        /* Left side: Logs list */
        .sidebar {
            width: 380px;
            background-color: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            overflow: hidden;
        }

        .sidebar-header {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sidebar-title {
            font-family: 'Outfit', sans-serif;
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
        }

        .event-list {
            flex: 1;
            overflow-y: auto;
            list-style: none;
        }

        .event-item {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            transition: background 0.15s;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .event-item:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }

        .event-item.active {
            background-color: var(--accent-glow);
            border-left: 3px solid var(--accent-primary);
        }

        .event-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .event-type-badge {
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            text-transform: uppercase;
        }

        .event-type-badge.http {
            background-color: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .event-type-badge.dns {
            background-color: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .event-time {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .event-method {
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .event-target {
            font-size: 0.8rem;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-family: 'Fira Code', monospace;
        }

        /* Right side: Inspector */
        .inspector {
            flex: 1;
            background-color: var(--bg-primary);
            overflow-y: auto;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-muted);
            gap: 1rem;
        }

        .empty-state svg {
            opacity: 0.2;
        }

        .inspector-section {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
        }

        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            color: var(--accent-primary);
        }

        .key-val-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        .key-val-table th, .key-val-table td {
            padding: 0.5rem 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .key-val-table th {
            color: var(--text-secondary);
            font-weight: 600;
            width: 30%;
        }

        .key-val-table td {
            font-family: 'Fira Code', monospace;
            word-break: break-all;
        }

        pre.code-block {
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            padding: 1rem;
            border-radius: 6px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 400px;
            overflow-y: auto;
        }

        .decoder-card {
            background: rgba(16, 185, 129, 0.05);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 6px;
            padding: 1rem;
            margin-top: 0.75rem;
        }

        .decoder-label {
            font-weight: 700;
            font-size: 0.75rem;
            color: var(--success);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }

        .decoder-content {
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            word-break: break-all;
        }

        .splitter {
            width: 6px;
            cursor: col-resize;
            background-color: rgba(255, 255, 255, 0.02);
            align-self: stretch;
            border-left: 1px solid var(--border-color);
            border-right: 1px solid var(--border-color);
            transition: background 0.2s;
        }

        .splitter:hover, .splitter.dragging {
            background-color: var(--accent-primary);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-group">
            <div class="logo-icon">L</div>
            <h1>LocalListener Dashboard</h1>
        </div>
        <div class="controls">
            <div class="url-display" title="Copy webhook URL to clipboard" onclick="copyText('webhook-url-val')">
                <span>Webhook URL:</span>
                <span id="webhook-url-val">http://127.0.0.1:8080/webhook/exfil</span>
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer;"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            </div>
            <div class="url-display" title="Point DNS server here" onclick="copyText('dns-val')">
                <span>DNS UDP server:</span>
                <span id="dns-val">127.0.0.1:1053</span>
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer;"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            </div>
            <button id="clear-btn" class="btn btn-danger">Clear Bin</button>
        </div>
    </header>

    <div class="main-layout">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">Captured Events (<span id="event-count">0</span>)</div>
            </div>
            <ul id="event-list-container" class="event-list">
                <!-- Dynamically populated -->
            </ul>
        </div>
        
        <div id="layout-splitter" class="splitter"></div>

        <!-- Inspector -->
        <div class="inspector">
            <div id="empty-inspector-state" class="empty-state">
                <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2" ry="2"></rect><path d="M12 18h.01M8 14h8M8 10h8M8 6h8"></path></svg>
                <p>No captured requests or DNS resolves selected</p>
            </div>
            
            <div id="inspector-details-panel" style="display: none;">
                <!-- General section -->
                <div class="inspector-section" style="margin-bottom: 1.5rem;">
                    <div class="section-title">Request Summary</div>
                    <table class="key-val-table">
                        <tr><th>Type</th><td id="ins-type">-</td></tr>
                        <tr><th>Timestamp</th><td id="ins-time">-</td></tr>
                        <tr><th>Sender IP</th><td id="ins-ip">-</td></tr>
                        <tr><th>Method</th><td id="ins-method">-</td></tr>
                        <tr><th>Target Destination</th><td id="ins-target" style="color:var(--accent-primary); font-weight:600;">-</td></tr>
                    </table>
                </div>

                <!-- Decodings Section -->
                <div id="ins-decoders-container" class="inspector-section" style="margin-bottom: 1.5rem; display: none;">
                    <div class="section-title">Auto-Decoded Payload Findings</div>
                    <div id="decoders-list">
                        <!-- Populated dynamically -->
                    </div>
                </div>

                <!-- Headers section -->
                <div class="inspector-section" style="margin-bottom: 1.5rem;">
                    <div class="section-title">Request Headers</div>
                    <table id="ins-headers-table" class="key-val-table">
                        <!-- Headers rows populated dynamically -->
                    </table>
                </div>

                <!-- Payload body section -->
                <div class="inspector-section">
                    <div class="section-title">Raw Content Body</div>
                    <pre id="ins-body" class="code-block"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        let events = [];
        let selectedEventId = null;

        // Auto-detect current host to build endpoints dynamically
        const currentHost = window.location.host;
        document.getElementById('webhook-url-val').textContent = `http://${currentHost}/webhook/exfil`;
        document.getElementById('dns-val').textContent = `${window.location.hostname}:1053`;

        async function fetchEvents() {
            try {
                const res = await fetch('/api/events');
                events = await res.json();
                document.getElementById('event-count').textContent = events.length;
                renderEventList();
                if (selectedEventId) {
                    const activeEvent = events.find(e => e.id === selectedEventId);
                    if (activeEvent) {
                        renderEventDetails(activeEvent);
                    }
                }
            } catch (e) {
                console.error("Error loading requests logs:", e);
            }
        }

        function renderEventList() {
            const list = document.getElementById('event-list-container');
            const items = events.map(e => `
                <li class="event-item ${e.id === selectedEventId ? 'active' : ''}" onclick="selectEvent('${e.id}')">
                    <div class="event-meta">
                        <span class="event-type-badge ${e.type.toLowerCase()}">${e.type}</span>
                        <span class="event-time">${e.timestamp.split(' ').pop()}</span>
                    </div>
                    <div class="event-method">${e.method}</div>
                    <div class="event-target" title="${e.target}">${escapeHtml(e.target)}</div>
                </li>
            `).join("");
            list.innerHTML = items || '<div class="empty-state" style="padding:2rem; font-size:0.8rem;">Waiting for incoming Webhook requests or DNS queries...</div>';
        }

        function selectEvent(id) {
            selectedEventId = id;
            const event = events.find(e => e.id === id);
            if (event) {
                renderEventDetails(event);
                renderEventList();
            }
        }

        function renderEventDetails(e) {
            document.getElementById('empty-inspector-state').style.display = 'none';
            document.getElementById('inspector-details-panel').style.display = 'block';

            document.getElementById('ins-type').textContent = e.type;
            document.getElementById('ins-time').textContent = e.timestamp;
            document.getElementById('ins-ip').textContent = e.source_ip;
            document.getElementById('ins-method').textContent = e.method;
            document.getElementById('ins-target').textContent = e.target;

            // Headers
            const headersTable = document.getElementById('ins-headers-table');
            headersTable.innerHTML = Object.entries(e.headers).map(([k, v]) => `
                <tr><th>${k}</th><td>${escapeHtml(v)}</td></tr>
            `).join("");

            // Body
            document.getElementById('ins-body').textContent = e.body || "[Empty Body Payload]";

            // Decoders
            const decodersContainer = document.getElementById('ins-decoders-container');
            const decodersList = document.getElementById('decoders-list');
            if (e.decodings && Object.keys(e.decodings).length > 0) {
                decodersContainer.style.display = 'block';
                decodersList.innerHTML = Object.entries(e.decodings).map(([type, decoded]) => `
                    <div class="decoder-card">
                        <div class="decoder-label">${type}</div>
                        <div class="decoder-content">${escapeHtml(decoded)}</div>
                    </div>
                `).join("");
            } else {
                decodersContainer.style.display = 'none';
            }
        }

        document.getElementById('clear-btn').addEventListener('click', async () => {
            if (!confirm("Clear all captured event logs?")) return;
            try {
                await fetch('/api/events/clear', { method: 'POST' });
                selectedEventId = null;
                document.getElementById('inspector-details-panel').style.display = 'none';
                document.getElementById('empty-inspector-state').style.display = 'flex';
                fetchEvents();
            } catch (e) {
                console.error("Failed clearing logs:", e);
            }
        });

        function escapeHtml(text) {
            return text
                .toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function copyText(id) {
            const text = document.getElementById(id).textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert("Copied to clipboard!");
            });
        }

        // Draggable Splitter
        const splitter = document.getElementById("layout-splitter");
        const sidebar = document.querySelector(".sidebar");
        let startX, startWidth;

        splitter.addEventListener("mousedown", (e) => {
            startX = e.clientX;
            startWidth = sidebar.getBoundingClientRect().width;
            splitter.classList.add("dragging");
            document.addEventListener("mousemove", drag);
            document.addEventListener("mouseup", stopDrag);
            e.preventDefault();
        });

        function drag(e) {
            const width = startWidth + (e.clientX - startX);
            if (width >= 250 && width <= 600) {
                sidebar.style.width = `${width}px`;
            }
        }

        function stopDrag() {
            splitter.classList.remove("dragging");
            document.removeEventListener("mousemove", drag);
            document.removeEventListener("mouseup", stopDrag);
        }

        // Live Poll every 1 second
        setInterval(fetchEvents, 1000);
        fetchEvents();
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    # Start UDP DNS server in background thread
    dns_thread = threading.Thread(target=start_dns_server, kwargs={"port": 1053}, daemon=True)
    dns_thread.start()
    
    # Run FastAPI Server on Port 8080
    uvicorn.run(app, host="127.0.0.1", port=8080)
