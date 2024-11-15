#!/usr/bin/env python3
""" Module of Users views for authentication
This module handles the user login (session-based authentication) and logout 
routes for the API.
"""
import os
from api.v1.views import app_views
from models.user import User
from flask import jsonify, request, abort


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def session_auth():
    """
    POST /api/v1/auth_session/login
    Authenticates a user by email and password, creates a session, and sets a 
    session cookie for the user.

    Form Data (application/x-www-form-urlencoded):
        - email (str): The email of the user.
        - password (str): The password of the user.

    Returns:
        - A JSON response with user data if authentication is successful.
        - 400 if either email or password is missing.
        - 404 if no user is found with the provided email.
        - 401 if the password is incorrect.
    """
    # Retrieve email and password from form data
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the email is provided
    if email is None or email == '':
        return jsonify({"error": "email missing"}), 400  # Return 400 if email is missing

    # Check if the password is provided
    if password is None or password == '':
        return jsonify({"error": "password missing"}), 400  # Return 400 if password is missing

    # Search for a user with the provided email
    users = User.search({"email": email})
    
    # If no user is found with the provided email, return 404
    if not users or users == []:
        return jsonify({"error": "no user found for this email"}), 404

    # Loop through all users found with the email (should typically be only one)
    for user in users:
        # Validate the password for the found user
        if user.is_valid_password(password):
            # Import auth to create a session for the authenticated user
            from api.v1.app import auth
            session_id = auth.create_session(user.id)  # Create a session ID

            # Prepare the response with the user data
            resp = jsonify(user.to_json())

            # Get the session name from environment variables and set the session cookie
            session_name = os.getenv('SESSION_NAME')
            resp.set_cookie(session_name, session_id)  # Set the session cookie for the user

            # Return the user data along with the session cookie
            return resp

    # If the password is incorrect, return 401 (Unauthorized)
    return jsonify({"error": "wrong password"}), 401


@app_views.route('/auth_session/logout', methods=['DELETE'], strict_slashes=False)
def logout():
    """
    DELETE /api/v1/auth_session/logout
    Logs the user out by destroying their session and clearing the session cookie.

    Returns:
        - An empty JSON response with status 200 if logout is successful.
        - 404 if the session cannot be destroyed (e.g., the user is not authenticated).
    """
    from api.v1.app import auth

    # Attempt to destroy the session for the current user
    if auth.destroy_session(request):
        return jsonify({}), 200  # Return empty JSON with status 200 on successful logout

    # If the session could not be destroyed, return 404 (Not Found)
    abort(404)
