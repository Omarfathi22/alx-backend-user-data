#!/usr/bin/env python3
"""
This module defines the User model for interacting with the 'users' table
in the database using SQLAlchemy ORM.
"""


from sqlalchemy import Column, Integer, String # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore


Base = declarative_base()

class User(Base):
    """
    Defines the User model for the 'users' table.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
