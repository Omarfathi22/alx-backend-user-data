#!/usr/bin/env python3
"""
Route module for the API
"""
import os
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(app_views)

# Enable CORS for the API (consider restricting origins in production)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize auth based on environment variable
auth = None
AUTH_TYPE = os.getenv("AUTH_TYPE")

if AUTH_TYPE == 'auth':
    from api.v1.auth.auth import Auth
    auth = Auth()
elif AUTH_TYPE == 'basic_auth':
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()

@app.before_request
def before_request():
    """
    Executes before every request to handle authentication
    """
    # Skip authentication if no auth system is set
    if not auth:
        return

    # Define routes that do not require authentication
    excluded_list = ['/api/v1/status/', '/api/v1/unauthorized/', '/api/v1/forbidden/']

    # Only apply authentication to non-excluded paths
    if auth.require_auth(request.path, excluded_list):
        # Check for Authorization header
        if auth.authorization_header(request) is None:
            abort(401, description="Unauthorized")

        # Check for current user authorization
        if auth.current_user(request) is None:
            abort(403, description='Forbidden')

@app.errorhandler(404)
def not_found(error):
    """Handler for 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(401)
def unauthorized(error):
    """Handler for 401 errors"""
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(error):
    """Handler for 403 errors"""
    return jsonify({"error": "Forbidden"}), 403

def start_api():
    """Start the Flask application with the given host and port."""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = os.getenv("API_PORT", "5000")
    app.run(host=host, port=port)

if __name__ == "__main__":
    start_api()
