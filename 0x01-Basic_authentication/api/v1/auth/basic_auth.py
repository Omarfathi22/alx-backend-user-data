#!/usr/bin/env python3
"""
Module for authentication using Basic Auth.
"""

from typing import TypeVar
from api.v1.auth.auth import Auth
import base64
from models.user import User


class BasicAuth(Auth):
    """Basic Authentication class inheriting from the base Auth class.
    
    This class implements the basic HTTP authentication using a username and password
    passed in an HTTP header in the form of Base64 encoded string.
    """

    def extract_base64_authorization_header(self, authorization_header: str) -> str:
        """
        Extracts the base64 encoded authorization token from the authorization header.

        Args:
            authorization_header (str): The Authorization header value.

        Returns:
            str: The base64 encoded token or None if not found or the format is incorrect.
        """
        if not authorization_header or not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith('Basic '):
            return None

        return authorization_header.split(' ')[-1]

    def decode_base64_authorization_header(self, base64_authorization_header: str) -> str:
        """
        Decodes the Base64 encoded authorization header to get the user credentials.

        Args:
            base64_authorization_header (str): The Base64 encoded authorization string.

        Returns:
            str: The decoded string (username:password) or None if decoding fails.
        """
        if not base64_authorization_header or not isinstance(base64_authorization_header, str):
            return None

        try:
            decoded_bytes = base64.b64decode(base64_authorization_header.encode('utf-8'))
            return decoded_bytes.decode('utf-8')
        except (base64.binascii.Error, UnicodeDecodeError):
            return None

    def extract_user_credentials(self, decoded_base64_authorization_header: str) -> (str, str): # type: ignore
        """
        Extracts the email and password from the decoded base64 string.

        Args:
            decoded_base64_authorization_header (str): The decoded string containing 'email:password'.

        Returns:
            tuple: A tuple containing the email and password, or (None, None) if invalid format.
        """
        if not decoded_base64_authorization_header or not isinstance(decoded_base64_authorization_header, str):
            return None, None
        if ':' not in decoded_base64_authorization_header:
            return None, None

        email, password = decoded_base64_authorization_header.split(':', 1)
        return email, password

    def user_object_from_credentials(self, user_email: str, user_pwd: str) -> TypeVar('User'): # type: ignore
        """
        Retrieves the user object based on email and password credentials.

        Args:
            user_email (str): The email of the user.
            user_pwd (str): The password of the user.

        Returns:
            User: The user object if valid credentials are found, or None if not.
        """
        if not user_email or not isinstance(user_email, str):
            return None
        if not user_pwd or not isinstance(user_pwd, str):
            return None

        try:
            users = User.search({"email": user_email})
            if not users:
                return None

            for user in users:
                if user.is_valid_password(user_pwd):
                    return user
            return None
        except Exception as e:
            return None

    def current_user(self, request=None) -> TypeVar('User'): # type: ignore
        """
        Returns the current user based on the authorization header in the request.

        Args:
            request (FlaskRequest): The incoming HTTP request.

        Returns:
            User: The authenticated user, or None if no valid authentication found.
        """
        auth_header = self.authorization_header(request)
        if auth_header:
            token = self.extract_base64_authorization_header(auth_header)
            if token:
                decoded = self.decode_base64_authorization_header(token)
                if decoded:
                    email, password = self.extract_user_credentials(decoded)
                    if email:
                        return self.user_object_from_credentials(email, password)

        return None
