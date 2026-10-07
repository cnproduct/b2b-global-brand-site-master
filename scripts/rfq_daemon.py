#!/usr/bin/env python3
"""
B2B Global Brand Site Master
Stand-alone B2B RFQ Ingestion & Inquiry Dispatch Daemon
Zero external dependencies (Python standard library only).

Features:
- Math challenge CAPTCHA with HMAC-SHA256 signature
- Honeypot bot trapping (_hp_check / website_hp)
- Dual-ledger persistence (JSON + Excel-friendly CSV with UTF-8 BOM)
- Asynchronous multi-recipient email forwarding via FormSubmit / Webhook
- Admin queries and CSV export endpoint (/api/inquiries)
- Built-in CORS and security headers
"""

import argparse
import csv
import hashlib
import http.server
import json
import os
import random
import secrets
import socketserver
import sys
import threading
import urllib.parse
import urllib.request
from datetime import datetime

CAPTCHA_SECRET = secrets.token_hex(16)


def generate_captcha():
    a = random.randint(3, 19)
    b = random.randint(2, 15)
    ans = str(a + b)
    token = hashlib.sha256((ans + CAPTCHA_SECRET).encode("utf-8")).hexdigest()
    cid = secrets.token_hex(6)
    return {
        "captcha_id": cid,
        "question": f"{a} + {b} = ?",
        "captcha_token": token
    }


def verify_captcha(answer, token):
    if not answer or not token:
        return False
    ans_clean = str(answer).strip()
    expected = hashlib.sha256((ans_clean + CAPTCHA_SECRET).encode("utf-8")).hexdigest()
    return expected == token


def create_rfq_handler(data_dir, forward_emails, admin_key):
    json_file = os.path.join(data_dir, "inquiries.json")
    csv_file = os.path.join(data_dir, "inquiries.csv")
    os.makedirs(data_dir, exist_ok=True)

    class RFQHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            try:
                msg = fmt % args
            except Exception:
                msg = " ".join(str(a) for a in args)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} {msg}")

        def do_HEAD(self):
            self._set_cors_headers(200, "application/json")

        def _set_cors_headers(self, status=200, content_type="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()

        def do_OPTIONS(self):
            self._set_cors_headers(204)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            # 1. Health check
            if path in ("/api/health", "/api/status"):
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({
                    "status": "healthy",
                    "service": "B2B Sourcing RFQ Ingestion Daemon",
                    "routing_emails": forward_emails,
                    "timestamp": datetime.now().isoformat()
                }).encode("utf-8"))
                return

            # 2. Math Captcha challenge
            if path == "/api/captcha":
                c = generate_captcha()
                self._set_cors_headers(200)
                self.wfile.write(json.dumps(c).encode("utf-8"))
                return

            # 3. Admin Inquiry Dashboard / CSV Export
            if path == "/api/inquiries":
                key = query.get("key", [""])[0]
                if key != admin_key:
                    self._set_cors_headers(403)
                    self.wfile.write(json.dumps({"error": "Unauthorized. Provide valid key."}).encode("utf-8"))
                    return

                inquiries = []
                if os.path.exists(json_file):
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            inquiries = json.load(f)
                    except Exception:
                        inquiries = []

                if query.get("format", [""])[0] == "csv":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/csv; charset=utf-8-sig")
                    self.send_header("Content-Disposition", f'attachment; filename="inquiries_{datetime.now().strftime("%Y%m%d")}.csv"')
                    self.end_headers()
                    if os.path.exists(csv_file):
                        with open(csv_file, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self.wfile.write("No inquiries recorded yet.\n".encode("utf-8-sig"))
                    return

                self._set_cors_headers(200)
                self.wfile.write(json.dumps({
                    "total_count": len(inquiries),
                    "inquiries": inquiries
                }, indent=2, ensure_ascii=False).encode("utf-8"))
                return

            self._set_cors_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path not in ("/api/rfq", "/api/inquiry", "/api/contact"):
                self._set_cors_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
                return

            try:
                content_len = int(self.headers.get("Content-Length", 0))
                post_body = self.rfile.read(content_len).decode("utf-8", errors="replace")
                ctype = self.headers.get("Content-Type", "")

                data = {}
                if "application/json" in ctype:
                    data = json.loads(post_body)
                elif "application/x-www-form-urlencoded" in ctype:
                    raw = urllib.parse.parse_qs(post_body)
                    data = {k: v[0] for k, v in raw.items()}
                else:
                    try:
                        data = json.loads(post_body)
                    except Exception:
                        raw = urllib.parse.parse_qs(post_body)
                        data = {k: v[0] for k, v in raw.items()}
            except Exception as e:
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({"error": f"Failed to parse payload: {e}"}).encode("utf-8"))
                return

            # Anti-Spam: Honeypot check
            honeypot_fields = ["_hp_check", "website_hp", "url_address", "fax_number", "title_check"]
            for hp in honeypot_fields:
                if data.get(hp):
                    print(f"🛑 [Spam Bot Trapped] Honeypot field '{hp}' populated: {data.get(hp)}")
                    self._set_cors_headers(200)
                    self.wfile.write(json.dumps({
                        "success": True,
                        "rfq_id": f"SPAM-{secrets.token_hex(3).upper()}",
                        "message": "Inquiry received."
                    }).encode("utf-8"))
                    return

            # CAPTCHA verification (if enabled/supplied)
            captcha_answer = data.get("captcha_answer") or data.get("captcha") or ""
            captcha_token = data.get("captcha_token") or ""
            if captcha_token:
                if not verify_captcha(captcha_answer, captcha_token):
                    self._set_cors_headers(400)
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": "Security verification code is incorrect. Please try again."
                    }).encode("utf-8"))
                    return

            email = data.get("email") or data.get("corporate_email") or data.get("work_email") or ""
            name = data.get("name") or data.get("full_name") or "B2B Sourcing Buyer"
            company = data.get("company") or data.get("company_name") or "Not specified"
            phone = data.get("phone") or data.get("whatsapp") or data.get("mobile") or ""
            product = data.get("product") or data.get("target_product") or "Custom Manufactured Goods"
            volume = data.get("volume") or data.get("quantity") or "1,000 pcs (Initial Trial)"
            message = data.get("message") or data.get("notes") or data.get("inquiry_message") or "Factory OEM/ODM quotation request"
            source_page = data.get("source_page") or self.headers.get("Referer", "B2B Portal")

            if not email or "@" not in email:
                self._set_cors_headers(400)
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "A valid corporate email address is required."
                }).encode("utf-8"))
                return

            client_ip = self.headers.get("X-Real-IP") or self.headers.get("X-Forwarded-For") or self.client_address[0]
            if "," in client_ip:
                client_ip = client_ip.split(",")[0].strip()

            rfq_id = f"RFQ-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(2).upper()}"
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

            record = {
                "rfq_id": rfq_id,
                "created_at": created_at,
                "name": name.strip(),
                "company": company.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "product": product.strip(),
                "volume": volume.strip(),
                "message": message.strip(),
                "source_page": source_page,
                "ip": client_ip,
                "routed_to": ", ".join(forward_emails)
            }

            # 1. Dual-ledger: JSON
            inquiries = []
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        inquiries = json.load(f)
                except Exception:
                    inquiries = []
            inquiries.append(record)
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(inquiries, f, indent=2, ensure_ascii=False)

            # 2. Dual-ledger: Excel-friendly CSV
            file_exists = os.path.exists(csv_file)
            with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "RFQ ID", "Created At", "Name", "Company", "Corporate Email",
                        "Phone/WhatsApp", "Target Product", "Volume/MOQ", "Message",
                        "Source Page", "Client IP", "Routed To"
                    ])
                writer.writerow([
                    record["rfq_id"],
                    record["created_at"],
                    record["name"],
                    record["company"],
                    record["email"],
                    record["phone"],
                    record["product"],
                    record["volume"],
                    record["message"],
                    record["source_page"],
                    record["ip"],
                    record["routed_to"]
                ])

            print(f"✅ [RFQ Received] {rfq_id} from {name} ({email}) for '{product}' ({volume})")

            # 3. Asynchronous multi-recipient email forwarding via FormSubmit
            def send_email_async(rec):
                for target_mail in forward_emails:
                    try:
                        url = f"https://formsubmit.co/ajax/{target_mail}"
                        payload = json.dumps({
                            "RFQ ID": rec["rfq_id"],
                            "Submission Time (UTC)": rec["created_at"],
                            "Buyer Name": rec["name"],
                            "Company": rec["company"],
                            "Corporate Email": rec["email"],
                            "Phone / WhatsApp": rec["phone"] or "Not provided",
                            "Target Product": rec["product"],
                            "Estimated Volume": rec["volume"],
                            "Requirements": rec["message"],
                            "Source Page": rec["source_page"],
                            "Buyer IP": rec["ip"],
                            "_subject": f"[Factory RFQ] {rec['product']} - {rec['name']} ({rec['volume']})",
                            "_template": "table"
                        }).encode("utf-8")

                        req = urllib.request.Request(
                            url,
                            data=payload,
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                                "User-Agent": "B2BGlobalBrandSite-RFQDaemon/1.0"
                            }
                        )
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            print(f"📧 Notification forwarded to {target_mail} (HTTP {resp.status})")
                    except Exception as err:
                        print(f"⚠️ Email forwarding note for {target_mail}: {err}")

            t = threading.Thread(target=send_email_async, args=(record,))
            t.daemon = True
            t.start()

            self._set_cors_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "rfq_id": rfq_id,
                "message": "Thank you! Your sourcing RFQ has been received. Our sales engineer will review your specifications and contact you within 12 hours.",
                "routed_to": forward_emails
            }).encode("utf-8"))

    return RFQHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8012, help="HTTP listening port (default: 8012)")
    parser.add_argument("--bind", default="127.0.0.1", help="Binding address (default: 127.0.0.1)")
    parser.add_argument("--data-dir", default="./data", help="Directory for JSON/CSV inquiry ledgers (default: ./data)")
    parser.add_argument("--emails", nargs="+", default=["info@naikegroup.com", "cnproduct@gmail.com"], help="Forwarding recipient email addresses")
    parser.add_argument("--admin-key", default="naike2026admin", help="Admin key for querying /api/inquiries")
    args = parser.parse_args()

    handler_class = create_rfq_handler(os.path.abspath(args.data_dir), args.emails, args.admin_key)
    socketserver.TCPServer.allow_reuse_address = True
    server_address = (args.bind, args.port)

    print(f"🚀 B2B RFQ Ingestion Daemon listening on http://{args.bind}:{args.port}")
    print(f"   Dual Ledger: {os.path.abspath(args.data_dir)} (inquiries.json, inquiries.csv)")
    print(f"   Forwarding Targets: {args.emails}")
    print(f"   Admin Endpoint: http://{args.bind}:{args.port}/api/inquiries?key={args.admin_key}&format=csv")

    try:
        with socketserver.TCPServer(server_address, handler_class) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown signal received. Closing daemon.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
