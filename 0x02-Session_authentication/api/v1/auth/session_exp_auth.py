#!/usr/bin/env python3
""" Module of Expiration of Session Authentication
"""
from api.v1.auth.session_auth import SessionAuth
from datetime import datetime, timedelta
from models.user import User
from os import getenv


class SessionExpAuth(SessionAuth):
    """Session Expiration Class that extends SessionAuth for handling session expiry"""

    def __init__(self):
        """Constructor Method: Initializes session expiration duration"""
        # Retrieve session duration from environment variable (default to 0 if not found)
        SESSION_DURATION = getenv('SESSION_DURATION')

        try:
            # Try converting the session duration to an integer
            session_duration = int(SESSION_DURATION)
        except Exception:
            # If there's an error (invalid value or missing), default to 0 (no expiration)
            session_duration = 0

        # Store the session duration
        self.session_duration = session_duration

    def create_session(self, user_id=None):
        """Creates a session with an expiration time"""
        # Call the parent method to create the session
        session_id = super().create_session(user_id)

        # If session creation fails, return None
        if session_id is None:
            return None

        # Create a dictionary that will store the user ID and the creation timestamp of the session
        session_dictionary = {
            "user_id": user_id,
            "created_at": datetime.now()
        }

        # Store the session information in the dictionary, using session_id as the key
        self.user_id_by_session_id[session_id] = session_dictionary

        # Return the generated session ID
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """Gets the user ID associated with a session ID, checking for expiration"""
        # If no session ID is provided, return None
        if session_id is None:
            return None

        # Check if the session_id exists in the dictionary of active sessions
        if session_id not in self.user_id_by_session_id.keys():
            return None

        # Retrieve the session details from the dictionary
        session_dictionary = self.user_id_by_session_id.get(session_id)

        # If session details do not exist, return None
        if session_dictionary is None:
            return None

        # If the session has no expiration (i.e., session_duration is 0 or negative), return the user ID
        if self.session_duration <= 0:
            return session_dictionary.get('user_id')

        # Retrieve the session creation time
        created_at = session_dictionary.get('created_at')

        # If the session creation time is missing, return None
        if created_at is None:
            return None

        # Calculate the expiration time by adding session_duration to the creation time
        expired_time = created_at + timedelta(seconds=self.session_duration)

        # If the session has expired (current time > expiration time), return None
        if expired_time < datetime.now():
            return None

        # Return the user ID if the session is valid (i.e., not expired)
        return session_dictionary.get('user_id')
