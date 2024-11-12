#!/usr/bin/env python3
""" User module
"""
import hashlib
from models.base import Base

class User(Base):
    """ User class for managing user data
    Attributes:
        email (str): The user's email address.
        _password (str): The hashed password.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """ Initialize a User instance with provided attributes
        Args:
            *args (list): Positional arguments.
            **kwargs (dict): Keyword arguments including 'email', 'first_name',
                             'last_name', and '_password'.
        """
        super().__init__(*args, **kwargs)
        self.email = kwargs.get('email')
        self._password = kwargs.get('_password')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')

    @property
    def password(self) -> str:
        """ Getter for password.
        Returns:
            str: The hashed password.
        """
        return self._password

    @password.setter
    def password(self, pwd: str):
        """ Setter for the password. Encrypts password with SHA256.
        Args:
            pwd (str): The password to be hashed.
        """
        if pwd and isinstance(pwd, str):
            self._password = hashlib.sha256(pwd.encode()).hexdigest().lower()
        else:
            self._password = None

    def is_valid_password(self, pwd: str) -> bool:
        """ Validates if the given password matches the stored password.
        Args:
            pwd (str): The password to check.
        Returns:
            bool: True if the password is valid, False otherwise.
        """
        if pwd is None or not isinstance(pwd, str):
            return False
        # Directly hash the provided password and compare
        return hashlib.sha256(pwd.encode()).hexdigest().lower() == self.password

    def display_name(self) -> str:
        """ Displays the user's full name or email if not available.
        Returns:
            str: A formatted string of the user's display name.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif self.email:
            return self.email
        return ""
