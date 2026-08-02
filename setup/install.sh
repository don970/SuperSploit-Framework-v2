#!/bin/bash

# SuperSploit Framework Automated Installer
# This script sets up necessary directories, initializes databases, and configures permissions.

echo "=========================================="
echo " SuperSploit Framework Installation"
echo "=========================================="

# --- Configuration ---
SUPERSSPLOIT_HOME="/home/donald/.SuperSploit" # Base directory for SuperSploit data
SOURCE_DIR="$SUPERSSPLOIT_HOME/source"
DATA_DIR="$SUPERSSPLOIT_HOME/data"
LOG_DIR="$SUPERSSPLOIT_HOME/logs"
DB_DIR="$SUPERSSPLOIT_HOME/db"
TOOLS_DIR="$SUPERSSPLOIT_HOME/tools"

# --- Pre-installation Checks ---
echo "[*] Checking for root privileges..."
if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run this script with sudo: sudo ./setup/install.sh"
  exit 1
fi

echo "[*] Checking Python 3.8+ installation..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
  echo "[-] Python 3.8 or higher is required. Detected: $PYTHON_VERSION"
  echo "    Please install Python 3.8+ and try again."
  exit 1
fi

# --- Directory Setup ---
echo "[*] Creating SuperSploit home directory structure..."
mkdir -p "$SUPERSSPLOIT_HOME"
mkdir -p "$SOURCE_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$DB_DIR"
mkdir -p "$TOOLS_DIR"

# Copy core framework files (assuming current directory is the cloned repo root)
echo "[*] Copying framework source files..."
cp -r ../.data "$SUPERSSPLOIT_HOME/"
cp -r ../docs "$SUPERSSPLOIT_HOME/"
cp -r ../modules "$SUPERSSPLOIT_HOME/"
cp -r ../SuperSploit.py "$SUPERSSPLOIT_HOME/"
cp -r ../LICENSE* "$SUPERSSPLOIT_HOME/"
cp -r ../README.md "$SUPERSSPLOIT_HOME/"
cp -r ../CONTRIBUTING.md "$SUPERSSPLOIT_HOME/"
cp -r ../CODE_OF_CONDUCT.md "$SUPERSSPLOIT_HOME/"
cp -r ../SECURITY.md "$SUPERSSPLOIT_HOME/"
cp -r ../CHANGELOG.md "$SUPERSSPLOIT_HOME/"
cp -r ../ROADMAP.md "$SUPERSSPLOIT_HOME/"
cp -r ../PRIVACY_POLICY.md "$SUPERSSPLOIT_HOME/"

# --- Database Initialization ---
echo "[*] Initializing SuperSploit databases..."
# This assumes your framework will create/manage SQLite DBs in $DB_DIR
# You might need to add specific commands here to initialize schema if not done by the app on first run
touch "$DB_DIR/targets.sqlite" # Placeholder for main targets database
touch "$DB_DIR/sessions.sqlite" # Placeholder for C2 sessions database

# --- Permissions Configuration ---
echo "[*] Setting appropriate permissions..."
chmod -R 755 "$SUPERSSPLOIT_HOME" # General read/execute for others, write for owner
chmod 700 "$DB_DIR" # Restrict access to database directory
chmod 600 "$DB_DIR"/*.sqlite # Restrict access to database files
chmod +x "$SUPERSSPLOIT_HOME/SuperSploit.py" # Make main script executable

echo "[*] Installation complete!"
echo "    You can now run SuperSploit from: $SUPERSSPLOIT_HOME/SuperSploit.py"
echo "    Consider adding $SUPERSSPLOIT_HOME to your PATH for easier access."
echo "=========================================="