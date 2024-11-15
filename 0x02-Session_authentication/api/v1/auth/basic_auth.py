#!/usr/bin/env python3
"""
Module for authentication using Basic Auth.

This module provides methods for handling authentication using Basic Auth,
including extracting and decoding the authorization header, extracting user
credentials from it, and verifying those credentials to retrieve the associated
user object.
"""

from typing import TypeVar
from api.v1.auth.auth import Auth
import base64
from models.user import User


class BasicAuth(Auth):
    """
    Basic Authentication class for handling the extraction and validation 
    of Basic Auth credentials from HTTP requests.

    This class extends the Auth base class and implements methods to extract 
    the authorization header, decode it, and validate user credentials.
    """

    def extract_base64_authorization_header(self, authorization_header: str) -> str:
        """
        Extracts the Base64-encoded authorization token from the 'Authorization'
        header if it is in the correct format.

        Args:
            authorization_header (str): The 'Authorization' header from the HTTP request.

        Returns:
            str: The Base64 token if the header is valid, None otherwise.
        """
        if authorization_header is None:
            return None
        if not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith('Basic '):
            return None

        # Extract the token after the 'Basic ' prefix.
        token = authorization_header.split(' ')[-1]
        return token

    def decode_base64_authorization_header(self, base64_authorization_header: str) -> str:
        """
        Decodes a Base64-encoded authorization header to retrieve the plain text
        credentials (email:password).

        Args:
            base64_authorization_header (str): The Base64-encoded authorization header.

        Returns:
            str: The decoded credentials (email:password) or None if decoding fails.
        """
        if base64_authorization_header is None:
            return None
        if not isinstance(base64_authorization_header, str):
            return None

        try:
            item_to_decode = base64_authorization_header.encode('utf-8')
            decoded = base64.b64decode(item_to_decode)
            return decoded.decode('utf-8')  # Decoding from UTF-8 to string.
        except Exception:
            return None  # Return None if there is any error in decoding.

    def extract_user_credentials(self, decoded_base64_authorization_header: str) -> (str, str): # type: ignore
        """
        Extracts the user credentials (email and password) from the decoded 
        Base64 authorization header.

        Args:
            decoded_base64_authorization_header (str): The decoded Base64 string in 'email:password' format.

        Returns:
            tuple: A tuple containing the email and password (str, str).
                   Returns (None, None) if extraction fails.
        """
        if decoded_base64_authorization_header is None:
            return (None, None)
        if not isinstance(decoded_base64_authorization_header, str):
            return (None, None)
        if ':' not in decoded_base64_authorization_header:
            return (None, None)

        # Split the decoded string into email and password.
        email, password = decoded_base64_authorization_header.split(':')
        return (email, password)

    def user_object_from_credentials(self, user_email: str, user_pwd: str) -> TypeVar('User'): # type: ignore
        """
        Retrieves the user object based on the provided email and password.

        This method searches for the user by their email and verifies the 
        password. If valid, it returns the corresponding user object.

        Args:
            user_email (str): The email of the user.
            user_pwd (str): The password of the user.

        Returns:
            User: The user object if the credentials are valid, None otherwise.
        """
        if user_email is None or not isinstance(user_email, str):
            return None
        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        try:
            # Search for the user by email in the database.
            users = User.search({"email": user_email})
            if not users or users == []:
                return None  # No user found with the given email.

            for user in users:
                if user.is_valid_password(user_pwd):
                    return user  # Return the user object if the password is valid.
            return None  # Return None if the password is invalid.
        except Exception:
            return None  # Return None if any error occurs during user retrieval.

    def current_user(self, request=None) -> TypeVar('User'): # type: ignore
        """
        Retrieves the current user from the request based on Basic Auth credentials.

        This method extracts the authorization header from the request, decodes 
        it, extracts the user credentials, and returns the user object if the 
        credentials are valid.

        Args:
            request (optional): The Flask request object. Defaults to None.

        Returns:
            User: The authenticated user object if credentials are valid, None otherwise.
        """
        # Retrieve the authorization header from the request.
        auth_header = self.authorization_header(request)
        if auth_header is not None:
            # Extract the Base64-encoded token from the authorization header.
            token = self.extract_base64_authorization_header(auth_header)
            if token is not None:
                # Decode the Base64 token to get the credentials.
                decoded = self.decode_base64_authorization_header(token)
                if decoded is not None:
                    # Extract email and password from the decoded credentials.
                    email, password = self.extract_user_credentials(decoded)
                    if email is not None:
                        # Retrieve the user object based on the credentials.
                        return self.user_object_from_credentials(email, password)

        return None  # Return None if no valid user credentials are found.
