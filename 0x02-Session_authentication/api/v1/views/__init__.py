#!/usr/bin/env python3
""" 
This module initializes the Blueprint for the API views.
The Blueprint `app_views` handles the routing for all the API endpoints under the `/api/v1` prefix.
It imports various route handlers for different resources and functionality like index, users, and session authentication.
"""
from flask import Blueprint

# Initialize the Blueprint for API views with a URL prefix "/api/v1"
app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

# Import route definitions for different parts of the app
from api.v1.views.index import *  # Import routes related to status and error handling
from api.v1.views.users import *  # Import routes for user management (CRUD operations)
from api.v1.views.session_auth import *  # Import routes for session-based authentication (login/logout)

# Load existing user data from the file storage at the app's startup
User.load_from_file()
