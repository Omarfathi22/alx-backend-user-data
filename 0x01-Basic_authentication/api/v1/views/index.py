#!/usr/bin/env python3
""" Module for Index views
"""
from flask import jsonify, abort
from api.v1.views import app_views
from models.user import User


# Unauthorized access route
@app_views.route('/unauthorized', methods=['GET'], strict_slashes=False)
def unauthorized() -> str:
    """ Returns a 401 Unauthorized error
    This route is used to simulate unauthorized access.
    """
    abort(401, description='Unauthorized access. Please check your credentials.')


# Forbidden access route
@app_views.route('/forbidden', methods=['GET'], strict_slashes=False)
def forbidden() -> str:
    """ Returns a 403 Forbidden error
    This route is used to simulate forbidden access.
    """
    abort(403, description='Forbidden access. You do not have permission to access this resource.')


# Status route
@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status() -> str:
    """ Returns the status of the API
    This route is used to check if the API is up and running.
    
    Return:
      - the status of the API in JSON format: {"status": "OK"}
    """
    return jsonify({"status": "OK"})


# Stats route
@app_views.route('/stats/', strict_slashes=False)
def stats() -> str:
    """ Returns the number of each object in the system
    This route returns a count of all users in the system.
    
    Return:
      - A JSON object containing the count of users in the system.
    """
    try:
        stats = {}
        stats['users'] = User.count()  # Get the count of users from the User model
        return jsonify(stats)
    except Exception as e:
        # Log the error for debugging purposes (if needed)
        # logging.error(f"Error fetching stats: {e}")
        return jsonify({"error": "Unable to retrieve stats."}), 500
