#!/usr/bin/env python3
"""
Flask application for user authentication and session management.
Provides routes for user registration, login, session management,
password reset, and profile retrieval.
"""

from flask import Flask, jsonify, request, abort, redirect
from auth import Auth

AUTH = Auth()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index() -> str:
    """
    Welcome endpoint.

    Returns:
        str: A welcome message in JSON format.
    """
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'])
def users() -> str:
    """
    User registration endpoint.

    Retrieves email and password from the request and attempts to register
    a new user. If the user already exists, returns a 400 status code.

    Returns:
        str: A success message with the user's email, or an error message.
    """
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        user = AUTH.register_user(email, password)
        return jsonify({"email": user.email, "message": "user created"})
    except Exception:
        return jsonify({"message": "email already registered"}), 400


@app.route('/sessions', methods=['POST'])
def login() -> str:
    """
    User login endpoint.

    Validates the user's email and password, creates a session, and sets a
    session ID in a cookie. If the credentials are invalid, aborts with a 401 status.

    Returns:
        str: A success message in JSON format with the email.
    """
    email = request.form.get('email')
    password = request.form.get('password')

    if not AUTH.valid_login(email, password):
        abort(401)
    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie('session_id', session_id)

    return response


@app.route('/sessions', methods=['DELETE'])
def logout() -> str:
    """
    User logout endpoint.

    Retrieves the session ID from the cookies, destroys the session, and redirects to the index.
    If the session ID is invalid, aborts with a 403 status.

    Returns:
        str: A redirection to the index route.
    """
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect('/')


@app.route('/profile', methods=['GET'])
def profile() -> str:
    """
    User profile endpoint.

    Retrieves the session ID from the cookies and fetches the user's profile.
    If the session ID is invalid, aborts with a 403 status.

    Returns:
        str: The user's email in JSON format.
    """
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email}), 200
    abort(403)


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token() -> str:
    """
    Password reset token endpoint.

    Generates a reset token for the user's email.
    If the email is not registered, aborts with a 403 status.

    Returns:
        str: The email and reset token in JSON format.
    """
    email = request.form.get('email')
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token}), 200
    except Exception:
        abort(403)


@app.route('/reset_password', methods=['PUT'])
def update_password() -> str:
    """
    Password update endpoint.

    Updates the user's password using the reset token.
    If the token is invalid, aborts with a 403 status.

    Returns:
        str: A success message in JSON format.
    """
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"}), 200
    except Exception:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
