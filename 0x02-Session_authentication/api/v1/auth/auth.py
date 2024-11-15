#!/usr/bin/env python3
"""
Module for authentication

This module defines the Auth class which provides basic authentication methods
for handling user requests in a Flask API. It includes methods for checking 
authorization, obtaining authorization headers, and managing session cookies.
"""

from typing import List, TypeVar
from flask import request
import os


class Auth:
    """
    Auth class for managing authentication-related tasks.

    This class provides several methods for handling authentication requirements,
    such as checking if a path requires authentication, retrieving the authorization 
    header from a request, and working with session cookies.
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Determine if a given path requires authentication.

        This method checks if a path should be excluded from authentication based 
        on a list of excluded paths and wildcard matching.

        Args:
            path (str): The path being requested (e.g., "/api/v1/users").
            excluded_paths (List[str]): A list of paths that do not require authentication.

        Returns:
            bool: True if the path requires authentication, False if it is excluded.
        """
        if path is None:
            return True  # If the path is None, treat it as requiring authentication.

        if excluded_paths is None or excluded_paths == []:
            return True  # If no excluded paths are provided, all paths require authentication.

        if path in excluded_paths:
            return False  # If the path is explicitly excluded, no authentication is required.

        # Check if the path matches any pattern in the excluded paths list (wildcard handling).
        for excluded_path in excluded_paths:
            if excluded_path.startswith(path):
                return False
            elif path.startswith(excluded_path):
                return False
            elif excluded_path[-1] == "*":
                if path.startswith(excluded_path[:-1]):
                    return False

        return True  # If no match is found, the path requires authentication.

    def authorization_header(self, request=None) -> str:
        """
        Retrieve the authorization header from the request.

        This method extracts the "Authorization" header from the HTTP request
        and returns its value.

        Args:
            request (optional): The Flask request object. Defaults to None.

        Returns:
            str: The value of the "Authorization" header, or None if not found.
        """
        if request is None:
            return None  # If no request is provided, return None.

        # Extract the 'Authorization' header from the request headers.
        header = request.headers.get('Authorization')

        if header is None:
            return None  # Return None if the header is not found.

        return header  # Return the authorization header value.

    def current_user(self, request=None) -> TypeVar('User'): # type: ignore
        """
        Get the current user based on the request.

        This method can be overridden by subclasses to implement actual user 
        retrieval based on the request. For now, it returns None.

        Args:
            request (optional): The Flask request object. Defaults to None.

        Returns:
            TypeVar('User'): The current user object (None in this case).
        """
        return None  # This base method currently returns None, meaning no user is authenticated.

    def session_cookie(self, request=None):
        """
        Retrieve the session cookie from the request.

        This method retrieves the session ID stored in a cookie by extracting
        the cookie named by the 'SESSION_NAME' environment variable.

        Args:
            request (optional): The Flask request object. Defaults to None.

        Returns:
            str: The value of the session cookie, or None if not found.
        """
        if request is None:
            return None  # If no request is provided, return None.

        session_name = os.getenv('SESSION_NAME')  # Retrieve the session cookie name from environment variable.
        return request.cookies.get(session_name)  # Return the session cookie value.
