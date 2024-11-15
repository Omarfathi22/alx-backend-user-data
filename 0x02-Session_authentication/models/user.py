#!/usr/bin/env python3
""" User module for managing user data
"""
import hashlib
from models.base import Base


class User(Base):
    """ User class to represent a user entity in the system
    This class provides functionality for managing user credentials, including
    password storage and validation, and displaying the user's name.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """ Initialize a User instance
        Args:
            *args: Variable length argument list, passed to the parent constructor.
            **kwargs: Dictionary of keyword arguments. Expected keys:
                - 'email': User's email address
                - '_password': User's password (hashed)
                - 'first_name': User's first name
                - 'last_name': User's last name
        """
        super().__init__(*args, **kwargs)
        self.email = kwargs.get('email')
        self._password = kwargs.get('_password')  # 'password' should be stored as a hashed value
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')

    @property
    def password(self) -> str:
        """ Getter for the user's password.
        Returns:
            str: The hashed password of the user.
        """
        return self._password

    @password.setter
    def password(self, pwd: str):
        """ Setter for the user's password.
        This method encrypts the password using SHA256 before storing it.
        Args:
            pwd (str): The plain-text password to be hashed and stored.
        """
        if pwd is None or type(pwd) is not str:
            self._password = None  # If no valid password is provided, set password to None
        else:
            # Hash the password using SHA256 and store it in lowercase
            self._password = hashlib.sha256(pwd.encode()).hexdigest().lower()

    def is_valid_password(self, pwd: str) -> bool:
        """ Check if the provided password is valid by comparing it with the stored hashed password.
        Args:
            pwd (str): The plain-text password to validate.
        Returns:
            bool: True if the hashed input matches the stored password, otherwise False.
        """
        if pwd is None or type(pwd) is not str:
            return False  # Invalid input if password is not a string
        if self.password is None:
            return False  # If no password is set, return False
        # Compare the hash of the provided password with the stored hash
        pwd_e = pwd.encode()
        return hashlib.sha256(pwd_e).hexdigest().lower() == self.password

    def display_name(self) -> str:
        """ Generate the display name for the user based on available information (email, first name, last name).
        If the user has both first and last names, display them. If not, display the email if available.
        Returns:
            str: The user's full name or email if name is not available. If no name or email, returns an empty string.
        """
        if self.email is None and self.first_name is None and self.last_name is None:
            return ""  # Return an empty string if no name or email is set
        if self.first_name is None and self.last_name is None:
            return "{}".format(self.email)  # If no name, return email
        if self.last_name is None:
            return "{}".format(self.first_name)  # If no last name, return first name only
        if self.first_name is None:
            return "{}".format(self.last_name)  # If no first name, return last name only
        else:
            # Return both first and last name if available
            return "{} {}".format(self.first_name, self.last_name)
