"""
SuperSploit Command Center REST API
Provides a secure gateway for the Android Flagship App to interact with the framework.
"""

import sys
import os
import json
import secrets
from flask import Flask, request, jsonify, send_file
from functools import wraps

# Framework Integration
api_dir = os.path.dirname(os.path.abspath(__file__))
framework_root = os.path.abspath(os.path.join(api_dir, "..", ".."))
source_dir = os.path.join(framework_root, "source")

if source_dir not in sys.path:
    sys.path.append(source_dir)

from core.database import DatabaseManagment

app = Flask(__name__)

# Security: Load or generate API Key
config_path = os.path.join(framework_root, ".data", ".config", "api_config.json")
if not os.path.exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    api_key = secrets.token_hex(32)
    with open(config_path, "w") as f:
        json.dump({"api_key": api_key}, f)
else:
    with open(config_path, "r") as f:
        api_key = json.load(f).get("api_key")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        provided_key = request.headers.get("X-API-Key")
        if not provided_key or provided_key != api_key:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# --- Endpoints ---

@app.route("/api/v1/status", methods=["GET"])
@require_auth
def get_status():
    return jsonify({
        "status": "online",
        "framework": "SuperSploit v2.2",
        "workspaces": DatabaseManagment.get_active_workspace()
    })

@app.route("/api/v1/profiles", methods=["GET"])
@require_auth
def list_profiles():
    profiles = DatabaseManagment.getProfiles()
    return jsonify(dict(profiles))

@app.route("/api/v1/profiles/<name>", methods=["GET"])
@require_auth
def get_profile(name):
    profiles = DatabaseManagment.getProfiles()
    if name in profiles:
        return jsonify(profiles[name])
    return jsonify({"error": "Profile not found"}), 404

@app.route("/api/v1/targets", methods=["GET"])
@require_auth
def list_targets():
    return jsonify(DatabaseManagment.getTargets())

@app.route("/api/v1/recon/modules", methods=["GET"])
@require_auth
def list_modules():
    db, all_files = DatabaseManagment.UpdateReconDB()
    # Format: { "category": ["module_name", ...] }
    formatted = {}
    for cat, paths in db.items():
        formatted[cat] = [os.path.basename(p) for p in paths]
    return jsonify(formatted)

@app.route("/api/v1/recon/run", methods=["POST"])
@require_auth
def run_recon():
    data = request.json
    module_name = data.get("module")
    target = data.get("target")
    args = data.get("args", []) # Optional extra args

    if not module_name or not target:
        return jsonify({"error": "Missing module or target"}), 400

    # Resolve module path
    db, all_files = DatabaseManagment.UpdateReconDB()
    module_path = None
    for p in all_files:
        if os.path.basename(p) == module_name:
            module_path = p
            break
    
    if not module_path:
        return jsonify({"error": "Module not found"}), 404

    # Trigger via background subprocess to avoid blocking the API
    # We use the framework's internal logic as much as possible
    try:
        import subprocess
        # Set R_HOST in the database first so the module picks it up
        db_inst = DatabaseManagment.get()
        db_inst["R_HOST"] = target
        db_inst["RECON_NAME"] = module_name
        db_inst["RECON_PATH"] = module_path
        
        # We spawn a detached process that runs a small wrapper to trigger the Recon engine
        # This is a bit of a hack but ensures the Recon() class logic (hooks, etc) is used.
        trigger_cmd = f"from core.recon_engine import Recon; Recon()"
        # Note: This might still prompt for [y/n] module run if we're not careful.
        # For the API, we should probably force 'module' mode.
        
        # PROD VERSION: Use a task queue like Celery or a simple job manager.
        # MVP VERSION: Subprocess.
        subprocess.Popen([
            sys.executable, "-c", 
            f"import sys; sys.path.append('{source_dir}'); from core.database import DatabaseManagment; db=DatabaseManagment.get(); db['R_HOST']='{target}'; db['RECON_NAME']='{module_name}'; db['RECON_PATH']='{module_path}'; from core.recon_engine import Recon; r=Recon()"
        ], start_new_session=True)

        return jsonify({
            "status": "started",
            "module": module_name,
            "target": target
        }), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/loot/reports", methods=["GET"])
@require_auth
def list_reports():
    loot_dir = os.path.join(DatabaseManagment.getInstall(), ".data", ".loot", "reports")
    if not os.path.exists(loot_dir):
        return jsonify([])
    
    reports = []
    for f in os.listdir(loot_dir):
        if f.endswith(".pdf"):
            reports.append({
                "filename": f,
                "path": os.path.join(loot_dir, f),
                "size": os.path.getsize(os.path.join(loot_dir, f))
            })
    return jsonify(reports)

@app.route("/api/v1/loot/reports/<filename>", methods=["GET"])
@require_auth
def download_report(filename):
    loot_dir = os.path.join(DatabaseManagment.getInstall(), ".data", ".loot", "reports")
    report_path = os.path.join(loot_dir, filename)
    if os.path.exists(report_path) and filename.endswith(".pdf"):
        return send_file(report_path)
    return jsonify({"error": "Report not found"}), 404

if __name__ == "__main__":
    print(f"[*] SuperSploit Command Center API Starting...")
    print(f"[*] API Key for Mobile App: {api_key}")
    # In production, use a real WSGI server with TLS
    app.run(host="0.0.0.0", port=8443, debug=False)
