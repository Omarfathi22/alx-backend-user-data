#!/usr/bin/env python3
"""
Authentication module for managing user registration, login, sessions, 
and password reset functionalities.
"""

import bcrypt
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound # type: ignore
from uuid import uuid4
from typing import Union


def _hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password as a string.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _generate_uuid() -> str:
    """
    Generates a new UUID as a string.

    Returns:
        str: A unique UUID string.
    """
    return str(uuid4())


class Auth:
    """
    Auth class to interact with the authentication database.
    Handles user registration, session management, and password reset.
    """

    def __init__(self):
        """
        Initializes the Auth instance with a database connection.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> Union[None, User]:
        """
        Registers a new user with the provided email and password.
        If the user already exists, raises a ValueError.

        Args:
            email (str): The user's email address.
            password (str): The user's plaintext password.

        Returns:
            User: The newly created user object.
        """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validates a user's login credentials.

        Args:
            email (str): The user's email address.
            password (str): The user's plaintext password.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))

    def create_session(self, email: str) -> Union[str, None]:
        """
        Creates a new session ID for the user and stores it in the database.

        Args:
            email (str): The user's email address.

        Returns:
            str: The new session ID, or None if the user is not found.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None
        user.session_id = _generate_uuid()
        return user.session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """
        Retrieves a user based on their session ID.

        Args:
            session_id (str): The session ID.

        Returns:
            User: The corresponding user object, or None if not found.
        """
        if session_id is None:
            return None
        try:
            return self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

    def destroy_session(self, user_id: str) -> None:
        """
        Destroys the session for a user by removing their session ID.

        Args:
            user_id (str): The user's unique ID.
        """
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return
        user.session_id = None

    def get_reset_password_token(self, email: str) -> str:
        """
        Generates a password reset token for the user.

        Args:
            email (str): The user's email address.

        Returns:
            str: The generated reset token.

        Raises:
            ValueError: If the email does not exist in the database.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError("User not found")
        user.reset_token = _generate_uuid()
        return user.reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Updates a user's password using their reset token.

        Args:
            reset_token (str): The reset token associated with the user.
            password (str): The new plaintext password.

        Raises:
            ValueError: If the reset token is invalid.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError("Invalid reset token")
        user.hashed_password = _hash_password(password)
        user.reset_token = None
