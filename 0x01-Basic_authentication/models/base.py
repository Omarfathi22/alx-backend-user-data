#!/usr/bin/env python3
""" Base module
"""
from datetime import datetime
from typing import TypeVar, List, Iterable, Dict, Optional
from os import path
import json
import uuid


TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATA: Dict[str, Dict[str, 'Base']] = {}


class Base:
    """ Base class for all models with common attributes and methods. """

    def __init__(self, *args: list, **kwargs: dict):
        """ Initialize a Base instance """
        s_class = str(self.__class__.__name__)
        if DATA.get(s_class) is None:
            DATA[s_class] = {}

        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', self.created_at)

        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(self.created_at, TIMESTAMP_FORMAT)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.strptime(self.updated_at, TIMESTAMP_FORMAT)

    def __eq__(self, other: TypeVar('Base')) -> bool: # type: ignore
        """ Equality comparison """
        return isinstance(other, Base) and self.id == other.id

    def to_json(self, for_serialization: bool = False) -> dict:
        """ Convert the object to a JSON serializable dictionary """
        result = {}
        for key, value in self.__dict__.items():
            if not for_serialization and key[0] == '_':
                continue
            if isinstance(value, datetime):
                result[key] = value.strftime(TIMESTAMP_FORMAT)
            else:
                result[key] = value
        return result

    @classmethod
    def load_from_file(cls) -> None:
        """ Load all objects from the file into the class """
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        if not path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            try:
                objs_json = json.load(f)
                for obj_id, obj_json in objs_json.items():
                    DATA[s_class][obj_id] = cls(**obj_json)
            except json.JSONDecodeError:
                print(f"Error decoding {file_path}")

    @classmethod
    def save_to_file(cls) -> None:
        """ Save all objects to a JSON file """
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        objs_json = {obj_id: obj.to_json(True) for obj_id, obj in DATA[s_class].items()}

        try:
            with open(file_path, 'w') as f:
                json.dump(objs_json, f)
        except IOError as e:
            print(f"Error saving data to {file_path}: {e}")

    def save(self) -> None:
        """ Save the current object to the class data and file """
        s_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()
        DATA[s_class][self.id] = self
        self.__class__.save_to_file()

    def remove(self) -> None:
        """ Remove the object from the class data and file """
        s_class = self.__class__.__name__
        if self.id in DATA[s_class]:
            del DATA[s_class][self.id]
            self.__class__.save_to_file()

    @classmethod
    def count(cls) -> int:
        """ Count the number of objects """
        s_class = cls.__name__
        return len(DATA[s_class])

    @classmethod
    def all(cls) -> Iterable[TypeVar('Base')]: # type: ignore
        """ Return all objects """
        return cls.search()

    @classmethod
    def get(cls, id: str) -> Optional[TypeVar('Base')]: # type: ignore
        """ Return an object by its ID """
        s_class = cls.__name__
        return DATA[s_class].get(id)

    @classmethod
    def search(cls, attributes: dict = {}) -> List[TypeVar('Base')]: # type: ignore
        """ Search for objects matching the given attributes """
        s_class = cls.__name__

        def _search(obj) -> bool:
            if not attributes:
                return True
            return all(getattr(obj, key) == value for key, value in attributes.items())

        return [obj for obj in DATA[s_class].values() if _search(obj)]
