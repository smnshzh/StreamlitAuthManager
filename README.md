
# AuthManager Module

The `AuthManager` module provides a class-based solution for handling user authentication in a Streamlit app. This includes functionalities for secure login, logout, session tracking, and token-based authentication, making it reusable and adaptable across different client projects.

## Features

- **User Verification**: Authenticates users by verifying their credentials with a SQL Server database.
- **Token Management**: Generates and validates tokens with configurable expiration for secure session handling.
- **Secure Cookie Management**: Uses encrypted cookies to maintain user sessions.
- **Password Hashing**: Ensures secure password storage with SHA-256 hashing.

## Requirements

Install the following dependencies:

```bash
pip install streamlit pyodbc itsdangerous streamlit-cookies-manager
```

## Setup

1. Clone this repository and add `auth.py` to your Streamlit app directory.
2. Prepare your database and connection configuration with user credentials.

## Usage

### 1. Initialize the `AuthManager` Class

Set up your database configuration and secret key, and initialize `AuthManager` as follows:

```python
from auth import AuthManager

db_config = {
    "DRIVER": "{ODBC Driver 17 for SQL Server}",
    "SERVER": ".",
    "DATABASE": "appdb",
    "UID": "sa",
    "PWD": "YourPassword"
}
secret_key = "your_secret_key"
auth_manager = AuthManager(db_config, secret_key)
```

### 2. Verify User Credentials

Verify user login details with `verify_user`:

```python
if auth_manager.verify_user("username", "password"):
    st.success("Logged in successfully!")
else:
    st.error("Invalid username or password.")
```

### 3. Token Generation and Validation

Generate a token upon successful login and validate it to maintain the session:

```python
# Generate token for user session
token = auth_manager.generate_token("user_id")

# Validate the token within the specified expiration time
user_id = auth_manager.validate_token(token)
if user_id:
    st.write("Token is valid for user:", user_id)
else:
    st.error("Token is invalid or expired.")
```

### 4. Cookie Management

Set and retrieve cookies to maintain sessions across app visits:

```python
# Set a session cookie
auth_manager.set_cookie("auth_token", token)

# Retrieve the session cookie
session_token = auth_manager.get_cookie("auth_token")

# Log out and clear session
auth_manager.logout()
```

## Example Streamlit App Integration

Integrate `AuthManager` in your Streamlit app to enable secure user authentication:

```python
import streamlit as st
from auth import AuthManager

# Initialize AuthManager
auth_manager = AuthManager(db_config, secret_key)

if "username" in st.session_state:
    st.write(f"Welcome back, {st.session_state['username']}!")
    if st.button("Logout"):
        auth_manager.logout()
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if auth_manager.verify_user(username, password):
            token = auth_manager.generate_token(username)
            auth_manager.set_cookie("auth_token", token)
            st.session_state["username"] = username
            st.success("Logged in successfully!")
        else:
            st.error("Invalid login credentials.")
```

## Configuration

- **Database**: Set the database connection details (`DRIVER`, `SERVER`, `DATABASE`, `UID`, `PWD`) as shown.
- **Secret Key**: Provide a unique, secure `secret_key` for token management.
- **Cookie Key**: Customize the `cookie_key` if needed to specify the name of the authentication cookie.

## License

This project is licensed under the MIT License.
