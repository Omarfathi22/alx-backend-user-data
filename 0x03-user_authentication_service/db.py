#!/usr/bin/env python3
"""
DB module for managing database interactions with the User table.
"""

from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.orm.session import Session # type: ignore
from sqlalchemy.exc import InvalidRequestError # type: ignore
from sqlalchemy.orm.exc import NoResultFound # type: ignore

from user import Base, User


class DB:
    """
    DB class for interacting with the User table in the database.
    Provides methods for adding, querying, and updating user records.
    """

    def __init__(self) -> None:
        """
        Initialize a new DB instance.
        Creates a SQLite database and ensures the User table is ready for use.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)  # Clear existing tables for a fresh start
        Base.metadata.create_all(self._engine)  # Create tables based on User model
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Provides a memoized session object for interacting with the database.

        Returns:
            Session: A SQLAlchemy session instance.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a new user to the database.

        Args:
            email (str): The user's email address.
            hashed_password (str): The hashed password of the user.

        Returns:
            User: The newly created User object.
        """
        new_user = User(email=email, hashed_password=hashed_password)
        self._session.add(new_user)  # Stage the new user for addition
        self._session.commit()  # Commit the addition to the database
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """
        Finds a user in the database based on keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments corresponding to User fields.

        Returns:
            User: The User object that matches the query.

        Raises:
            InvalidRequestError: If no filtering criteria are provided.
            NoResultFound: If no matching user is found.
        """
        if not kwargs:
            raise InvalidRequestError("No filtering criteria provided")

        user = self._session.query(User).filter_by(**kwargs).first()
        if not user:
            raise NoResultFound("No user found with the specified criteria")
        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Updates a user's attributes in the database.

        Args:
            user_id (int): The ID of the user to update.
            **kwargs: Key-value pairs of attributes to update.

        Raises:
            ValueError: If an attribute to update does not exist on the User model.
        """
        user = self.find_user_by(id=user_id)
        for key, value in kwargs.items():
            if not hasattr(user, key):
                raise ValueError(f"User has no attribute '{key}'")
            setattr(user, key, value)  # Update the attribute on the user object

        self._session.commit()  # Persist the changes to the database
