#!/usr/bin/env python3
"""
Module for authentication logic.
"""

from typing import List, TypeVar
from flask import request


class Auth:
    """Base authentication class providing methods for request authentication."""

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Determines if a given path requires authentication or if it's excluded.

        Args:
            path (str): The request path to check.
            excluded_paths (List[str]): List of paths to be excluded from authentication.

        Returns:
            bool: Returns True if authentication is required, False if the path is excluded.
        """
        if path is None:
            return True  # If the path is None, authentication is required.

        if not excluded_paths:
            return True  # If no excluded paths are provided, authentication is required.

        if path in excluded_paths:
            return False  # If the path is explicitly excluded, no authentication is needed.

        # Check if path matches any of the excluded paths (supports wildcards at the end).
        for excluded_path in excluded_paths:
            if excluded_path.endswith("*"):
                # Support wildcard at the end of the path (e.g., '/api/v1/*').
                if path.startswith(excluded_path[:-1]):
                    return False
            elif path.startswith(excluded_path) or excluded_path.startswith(path):
                return False

        return True  # If no match, authentication is required.

    def authorization_header(self, request=None) -> str:
        """
        Retrieves the value of the 'Authorization' header from the request.

        Args:
            request (flask.Request, optional): The incoming HTTP request. Defaults to None.

        Returns:
            str: The 'Authorization' header value or None if not present.
        """
        if request is None:
            return None  # If no request is passed, return None.

        # Retrieve the 'Authorization' header from the request headers.
        return request.headers.get('Authorization', None)

    def current_user(self, request=None) -> TypeVar('User'): # type: ignore
        """
        Retrieves the current user from the request.

        Args:
            request (flask.Request, optional): The incoming HTTP request. Defaults to None.

        Returns:
            User or None: In the base class, this always returns None as authentication logic
                          is implemented in subclasses.
        """
        return None  # Base class implementation does not fetch any user.
