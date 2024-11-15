#!/usr/bin/env python3
"""
Route module for the API.

This module sets up and configures the Flask application, including error handling,
authentication middleware, and routes. It dynamically selects the authentication 
method based on the AUTH_TYPE environment variable and ensures proper security 
throughout the API routes.
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin
import os


# Initialize the Flask application
app = Flask(__name__)

# Register the blueprint for views (routes)
app.register_blueprint(app_views)

# Enable Cross-Origin Resource Sharing (CORS) for all API routes
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize the 'auth' variable for dynamic authentication
auth = None

# Get the authentication type from the environment variable
AUTH_TYPE = os.getenv("AUTH_TYPE")

# Dynamically import the appropriate authentication module based on the AUTH_TYPE
if AUTH_TYPE == 'auth':
    from api.v1.auth.auth import Auth
    auth = Auth()
elif AUTH_TYPE == 'basic_auth':
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
elif AUTH_TYPE == 'session_auth':
    from api.v1.auth.session_auth import SessionAuth # type: ignore
    auth = SessionAuth()


@app.before_request
def before_request():
    """
    Runs before each request to apply authentication checks.

    If authentication is enabled (auth is not None), the function ensures that:
    - The user is authenticated either by session cookie or authorization header.
    - The request path requires authentication, excluding certain public routes.
    - The user is authorized to access the requested resource (403 if forbidden).

    If any of these checks fail, the request will be aborted with a specific error.
    """
    if auth is None:
        pass  # No authentication required, proceed normally
    else:
        # Attach the current user to the request object based on the authentication method
        setattr(request, "current_user", auth.current_user(request))

        # List of routes that do not require authentication
        excluded_list = ['/api/v1/status/', '/api/v1/unauthorized/', '/api/v1/forbidden/', '/api/v1/auth_session/login/']

        # Check if the current request path requires authentication
        if auth.require_auth(request.path, excluded_list):
            # Check if authorization header or session cookie is provided
            cookie = auth.session_cookie(request)
            if auth.authorization_header(request) is None and cookie is None:
                abort(401, description="Unauthorized")  # Unauthorized if neither is provided

            # Ensure that the current user is valid (authenticated)
            if auth.current_user(request) is None:
                abort(403, description='Forbidden')  # Forbidden if user is not authenticated


@app.errorhandler(404)
def not_found(error) -> str:
    """
    Handle 404 errors (resource not found).
    
    Returns a JSON response with an error message for resource not found.
    
    Args:
        error (Error): The error that triggered the handler.
    
    Returns:
        str: A JSON response with a 404 status code and error message.
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """
    Handle 401 errors (unauthorized access).
    
    Returns a JSON response with an error message indicating unauthorized access.
    
    Args:
        error (Error): The error that triggered the handler.
    
    Returns:
        str: A JSON response with a 401 status code and error message.
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """
    Handle 403 errors (forbidden access).
    
    Returns a JSON response with an error message indicating forbidden access.
    
    Args:
        error (Error): The error that triggered the handler.
    
    Returns:
        str: A JSON response with a 403 status code and error message.
    """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    # Retrieve host and port for the API server from environment variables (default to 0.0.0.0 and 5000)
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    
    # Run the Flask application on the specified host and port
    app.run(host=host, port=port)
