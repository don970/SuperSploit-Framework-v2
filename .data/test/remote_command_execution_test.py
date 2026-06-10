from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "<h1>Network Diagnostic Tool</h1><p>Use /ping?target=IP to test connectivity.</p>"

@app.route('/ping', methods=['GET'])
def ping():
    # Extract the 'target' parameter from the URL
    target = request.args.get('target', '')
    
    if not target:
        return "Please provide a target to ping. Example: /ping?target=127.0.0.1"
    
    # ⚠️ VULNERABILITY: Directly interpolating user input into a shell command
    command = f"ping -c 3 {target}"
    
    try:
        # shell=True combined with unsanitized input allows arbitrary command injection
        # e.g., target="127.0.0.1; cat /etc/passwd"
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return f"<h3>Ping Results for {target}:</h3><pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<h3>Error executing ping:</h3><pre>{e.output}</pre>"

if __name__ == '__main__':
    print("[*] Starting Vulnerable Network Diagnostic Server on port 8080...")
    print("[*] WARNING: Do not run this on a public-facing network!")
    app.run(host='0.0.0.0', port=8080)
