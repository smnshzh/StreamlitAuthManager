import streamlit as st
import hashlib
import pyodbc
from itsdangerous import URLSafeTimedSerializer
from streamlit_cookies_manager import EncryptedCookieManager

class AuthManager:
    def __init__(self, db_config, secret_key, cookie_key="auth_cookie"):
        """
        Initializes the AuthManager with database configuration, secret key for token management, and cookie key.

        Parameters:
            db_config (dict): Dictionary with database connection details, including DRIVER, SERVER, DATABASE, UID, and PWD.
            secret_key (str): Secret key used for token generation and validation.
            cookie_key (str): Optional; key name for the cookie.
        """
        self.conn_str = (
            f"DRIVER={db_config['DRIVER']};"
            f"SERVER={db_config['SERVER']};"
            f"DATABASE={db_config['DATABASE']};"
            f"UID={db_config['UID']};"
            f"PWD={db_config['PWD']}"
        )
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.cookie_manager = EncryptedCookieManager(key=cookie_key)

    def hash_password(self, password):
        """
        Hashes a password using SHA-256.

        Parameters:
            password (str): The password to be hashed.
        
        Returns:
            str: Hashed password.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        """
        Verifies user credentials by querying the database.

        Parameters:
            username (str): Username of the user.
            password (str): Plain-text password of the user.

        Returns:
            bool: True if credentials are valid, otherwise False.
        """
        hashed_password = self.hash_password(password)
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, hashed_password))
                return cursor.fetchone() is not None
        except Exception as e:
            st.error("Error verifying user: " + str(e))
            return False

    def generate_token(self, user_id, expires_in=3600):
        """
        Generates a timed token for the user.

        Parameters:
            user_id (str): Unique identifier for the user.
            expires_in (int): Expiration time for the token in seconds.

        Returns:
            str: Generated token.
        """
        return self.serializer.dumps(user_id, salt="auth_salt")

    def validate_token(self, token, max_age=3600):
        """
        Validates a token within the expiration period.

        Parameters:
            token (str): Token to be validated.
            max_age (int): Maximum age of the token in seconds.

        Returns:
            str or None: User ID if token is valid; None otherwise.
        """
        try:
            return self.serializer.loads(token, salt="auth_salt", max_age=max_age)
        except Exception:
            return None

    def set_cookie(self, key, value):
        """
        Sets a cookie for maintaining user session.

        Parameters:
            key (str): Cookie key.
            value (str): Cookie value.
        """
        self.cookie_manager[key] = value
        self.cookie_manager.save()

    def get_cookie(self, key):
        """
        Retrieves the value of a cookie.

        Parameters:
            key (str): Cookie key.

        Returns:
            str: Cookie value or None if not found.
        """
        return self.cookie_manager.get(key)

    def logout(self):
        """
        Clears the user session by removing the authentication cookie.
        """
        self.cookie_manager.clear()
        self.cookie_manager.save()
