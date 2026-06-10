#!/usr/bin/env python3
"""Warning: Never run this server on a public-facing network.
It is designed to be exploited and provides a direct path for 
an attacker to compromise the host machine. Run it only in a local,
isolated virtual environment."""

import sqlite3
import os
import pickle
import base64
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Setup a dummy database in memory
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.execute("CREATE TABLE users (id INTEGER, username TEXT, secret TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'admin', 'FLAG{SQL_INJECTION_MASTER}')")
    return conn

db = init_db()

@app.route('/')
def home():
    return """
    <h1>VulnServer v1.0</h1>
    <ul>
        <li><a href="/ping?host=8.8.8.8">Network Diagnostics (Ping)</a></li>
        <li><a href="/user?id=1">User Lookup</a></li>
        <li><a href="/load_session?data=gASVBQAAAAAAAACMCWhlbGxvX3dvcmSULg==">Restore Session (Beta)</a></li>
    </ul>
    """

# 1. Command Injection Vulnerability
@app.route('/ping')
def ping():
    host = request.args.get('host')
    # UNSAFE: Directly passing user input to the shell
    command = f"ping -c 1 {host}"
    output = os.popen(command).read()
    return f"<pre>{output}</pre>"

# 2. SQL Injection (SQLi) Vulnerability
@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    # UNSAFE: Using f-strings instead of parameterized queries
    query = f"SELECT username, secret FROM users WHERE id = {user_id}"
    cursor = db.execute(query)
    result = cursor.fetchone()
    return f"User Info: {result}"

# 3. Insecure Deserialization (Pickle)
@app.route('/load_session')
def load_session():
    data = request.args.get('data')
    # UNSAFE: Unpickling untrusted data
    decoded_data = base64.b64decode(data)
    obj = pickle.loads(decoded_data)
    return f"Session restored for: {obj}"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)