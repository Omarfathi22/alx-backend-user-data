#!/usr/bin/env python3
""" Base module for handling objects and persistence
"""
from datetime import datetime
from typing import TypeVar, List, Iterable
from os import path
import json
import uuid


# Constant for datetime formatting
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Global dictionary to store objects of different classes
DATA = {}


class Base:
    """ Base class for all models, providing common functionality for
    handling object persistence (save, load, remove, etc.) and metadata
    management (timestamps, unique IDs).
    """

    def __init__(self, *args: list, **kwargs: dict):
        """ Initialize a Base instance with attributes and timestamps.
        Args:
            *args: Variable-length argument list (unused in this implementation).
            **kwargs: Dictionary of keyword arguments. Expected keys:
                - 'id': The unique identifier (defaults to a new UUID if not provided).
                - 'created_at': The timestamp when the object was created.
                - 'updated_at': The timestamp when the object was last updated.
        """
        # Class name used to organize objects in the global DATA dictionary
        s_class = str(self.__class__.__name__)

        # Initialize storage for this class if not already done
        if DATA.get(s_class) is None:
            DATA[s_class] = {}

        # Assign unique ID or use one provided in kwargs
        self.id = kwargs.get('id', str(uuid.uuid4()))

        # Handle 'created_at' and 'updated_at' timestamps
        if kwargs.get('created_at') is not None:
            self.created_at = datetime.strptime(kwargs.get('created_at'), TIMESTAMP_FORMAT)
        else:
            self.created_at = datetime.utcnow()

        if kwargs.get('updated_at') is not None:
            self.updated_at = datetime.strptime(kwargs.get('updated_at'), TIMESTAMP_FORMAT)
        else:
            self.updated_at = datetime.utcnow()

    def __eq__(self, other: TypeVar('Base')) -> bool: # type: ignore
        """ Check equality of two Base objects based on their ID.
        Args:
            other (Base): The other object to compare with.
        Returns:
            bool: True if the objects are of the same type and have the same ID, False otherwise.
        """
        if type(self) != type(other):
            return False
        if not isinstance(self, Base):
            return False
        return (self.id == other.id)

    def to_json(self, for_serialization: bool = False) -> dict:
        """ Convert the object to a dictionary format, suitable for JSON serialization.
        Args:
            for_serialization (bool): If True, include only the attributes that can be serialized.
        Returns:
            dict: The dictionary representation of the object.
        """
        result = {}
        for key, value in self.__dict__.items():
            if not for_serialization and key[0] == '_':
                continue  # Skip private attributes (those starting with '_')
            if isinstance(value, datetime):
                result[key] = value.strftime(TIMESTAMP_FORMAT)  # Convert datetime to string
            else:
                result[key] = value
        return result

    @classmethod
    def load_from_file(cls):
        """ Load all objects of this class from a JSON file.
        This method reads the file, parses the JSON, and loads each object into the global DATA dictionary.
        """
        s_class = cls.__name__
        file_path = ".db_{}.json".format(s_class)
        DATA[s_class] = {}  # Reset the class data before loading new data

        if not path.exists(file_path):
            return  # No file exists, nothing to load

        with open(file_path, 'r') as f:
            objs_json = json.load(f)
            for obj_id, obj_json in objs_json.items():
                DATA[s_class][obj_id] = cls(**obj_json)  # Instantiate objects from JSON data

    @classmethod
    def save_to_file(cls):
        """ Save all objects of this class to a JSON file.
        This method serializes the objects into JSON and writes them to disk.
        """
        s_class = cls.__name__
        file_path = ".db_{}.json".format(s_class)
        objs_json = {}

        # Serialize each object to a JSON-compatible format
        for obj_id, obj in DATA[s_class].items():
            objs_json[obj_id] = obj.to_json(True)

        # Write the serialized data to a file
        with open(file_path, 'w') as f:
            json.dump(objs_json, f)

    def save(self):
        """ Save the current object to the global DATA dictionary and update the file.
        This method updates the 'updated_at' timestamp and writes the object to the global dictionary.
        """
        s_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()  # Update the 'updated_at' timestamp
        DATA[s_class][self.id] = self  # Save the object in the global DATA dictionary
        self.__class__.save_to_file()  # Persist all objects to file

    def remove(self):
        """ Remove the current object from the global DATA dictionary and update the file.
        This method deletes the object from memory and writes the updated state to disk.
        """
        s_class = self.__class__.__name__
        if DATA[s_class].get(self.id) is not None:
            del DATA[s_class][self.id]  # Remove the object from the global dictionary
            self.__class__.save_to_file()  # Persist the changes to the file

    @classmethod
    def count(cls) -> int:
        """ Count the total number of objects of this class.
        Returns:
            int: The number of objects currently stored in the global DATA dictionary.
        """
        s_class = cls.__name__
        return len(DATA[s_class].keys())  # Return the count of objects in the DATA dictionary

    @classmethod
    def all(cls) -> Iterable[TypeVar('Base')]: # type: ignore
        """ Return all objects of this class.
        This method calls the search method with an empty filter to return all objects.
        Returns:
            list: A list of all objects of this class.
        """
        return cls.search()  # Return all objects by passing an empty dictionary as the filter

    @classmethod
    def get(cls, id: str) -> TypeVar('Base'): # type: ignore
        """ Get a single object by its ID.
        Args:
            id (str): The unique identifier of the object to retrieve.
        Returns:
            Base: The object with the specified ID, or None if not found.
        """
        s_class = cls.__name__
        return DATA[s_class].get(id)  # Return the object with the given ID, or None if not found

    @classmethod
    def search(cls, attributes: dict = {}) -> List[TypeVar('Base')]: # type: ignore
        """ Search for objects that match the specified attributes.
        Args:
            attributes (dict): A dictionary of attribute-value pairs to filter objects by.
        Returns:
            list: A list of objects that match the specified attributes.
        """
        s_class = cls.__name__

        def _search(obj):
            """ Helper function to check if an object matches the given attributes.
            Args:
                obj (Base): The object to check.
            Returns:
                bool: True if the object matches all attribute-value pairs, otherwise False.
            """
            if len(attributes) == 0:
                return True  # No filter, return all objects
            for k, v in attributes.items():
                if getattr(obj, k) != v:
                    return False  # If any attribute doesn't match, return False
            return True  # All attributes match

        # Filter objects using the helper function and return the list of matching objects
        return list(filter(_search, DATA[s_class].values()))
