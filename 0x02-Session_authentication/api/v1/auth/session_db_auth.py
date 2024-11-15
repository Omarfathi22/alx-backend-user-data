#!/usr/bin/env python3
""" Module of Session in Database
"""
from api.v1.auth.session_exp_auth import SessionExpAuth
from datetime import datetime, timedelta
from models.user_session import UserSession # type: ignore


class SessionDBAuth(SessionExpAuth):
    """Session in database Class, inherits from SessionExpAuth to handle sessions with expiration logic"""

    def create_session(self, user_id=None):
        """Creates a session in the database for the given user_id"""
        # Call the superclass method to create a session (inherits from SessionExpAuth)
        session_id = super().create_session(user_id)

        # If session creation fails (session_id is None), return None
        if session_id is None:
            return None

        # Create a new UserSession object and save it to the database (or file)
        kwargs = {'user_id': user_id, 'session_id': session_id}
        user_session = UserSession(**kwargs)
        user_session.save()  # Save session to database (or file)
        UserSession.save_to_file()  # Save to file (presumably for persistence)

        # Return the session_id after successfully creating and saving the session
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """Returns the user_id for a given session_id, or None if the session is invalid/expired"""
        # If session_id is not provided, return None
        if session_id is None:
            return None

        # Load existing user sessions from file (to check against database)
        UserSession.load_from_file()

        # Search for a user session matching the given session_id
        user_session = UserSession.search({
            'session_id': session_id
        })

        # If no session is found, return None
        if not user_session:
            return None

        # Assume there's only one result and get the first user session
        user_session = user_session[0]

        # Calculate the expiration time by adding session duration to the session creation time
        expired_time = user_session.created_at + timedelta(seconds=self.session_duration)

        # If the session has expired, return None
        if expired_time < datetime.utcnow():
            return None

        # Return the user_id if the session is valid (not expired)
        return user_session.user_id

    def destroy_session(self, request=None):
        """Removes the session from the database, invalidating the session"""
        # If no request is provided, return False
        if request is None:
            return False

        # Get the session_id from the request cookies
        session_id = self.session_cookie(request)
        if session_id is None:
            return False

        # Get the user_id associated with the session_id
        user_id = self.user_id_for_session_id(session_id)

        # If no user_id is found (session does not exist or expired), return False
        if not user_id:
            return False

        # Search for the user session by session_id in the database
        user_session = UserSession.search({
            'session_id': session_id
        })

        # If no session is found, return False
        if not user_session:
            return False

        # Get the first user session (should only be one result)
        user_session = user_session[0]

        # Attempt to remove the session from the database (or file)
        try:
            user_session.remove()  # Remove the session from the database
            UserSession.save_to_file()  # Save changes to the file
        except Exception:
            # If there's an error during removal, return False
            return False

        # Return True to indicate the session was successfully destroyed
        return True
