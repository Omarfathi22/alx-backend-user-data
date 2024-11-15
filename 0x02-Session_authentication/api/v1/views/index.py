#!/usr/bin/env python3
""" Module of Index views
This module contains views that handle various endpoints related to system status, 
unauthorized access, and forbidden access. It also provides a statistics endpoint 
that returns the number of user objects in the system.
"""

from flask import jsonify, abort
from api.v1.views import app_views


# Unauthorized access route
@app_views.route('/unauthorized', methods=['GET'], strict_slashes=False)
def unauthorized() -> str:
    """
    Handles unauthorized access.
    This route triggers a 401 Unauthorized error when accessed.

    Returns:
        - A 401 HTTP status code with a custom error message.
    """
    abort(401, description='Unauthorized')  # Abort with 401 status code and description


# Forbidden access route
@app_views.route('/forbidden', methods=['GET'], strict_slashes=False)
def forbidden() -> str:
    """
    Handles forbidden access.
    This route triggers a 403 Forbidden error when accessed.

    Returns:
        - A 403 HTTP status code with a custom error message.
    """
    abort(403, description='Forbidden')  # Abort with 403 status code and description


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status() -> str:
    """
    GET /api/v1/status
    Returns the status of the API.

    Returns:
        - A JSON response with the status of the API: {"status": "OK"}.
    """
    return jsonify({"status": "OK"})  # Respond with status OK


@app_views.route('/stats/', strict_slashes=False)
def stats() -> str:
    """
    GET /api/v1/stats
    Returns statistics about the objects in the system.
    Specifically, it returns the count of the 'User' objects in the database.

    Returns:
        - A JSON response containing the number of users in the system.
    """
    from models.user import User  # Import User model to fetch statistics
    stats = {}
    stats['users'] = User.count()  # Get the count of users from the User model
    return jsonify(stats)  # Return the statistics as a JSON response
