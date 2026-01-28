#!/bin/bash
# Script setup tự động deploy khi có push lên GitHub
# Sử dụng GitHub Webhook hoặc polling

PROJECT_DIR="/home/ubuntu/exam-scheduler-backend/project"
UPDATE_SCRIPT="$PROJECT_DIR/update_from_git.sh"

# Tạo file webhook listener (đơn giản với Python)
cat > /home/ubuntu/webhook_listener.py << 'EOF'
#!/usr/bin/env python3
import http.server
import subprocess
import json
import hmac
import hashlib

WEBHOOK_SECRET = "your-webhook-secret-here"  # Thay đổi secret này
UPDATE_SCRIPT = "/home/ubuntu/exam-scheduler-backend/project/update_from_git.sh"

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        payload = self.rfile.read(content_length)
        
        # Verify webhook signature (optional but recommended)
        signature = self.headers.get('X-Hub-Signature-256', '')
        if signature:
            expected_signature = 'sha256=' + hmac.new(
                WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                self.send_response(401)
                self.end_headers()
                return
        
        # Parse payload
        try:
            data = json.loads(payload.decode())
            ref = data.get('ref', '')
            
            # Chỉ deploy khi push vào main/master branch
            if 'refs/heads/main' in ref or 'refs/heads/master' in ref:
                # Run update script
                subprocess.Popen(['bash', UPDATE_SCRIPT])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "deploying"}')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "ignored"}')
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Webhook listener is running</h1>')
    
    def log_message(self, format, *args):
        pass  # Disable logging

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', 9000), WebhookHandler)
    print("Webhook listener started on port 9000")
    server.serve_forever()
EOF

chmod +x /home/ubuntu/webhook_listener.py
chmod +x "$UPDATE_SCRIPT"

# Tạo systemd service cho webhook listener
sudo tee /etc/systemd/system/webhook-listener.service > /dev/null << EOF
[Unit]
Description=GitHub Webhook Listener
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/webhook_listener.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Webhook listener setup completed!"
echo ""
echo "Next steps:"
echo "1. Update WEBHOOK_SECRET in /home/ubuntu/webhook_listener.py"
echo "2. Start the service: sudo systemctl start webhook-listener"
echo "3. Enable auto-start: sudo systemctl enable webhook-listener"
echo "4. Open port 9000 in Security Group"
echo "5. Configure GitHub webhook: http://your-ec2-ip:9000"
