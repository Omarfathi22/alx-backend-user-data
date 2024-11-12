#!/usr/bin/env python3
""" Main 5 - Testing user creation and authentication using BasicAuth
"""
import uuid
from api.v1.auth.basic_auth import BasicAuth # type: ignore
from models.user import User

def test_user_creation_and_authentication():
    """Test user creation and retrieval using BasicAuth."""

    # Create a user with random email and password
    user_email = str(uuid.uuid4()) + "@example.com"  # Unique email
    user_clear_pwd = str(uuid.uuid4())  # Unique password
    
    # Create a User instance
    user = User()
    user.email = user_email
    user.first_name = "Bob"
    user.last_name = "Dylan"
    user.password = user_clear_pwd
    
    # Display user details before saving
    print("New user created with email: {}".format(user_email))
    print("User's display name: {}".format(user.display_name()))
    
    # Save the user to the database (this should save the user to the storage)
    user.save()

    # Now test retrieving this user using BasicAuth
    a = BasicAuth()

    # Test with invalid credentials (None values)
    u = a.user_object_from_credentials(None, None)
    print("Test with None credentials: {}".format(u.display_name() if u else "None"))  # Expected: None
    
    # Test with invalid credentials (non-string, e.g., integers)
    u = a.user_object_from_credentials(89, 98)
    print("Test with non-string credentials: {}".format(u.display_name() if u else "None"))  # Expected: None
    
    # Test with non-existing email/password (invalid email)
    u = a.user_object_from_credentials("email@notfound.com", "pwd")
    print("Test with non-existing credentials: {}".format(u.display_name() if u else "None"))  # Expected: None
    
    # Test with valid email but incorrect password
    u = a.user_object_from_credentials(user_email, "incorrect_pwd")
    print("Test with valid email but incorrect password: {}".format(u.display_name() if u else "None"))  # Expected: None
    
    # Test with valid email and correct password
    u = a.user_object_from_credentials(user_email, user_clear_pwd)
    print("Test with valid credentials (correct email and password): {}".format(u.display_name() if u else "None"))  # Expected: Bob Dylan

if __name__ == "__main__":
    print("Testing user creation and authentication...\n")
    test_user_creation_and_authentication()
