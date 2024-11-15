#!/usr/bin/env python3
""" Module of Users views
This module defines the routes related to User management, including retrieving,
creating, updating, and deleting user data via the API.
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User


@app_views.route('/users', methods=['GET'], strict_slashes=False)
def view_all_users() -> str:
    """
    GET /api/v1/users
    Fetch and return a list of all user objects in JSON format.
    
    Returns:
        - A JSON list of all User objects
    """
    all_users = [user.to_json() for user in User.all()]
    return jsonify(all_users)


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def view_one_user(user_id: str = None) -> str:
    """
    GET /api/v1/users/:id
    Fetch and return a user object by user ID.

    Path Parameters:
        - user_id (str): The ID of the user to retrieve.

    Returns:
        - A JSON representation of the user object if found.
        - 404 if the user with the given ID doesn't exist.
        - 404 if user_id is "me" but the current user is not authenticated.
    """
    if user_id is None:
        abort(404)  # User ID is required in the URL

    # Handle special case where user_id is "me"
    if user_id == "me":
        if request.current_user is None:
            abort(404)  # Current user is required for "me" route
        user = request.current_user
        return jsonify(user.to_json())  # Return the authenticated user's info
    
    # Standard case to fetch the user by ID
    user = User.get(user_id)
    if user is None:
        abort(404)  # User not found
    return jsonify(user.to_json())


@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id: str = None) -> str:
    """
    DELETE /api/v1/users/:id
    Delete a user by user ID.

    Path Parameters:
        - user_id (str): The ID of the user to delete.

    Returns:
        - An empty JSON response ({}), with status 200 if deletion was successful.
        - 404 if the user with the given ID doesn't exist.
    """
    if user_id is None:
        abort(404)  # User ID is required

    user = User.get(user_id)
    if user is None:
        abort(404)  # User not found

    user.remove()  # Delete the user
    return jsonify({}), 200  # Return empty JSON and status 200 for success


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user() -> str:
    """
    POST /api/v1/users/
    Create a new user based on the provided JSON data.

    JSON Body:
        - email (str): The email of the user.
        - password (str): The password of the user.
        - first_name (str, optional): The first name of the user.
        - last_name (str, optional): The last name of the user.

    Returns:
        - A JSON representation of the created user object, with status 201 if successful.
        - 400 if there is a missing or invalid field.
    """
    rj = None
    error_msg = None

    # Attempt to parse the incoming JSON request
    try:
        rj = request.get_json()
    except Exception:
        rj = None

    if rj is None:
        error_msg = "Wrong format"  # JSON format error
    elif rj.get("email", "") == "":
        error_msg = "email missing"  # Email field is required
    elif rj.get("password", "") == "":
        error_msg = "password missing"  # Password field is required

    # If no error, try to create the user
    if error_msg is None:
        try:
            user = User()  # Create a new user instance
            user.email = rj.get("email")
            user.password = rj.get("password")
            user.first_name = rj.get("first_name")
            user.last_name = rj.get("last_name")
            user.save()  # Save the new user to the database
            return jsonify(user.to_json()), 201  # Return the created user with status 201
        except Exception as e:
            error_msg = f"Can't create User: {e}"  # Handle unexpected errors

    return jsonify({'error': error_msg}), 400  # Return error message if user creation failed


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id: str = None) -> str:
    """
    PUT /api/v1/users/:id
    Update a user's information based on the provided JSON data.

    Path Parameters:
        - user_id (str): The ID of the user to update.

    JSON Body:
        - first_name (str, optional): The new first name of the user.
        - last_name (str, optional): The new last name of the user.

    Returns:
        - A JSON representation of the updated user object, with status 200 if successful.
        - 404 if the user with the given ID doesn't exist.
        - 400 if the input data is in the wrong format.
    """
    if user_id is None:
        abort(404)  # User ID is required in the URL

    user = User.get(user_id)
    if user is None:
        abort(404)  # User not found

    rj = None
    try:
        rj = request.get_json()  # Parse the incoming JSON request
    except Exception:
        rj = None

    if rj is None:
        return jsonify({'error': "Wrong format"}), 400  # Invalid JSON format

    # Update the user's fields if provided in the request
    if rj.get('first_name') is not None:
        user.first_name = rj.get('first_name')
    if rj.get('last_name') is not None:
        user.last_name = rj.get('last_name')

    user.save()  # Save the updated user information
    return jsonify(user.to_json()), 200  # Return the updated user with status 200
