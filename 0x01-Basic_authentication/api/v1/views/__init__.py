#!/usr/bin/env python3
"""
Module that defines the API routes for version 1 of the service.
"""

from flask import Blueprint

# Create a Flask Blueprint for version 1 of the API
# This blueprint will handle all routes prefixed with '/api/v1'
app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

# Import the route handlers for different parts of the API
# The 'index' module handles general endpoints like status and stats.
# The 'users' module handles user-related operations like viewing, creating, and updating users.
from api.v1.views.index import *
from api.v1.views.users import *

# Load all user data from a file at the start of the application
# This ensures that user-related information is available for use when handling requests.
User.load_from_file()
