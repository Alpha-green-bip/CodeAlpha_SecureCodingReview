# ============================================================
#  VULNERABLE CODE — DO NOT USE IN PRODUCTION
#  This is intentionally bad code for educational purposes
# ============================================================

import sqlite3
import hashlib
import os
import subprocess
import pickle

# -------------------------------------------
# VULNERABILITY 1: SQL Injection
# -------------------------------------------
def login(username, password):
    """
    BAD CODE: Directly uses user input in SQL query.
    Attacker can type: ' OR '1'='1 to bypass login!
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # ❌ VULNERABLE: String formatting in SQL = SQL Injection
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    return result

# -------------------------------------------
# VULNERABILITY 2: Weak Password Hashing
# -------------------------------------------
def store_password(password):
    """
    BAD CODE: MD5 is broken and should never be used for passwords.
    """
    # ❌ VULNERABLE: MD5 is cracked easily using rainbow tables
    hashed = hashlib.md5(password.encode()).hexdigest()
    return hashed

# -------------------------------------------
# VULNERABILITY 3: Command Injection
# -------------------------------------------
def check_host(hostname):
    """
    BAD CODE: User input passed directly to shell command.
    Attacker can type: google.com; rm -rf /  (deletes everything!)
    """
    # ❌ VULNERABLE: shell=True with user input = Command Injection
    result = subprocess.run("ping -c 1 " + hostname, shell=True, capture_output=True)
    return result.stdout

# -------------------------------------------
# VULNERABILITY 4: Insecure File Handling
# -------------------------------------------
def read_file(filename):
    """
    BAD CODE: No path validation. Attacker can read any system file.
    Attacker passes: ../../etc/passwd  (reads sensitive system files)
    """
    # ❌ VULNERABLE: Path traversal attack possible
    with open(filename, 'r') as f:
        return f.read()

# -------------------------------------------
# VULNERABILITY 5: Hardcoded Credentials
# -------------------------------------------
# ❌ VULNERABLE: Secrets in source code = anyone who sees code gets them
DB_PASSWORD = "admin123"
SECRET_KEY  = "mysecretkey2024"
API_KEY     = "sk-1234567890abcdef"

# -------------------------------------------
# VULNERABILITY 6: Insecure Deserialization
# -------------------------------------------
def load_user_data(data):
    """
    BAD CODE: pickle.loads() on untrusted data can execute arbitrary code!
    """
    # ❌ VULNERABLE: Can run malicious code hidden in data
    user = pickle.loads(data)
    return user

# -------------------------------------------
# VULNERABILITY 7: No Input Validation
# -------------------------------------------
def set_user_age(age):
    """
    BAD CODE: No validation means age could be -999 or "hello"
    """
    # ❌ VULNERABLE: No type/range checking
    return f"User age is: {age}"
