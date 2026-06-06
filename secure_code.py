# ============================================================
#  SECURE CODE — Fixed version of vulnerable_code.py
#  CodeAlpha Internship Task 3 — Secure Coding Review
# ============================================================

import sqlite3
import hashlib
import os
import subprocess
import json
import re
import secrets
import logging

# Setup logging (always log security events!)
logging.basicConfig(
    filename='security.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------------------------------
# FIX 1: SQL Injection → Use Parameterized Queries
# -------------------------------------------
def login(username, password):
    """
    SECURE: Uses parameterized queries — SQL Injection impossible.
    The database treats input as DATA not as CODE.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # ✅ SECURE: Use ? placeholders — user input never touches SQL structure
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    
    # Hash the password before comparing
    hashed_password = hash_password(password)
    cursor.execute(query, (username, hashed_password))  # Input is a PARAMETER
    
    result = cursor.fetchone()
    conn.close()
    return result


# -------------------------------------------
# FIX 2: Weak Hashing → Use bcrypt/SHA-256 + Salt
# -------------------------------------------
def hash_password(password):
    """
    SECURE: Uses SHA-256 with a random salt.
    Ideally use bcrypt library (pip install bcrypt) for even better security.
    """
    # ✅ SECURE: Generate a random salt (different each time!)
    salt = secrets.token_hex(32)
    
    # SHA-256 with salt is far stronger than plain MD5
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    
    # Store "salt:hash" together so we can verify later
    return f"{salt}:{hashed}"

def verify_password(stored_hash, input_password):
    """Verify password by re-hashing with same salt"""
    salt, original_hash = stored_hash.split(":", 1)
    input_hash = hashlib.sha256((salt + input_password).encode()).hexdigest()
    return secrets.compare_digest(input_hash, original_hash)  # Timing-safe comparison


# -------------------------------------------
# FIX 3: Command Injection → Use list args, no shell=True
# -------------------------------------------
def check_host(hostname):
    """
    SECURE: Pass command as a LIST, never as a string.
    Also validate the input first.
    """
    # ✅ Input Validation: Only allow valid hostnames/IPs
    # This regex only allows letters, numbers, dots, hyphens
    if not re.match(r'^[a-zA-Z0-9.\-]+$', hostname):
        logging.warning(f"Invalid hostname attempted: {hostname}")
        raise ValueError("Invalid hostname! Only alphanumeric characters allowed.")
    
    # ✅ SECURE: Use list, NO shell=True — no injection possible
    result = subprocess.run(
        ["ping", "-c", "1", hostname],  # Each arg is separate
        shell=False,                     # NEVER True with user input!
        capture_output=True,
        timeout=10                       # Prevent hanging
    )
    return result.stdout.decode()


# -------------------------------------------
# FIX 4: Path Traversal → Validate and Restrict Path
# -------------------------------------------
def read_file(filename):
    """
    SECURE: Restricts file reading to a safe directory only.
    """
    # ✅ Define a SAFE base directory (only read from here)
    safe_directory = os.path.abspath("./safe_files/")
    
    # Build the full path and resolve it (removes ../ tricks)
    requested_path = os.path.abspath(os.path.join(safe_directory, filename))
    
    # ✅ Check the resolved path STARTS with safe directory
    if not requested_path.startswith(safe_directory):
        logging.warning(f"Path traversal attempt: {filename}")
        raise PermissionError("Access denied! Cannot read files outside safe directory.")
    
    # Check file exists
    if not os.path.isfile(requested_path):
        raise FileNotFoundError(f"File not found: {filename}")
    
    with open(requested_path, 'r') as f:
        return f.read()


# -------------------------------------------
# FIX 5: Hardcoded Credentials → Use Environment Variables
# -------------------------------------------
# ✅ SECURE: Load secrets from environment, never hardcode!
# Set these in your system before running:
#   export DB_PASSWORD="your_password"
#   export SECRET_KEY="your_secret"
#   export API_KEY="your_api_key"

DB_PASSWORD = os.environ.get("DB_PASSWORD")
SECRET_KEY  = os.environ.get("SECRET_KEY")
API_KEY     = os.environ.get("API_KEY")

# Warn if secrets are missing
if not DB_PASSWORD or not SECRET_KEY:
    logging.error("Required environment variables are not set!")
    raise EnvironmentError("Please set DB_PASSWORD and SECRET_KEY environment variables")


# -------------------------------------------
# FIX 6: Insecure Deserialization → Use JSON Instead
# -------------------------------------------
def load_user_data(data):
    """
    SECURE: Use JSON — it cannot execute arbitrary code.
    pickle should NEVER be used with untrusted data.
    """
    try:
        # ✅ SECURE: JSON parses only data, cannot execute code
        user = json.loads(data)
        return user
    except json.JSONDecodeError:
        logging.warning("Invalid JSON data received")
        raise ValueError("Invalid data format")


# -------------------------------------------
# FIX 7: Input Validation → Always Validate!
# -------------------------------------------
def set_user_age(age):
    """
    SECURE: Validate type and range before using input.
    """
    # ✅ Type check
    if not isinstance(age, int):
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValueError("Age must be a number!")
    
    # ✅ Range check
    if not (0 <= age <= 120):
        raise ValueError("Age must be between 0 and 120!")
    
    return f"User age is: {age}"
