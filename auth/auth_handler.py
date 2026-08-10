import json
import os
import bcrypt

USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")

def _load_users():
    if not os.path.exists(USERS_FILE):
        return {"users": {}}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"users": {}}

def _save_users(data):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_email_registered(email):
    """Check if an email is already registered."""
    data = _load_users()
    return email in data.get("users", {})

def create_user(name, email, password):
    """
    Create a new user with a hashed password.
    Returns (True, "Success message") or (False, "Error message").
    """
    if is_email_registered(email):
        return False, "Email is already registered."
    
    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    data = _load_users()
    if "users" not in data:
        data["users"] = {}
        
    data["users"][email] = {
        "name": name,
        "password": hashed_password
    }
    
    _save_users(data)
    return True, "Account created successfully."

def authenticate_user(email, password):
    """
    Authenticate a user by checking the hashed password.
    Returns (True, user_name) if successful, (False, error_msg) if not.
    """
    data = _load_users()
    users = data.get("users", {})
    
    if email not in users:
        return False, "Invalid email or password."
        
    user_data = users[email]
    stored_hash = user_data.get("password", "")
    
    # Verify the password
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, user_data.get("name", "User")
    else:
        return False, "Invalid email or password."
