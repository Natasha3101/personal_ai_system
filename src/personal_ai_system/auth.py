"""Authentication module for the Personal AI System."""

import hashlib
import os
from pathlib import Path

import yaml


class Auth:
    """Simple authentication system for the application."""

    def __init__(self, users_file: str = "data/users.yaml"):
        """Initialize authentication system.

        Args:
            users_file: Path to the users YAML file
        """
        self.users_file = Path(users_file)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)

        # Create default user file if it doesn't exist
        if not self.users_file.exists():
            self._create_default_users()

    def _create_default_users(self) -> None:
        """Create default users file with admin user."""
        default_users = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "email": "admin@personal-ai.local",
                "created_at": "2026-04-08",
            }
        }
        with open(self.users_file, "w") as f:
            yaml.dump(default_users, f)

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            True if authentication successful, False otherwise
        """
        if not self.users_file.exists():
            return False

        with open(self.users_file) as f:
            users = yaml.safe_load(f) or {}

        if username not in users:
            return False

        password_hash = self._hash_password(password)
        return users[username]["password_hash"] == password_hash

    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register a new user.

        Args:
            username: Username
            password: Plain text password
            email: Email address

        Returns:
            True if registration successful, False if user already exists
        """
        with open(self.users_file) as f:
            users = yaml.safe_load(f) or {}

        if username in users:
            return False

        users[username] = {
            "password_hash": self._hash_password(password),
            "email": email,
            "created_at": "2026-04-08",
        }

        with open(self.users_file, "w") as f:
            yaml.dump(users, f)

        return True

    def get_user_info(self, username: str) -> dict | None:
        """Get user information.

        Args:
            username: Username

        Returns:
            User information dictionary or None if not found
        """
        if not self.users_file.exists():
            return None

        with open(self.users_file) as f:
            users = yaml.safe_load(f) or {}

        if username not in users:
            return None

        user_info = users[username].copy()
        user_info.pop("password_hash", None)  # Don't return password hash
        user_info["username"] = username
        return user_info
